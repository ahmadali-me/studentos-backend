from pydantic import BaseModel

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "student"
    roll_number: str

class UserLogin(BaseModel):
    email: str
    password: str