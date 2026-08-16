from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    date: str

class NotificationCreate(BaseModel):
    title: str
    message: str
    date: Optional[str] = "2026-08-16"

@router.get("/", response_model=List[NotificationResponse])
def get_notifications():
    return [
        {"id": 1, "title": "Assignment Due", "message": "Submit your DBMS assignment by Friday.", "date": "2026-08-12"},
        {"id": 2, "title": "Exam Schedule", "message": "Mid-sem timetable has been released.", "date": "2026-08-10"}
    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate):
    return {
        "message": "Notification created successfully",
        "data": {
            "id": 3,
            "title": notification.title,
            "message": notification.message,
            "date": notification.date
        }
    }

@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(notification_id: int):
    return {
        "message": "Notification deleted successfully",
        "id": notification_id
    }