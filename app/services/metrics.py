from typing import List, Dict
from app.models.feedback import Feedback

class MetricsService:
    @staticmethod
    def calculate_nps(feedbacks: List[Feedback]) -> Dict:
        if not feedbacks:
            return {"score": 0, "promoters": 0, "neutrals": 0, "detractors": 0, "total": 0}
        
        total = len(feedbacks)
        promoters = len([f for f in feedbacks if f.nps >= 9])
        neutral = len([f for f in feedbacks if 7 <= f.nps <= 8])
        detractors = len([f for f in feedbacks if f.nps <= 6])
        
        # NPS Formula: % Promoters - % Detractors (Typically returned as an integer)
        score = int(((promoters - detractors) / total) * 100)
        return {
            "score": score,
            "promoters": promoters,
            "neutrals": neutral,
            "detractors": detractors,
            "total": total
        }

    @staticmethod
    def calculate_csat(feedbacks: List[Feedback]) -> Dict:
        if not feedbacks:
            return {"score": 0, "satisfied": 0, "neutral": 0, "unsatisfied": 0, "total": 0}
        
        total = len(feedbacks)
        satisfied = len([f for f in feedbacks if f.csat >= 4])
        neutral = len([f for f in feedbacks if f.csat == 3])
        unsatisfied = len([f for f in feedbacks if f.csat <= 2])
        
        # CSAT score as average (as seen in some requirements)
        avg_score = sum([f.csat for f in feedbacks]) / total
        # CSAT % as defined in image formula
        csat_pct = (satisfied / total) * 100
        
        return {
            "score": round(avg_score, 2), # Using average for overview
            "percentage": round(csat_pct, 2), # Using % for details
            "satisfied": satisfied,
            "neutral": neutral,
            "unsatisfied": unsatisfied,
            "total": total
        }

    @staticmethod
    def calculate_ces(feedbacks: List[Feedback]) -> Dict:
        if not feedbacks:
            return {"score": 0, "low": 0, "medium": 0, "high": 0, "total": 0}
        
        total = len(feedbacks)
        low = len([f for f in feedbacks if f.ces <= 2])
        medium = len([f for f in feedbacks if f.ces == 3])
        high = len([f for f in feedbacks if f.ces >= 4])
        
        avg_score = sum([f.ces for f in feedbacks]) / total
        
        return {
            "score": round(avg_score, 2),
            "low_effort": low,
            "medium_effort": medium,
            "high_effort": high,
            "total": total
        }

    @staticmethod
    def get_critical_segments(feedbacks: List[Feedback]) -> Dict:
        if not feedbacks: return {}
        
        # Segment 1: Detractores con alto esfuerzo (CES >= 4 and NPS <= 6)
        high_effort_detractors = [f for f in feedbacks if f.ces >= 4 and f.nps <= 6]
        
        # Segment 2: Promotores con bajo esfuerzo (CES <= 2 and NPS >= 9)
        low_effort_promoters = [f for f in feedbacks if f.ces <= 2 and f.nps >= 9]
        
        return {
            "high_effort_detractors": {
                "count": len(high_effort_detractors),
                "label": "Detractores con alto esfuerzo",
                "comments": [f.comment for f in high_effort_detractors if f.comment][:5]
            },
            "low_effort_promoters": {
                "count": len(low_effort_promoters),
                "label": "Promotores con bajo esfuerzo",
                "comments": [f.comment for f in low_effort_promoters if f.comment][:5]
            }
        }

    @classmethod
    def get_all_metrics(cls, feedbacks: List[Feedback]) -> Dict:
        return {
            "nps": cls.calculate_nps(feedbacks),
            "csat": cls.calculate_csat(feedbacks),
            "ces": cls.calculate_ces(feedbacks),
            "segments": cls.get_critical_segments(feedbacks)
        }
