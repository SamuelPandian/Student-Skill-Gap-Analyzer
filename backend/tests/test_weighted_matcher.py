import pytest
from app.matching.weighted_matcher import (
    calculate_weighted_match,
    SkillRequirement,
    StudentCompetency
)

def test_spec_benchmark_weighted_matching():
    """
    Test exact benchmark from NEXUS Spec Section 34 & 8:
    Python  req 5, stud 4, weight 30% -> 24.0
    SQL     req 4, stud 4, weight 20% -> 20.0
    Django  req 4, stud 2, weight 20% -> 10.0
    REST    req 3, stud 3, weight 15% -> 15.0
    Git     req 3, stud 3, weight 10% -> 10.0
    Docker  req 2, stud 0, weight  5% ->  0.0
    Expected Total Weighted Score = 79.00%
    """
    requirements = [
        SkillRequirement(skill_id=1, skill_name="Python", required_level=5.0, importance_weight=0.30),
        SkillRequirement(skill_id=2, skill_name="SQL", required_level=4.0, importance_weight=0.20),
        SkillRequirement(skill_id=3, skill_name="Django", required_level=4.0, importance_weight=0.20),
        SkillRequirement(skill_id=4, skill_name="REST API", required_level=3.0, importance_weight=0.15),
        SkillRequirement(skill_id=5, skill_name="Git", required_level=3.0, importance_weight=0.10),
        SkillRequirement(skill_id=6, skill_name="Docker", required_level=2.0, importance_weight=0.05),
    ]

    student_skills = [
        StudentCompetency(skill_id=1, skill_name="Python", proficiency_level=4.0),
        StudentCompetency(skill_id=2, skill_name="SQL", proficiency_level=4.0),
        StudentCompetency(skill_id=3, skill_name="Django", proficiency_level=2.0),
        StudentCompetency(skill_id=4, skill_name="REST API", proficiency_level=3.0),
        StudentCompetency(skill_id=5, skill_name="Git", proficiency_level=3.0),
        # Docker is missing (0.0)
    ]

    result = calculate_weighted_match(requirements, student_skills)
    
    assert result.weighted_score == 79.0
    
    # Verify individual contributions
    details_by_name = {d.skill_name: d for d in result.skills_detail}
    assert details_by_name["Python"].weighted_contribution == 24.0
    assert details_by_name["SQL"].weighted_contribution == 20.0
    assert details_by_name["Django"].weighted_contribution == 10.0
    assert details_by_name["REST API"].weighted_contribution == 15.0
    assert details_by_name["Git"].weighted_contribution == 10.0
    assert details_by_name["Docker"].weighted_contribution == 0.0
    assert details_by_name["Docker"].gap == 2.0

def test_overqualification_capped_at_100():
    requirements = [
        SkillRequirement(skill_id=1, skill_name="Python", required_level=5.0, importance_weight=1.00)
    ]
    student_skills = [
        StudentCompetency(skill_id=1, skill_name="Python", proficiency_level=7.0) # Overqualified 7/5
    ]
    result = calculate_weighted_match(requirements, student_skills)
    assert result.weighted_score == 100.0
    assert result.skills_detail[0].skill_score == 1.0

def test_invalid_weights_sum_raises_error():
    requirements = [
        SkillRequirement(skill_id=1, skill_name="Python", required_level=5.0, importance_weight=0.50),
        SkillRequirement(skill_id=2, skill_name="SQL", required_level=4.0, importance_weight=0.20),
    ] # Sum = 0.70 != 1.0
    student_skills = []

    with pytest.raises(ValueError, match="Skill weights must sum to 1.0"):
        calculate_weighted_match(requirements, student_skills)
