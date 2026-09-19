from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(
        Integer,
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    estimated_cost = Column(Float, default=0.0)
    duration = Column(Float, default=1.5)
    rating = Column(Float, default=4.5)
    description = Column(String(300), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)