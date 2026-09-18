from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: int
    destination_id: int
    name: str
    category: str
    estimated_cost: float
    duration: float | None
    rating: float | None
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True