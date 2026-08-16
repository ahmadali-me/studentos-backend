from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory mock database for notifications
notifications_db = [
    {"id": 1, "message": "Assignment submitted successfully", "is_read": False},
    {"id": 2, "message": "New timetable updated", "is_read": True}
]

class NotificationSchema(BaseModel):
    message: str
    is_read: bool = False

@router.get("/")
def get_notifications():
    return notifications_db

@router.post("/")
def create_notification(notif: NotificationSchema):
    new_id = len(notifications_db) + 1
    new_item = {"id": new_id, "message": notif.message, "is_read": notif.is_read}
    notifications_db.append(new_item)
    return new_item

@router.delete("/{notif_id}")
def delete_notification(notif_id: int):
    global notifications_db
    notifications_db = [n for n in notifications_db if n["id"] != notif_id]
    return {"message": "Notification deleted successfully"}

@router.put("/{notif_id}/read")
def mark_as_read(notif_id: int):
    for n in notifications_db:
        if n["id"] == notif_id:
            n["is_read"] = True
            return {"message": "Notification marked as read", "notification": n}
    raise HTTPException(status_code=404, detail="Notification not found")

@router.put("/read-all")
def mark_all_as_read():
    for n in notifications_db:
        n["is_read"] = True
    return {"message": "All notifications marked as read"}