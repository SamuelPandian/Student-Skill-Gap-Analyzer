from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.nexus_models import Job, JobSkill, Company, Skill
from app.schemas.job import JobResponse, JobSkillRequirementResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    result = []
    
    for job in jobs:
        req_skills = []
        for js in job.required_skills:
            req_skills.append(
                JobSkillRequirementResponse(
                    skill_id=js.skill_id,
                    skill_name=js.skill.skill_name,
                    category=js.skill.category,
                    required_proficiency=float(js.required_proficiency),
                    importance_weight=float(js.importance_weight),
                    is_mandatory=js.is_mandatory
                )
            )

        result.append(
            JobResponse(
                job_id=job.job_id,
                company_id=job.company_id,
                company_name=job.company.company_name,
                title=job.title,
                description=job.description,
                location=job.location,
                job_type=job.job_type,
                minimum_cgpa=float(job.minimum_cgpa),
                experience_requirement=job.experience_requirement,
                posted_date=job.posted_date,
                required_skills=req_skills
            )
        )
    return result

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    req_skills = []
    for js in job.required_skills:
        req_skills.append(
            JobSkillRequirementResponse(
                skill_id=js.skill_id,
                skill_name=js.skill.skill_name,
                category=js.skill.category,
                required_proficiency=float(js.required_proficiency),
                importance_weight=float(js.importance_weight),
                is_mandatory=js.is_mandatory
            )
        )

    return JobResponse(
        job_id=job.job_id,
        company_id=job.company_id,
        company_name=job.company.company_name,
        title=job.title,
        description=job.description,
        location=job.location,
        job_type=job.job_type,
        minimum_cgpa=float(job.minimum_cgpa),
        experience_requirement=job.experience_requirement,
        posted_date=job.posted_date,
        required_skills=req_skills
    )
