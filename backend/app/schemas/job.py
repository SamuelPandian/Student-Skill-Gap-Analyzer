from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class JobSkillRequirementResponse(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    required_proficiency: float
    importance_weight: float
    is_mandatory: bool

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    job_id: int
    company_id: int
    company_name: str
    title: str
    description: str
    location: Optional[str] = None
    job_type: str
    minimum_cgpa: float
    experience_requirement: str
    posted_date: Optional[date] = None
    required_skills: List[JobSkillRequirementResponse] = []

    class Config:
        from_attributes = True
