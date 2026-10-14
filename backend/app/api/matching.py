from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.nexus_models import (
    Student, Job, StudentSkill, JobSkill, Skill, 
    MatchResult, MatchSkillResult, ValidationStatus
)
from app.matching.weighted_matcher import (
    calculate_weighted_match, SkillRequirement, StudentCompetency
)
from app.matching.semantic_matcher import SemanticMatcher
from app.matching.reconciliation import evaluate_hybrid_match
from app.ml.readiness_model import TimeToReadinessModel
from app.schemas.matching import MatchResponse, SkillGapDetail, EstimatedReadiness

router = APIRouter(prefix="/matching", tags=["Hybrid Matching"])
semantic_matcher = SemanticMatcher()
readiness_model = TimeToReadinessModel()

@router.post("/{student_id}/{job_id}", response_model=MatchResponse)
def execute_hybrid_job_match(
    student_id: int, 
    job_id: int, 
    db: Session = Depends(get_db)
):
    # 1. Fetch Student & Job
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID {student_id} not found")

    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")

    if not job.required_skills:
        raise HTTPException(status_code=400, detail="Target job does not have any required skill specifications.")

    # 2. Build Requirements & Student Competencies
    requirements = []
    req_skills_json = []
    for js in job.required_skills:
        requirements.append(
            SkillRequirement(
                skill_id=js.skill_id,
                skill_name=js.skill.skill_name,
                required_level=float(js.required_proficiency),
                importance_weight=float(js.importance_weight),
                is_mandatory=js.is_mandatory
            )
        )
        req_skills_json.append({
            "skill": js.skill.skill_name,
            "required_level": float(js.required_proficiency),
            "weight": float(js.importance_weight),
            "is_mandatory": js.is_mandatory
        })

    student_skills = []
    for ss in student.skills:
        student_skills.append(
            StudentCompetency(
                skill_id=ss.skill_id,
                skill_name=ss.skill.skill_name,
                proficiency_level=float(ss.proficiency_level),
                source=ss.source.value,
                evidence_text=ss.evidence_text or ""
            )
        )

    # 3. Step A: Deterministic Weighted Skill Matcher Baseline
    try:
        weighted_res = calculate_weighted_match(requirements, student_skills)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

    # 4. Step B: Semantic Similarity Matcher
    student_resume_text = ""
    if student.resumes:
        # Get latest resume text
        latest_resume = sorted(student.resumes, key=lambda r: r.uploaded_at, reverse=True)[0]
        student_resume_text = latest_resume.parsed_text or ""
    
    if not student_resume_text:
        # Fallback to text summary of student skills
        student_resume_text = f"Student {student.name}, target role: {student.target_role}. Skills: " + ", ".join([f"{s.skill_name} level {s.proficiency_level}" for s in student_skills])

    semantic_score = semantic_matcher.calculate_semantic_score(
        student_text=student_resume_text,
        job_text=f"{job.title} {job.description}"
    )

    # 5. Step C: Hybrid Evaluator & 2-Pass LLM Reconciliation Loop
    decision = evaluate_hybrid_match(
        weighted_score=weighted_res.weighted_score,
        semantic_score=semantic_score,
        student_resume_text=student_resume_text,
        job_title=job.title,
        required_skills_json=req_skills_json
    )

    # 6. Extract Skill Gaps
    skill_gaps: List[SkillGapDetail] = []
    gaps_for_readiness = []
    for detail in weighted_res.skills_detail:
        if detail.gap > 0:
            skill_gaps.append(
                SkillGapDetail(
                    skill_id=detail.skill_id,
                    skill=detail.skill_name,
                    current_level=detail.student_level,
                    required_level=detail.required_level,
                    gap=detail.gap,
                    is_mandatory=detail.is_mandatory
                )
            )
            gaps_for_readiness.append({
                "gap": detail.gap,
                "difficulty": 3
            })

    # 7. Time-to-Readiness Prediction Range
    readiness_pred = readiness_model.predict_readiness_weeks(gaps_for_readiness)
    est_readiness = EstimatedReadiness(
        minimum_weeks=readiness_pred["minimum_weeks"],
        maximum_weeks=readiness_pred["maximum_weeks"],
        formatted_range=readiness_pred["formatted_range"]
    )

    # 8. Persist Result to DB
    match_rec = MatchResult(
        student_id=student_id,
        job_id=job_id,
        weighted_score=weighted_res.weighted_score,
        semantic_score=semantic_score,
        llm_score=decision.llm_score,
        final_score=decision.final_score,
        difference=decision.difference,
        validation_status=ValidationStatus(decision.validation_status),
        model_version="v1.0-hybrid"
    )
    db.add(match_rec)
    db.commit()
    db.refresh(match_rec)

    for detail in weighted_res.skills_detail:
        db.add(
            MatchSkillResult(
                match_id=match_rec.match_id,
                skill_id=detail.skill_id,
                required_level=detail.required_level,
                student_level=detail.student_level,
                skill_weight=detail.importance_weight,
                skill_score=detail.weighted_contribution,
                gap=detail.gap,
                llm_level=detail.student_level, # Placeholder for evidence detail
                llm_confidence=1.00,
                evidence="Evaluated from resume & competency state"
            )
        )
    db.commit()

    return MatchResponse(
        match_id=match_rec.match_id,
        student_id=student_id,
        job_id=job_id,
        job_title=job.title,
        company_name=job.company.company_name,
        weighted_score=weighted_res.weighted_score,
        semantic_score=semantic_score,
        llm_score=decision.llm_score,
        final_score=decision.final_score,
        difference=decision.difference,
        validation_status=decision.validation_status,
        skill_gaps=skill_gaps,
        estimated_readiness=est_readiness,
        mandatory_missing=weighted_res.mandatory_missing,
        reconciliation_notes=decision.reconciliation_notes
    )
