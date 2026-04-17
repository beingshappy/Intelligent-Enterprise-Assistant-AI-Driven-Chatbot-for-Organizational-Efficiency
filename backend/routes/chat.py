from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import List, Optional
from database.mongodb import get_database
from models.chat import ChatRequest, ChatResponse, Message
from ai.engine import ai_engine
from utils.auth import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.history import history_service
from middleware.ratelimit import limit_chat
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_access_token(auth.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.get("/history", response_model=List[Message])
async def get_chat_history(current_user = Depends(get_current_user)):
    user_email = current_user["sub"]
    try:
        history = await history_service.get_history(user_email)
        return history
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return []

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, req: Request, db = Depends(get_database), user = Depends(get_current_user)):
    # Apply Rate Limit
    await limit_chat.check_rate_limit(req)
    
    user_email = user["sub"]
    logger.info(f"Chat request from {user_email}: {request.message}")
    
    try:
        # 1. Detect Intent and Filter Bad Language
        is_bad, warning = ai_engine.filter_bad_language(request.message)
        if is_bad:
            # Safe violation logging (don't crash if DB fails here)
            try:
                await history_service.add_message(user_email, request.message, True)
                await history_service.add_message(user_email, warning, False)
            except: pass
            return ChatResponse(response=warning, context_used=False)

        # 2. Retrieve Conversation Context (History) - Fail-Safe
        history = []
        try:
            history = await history_service.get_history(user_email, limit=5)
        except Exception as e:
            logger.warning(f"History retrieval failed: {e}")
        
        # 3. Retrieve Knowledge Context (RAG) - Fail-Safe
        context = ""
        try:
            if db is not None:
                context = await ai_engine.get_relevant_context(request.message, db)
            else:
                logger.warning("Database unavailable, skipping RAG context retrieval.")
        except Exception as e:
            logger.warning(f"RAG Context retrieval failed: {e}")
        
        # 4. Generate AI Response
        response_text = await ai_engine.generate_response(request.message, context, history)
        
        # 5. Persist the interaction - Fail-Safe
        try:
            await history_service.add_message(user_email, request.message, True)
            await history_service.add_message(user_email, response_text, False)
        except: pass
        
        return ChatResponse(
            response=response_text,
            context_used=bool(context),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Chat Execution Fallback: {e}")
        # High-stability emergency reply
        return ChatResponse(
            response="[Safety Mode] I'm ready to assist with your documents. Please rephrase or try again in a moment.",
            context_used=False
        )
