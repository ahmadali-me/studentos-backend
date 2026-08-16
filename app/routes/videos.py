from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/videos", tags=["Videos"])

class VideoResponse(BaseModel):
    title: str
    subject: str
    video_url: str

@router.get("/", response_model=List[VideoResponse])
def get_videos():
    return [
        {"title": "Graphs and Trees Tutorial", "subject": "Data Structures", "video_url": "https://youtube.com/watch?v=example1"},
        {"title": "Process Synchronization", "subject": "Operating Systems", "video_url": "https://youtube.com/watch?v=example2"}
    ]