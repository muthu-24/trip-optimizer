from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityResponse


router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"]
)


@router.get(
    "/destination/{destination_id}",
    response_model=list[ActivityResponse]
)
def get_destination_activities(
    destination_id: int,
    db: Session = Depends(get_db)
):
    activities = (
        db.query(Activity)
        .filter(Activity.destination_id == destination_id)
        .order_by(Activity.rating.desc())
        .all()
    )

    return activities