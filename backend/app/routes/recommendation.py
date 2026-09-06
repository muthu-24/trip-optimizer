from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.destination import Destination
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import (
    calculate_score,
    generate_recommendation_reasons
)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
@router.post("/")
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    destinations = db.query(Destination).all()

    recommendations = []

    for destination in destinations:
        score = calculate_score(
            destination=destination,
            budget=request.budget,
            trip_duration=request.trip_duration,
            travel_style=request.travel_style,
            preferred_activities=request.preferred_activities,
            season=request.season
        )

        reasons = generate_recommendation_reasons(
    destination=destination,
    budget=request.budget,
    trip_duration=request.trip_duration,
    travel_style=request.travel_style,
    preferred_activities=request.preferred_activities,
    season=request.season
)

        recommendations.append({
    "destination": destination.name,
    "country": destination.country,
    "score": score,
    "average_daily_cost": destination.average_daily_cost,
    "estimated_trip_cost": round(
        destination.average_daily_cost * request.trip_duration,
        2
    ),
    "best_season": destination.best_season,
    "activities": destination.activities,
    "rating": destination.rating,
    "reasons": reasons
})

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "recommendations": recommendations
    }
    destinations = db.query(Destination).all()

    return {
        "message": "Recommendation system is working",
        "total_destinations": len(destinations)
    }