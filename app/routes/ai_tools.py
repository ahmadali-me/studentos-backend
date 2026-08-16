import os
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Mentor"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat_with_ai(data: ChatRequest):
    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    user_msg = data.question.lower()
    
    # 1. ALARM ACTION CHECK
    if "alarm" in user_msg:
        time_match = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm))', user_msg)
        extracted_time = time_match.group(0) if time_match else "07:00 AM"
        
        return {
            "success": True,
            "question": data.question,
            "answer": f"I have processed your request. Alarm action triggered for {extracted_time}.",
            "action": {
                "type": "SET_ALARM",
                "time": extracted_time,
                "status": "pending_frontend"
            }
        }

    # 2. NORMAL GROQ AI CHAT
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are StudentOS AI Mentor. "
                        "Answer the user's questions clearly and helpfully. "
                        "You can answer general, academic, programming, "
                        "career, internship and random normal questions. "
                        "If you are unsure, honestly say so."
                    )
                },
                {
                    "role": "user",
                    "content": data.question
                }
            ]
        )
        
        answer = response.choices[0].message.content
        
        return {
            "success": True,
            "question": data.question,
            "answer": answer,
            "action": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI error: {str(e)}"
        )