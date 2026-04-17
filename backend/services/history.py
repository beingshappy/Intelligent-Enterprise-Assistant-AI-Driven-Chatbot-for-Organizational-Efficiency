from datetime import datetime
from database.mongodb import db
from typing import List, Dict
from bson import ObjectId

class HistoryService:
    @staticmethod
    async def add_message(user_id: str, content: str, is_user: bool, role: str = "assistant"):
        message = {
            "user_id": user_id,
            "content": content,
            "is_user": is_user,
            "role": role,
            "timestamp": datetime.utcnow()
        }
        await db.chats.insert_one(message)

    @staticmethod
    async def get_history(user_id: str, limit: int = 10) -> List[Dict]:
        cursor = db.chats.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        history = []
        async for msg in cursor:
            # Format for the AI engine
            history.append({
                "content": msg["content"],
                "is_user": msg["is_user"],
                "timestamp": msg["timestamp"]
            })
        # Reverse to get chronological order [oldest -> newest]
        return history[::-1]

    @staticmethod
    async def clear_history(user_id: str):
        await db.chats.delete_many({"user_id": user_id})

history_service = HistoryService()
