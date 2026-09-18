from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.destination import Destination
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import (
    calculate_score_breakdown,
    calculate_trip_cost_breakdown,
    generate_recommendation_reasons,
    get_destination_description,
)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


@router.post("/")
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    destinations = db.query(Destination).all()

    recommendations = []

    budget_per_person = request.budget_per_person or request.budget

    for destination in destinations:
        breakdown = calculate_score_breakdown(
            destination=destination,
            budget=budget_per_person,
            trip_duration=request.trip_duration,
            travel_style=request.travel_style,
            preferred_activities=request.preferred_activities,
            season=request.season
        )

        reasons = generate_recommendation_reasons(
            destination=destination,
            budget=budget_per_person,
            trip_duration=request.trip_duration,
            travel_style=request.travel_style,
            preferred_activities=request.preferred_activities,
            season=request.season,
            num_travelers=request.num_travelers
        )

        description = get_destination_description(destination)
        cost_breakdown = calculate_trip_cost_breakdown(
            destination,
            request.trip_duration,
            num_travelers=request.num_travelers
        )

        recommendations.append({
            "id": destination.id,
            "destination": destination.name,
            "country": destination.country,
            "region": destination.region or "Sri Lanka",
            "category": destination.category,
            "budget_level": destination.budget_level,
            "score": breakdown["overall_score"],
            "score_breakdown": {
                "budget_match": breakdown["budget_pct"],
                "activity_match": breakdown["activity_pct"],
                "season_match": breakdown["season_pct"],
                "travel_style_match": breakdown["style_pct"],
                "rating_match": breakdown["rating_pct"],
                "overall_score": breakdown["overall_score"],
            },
            "cost_breakdown": {
                "accommodation": cost_breakdown["trip_accommodation"],
                "food": cost_breakdown["trip_food"],
                "transportation": cost_breakdown["trip_transportation"],
                "daily_average": cost_breakdown["daily_total"],
                "estimated_trip_cost": cost_breakdown["estimated_trip_total"],
                "num_travelers": request.num_travelers,
                "cost_per_person": cost_breakdown["cost_per_person"],
            },
            "description": description,
            "average_daily_cost": destination.average_daily_cost,
            "estimated_trip_cost": round(
                destination.average_daily_cost * request.trip_duration * request.num_travelers,
                2
            ),
            "estimated_trip_cost_per_person": round(
                destination.average_daily_cost * request.trip_duration,
                2
            ),
            "best_season": destination.best_season,
            "activities": destination.activities,
            "rating": destination.rating,
            "recommended_duration": destination.recommended_duration or 3,
            "reasons": reasons
        })

    # Sort destinations from highest overall match score to lowest
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "num_travelers": request.num_travelers,
        "budget_per_person": budget_per_person,
        "total_group_budget": request.total_group_budget,
        "recommendations": recommendations,
        "total_destinations": len(recommendations)
    }


@router.get("/destinations/{destination_id}")
def get_destination_detail(
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Return full destination detail for the Destination Details page."""
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