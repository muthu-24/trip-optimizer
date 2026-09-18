from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.routes import get_current_user
from app.models.saved_trip import SavedTrip
from app.schemas.saved_trip import SavedTripCreate, SavedTripSummary, SavedTripDetail


router = APIRouter(
    prefix="/api/saved-trips",
    tags=["Saved Trips"]
)


@router.post(
    "",
    response_model=SavedTripSummary,
    status_code=status.HTTP_201_CREATED
)
def save_trip(
    data: SavedTripCreate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = SavedTrip(
        user_id=current_user_id,
        destination_name=data.destination_name,
        trip_duration=data.trip_duration,
        budget=data.budget,
        num_travelers=data.num_travelers,
        travel_style=data.travel_style,
        season=data.season,
        total_route_distance=data.total_route_distance,
        itinerary_data=data.itinerary_data,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get(
    "",
    response_model=list[SavedTripSummary]
)
def list_saved_trips(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trips = (
        db.query(SavedTrip)
        .filter(SavedTrip.user_id == current_user_id)
        .order_by(SavedTrip.created_at.desc())
        .all()
    )
    return trips


@router.get(
    "/{trip_id}",
    response_model=SavedTripDetail
)
def get_saved_trip(
    trip_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(SavedTrip).filter(SavedTrip.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    if trip.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return trip


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_saved_trip(
    trip_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(SavedTrip).filter(SavedTrip.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    if trip.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(trip)
    db.commit()
