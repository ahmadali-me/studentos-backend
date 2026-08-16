from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="", tags=["Companies & Internships"])

# Pre-filled dummy databases so frontend gets data immediately
companies_db = [
    {
        "id": 1,
        "name": "Google",
        "role": "Software Engineer",
        "location": "Bangalore",
        "package": "20 LPA"
    },
    {
        "id": 2,
        "name": "Microsoft",
        "role": "SDE-1",
        "location": "Hyderabad",
        "package": "18 LPA"
    }
]

internships_db = [
    {
        "id": 1,
        "title": "Backend Intern",
        "company_name": "Amazon",
        "stipend": "40,000/month",
        "duration": "6 Months"
    },
    {
        "id": 2,
        "title": "Frontend Intern",
        "company_name": "Adobe",
        "stipend": "50,000/month",
        "duration": "3 Months"
    }
]

class Company(BaseModel):
    name: str
    role: str
    location: str
    package: Optional[str] = None

class Internship(BaseModel):
    title: str
    company_name: str
    stipend: str
    duration: str

# --- Companies Endpoints ---
@router.get("/companies", response_model=List[dict])
def get_companies():
    return companies_db

@router.post("/companies", status_code=201)
def add_company(company: Company):
    new_id = len(companies_db) + 1
    new_comp = {"id": new_id, **company.dict()}
    companies_db.append(new_comp)
    return {"message": "Company added successfully!", "company": new_comp}

@router.delete("/companies/{company_id}")
def delete_company(company_id: int):
    global companies_db
    companies_db = [c for c in companies_db if c.get("id") != company_id]
    return {"message": "Company deleted successfully"}

# --- Internships Endpoints ---
@router.get("/internships", response_model=List[dict])
def get_internships():
    return internships_db

@router.post("/internships", status_code=201)
def add_internship(internship: Internship):
    new_id = len(internships_db) + 1
    new_intern = {"id": new_id, **internship.dict()}
    internships_db.append(new_intern)
    return {"message": "Internship added successfully!", "internship": new_intern}

@router.delete("/internships/{internship_id}")
def delete_internship(internship_id: int):
    global internships_db
    internships_db = [i for i in internships_db if i.get("id") != internship_id]
    return {"message": "Internship deleted successfully"}