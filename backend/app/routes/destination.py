from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.destination import Destination
from app.services.recommendation_service import get_destination_description

router = APIRouter(
    prefix="/api/destinations",
    tags=["Destinations"]
)


@router.get("/{destination_id}")
def get_destination_by_id(
    destination_id: int,
    db: Session = Depends(get_db)
):
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    description = get_destination_description(destination)

    return {
        "id": destination.id,
        "name": destination.name,
        "country": destination.country,
        "region": destination.region or "Sri Lanka",
        "category": destination.category,
        "budget_level": destination.budget_level,
        "description": description,
        "average_daily_cost": destination.average_daily_cost,
        "best_season": destination.best_season,
        "activities": destination.activities,
        "rating": destination.rating,
        "recommended_duration": destination.recommended_duration or 3,
        "accommodation_cost": destination.accommodation_cost,
        "food_cost": destination.food_cost,
        "transport_cost": destination.transport_cost,
    }
