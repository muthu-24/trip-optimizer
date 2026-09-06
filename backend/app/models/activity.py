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
    estimated_cost = Column(Float, default=0)
    duration = Column(Float)
    rating = Column(Float)