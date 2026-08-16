from pydantic import BaseModel

class AttendanceMark(BaseModel):
    subject: str
    status: str  # "Present" ya "Absent"
    date: str    # "2026-03-01"