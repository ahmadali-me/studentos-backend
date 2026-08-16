from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/resume", tags=["Resume Builder"])

class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: str
    education: str
    skills: str
    experience: Optional[str] = "Fresher"

resume_db = []

@router.post("/builder-data")
def save_resume_builder_data(data: ResumeData):
    resume_db.append(data)
    return {"message": "Resume builder data saved successfully!", "data": data}

@router.get("/builder-data")
def get_resume_builder_data():
    if resume_db:
        return resume_db[-1]
    return {"message": "No resume data found yet."}