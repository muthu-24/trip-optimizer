from pydantic import BaseModel
from datetime import datetime
from typing import Any


class SavedTripCreate(BaseModel):
    destination_name: str
    trip_duration: int
    budget: float
    num_travelers: int = 1
    travel_style: str | None = None
    season: str | None = None
    total_route_distance: float | None = None
    itinerary_data: dict[str, Any]


class SavedTripSummary(BaseModel):
    id: int
    destination_name: str
    trip_duration: int
    budget: float
    num_travelers: int = 1
    travel_style: str | None
    season: str | None
    total_route_distance: float | None
    created_at: datetime

    class Config:
        from_attributes = True


class SavedTripDetail(BaseModel):
    id: int
    destination_name: str
    trip_duration: int
    budget: float
    num_travelers: int = 1
    travel_style: str | None
    season: str | None
    total_route_distance: float | None
    itinerary_data: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
