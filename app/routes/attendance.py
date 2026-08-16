from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

# Database Connection Import
from app.database.connection import attendance_collection

router = APIRouter(prefix="/attendance", tags=["Attendance System"])


# ------------------ SCHEMAS ------------------
class SingleAttendanceMark(BaseModel):
    roll_number: str
    subject: str
    status: str  # "Present" ya "Absent"
    date: Optional[str] = str(date.today())


class BulkAttendanceMark(BaseModel):
    subject: str
    date: Optional[str] = str(date.today())
    present_roll_numbers: List[str]
    absent_roll_numbers: List[str]


# ------------------ ENDPOINTS ------------------

# 1. Single Student Ki Attendance Mark Karo
@router.post("/mark")
async def mark_single_attendance(data: SingleAttendanceMark):
    if data.status.capitalize() not in ["Present", "Absent"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status sirf 'Present' ya 'Absent' ho sakta hai!",
        )

    record = {
        "roll_number": data.roll_number,
        "subject": data.subject,
        "status": data.status.capitalize(),
        "date": data.date,
    }

    result = await attendance_collection.insert_one(record)

    return {
        "message": f"Attendance for {data.roll_number} marked as {data.status}! ✅",
        "record_id": str(result.inserted_id),
    }


# 2. Bulk Class Attendance Mark Karo (Teacher / Admin View)
@router.post("/mark-bulk")
async def mark_bulk_attendance(data: BulkAttendanceMark):
    records = []

    for roll in data.present_roll_numbers:
        records.append(
            {
                "roll_number": roll,
                "subject": data.subject,
                "status": "Present",
                "date": data.date,
            }
        )

    for roll in data.absent_roll_numbers:
        records.append(
            {
                "roll_number": roll,
                "subject": data.subject,
                "status": "Absent",
                "date": data.date,
            }
        )

    if not records:
        raise HTTPException(
            status_code=400, detail="Koi roll number nahi mila!"
        )

    await attendance_collection.insert_many(records)

    return {
        "message": f"{len(records)} students ki attendance successfully record ho gayi! 🎉",
        "date": data.date,
        "subject": data.subject,
    }


# 3. Student Ki Saari Attendance History Nikalo
@router.get("/student/{roll_number}")
async def get_student_attendance_history(roll_number: str):
    cursor = attendance_collection.find({"roll_number": roll_number})
    history = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)

    return {
        "roll_number": roll_number,
        "total_records": len(history),
        "history": history,
    }


# 4. Student Ki Overall % aur Subject-wise Stats Nikalo 📊
@router.get("/stats/{roll_number}")
async def get_attendance_stats(roll_number: str):
    cursor = attendance_collection.find({"roll_number": roll_number})
    all_records = []

    async for doc in cursor:
        all_records.append(doc)

    if not all_records:
        return {
            "roll_number": roll_number,
            "overall_percentage": 0.0,
            "status": "No Attendance Record Found",
            "subjects": {},
        }

    total_classes = len(all_records)
    total_present = sum(
        1 for r in all_records if r.get("status") == "Present"
    )

    overall_percentage = round((total_present / total_classes) * 100, 2)

    # Subject-wise calculation
    subject_stats = {}
    for r in all_records:
        sub = r.get("subject", "General")
        if sub not in subject_stats:
            subject_stats[sub] = {"total": 0, "present": 0}

        subject_stats[sub]["total"] += 1
        if r.get("status") == "Present":
            subject_stats[sub]["present"] += 1

    # Format subject percentages
    for sub, counts in subject_stats.items():
        pct = round((counts["present"] / counts["total"]) * 100, 2)
        counts["percentage"] = f"{pct}%"

    return {
        "roll_number": roll_number,
        "total_classes": total_classes,
        "total_present": total_present,
        "overall_percentage": f"{overall_percentage}%",
        "eligible_for_exams": overall_percentage >= 75.0,
        "subject_breakdown": subject_stats,
    }