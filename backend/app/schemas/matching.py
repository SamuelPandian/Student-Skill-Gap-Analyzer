from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SkillGapDetail(BaseModel):
    skill_id: int
    skill: str
    current_level: float
    required_level: float
    gap: float
    is_mandatory: bool = False

class EstimatedReadiness(BaseModel):
    minimum_weeks: int
    maximum_weeks: int
    formatted_range: str = ""

class MatchResponse(BaseModel):
    match_id: Optional[int] = None
    student_id: int
    job_id: int
    job_title: str
    company_name: str
    weighted_score: float
    semantic_score: float
    llm_score: float
    final_score: float
    difference: float
    validation_status: str # "AGREED", "RECONCILED", "REVIEW_REQUIRED"
    skill_gaps: List[SkillGapDetail]
    estimated_readiness: EstimatedReadiness
    mandatory_missing: bool = False
    reconciliation_notes: Optional[str] = None
