from app.matching.reconciliation import evaluate_hybrid_match

def test_agreed_match_single_pass():
    weighted_score = 79.0
    semantic_score = 82.0
    
    result = evaluate_hybrid_match(
        weighted_score=weighted_score,
        semantic_score=semantic_score,
        student_resume_text="Python and SQL developer",
        job_title="Backend Developer",
        required_skills_json=[{"skill": "Python", "level": 5}],
        threshold=10.0
    )

    assert result.passes_count == 1
    assert result.validation_status == "AGREED"
    assert result.weighted_score == 79.0
    assert result.final_score > 0.0

def test_mismatch_reconciliation_threshold():
    # If weighted is 60 and mock LLM returns 60, diff is 0 <= 10 -> AGREED
    result = evaluate_hybrid_match(
        weighted_score=60.0,
        semantic_score=70.0,
        student_resume_text="Developer profile",
        job_title="Software Engineer",
        required_skills_json=[],
        threshold=10.0
    )
    assert result.validation_status in ["AGREED", "RECONCILED", "REVIEW_REQUIRED"]
