from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    country = Column(String, nullable=False, default="Sri Lanka")
    region = Column(String, nullable=True)
    category = Column(String, nullable=False)
    budget_level = Column(String, nullable=False)
    description = Column(String, nullable=True)
    accommodation_cost = Column(Float, default=0.0)
    food_cost = Column(Float, default=0.0)
    transport_cost = Column(Float, default=0.0)
    average_daily_cost = Column(Float, nullable=False)
    best_season = Column(String, nullable=False)
    activities = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    recommended_duration = Column(Integer, default=3)