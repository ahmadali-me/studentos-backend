from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

@router.get("/users", response_model=List[UserResponse])
def get_admin_users():
    return [
        {"id": 1, "name": "Ahmad Ali", "email": "ahmad@example.com", "role": "Student"},
        {"id": 2, "name": "Rahul Sharma", "email": "rahul@example.com", "role": "Student"},
        {"id": 3, "name": "Dr. Professor", "email": "prof@college.edu", "role": "Admin"}
    ]

@router.get("/analytics")
def get_admin_analytics():
    return {
        "total_students": 320,
        "active_courses": 12,
        "total_uploads": 45,
        "system_status": "Healthy"
    }

@router.get("/reports")
def get_admin_reports():
    return {
        "reports": [
            "Attendance Report - August",
            "Placement Performance Report",
            "Fee Clearance Status"
        ]
    }

@router.get("/feedback")
def get_admin_feedback():
    return [
        {"user": "Rahul Sharma", "feedback": "The UI looks great and fast!", "date": "2026-08-11"},
        {"user": "Ahmad Ali", "feedback": "Dark mode feature is working smoothly.", "date": "2026-08-12"}
    ]

@router.delete("/users/{user_id}")
def delete_admin_user(user_id: int):
    return {"message": f"User with ID {user_id} deleted successfully"}