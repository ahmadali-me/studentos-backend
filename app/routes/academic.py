import os
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

# DB Connection import
from app.database.connection import academic_collection

router = APIRouter(prefix="/academic", tags=["Academic Resources"])

# Uploads folder path setup
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 1. Upload PDF Endpoint
@router.post("/upload-pdf")
async def upload_pdf(
    title: str = Form(...),
    subject: str = Form(...),
    semester: int = Form(...),
    resource_type: str = Form(...),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Only PDF files are allowed!"
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file asynchronously
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        file_url = f"/uploads/{file.filename}"

        # Document structure for MongoDB
        new_resource = {
            "title": title,
            "subject": subject,
            "semester": semester,
            "resource_type": resource_type,
            "uploaded_by": uploaded_by,
            "file_url": file_url,
        }

        # Motor (Async) insert with await
        result = await academic_collection.insert_one(new_resource)

        return {
            "message": (
                f"Syllabus PDF '{file.filename}' uploaded successfully! 🚀"
            ),
            "resource_id": str(result.inserted_id),
            "file_path": file_url,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# 2. Get All Resources (JSON Format List)
@router.get("/resources")
async def get_resources(
    title: Optional[str] = Query(
        None, description="Search directly by PDF name/title"
    ),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    resource_type: Optional[str] = Query(None, description="Filter by type"),
):
    query = {}

    if title:
        query["title"] = {"$regex": title, "$options": "i"}

    if subject:
        query["subject"] = {"$regex": subject, "$options": "i"}

    if semester is not None:
        query["semester"] = semester

    if resource_type:
        query["resource_type"] = resource_type

    resources = []
    cursor = academic_collection.find(query)

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resources.append(doc)

    return {"count": len(resources), "resources": resources}


# 3. Direct View/Download PDF (Single Click Endpoint) 🚀
@router.get("/view-pdf")
async def view_pdf(
    title: str = Query(..., description="Enter PDF title/name to view directly")
):
    # Database me title dhoondo
    resource = await academic_collection.find_one({"title": {"$regex": title, "$options": "i"}})
    
    if not resource:
        raise HTTPException(status_code=404, detail="Is title se koi PDF nahi mili!")

    # File path nikal kar verify karo
    file_name = resource["file_url"].replace("/uploads/", "")
    file_path = os.path.join(UPLOAD_DIR, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file server par nahi mili!")

    # Direct PDF file browser me open kar do
    return FileResponse(file_path, media_type="application/pdf", filename=file_name)