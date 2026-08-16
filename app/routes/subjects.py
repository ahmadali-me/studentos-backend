from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/subjects", tags=["Subjects"])

class SubjectResponse(BaseModel):
    subject_code: str
    subject_name: str
    semester: int

@router.get("/", response_model=List[SubjectResponse])
def get_subjects():
    return [
        {"subject_code": "CS101", "subject_name": "Data Structures and Algorithms", "semester": 3},
        {"subject_code": "CS102", "subject_name": "Operating Systems", "semester": 3},
        {"subject_code": "CS103", "subject_name": "Database Management Systems", "semester": 4}
    ]