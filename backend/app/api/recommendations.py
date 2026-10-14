from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date

from app.database import get_db
from app.models.nexus_models import (
    Student, Job, SkillPrerequisite, StudentSkill, 
    Course, CourseSkill, LearningProgress, ProgressStatus, SkillSource
)
from app.graph.prerequisites import (
    PrerequisiteEdge, generate_ordered_learning_path
)

router = APIRouter(prefix="/students", tags=["Recommendations & Learning Path"])

@router.get("/{student_id}/learning-path")
def get_student_learning_path(student_id: int, target_job_id: int = None, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # If job not specified, get first job or student's target role job
    if target_job_id:
        job = db.query(Job).filter(Job.job_id == target_job_id).first()
    else:
        job = db.query(Job).first()

    if not job:
        raise HTTPException(status_code=400, detail="No target job found to evaluate learning path")

    # Fetch student skills
    student_skills_map = {ss.skill_id: float(ss.proficiency_level) for ss in student.skills}
    satisfied_skills = {s_id for s_id, lvl in student_skills_map.items() if lvl >= 3.0}

    # Fetch job required skills
    gaps = {}
    skill_names = {}
    for js in job.required_skills:
        skill_names[js.skill_id] = js.skill.skill_name
        curr_lvl = student_skills_map.get(js.skill_id, 0.0)
        req_lvl = float(js.required_proficiency)
        if curr_lvl < req_lvl:
            gaps[js.skill_id] = (curr_lvl, req_lvl)

    # Fetch prerequisite DAG edges
    all_prereqs = db.query(SkillPrerequisite).all()
    edges = [
        PrerequisiteEdge(
            skill_id=p.skill_id,
            prerequisite_skill_id=p.prerequisite_skill_id,
            relationship_strength=float(p.relationship_strength)
        )
        for p in all_prereqs
    ]

    try:
        path = generate_ordered_learning_path(edges, skill_names, gaps, satisfied_skills)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prerequisite path generation error: {e}")

    # Map steps to actual course recommendations
    results = []
    for step in path:
        # Find best matching course covering this skill
        best_course = db.query(CourseSkill).filter(CourseSkill.skill_id == step.skill_id).first()
        course_info = None
        if best_course:
            course_info = {
                "course_id": best_course.course.course_id,
                "course_name": best_course.course.course_name,
                "provider": best_course.course.provider,
                "duration_hours": best_course.course.duration_hours,
                "url": best_course.course.course_url
            }

        results.append({
            "step_number": step.step_number,
            "skill_id": step.skill_id,
            "skill_name": step.skill_name,
            "status": step.status,
            "current_level": step.current_level,
            "required_level": step.required_level,
            "prerequisites_satisfied": step.prerequisites_satisfied,
            "recommended_course": course_info
        })

    return {
        "student_id": student_id,
        "target_job_id": job.job_id,
        "target_job_title": job.title,
        "learning_path": results
    }

@router.post("/progress/update")
def update_learning_progress(
    student_id: int,
    course_id: int,
    status_str: str,
    completion_percentage: float = 100.0,
    db: Session = Depends(get_db)
):
    """
    CONTINUOUS CLOSED LOOP FEEDBACK ENDPOINT (NEXUS Spec Section 22)
    When student completes course -> learning progress recorded -> STUDENT_SKILL updated.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    prog = db.query(LearningProgress).filter(
        LearningProgress.student_id == student_id,
        LearningProgress.course_id == course_id
    ).first()

    status_enum = ProgressStatus(status_str.upper())

    if not prog:
        prog = LearningProgress(
            student_id=student_id,
            course_id=course_id,
            status=status_enum,
            completion_percentage=completion_percentage,
            started_date=date.today()
        )
        db.add(prog)
    else:
        prog.status = status_enum
        prog.completion_percentage = completion_percentage

    if status_enum == ProgressStatus.COMPLETED:
        prog.completed_date = date.today()
        
        # CONTINUOUS FEEDBACK LOOP: Update student skill competencies for skills covered by course
        for cs in course.course_skills:
            st_skill = db.query(StudentSkill).filter(
                StudentSkill.student_id == student_id,
                StudentSkill.skill_id == cs.skill_id
            ).first()

            target_lvl = float(cs.target_proficiency)

            if st_skill:
                # Upgrade student proficiency level
                if float(st_skill.proficiency_level) < target_lvl:
                    st_skill.proficiency_level = target_lvl
                    st_skill.source = SkillSource.COURSE
            else:
                db.add(
                    StudentSkill(
                        student_id=student_id,
                        skill_id=cs.skill_id,
                        proficiency_level=target_lvl,
                        confidence_score=0.90,
                        source=SkillSource.COURSE,
                        evidence_text=f"Completed course: {course.course_name}"
                    )
                )

    db.commit()
    return {
        "message": "Learning progress recorded and student competencies recalculated.",
        "student_id": student_id,
        "course_id": course_id,
        "status": status_enum.value
    }
