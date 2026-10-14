from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.nexus_models import Course, CourseSkill

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("")
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    res = []
    for c in courses:
        covered_skills = []
        for cs in c.course_skills:
            covered_skills.append({
                "skill_id": cs.skill_id,
                "skill_name": cs.skill.skill_name,
                "target_proficiency": float(cs.target_proficiency),
                "coverage_level": float(cs.coverage_level)
            })

        res.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "provider": c.provider,
            "difficulty": c.difficulty,
            "duration_hours": c.duration_hours,
            "course_url": c.course_url,
            "description": c.description,
            "covered_skills": covered_skills
        })
    return res

@router.get("/{course_id}")
def get_course_details(course_id: int, db: Session = Depends(get_db)):
    c = db.query(Course).filter(Course.course_id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
        
    covered_skills = []
    for cs in c.course_skills:
        covered_skills.append({
            "skill_id": cs.skill_id,
            "skill_name": cs.skill.skill_name,
            "target_proficiency": float(cs.target_proficiency),
            "coverage_level": float(cs.coverage_level)
        })

    return {
        "course_id": c.course_id,
        "course_name": c.course_name,
        "provider": c.provider,
        "difficulty": c.difficulty,
        "duration_hours": c.duration_hours,
        "course_url": c.course_url,
        "description": c.description,
        "covered_skills": covered_skills
    }
