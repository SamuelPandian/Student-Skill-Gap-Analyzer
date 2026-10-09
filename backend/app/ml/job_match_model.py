from typing import Dict, Any

class JobMatchPredictor:
    """
    Predictive Job Match Probability model combining weighted skill score,
    mandatory skill completion, and semantic similarity.
    """
    def predict_match_probability(
        self,
        weighted_score: float,
        mandatory_missing: bool,
        semantic_score: float = 70.0,
        cgpa_eligible: bool = True
    ) -> Dict[str, Any]:
        
        # Base probability driven by weighted score
        prob = (weighted_score * 0.70) + (semantic_score * 0.30)
        
        # Penalize missing mandatory skills heavily
        if mandatory_missing:
            prob = prob * 0.50
            
        # Penalize if minimum CGPA requirement not met
        if not cgpa_eligible:
            prob = prob * 0.80

        probability = max(0.0, min(99.0, round(prob, 1)))

        if probability >= 80.0:
            category = "HIGH_MATCH"
        elif probability >= 55.0:
            category = "MODERATE_MATCH"
        else:
            category = "DEVELOPMENT_NEEDED"

        return {
            "match_probability": probability,
            "category": category,
            "is_mandatory_satisfied": not mandatory_missing
        }
