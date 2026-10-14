from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.config import settings
from app.models.nexus_models import Student
from app.schemas.student import StudentCreate, StudentLogin, TokenResponse, StudentProfileResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/register", response_model=TokenResponse)
def register_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.email == student_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )
    
    hashed_pwd = hash_password(student_in.password)
    student = Student(
        name=student_in.name,
        email=student_in.email,
        password_hash=hashed_pwd,
        graduation_year=student_in.graduation_year,
        cgpa=student_in.cgpa,
        preferred_location=student_in.preferred_location,
        target_role=student_in.target_role
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    token = create_access_token({"sub": str(student.student_id), "email": student.email})
    return TokenResponse(
        access_token=token,
        student_id=student.student_id,
        name=student.name
    )

@router.post("/login", response_model=TokenResponse)
def login_student(login_in: StudentLogin, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == login_in.email).first()
    if not student or not verify_password(login_in.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(student.student_id), "email": student.email})
    return TokenResponse(
        access_token=token,
        student_id=student.student_id,
        name=student.name
    )
