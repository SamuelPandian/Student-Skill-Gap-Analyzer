from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    preferred_location: Optional[str] = None
    target_role: Optional[str] = None

class StudentCreate(StudentBase):
    password: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_id: int
    name: str

class StudentSkillUpdate(BaseModel):
    skill_id: int
    proficiency_level: float = Field(..., ge=0.0, le=5.0)
    source: Optional[str] = "SELF_ASSESSMENT"

class StudentSkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    proficiency_level: float
    confidence_score: float
    source: str
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class StudentProfileResponse(StudentBase):
    student_id: int
    created_at: datetime
    skills: List[StudentSkillResponse] = []

    class Config:
        from_attributes = True
