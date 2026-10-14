from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from app.database import get_db
from app.models.nexus_models import Student, StudentSkill, Skill, Resume, ProcessingStatus, SkillSource
from app.schemas.student import StudentProfileResponse, StudentSkillResponse, StudentSkillUpdate
from app.nlp.resume_parser import ResumeParser

router = APIRouter(prefix="/students", tags=["Students"])
parser = ResumeParser()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/{student_id}", response_model=StudentProfileResponse)
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Format student skills
    skills_list = []
    for ss in student.skills:
        skills_list.append(
            StudentSkillResponse(
                skill_id=ss.skill_id,
                skill_name=ss.skill.skill_name,
                category=ss.skill.category,
                proficiency_level=float(ss.proficiency_level),
                confidence_score=float(ss.confidence_score),
                source=ss.source,
                last_updated=ss.last_updated
            )
        )

    res = StudentProfileResponse(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        graduation_year=student.graduation_year,
        cgpa=float(student.cgpa) if student.cgpa else None,
        preferred_location=student.preferred_location,
        target_role=student.target_role,
        created_at=student.created_at,
        skills=skills_list
    )
    return res

@router.get("/{student_id}/skills", response_model=List[StudentSkillResponse])
def get_student_skills(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = []
    for ss in student.skills:
        result.append(
            StudentSkillResponse(
                skill_id=ss.skill_id,
                skill_name=ss.skill.skill_name,
                category=ss.skill.category,
                proficiency_level=float(ss.proficiency_level),
                confidence_score=float(ss.confidence_score),
                source=ss.source,
                last_updated=ss.last_updated
            )
        )
    return result

@router.put("/{student_id}/skills")
def update_student_skill(student_id: int, update_in: StudentSkillUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    skill = db.query(Skill).filter(Skill.skill_id == update_in.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing_skill = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_id,
        StudentSkill.skill_id == update_in.skill_id
    ).first()

    if existing_skill:
        existing_skill.proficiency_level = update_in.proficiency_level
        existing_skill.source = SkillSource(update_in.source or "SELF_ASSESSMENT")
    else:
        new_ss = StudentSkill(
            student_id=student_id,
            skill_id=update_in.skill_id,
            proficiency_level=update_in.proficiency_level,
            confidence_score=1.00,
            source=SkillSource(update_in.source or "SELF_ASSESSMENT")
        )
        db.add(new_ss)

    db.commit()
    return {"message": "Student skill updated successfully", "student_id": student_id, "skill_id": update_in.skill_id}

@router.post("/{student_id}/resume")
async def upload_student_resume(
    student_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    file_path = os.path.join(UPLOAD_DIR, f"{student_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save Resume Record
    resume_rec = Resume(
        student_id=student_id,
        file_name=file.filename,
        file_path=file_path,
        processing_status=ProcessingStatus.PROCESSING
    )
    db.add(resume_rec)
    db.commit()
    db.refresh(resume_rec)

    # Extract plain text & skills
    all_skills = db.query(Skill).all()
    canonical_skill_names = [s.skill_name for s in all_skills]
    skill_map = {s.skill_name.lower(): s.skill_id for s in all_skills}

    try:
        parsed_data = parser.parse_resume(file_path, canonical_skill_names)
        resume_rec.parsed_text = parsed_data["parsed_text"]
        resume_rec.processing_status = ProcessingStatus.COMPLETED

        # Update candidate name from resume if detected
        extracted_name = parsed_data.get("candidate_name")
        if extracted_name and len(extracted_name) > 2:
            student.name = extracted_name

        # Clean prior resume-sourced skills so the profile accurately reflects ONLY the newly uploaded resume
        db.query(StudentSkill).filter(
            StudentSkill.student_id == student_id,
            StudentSkill.source == SkillSource.RESUME
        ).delete(synchronize_session=False)

        # Update STUDENT_SKILL table with newly parsed evidence
        detected = parsed_data["detected_skills"]
        for d in detected:
            s_name = d["skill_name"].lower()
            if s_name in skill_map:
                s_id = skill_map[s_name]
                st_skill = db.query(StudentSkill).filter(
                    StudentSkill.student_id == student_id,
                    StudentSkill.skill_id == s_id
                ).first()

                if st_skill:
                    st_skill.proficiency_level = d["proficiency_level"]
                    st_skill.confidence_score = d["confidence_score"]
                    st_skill.source = SkillSource.RESUME
                    st_skill.evidence_text = d["evidence_text"]
                else:
                    db.add(
                        StudentSkill(
                            student_id=student_id,
                            skill_id=s_id,
                            proficiency_level=d["proficiency_level"],
                            confidence_score=d["confidence_score"],
                            source=SkillSource.RESUME,
                            evidence_text=d["evidence_text"]
                        )
                    )

        db.commit()

        # Query updated full skills list for the student
        updated_skills = [
            {
                "skill_id": ss.skill_id,
                "skill_name": ss.skill.skill_name,
                "proficiency_level": float(ss.proficiency_level),
                "source": ss.source.value
            }
            for ss in student.skills
        ]

        return {
            "message": "Resume uploaded and processed successfully",
            "resume_id": resume_rec.resume_id,
            "student_id": student.student_id,
            "student_name": student.name,
            "detected_skills_count": len(detected),
            "detected_skills": detected,
            "updated_skills": updated_skills
        }
    except Exception as e:
        resume_rec.processing_status = ProcessingStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {e}")
