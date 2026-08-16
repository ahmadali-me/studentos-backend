from fastapi import APIRouter, File, UploadFile, HTTPException, status
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import motor.motor_asyncio
import certifi
from bson import ObjectId

load_dotenv()

router = APIRouter(prefix="/upload", tags=["File Management"])

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Direct yahi par connection bana liya taaki circular import ka chakkar hi khatam ho jaye
MONGO_URL = os.getenv("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
database = client.studentos_db
files_collection = database["uploaded_files"]

@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file, folder="studentos/images")
        file_data = {
            "filename": file.filename,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "file_type": "image"
        }
        await files_collection.insert_one(file_data)
        return {
            "message": "Image uploaded successfully!",
            "data": {k: v for k, v in file_data.items() if k != "_id"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed!")
    try:
        result = cloudinary.uploader.upload(file.file, folder="studentos/pdfs", resource_type="raw")
        file_data = {
            "filename": file.filename,
            "url": result.get("url"),
            "public_id": result.get("public_id"),
            "file_type": "pdf"
        }
        await files_collection.insert_one(file_data)
        return {
            "message": "PDF uploaded successfully!",
            "data": {k: v for k, v in file_data.items() if k != "_id"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF resumes are allowed!")
    try:
        result = cloudinary.uploader.upload(file.file, folder="studentos/resumes", resource_type="raw")
        file_data = {
            "filename": file.filename,
            "url": result.get("url"),
            "public_id": result.get("public_id"),
            "file_type": "resume"
        }
        await files_collection.insert_one(file_data)
        return {
            "message": "Resume uploaded successfully!",
            "url": result.get("url"),
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-files")
async def get_all_files():
    try:
        cursor = files_collection.find({})
        all_files = await cursor.to_list(length=100)

        images = []
        pdfs = []

        for f in all_files:
            file_id_str = str(f.get("_id"))
            file_info = {
                "id": file_id_str,
                "file_id": file_id_str,
                "filename": f.get("filename"),
                "url": f.get("url"),
                "file_type": f.get("file_type")
            }
            if f.get("file_type") == "image":
                images.append(file_info)
            elif f.get("file_type") in ["pdf", "resume"]:
                pdfs.append(file_info)

        return {
            "images": images,
            "pdfs": pdfs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(file_id: str):
    try:
        obj_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_record = await files_collection.find_one({"_id": obj_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    if "public_id" in file_record and file_record["public_id"]:
        try:
            resource_type = "raw" if file_record.get("file_type") in ["pdf", "resume"] else "image"
            cloudinary.uploader.destroy(file_record["public_id"], resource_type=resource_type)
        except Exception:
            pass
            
    await files_collection.delete_one({"_id": obj_id})
    return {"message": "File deleted successfully", "file_id": file_id}

@router.put("/{file_id}", status_code=status.HTTP_200_OK)
async def replace_file(file_id: str, file: UploadFile = File(...)):
    try:
        obj_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_record = await files_collection.find_one({"_id": obj_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_type = file_record.get("file_type", "image")
    folder = "studentos/images"
    resource_type = "image"
    if file_type == "pdf":
        folder = "studentos/pdfs"
        resource_type = "raw"
    elif file_type == "resume":
        folder = "studentos/resumes"
        resource_type = "raw"

    try:
        result = cloudinary.uploader.upload(file.file, folder=folder, resource_type=resource_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
    
    if "public_id" in file_record and file_record["public_id"]:
        try:
            cloudinary.uploader.destroy(file_record["public_id"], resource_type=resource_type)
        except Exception:
            pass

    update_data = {
        "filename": file.filename,
        "url": result.get("secure_url") or result.get("url"),
        "public_id": result.get("public_id")
    }
    
    await files_collection.update_one({"_id": obj_id}, {"$set": update_data})
    
    return {
        "message": "File replaced successfully",
        "file_id": file_id,
        "url": update_data["url"],
        "filename": update_data["filename"]
    }