import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongodb(self):
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("DATABASE_NAME", "enterprise_assistant")
        
        # Adaptive Retry Strategy (Stabilizes startup if DB is slow)
        max_retries = 5
        retry_delay = 5 # seconds
        
        for i in range(max_retries):
            try:
                # 5 second timeout for demo stability
                self.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
                self.db = self.client[db_name]
                # Simple ping to verify connection
                await self.client.admin.command('ping')
                print(f" [OK] DATABASE: Connected to {db_name}")
                return # Success
            except Exception as e:
                print(f" [!] DATABASE ATTEMPT {i+1} FAILED: Retrying in {retry_delay}s...")
                if i == max_retries - 1:
                    print(f" [!] FINAL DATABASE ERROR: {e}")
                    print(" [!] WARN: System running in 'Degraded Mode' (Limited History)")
                    self.db = None
                else:
                    await asyncio.sleep(retry_delay)

    async def close_mongodb_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

    # INTERNAL PROPERTIES: Allows 'db.chats' instead of 'db.db.chats'
    @property
    def chats(self):
        return self.db.chats if self.db is not None else None
    @property
    def users(self):
        return self.db.users if self.db is not None else None
    @property
    def documents(self):
        return self.db.documents if self.db is not None else None

from fastapi import HTTPException

db = Database()

async def get_database():
    if db.db is None:
        # Check one last time if it can connect 
        # (Useful if DB started late)
        await db.connect_to_mongodb()
        
    if db.db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database Connection Failed. Please ensure MongoDB is running on port 27017."
        )
    return db.db
