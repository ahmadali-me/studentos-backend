from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

# Correct import for database connection from app folder
from app.database.connection import (
    academic_collection,
    attendance_collection,
    student_collection,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])

# Pydantic models for new endpoints
class GoalSchema(BaseModel):
    title: str
    is_completed: bool = False

class CGPASchema(BaseModel):
    cgpa: float

class StreakSchema(BaseModel):
    streak_count: int

# In-memory mock data for dashboard add-ons
goals_db = [{"id": 1, "title": "Complete DSA sheet", "is_completed": False}]
cgpa_db = {"cgpa": 8.5}
streak_db = {"streak_count": 5}


# --- CGPA Endpoints (Placed BEFORE dynamic route) ---
@router.get("/cgpa")
def get_cgpa():
    return cgpa_db

@router.post("/cgpa")
def update_cgpa(data: CGPASchema):
    cgpa_db["cgpa"] = data.cgpa
    return {"message": "CGPA updated successfully", "data": cgpa_db}


# --- Goals Endpoints (Placed BEFORE dynamic route) ---
@router.get("/goals")
def get_goals():
    return goals_db

@router.post("/goals")
def add_goal(goal: GoalSchema):
    new_id = len(goals_db) + 1
    new_goal = {"id": new_id, "title": goal.title, "is_completed": goal.is_completed}
    goals_db.append(new_goal)
    return new_goal

@router.put("/goals/{goal_id}")
def update_goal(goal_id: int, goal: GoalSchema):
    for g in goals_db:
        if g["id"] == goal_id:
            g["title"] = goal.title
            g["is_completed"] = goal.is_completed
            return {"message": "Goal updated", "goal": g}
    raise HTTPException(status_code=404, detail="Goal not found")

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    global goals_db
    goals_db = [g for g in goals_db if g["id"] != goal_id]
    return {"message": "Goal deleted successfully"}


# --- Streak Endpoints (Placed BEFORE dynamic route) ---
@router.get("/streak")
def get_streak():
    return streak_db

@router.post("/streak")
def update_streak(streak: StreakSchema):
    streak_db["streak_count"] = streak.streak_count
    return {"message": "Streak updated", "data": streak_db}


# --- Dynamic Route (Placed AFTER all static routes) ---
@router.get("/{roll_number}")
async def get_student_dashboard(roll_number: str):
    # 1. Fetch Student Profile
    student = await student_collection.find_one({"roll_number": roll_number})
    
    # Profile fallback agar specific roll number na mile
    if not student:
        student_name = "Student"
        department = "N/A"
        semester = "N/A"
    else:
        student_name = student.get("full_name", "Student")
        department = student.get("department", "N/A")
        semester = student.get("semester", "N/A")

    # 2. Calculate Total Academic PDFs
    total_resources = await academic_collection.count_documents({})

    # 3. Calculate Overall Attendance Percentage
    cursor = attendance_collection.find({"roll_number": roll_number})
    all_attendance = []
    async for doc in cursor:
        all_attendance.append(doc)
    
    total_classes = len(all_attendance)
    if total_classes > 0:
        total_present = sum(
            1 for r in all_attendance if r.get("status") == "Present"
        )
        attendance_percentage = round((total_present / total_classes) * 100, 2)
    else:
        attendance_percentage = 0.0

    # 4. Final Combined Dashboard Data
    return {
        "message": f"Welcome back, {student_name}! 🚀",
        "student_info": {
            "name": student_name,
            "roll_number": roll_number,
            "department": department,
            "semester": semester,
        },
        "attendance_summary": {
            "total_classes": total_classes,
            "overall_percentage": f"{attendance_percentage}%",
            "is_eligible": attendance_percentage >= 75.0,
        },
        "academic_summary": {
            "total_pdfs_available": total_resources
        }
    }