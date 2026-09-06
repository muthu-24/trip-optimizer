from pydantic import BaseModel
from typing import List


class RecommendationRequest(BaseModel):
    budget: float
    trip_duration: int
    travel_style: str
    preferred_activities: List[str]
    season: str