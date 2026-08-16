from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.database.connection import database

router = APIRouter(
    prefix="/api/internships",
    tags=["Internships"]
)

class InternshipSchema(BaseModel):
    title: str
    company: str
    role: Optional[str] = None
    location: Optional[str] = None
    stipend: Optional[str] = None
    description: Optional[str] = None
    apply_link: Optional[str] = None

class ApplicationSchema(BaseModel):
    student_name: str
    email: str
    roll_number: str

internships_collection = database.get_collection("internships")
applications_collection = database.get_collection("internship_applications")

@router.get("/", response_model=List[dict])
async def get_all_internships():
    internships = []
    cursor = internships_collection.find({})
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        # Ensure role and location are explicitly returned if present
        document["role"] = document.get("role", "N/A")
        document["location"] = document.get("location", "N/A")
        internships.append(document)
    return internships

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_internship(internship: InternshipSchema):
    internship_dict = internship.dict()
    result = await internships_collection.insert_one(internship_dict)
    return {
        "message": "Internship created successfully!",
        "id": str(result.inserted_id)
    }

@router.get("/{internship_id}")
async def get_internship_by_id(internship_id: str):
    from bson import ObjectId
    try:
        obj_id = ObjectId(internship_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid internship ID format")
    
    internship = await internships_collection.find_one({"_id": obj_id})
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    internship["id"] = str(internship["_id"])
    del internship["_id"]
    return internship

@router.post("/{internship_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_internship(internship_id: str, application: ApplicationSchema):
    from bson import ObjectId
    try:
        obj_id = ObjectId(internship_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid internship ID format")
    
    internship = await internships_collection.find_one({"_id": obj_id})
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    application_data = application.dict()
    application_data["internship_id"] = internship_id
    application_data["internship_title"] = internship.get("title")
    
    result = await applications_collection.insert_one(application_data)
    return {
        "message": "Successfully applied for the internship!",
        "application_id": str(result.inserted_id)
    }