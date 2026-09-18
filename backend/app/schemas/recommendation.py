from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class RecommendationRequest(BaseModel):
    num_travelers: int = Field(default=1, ge=1, le=50, description="Number of travelers")
    budget_per_person: Optional[float] = Field(default=None, gt=0, le=10_000_000, description="Budget per person in LKR")
    budget: Optional[float] = Field(default=None, gt=0, le=10_000_000, description="Budget in LKR (per person)")
    trip_duration: int = Field(..., ge=1, le=30, description="Trip duration must be between 1 and 30 days")
    travel_style: Optional[str] = Field(default="adventure", description="Preferred travel style")
    preferred_activities: List[str] = Field(default_factory=list, description="List of preferred activities")
    season: Optional[str] = Field(default="", description="Planned travel season window")

    @model_validator(mode="after")
    def validate_and_sync_budget(self):
        if self.budget_per_person is None and self.budget is None:
            raise ValueError("Either budget_per_person or budget must be provided.")
        if self.budget_per_person is None and self.budget is not None:
            self.budget_per_person = self.budget
        elif self.budget is None and self.budget_per_person is not None:
            self.budget = self.budget_per_person
        return self

    @property
    def total_group_budget(self) -> float:
        return round((self.budget_per_person or 0.0) * self.num_travelers, 2)