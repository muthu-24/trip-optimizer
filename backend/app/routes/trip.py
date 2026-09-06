from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity import Activity
from app.services.trip_planner import (
    calculate_activity_score,
    generate_itinerary
)


router = APIRouter(
    prefix="/api/trips",
    tags=["Trips"]
)


@router.post("/activities/{destination_id}")
def get_personalized_activities(
    destination_id: int,
    budget: float,
    travel_style: str,
    trip_duration: int,
    preferred_activities: list[str],
    db: Session = Depends(get_db)
):
    activities = (
        db.query(Activity)
        .filter(Activity.destination_id == destination_id)
        .all()
    )

    scored_activities = []

    for activity in activities:
        score = calculate_activity_score(
            activity=activity,
            preferred_activities=preferred_activities,
            travel_style=travel_style,
            budget=budget
        )

        scored_activities.append({
            "id": activity.id,
            "name": activity.name,
            "category": activity.category,
            "estimated_cost": activity.estimated_cost,
            "duration": activity.duration,
            "rating": activity.rating,
            "score": score
        })

    scored_activities.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    itinerary = generate_itinerary(
        scored_activities=scored_activities,
        trip_duration=trip_duration
    )

    return {
        "destination_id": destination_id,
        "activities": scored_activities,
        "itinerary": itinerary
    }