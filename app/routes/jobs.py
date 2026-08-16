from datetime import date
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

# Database connection collection import
from app.database.connection import student_collection

# Create jobs collection from existing db connection
jobs_collection = student_collection.database["jobs"]

router = APIRouter(prefix="/jobs", tags=["Internships & Job Portal"])


# 1. Pydantic Schema Job Post karne ke liye
class JobCreateSchema(BaseModel):
    title: str  # e.g. "Frontend Developer Intern"
    company_name: str  # e.g. "Google" ya "TechCorp"
    job_type: str  # "Internship", "Full-time", "Part-time"
    location: str  # "Remote" ya "Mumbai, India"
    stipend_salary: str  # e.g. "₹15,000/month" ya "6 LPA"
    description: str
    skills_required: str  # e.g. "React, FastAPI, Python"
    apply_link: str  # Google Form ya career page ka URL
    posted_by: Optional[str] = "Placement Cell"


# ------------------ ENDPOINTS ------------------


# 1. Post a New Job / Internship (Admin / Placement Cell View)
@router.post("/create")
async def create_job_post(data: JobCreateSchema):
    new_job = data.model_dump()
    new_job["posted_date"] = str(date.today())

    result = await jobs_collection.insert_one(new_job)

    return {
        "message": f"Job/Internship '{data.title}' successfully post ho gayi! 🎉",
        "job_id": str(result.inserted_id),
    }


# 2. Get All Jobs / Filter Jobs (Student View)
@router.get("/all")
async def get_all_jobs(
    job_type: Optional[str] = Query(
        None, description="Filter by type: Internship / Full-time"
    ),
    title: Optional[str] = Query(None, description="Search by title"),
):
    query = {}

    if job_type:
        query["job_type"] = {"$regex": job_type, "$options": "i"}

    if title:
        query["title"] = {"$regex": title, "$options": "i"}

    jobs = []
    cursor = jobs_collection.find(query)

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        jobs.append(doc)

    return {"count": len(jobs), "jobs": jobs}


# 3. Get Specific Job Details by ID
@router.get("/{job_id}")
async def get_job_details(job_id: str):
    try:
        job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(
            status_code=400, detail="Invalid Job ID format!"
        )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Is ID se koi job nahi mili!",
        )

    job["_id"] = str(job["_id"])
    return job