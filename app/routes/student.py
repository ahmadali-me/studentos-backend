from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

# Database connection import
from app.database.connection import student_collection
from app.schemas.student import StudentProfileUpdate

router = APIRouter(prefix="/student", tags=["Student Profile"])


# 1. Get Student Profile (From MongoDB)
@router.get("/me")
async def get_my_profile(
    roll_number: Optional[str] = Query("CS-101", description="Student Roll Number")
):
    student = await student_collection.find_one({"roll_number": roll_number})

    if not student:
        # Fallback if DB is empty: return first student
        student = await student_collection.find_one({})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database me koi student profile nahi mili!"
            )

    student["_id"] = str(student["_id"])
    return student


# 2. Update Student Profile (In MongoDB)
@router.put("/me")
async def update_profile(
    data: StudentProfileUpdate,
    roll_number: str = Query("CS-101", description="Roll number to update")
):
    # Only get fields that user actually provided
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update karne ke liye koi valid data nahi mila!"
        )

    # MongoDB me update query
    result = await student_collection.update_one(
        {"roll_number": roll_number},
        {"$set": update_data},
        upsert=True  # Agar student exist nahi karta toh naya create kar dega
    )

    # Fetch updated profile
    updated_student = await student_collection.find_one({"roll_number": roll_number})
    if updated_student:
        updated_student["_id"] = str(updated_student["_id"])

    return {
        "message": "Profile updated successfully! 🎉",
        "student": updated_student
    }