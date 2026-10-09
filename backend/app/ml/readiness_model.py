from typing import Dict, Any, List
import math

class TimeToReadinessModel:
    """
    Predictive ML & Rule-Based Heuristic Model for Time-to-Readiness Estimation
    Output: Estimated week ranges (e.g. 6 to 9 weeks). Avoid false precision!
    """
    def __init__(self, weekly_study_hours: float = 10.0):
        self.weekly_study_hours = max(2.0, float(weekly_study_hours))

    def predict_readiness_weeks(
        self,
        skill_gaps: List[Dict[str, Any]],
        prerequisite_depth: int = 1
    ) -> Dict[str, Any]:
        if not skill_gaps:
            return {
                "minimum_weeks": 0,
                "maximum_weeks": 1,
                "estimated_hours": 0,
                "formatted_range": "0–1 weeks (Ready)"
            }

        total_gap_points = 0.0
        weighted_hours = 0.0

        for item in skill_gaps:
            gap = float(item.get("gap", 0.0))
            difficulty = float(item.get("difficulty", 3)) # 1 to 5 scale
            
            total_gap_points += gap
            # Average ~15 hours of study needed per 1.0 gap point for difficulty 3
            item_hours = gap * (10.0 + difficulty * 2.0)
            weighted_hours += item_hours

        # Account for prerequisite depth complexity multiplier
        complexity_factor = 1.0 + (prerequisite_depth * 0.10)
        total_hours = weighted_hours * complexity_factor

        base_weeks = total_hours / self.weekly_study_hours
        
        # Calculate realistic range (min to max weeks)
        min_weeks = max(1, int(math.floor(base_weeks * 0.85)))
        max_weeks = max(min_weeks + 1, int(math.ceil(base_weeks * 1.25)))

        return {
            "minimum_weeks": min_weeks,
            "maximum_weeks": max_weeks,
            "estimated_hours": round(total_hours, 1),
            "formatted_range": f"{min_weeks}–{max_weeks} weeks"
        }
