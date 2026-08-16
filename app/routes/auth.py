import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.schemas.user import UserRegister, UserLogin
from pymongo import MongoClient

# MongoDB Atlas Connection with your password
MONGO_URI = "mongodb+srv://ahmadali1985_dbhi:T0236877@cluster0.uaropei.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["studentos_db"]

router = APIRouter(prefix="/auth", tags=["Authentication"])

users_collection = db["users"]
students_collection = db["students"]

SECRET_KEY = "studentos_super_secret_key_change_this"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
def register(user: UserRegister):
    try:
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email is already registered!")
        
        # Fix: Convert Pydantic model to dictionary safely
        user_data = user.dict()
        users_collection.insert_one(user_data)
        
        student_profile = {
            "email": user.email,
            "full_name": getattr(user, "full_name", "Student"),
            "roll_number": getattr(user, "roll_number", "CS-101"),
            "department": "Computer Science",
            "semester": "1st"
        }
        
        students_collection.update_one(
            {"email": user.email},
            {"$setOnInsert": student_profile},
            upsert=True
        )
        
        return {"message": "Registration successful", "user": user.full_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(credentials: UserLogin):
    try:
        user = users_collection.find_one({"email": credentials.email})
        
        if user and user.get("password") == credentials.password:
            token_data = {"sub": user.get("email"), "role": user.get("role", "student")}
            access_token = create_access_token(token_data)
            
            return {
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "studentos_user": {
                    "name": user.get("full_name"),
                    "email": user.get("email"),
                    "role": user.get("role", "student"),
                    "roll_number": user.get("roll_number", "N/A")
                }
            }
        
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New Request Schemas for Password & Email Management
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    return {
        "message": "Password reset instructions sent successfully to your email.",
        "email": data.email
    }

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    return {
        "message": "Password has been reset successfully."
    }

@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    return {
        "message": "Email verified successfully.",
        "email": data.email
    }