import uvicorn
import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.mongodb import db
from routes import auth, chat, documents, admin
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intelligent Enterprise Assistant AI")

# CORS Middleware (Hardened for local networking stability)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*" 
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from ai.engine import ai_engine

# Startup and Shutdown events
@app.on_event("startup")
async def startup():
    await db.connect_to_mongodb()
    logger.info("Application startup: MongoDB connected")
    
    # Run heavy AI loading in a BACKGROUND THREAD to prevent blocking port 8000
    import asyncio
    loop = asyncio.get_event_loop()
    def background_load():
        try:
            print(" [.] AI: Cognitive engine loading in background...")
            ai_engine._load_models()
            print(" [OK] AI ENGINE: READY (Knowledge Support Live)")
        except Exception as e:
            print(f" [!] AI ENGINE: Running in Lightweight Fallback Mode ({e})")
            
    loop.run_in_executor(None, background_load)
    logger.info(" [OK] SYSTEM: Intelligent Enterprise Assistant is RESPONSIVE.")

@app.on_event("shutdown")
async def shutdown():
    await db.close_mongodb_connection()
    logger.info("Application shutdown: MongoDB connection closed")

# Middleware for timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # ENSURE CORS ON EVERY SINGLE RESPONSE (Enterprise Stability)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Path: {request.url.path} | Time: {process_time:.4f}s")
    return response

# Global Error Handling with Explicit CORS support
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(documents.router, prefix="/api/documents", tags=["Document Processing"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Panel"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Intelligent Enterprise Assistant API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
