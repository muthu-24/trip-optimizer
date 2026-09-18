from fastapi import APIRouter, Depends, HTTPException, status
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
    budget: float = 0.0,
    travel_style: str = "adventure",
    trip_duration: int = 3,
    preferred_activities: list[str] = [],
    num_travelers: int = 1,
    budget_per_person: float | None = None,
    db: Session = Depends(get_db)
):
    # 1. Parameter Validation
    if destination_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination ID must be a positive integer"
        )

    effective_budget = budget_per_person if (budget_per_person is not None and budget_per_person > 0) else budget

    if effective_budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Trip budget must be greater than 0"
        )

    if num_travelers < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Number of travelers must be at least 1"
        )

    if trip_duration < 1 or trip_duration > 30:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Trip duration must be between 1 and 30 days"
        )

    # 2. Destination Existence Check
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )

    # 3. Retrieve Destination Activities
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
            budget=effective_budget
        )

        scored_activities.append({
            "id": activity.id,
            "name": activity.name,
            "category": activity.category,
            "estimated_cost": activity.estimated_cost,
            "duration": activity.duration,
            "rating": activity.rating,
            "latitude": activity.latitude,
            "longitude": activity.longitude,
            "score": score
        })

    scored_activities.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # 4. Generate Balanced Itinerary
    itinerary = generate_itinerary(
        scored_activities=scored_activities,
        trip_duration=trip_duration
    )

    for day_plan in itinerary:
        total_activity_cost += day_plan.get("total_cost", 0.0)

    planned_duration = len(itinerary) if itinerary else trip_duration
    insufficient_activities = len(itinerary) < trip_duration

    cost_breakdown = calculate_trip_cost_breakdown(
        destination=destination,
        trip_duration=planned_duration,
        total_activity_costs=total_activity_cost,
        num_travelers=num_travelers
    )

    total_route_distance = round(
        sum(d.get("total_distance", 0.0) for d in itinerary), 2
    )
    total_transit_minutes = sum(
        d.get("transit_duration_minutes", 0) for d in itinerary
    )

    total_scheduled_activities = sum(len(d.get("activities", [])) for d in itinerary)
    itinerary_notice = None
    if insufficient_activities:
        itinerary_notice = (
            f"This destination has {total_scheduled_activities} suitable attractions, "
            f"which is fewer than your requested {trip_duration} days. "
            f"The itinerary has been gracefully planned for {planned_duration} days to maintain a realistic, "
            f"high-quality experience without duplicate activities or artificial fillers."
        )

    return {
        "destination_id": destination_id,
        "destination_name": destination.name,
        "num_travelers": num_travelers,
        "budget_per_person": effective_budget,
        "total_group_budget": round(effective_budget * num_travelers, 2),
        "activities": scored_activities,
        "itinerary": itinerary,
        "cost_breakdown": cost_breakdown,
        "total_route_distance": total_route_distance,
        "total_transit_minutes": total_transit_minutes,
        "requested_trip_duration": trip_duration,
        "actual_trip_duration": planned_duration,
        "insufficient_activities": insufficient_activities,
        "itinerary_notice": itinerary_notice,
    }