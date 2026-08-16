import motor.motor_asyncio
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URL,
    tlsCAFile=certifi.where()
)

database = client.studentos_db

# Collections for all routes to prevent any import errors
academic_collection = database.get_collection("academic_resources")
internships_collection = database.get_collection("internships")
attendance_collection = database.get_collection("attendance")
student_collection = database.get_collection("students")
users_collection = database.get_collection("users")