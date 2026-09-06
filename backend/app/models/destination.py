from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    category = Column(String, nullable=False)
    budget_level = Column(String, nullable=False)
    average_daily_cost = Column(Float, nullable=False)
    best_season = Column(String, nullable=False)
    activities = Column(String, nullable=False)
    rating = Column(Float, nullable=False)