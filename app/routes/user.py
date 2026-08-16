from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
# Apne database collections yahan import kar lena jahan se connect kiya hai
# from app.routes.auth import users_collection, students_collection

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_by_admin(user_id: str):
    try:
        # Check if user_id is a valid ObjectId format for MongoDB
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
            
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Optional: students collection se bhi data delete karna ho toh
        # students_collection.delete_one({"user_id": user_id}) 
        
        return {"message": "User deleted successfully by admin"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))