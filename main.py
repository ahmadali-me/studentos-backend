from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.academic import router as academic_router
from app.routes.attendance import router as attendance_router
from app.routes.student import router as student_router
from app.routes.dashboard import router as dashboard_router
from app.routes.jobs import router as jobs_router
from app.routes.ai_tools import router as ai_tools_router
from app.routes.community import router as community_router
from app.routes.upload import router as upload_router
from app.routes.subjects import router as subjects_router
from app.routes.pyqs import router as pyqs_router
from app.routes.videos import router as videos_router
from app.routes.notifications import router as notifications_router
from app.routes.admin import router as admin_router
from app.routes.resume_builder import router as resume_builder_router
from app.routes.settings import router as settings_router
from app.routes.companies import router as companies_router
from app.routes.internships import router as internships_router

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://student-os-frontend-eight.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers inclusion (with alias)
app.include_router(auth_router)
app.include_router(academic_router)
app.include_router(attendance_router)
app.include_router(student_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(ai_tools_router)
app.include_router(community_router)
app.include_router(upload_router)
app.include_router(subjects_router)
app.include_router(pyqs_router)
app.include_router(videos_router)
app.include_router(notifications_router)
app.include_router(admin_router)
app.include_router(resume_builder_router)
app.include_router(settings_router)
app.include_router(companies_router)
app.include_router(internships_router)

@app.get("/")
def read_root():
    return {"message": "StudentOS Backend is live!"}