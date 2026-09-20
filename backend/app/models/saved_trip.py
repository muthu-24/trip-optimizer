from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class SavedTrip(Base):
    __tablename__ = "saved_trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    destination_name = Column(String(200), nullable=False)
    trip_duration = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    num_travelers = Column(Integer, default=1, nullable=True)
    travel_style = Column(String(100), nullable=True)
    season = Column(String(100), nullable=True)
    total_route_distance = Column(Float, nullable=True)
    itinerary_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
