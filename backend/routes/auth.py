from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import List
from models.user import UserCreate, UserInDB, UserResponse, UserBase
from database.mongodb import get_database
from utils.auth import get_password_hash, verify_password, create_access_token
from services.otp import otp_service
from pydantic import BaseModel, EmailStr
from fastapi import Request
from middleware.ratelimit import limit_auth

router = APIRouter()

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db = Depends(get_database)):
    # Normalize email
    user_email = user.email.lower().strip()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = user.dict()
    user_dict["email"] = user_email # Ensure normalized email is stored
    hashed_password = get_password_hash(user_dict.pop("password"))
    
    new_user = UserInDB(
        **user_dict,
        hashed_password=hashed_password,
        is_verified=False
    )
    
    result = await db.users.insert_one(new_user.dict(by_alias=True, exclude_none=True))
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    # Format for response
    created_user["id"] = str(created_user["_id"])
    return created_user

@router.post("/login")
async def login(credentials: LoginRequest, req: Request, db = Depends(get_database)):
    # Apply Rate Limit
    await limit_auth.check_rate_limit(req)
    
    # Normalize email for lookup
    lookup_email = credentials.email.lower().strip()
    user = await db.users.find_one({"email": lookup_email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate OTP (Master code for demo admin)
    otp = "123456" if credentials.email == "admin@company.com" else otp_service.generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=60)
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"otp": otp, "otp_expiry": expiry}}
    )
    
    # Send OTP (Still send/log it for other users)
    if credentials.email != "admin@company.com":
        otp_service.send_otp(user["email"], otp)
    else:
        # Just log it for the admin in the background
        print(f"\n[DEMO] ADMIN LOGIN DETECTED. MASTER CODE: {otp}\n")
    
    return {"message": "OTP sent to your email"}

@router.post("/verify-otp")
async def verify_otp(request: OTPVerifyRequest, db = Depends(get_database)):
    # Normalize email for consistent lookup
    lookup_email = request.email.lower().strip()
    user = await db.users.find_one({"email": lookup_email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Sanitized check (strip any accidental spaces from user input)
    submitted_otp = request.otp.strip()
    if not user.get("otp") or user.get("otp") != submitted_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > user.get("otp_expiry"):
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Verify user
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"is_verified": True, "otp": None, "otp_expiry": None}}
    )
    
    # Create token
    access_token = create_access_token(data={"sub": str(user["email"]), "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
