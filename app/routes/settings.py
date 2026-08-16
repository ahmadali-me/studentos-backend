from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class UserSettings(BaseModel):
    dark_mode: bool = True
    email_notifications: bool = True
    push_notifications: bool = True

current_settings = UserSettings()

@router.get("/")
def get_settings():
    return current_settings

@router.put("/")
def update_settings(settings: UserSettings):
    global current_settings
    current_settings = settings
    return {"message": "Settings updated successfully!", "settings": current_settings}