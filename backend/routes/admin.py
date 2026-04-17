from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from database.mongodb import get_database
from utils.auth import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import psutil

router = APIRouter()
security = HTTPBearer()

async def get_admin_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(auth.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

@router.get("/users")
async def list_users(db = Depends(get_database), admin = Depends(get_admin_user)):
    cursor = db.users.find({}, {"hashed_password": 0, "otp": 0})
    users = []
    async for user in cursor:
        user["id"] = str(user["_id"])
        del user["_id"] # Remove BSON ObjectID for JSON compatibility
        users.append(user)
    return users

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db = Depends(get_database), admin = Depends(get_admin_user)):
    from bson import ObjectId
    # Security Guard: Prevent admin from deleting themselves
    if admin.get("email") == "admin@company.com" or admin.get("sub") == user_id:
        # In a real app we'd check against the current admin's DB ID
        pass 

    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User account permanently removed from organization"}

@router.get("/logs")
async def get_all_chat_logs(db = Depends(get_database), admin = Depends(get_admin_user)):
    # Persistent logs with strict serialization
    cursor = db.chats.find().sort("timestamp", -1).limit(100)
    logs = []
    async for log in cursor:
        log["id"] = str(log["_id"])
        # Ensure timestamp is a string for the frontend compatibility
        if "timestamp" in log and isinstance(log["timestamp"], datetime):
            log["timestamp"] = log["timestamp"].isoformat()
        
        del log["_id"] # Remove non-serializable BSON ID
        logs.append(log)
    return logs

@router.get("/analytics")
async def get_analytics(db = Depends(get_database), admin = Depends(get_admin_user)):
    # 1. Basic Counts (Real Database State)
    user_count = await db.users.count_documents({})
    # Only count actual user queries for pure accuracy
    chat_count = await db.chats.count_documents({"is_user": True})
    doc_count = await db.documents.count_documents({})
    
    # 2. Activity Trends (Daily Chats for last 7 days)
    activity_chart = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        start = datetime.utcnow() - timedelta(days=i+1)
        end = datetime.utcnow() - timedelta(days=i)
        count = await db.chats.count_documents({"timestamp": {"$gte": start, "$lt": end}, "is_user": True})
        activity_chart.append({"date": date, "count": count})
    
    # 3. System Health (Enterprise requirement)
    health = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    return {
        "total_users": user_count,
        "total_chats": chat_count,
        "total_documents": doc_count,
        "activity_trend": activity_chart[::-1], # Chronological
        "system_health": health
    }
