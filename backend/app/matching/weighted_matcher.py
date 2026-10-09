from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class SkillRequirement:
    skill_id: int
    skill_name: str
    required_level: float
    importance_weight: float
    is_mandatory: bool = False

@dataclass
class StudentCompetency:
    skill_id: int
    skill_name: str
    proficiency_level: float
    source: str = "RESUME"
    evidence_text: str = ""

@dataclass
class SkillMatchDetail:
    skill_id: int
    skill_name: str
    required_level: float
    student_level: float
    importance_weight: float
    skill_score: float         # 0.0 to 1.0
    weighted_contribution: float # skill_score * weight * 100
    gap: float                 # max(required - student, 0)
    is_mandatory: bool
    is_missing: bool

@dataclass
class WeightedMatchResult:
    weighted_score: float     # 0.0 to 100.0 percentage
    skills_detail: List[SkillMatchDetail]
    total_weight_validated: float
    mandatory_missing: bool

def calculate_weighted_match(
    requirements: List[SkillRequirement],
    student_skills: List[StudentCompetency],
    weight_tolerance: float = 0.001
) -> WeightedMatchResult:
    """
    FROZEN BASELINE WEIGHTED MATCHING ALGORITHM (NEXUS Specification Section 8 & 34)
    
    SkillScore_i = min(StudentLevel_i / RequiredLevel_i, 1.0)
    Contribution_i = SkillScore_i * Weight_i * 100
    WeightedSkillScore = Sum(Contribution_i)
    Gap_i = max(RequiredLevel_i - StudentLevel_i, 0)
    """
    if not requirements:
        raise ValueError("Job requirements list cannot be empty")

    # 1. Validate that weights sum to 1.0 (or 100%)
    total_weight = sum(req.importance_weight for req in requirements)
    if abs(total_weight - 1.0) > weight_tolerance and abs(total_weight - 100.0) > weight_tolerance:
        raise ValueError(f"Skill weights must sum to 1.0 (or 100%). Current sum: {total_weight}")
    
    # Normalize weights to fraction (0.0 to 1.0) if passed as percentage (e.g. 30 instead of 0.3)
    normalized_requirements = []
    for req in requirements:
        weight = req.importance_weight
        if total_weight > 1.5: # User passed percentages like 30, 20, 20...
            weight = weight / 100.0
        normalized_requirements.append(
            SkillRequirement(
                skill_id=req.skill_id,
                skill_name=req.skill_name,
                required_level=req.required_level,
                importance_weight=weight,
                is_mandatory=req.is_mandatory
            )
        )

    # 2. Build student competency lookup map by skill_id
    student_map: Dict[int, StudentCompetency] = {
        sc.skill_id: sc for sc in student_skills
    }

    skills_detail: List[SkillMatchDetail] = []
    total_weighted_score = 0.0
    mandatory_missing = False

    for req in normalized_requirements:
        student_comp = student_map.get(req.skill_id)
        
        if student_comp is not None:
            student_lvl = float(student_comp.proficiency_level)
            is_missing = False
        else:
            student_lvl = 0.0
            is_missing = True

        # Cap skill score at 1.0 for overqualification
        if req.required_level > 0:
            skill_score = min(student_lvl / req.required_level, 1.0)
        else:
            skill_score = 1.0

        gap = max(req.required_level - student_lvl, 0.0)
        weighted_contribution = skill_score * req.importance_weight * 100.0
        total_weighted_score += weighted_contribution

        if req.is_mandatory and gap > 0:
            mandatory_missing = True

        skills_detail.append(
            SkillMatchDetail(
                skill_id=req.skill_id,
                skill_name=req.skill_name,
                required_level=req.required_level,
                student_level=student_lvl,
                importance_weight=req.importance_weight,
                skill_score=round(skill_score, 4),
                weighted_contribution=round(weighted_contribution, 2),
                gap=round(gap, 2),
                is_mandatory=req.is_mandatory,
                is_missing=is_missing
            )
        )

    return WeightedMatchResult(
        weighted_score=round(total_weighted_score, 2),
        skills_detail=skills_detail,
        total_weight_validated=round(total_weight, 4),
        mandatory_missing=mandatory_missing
    )
