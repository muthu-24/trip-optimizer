from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity import Activity
from app.models.destination import Destination
from app.services.trip_planner import (
    calculate_activity_score,
    generate_itinerary
)
from app.services.recommendation_service import calculate_trip_cost_breakdown


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
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    activities = (
        db.query(Activity)
        .filter(Activity.destination_id == destination_id)
        .all()
    )

    scored_activities = []
    total_activity_cost = 0.0

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

    for day_plan in itinerary:
        total_activity_cost += day_plan["total_cost"]

    cost_breakdown = {}
    if destination:
        cost_breakdown = calculate_trip_cost_breakdown(
            destination=destination,
            trip_duration=trip_duration,
            total_activity_costs=total_activity_cost
        )

    return {
        "destination_id": destination_id,
        "destination_name": destination.name if destination else "",
        "activities": scored_activities,
        "itinerary": itinerary,
        "cost_breakdown": cost_breakdown,
    }