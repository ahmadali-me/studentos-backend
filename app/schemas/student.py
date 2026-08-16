from pydantic import BaseModel
from typing import Optional

class StudentProfileUpdate(BaseModel):
    roll_number: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    phone: Optional[str] = None