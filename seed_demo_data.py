import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv
from passlib.context import CryptContext

# Define the same password context as in the app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv(dotenv_path="backend/.env")

async def seed_data():
    print("[SEED] Starting Demo Data Seeding...")
    
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "enterprise_assistant")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    # Sample Documents
    docs = [
        {
            "filename": "HR_Policy_2024.pdf",
            "content_type": "application/pdf",
            "extracted_text": "Company employees are entitled to 20 days of paid annual leave. Sick leave requires a medical certificate if longer than 3 days. Performance bonuses are distributed every March.",
            "keywords": ["leave", "policy", "bonus"],
            "summary": "Standard HR policy regarding annual leave and bonuses.",
            "uploaded_by": "admin@company.com",
            "upload_date": datetime.utcnow()
        },
        {
            "filename": "IT_Support_Manual.docx",
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "extracted_text": "To reset your password, visit portal.company.com. For hardware issues, raise a ticket at it-helpdesk. Laptop replacements occur every 3 years for all staff.",
            "keywords": ["password", "hardware", "ticket"],
            "summary": "Technical support guidelines for employees.",
            "uploaded_by": "admin@company.com",
            "upload_date": datetime.utcnow()
        }
    ]

    try:
        await db.documents.delete_many({}) 
        await db.documents.insert_many(docs)
        print(f"OK - Inserted {len(docs)} sample documents.")

        # Create a default admin user (password: admin123)
        hashed_password = pwd_context.hash("admin123")
        
        admin_user = {
            "name": "Admin User",
            "email": "admin@company.com",
            "role": "admin",
            "hashed_password": hashed_password,
            "is_verified": True,
            "created_at": datetime.utcnow()
        }
        
        await db.users.delete_many({"email": "admin@company.com"})
        await db.users.insert_one(admin_user)
        print("OK - Created Admin User: admin@company.com / admin123")

        # Create a default staff user (password: employee123)
        staff_user = {
            "name": "Staff Member",
            "email": "employee@company.com",
            "role": "employee",
            "hashed_password": pwd_context.hash("employee123"),
            "is_verified": True,
            "created_at": datetime.utcnow()
        }
        await db.users.delete_many({"email": "employee@company.com"})
        await db.users.insert_one(staff_user)
        print("OK - Created Employee User: employee@company.com / employee123")

        print("\nSUCCESS: Seeding Complete! System ready for demo.")
    except Exception as e:
        print(f"FAIL - Seeding failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
