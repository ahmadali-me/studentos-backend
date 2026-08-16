from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    date: str

@router.get("/", response_model=List[NotificationResponse])
def get_notifications():
    return [
        {"id": 1, "title": "Assignment Due", "message": "Submit your DBMS assignment by Friday.", "date": "2026-08-12"},
        {"id": 2, "title": "Exam Schedule", "message": "Mid-sem timetable has been released.", "date": "2026-08-10"}
    ]