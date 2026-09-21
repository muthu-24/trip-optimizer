import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.auth.routes import router as auth_router
from app.routes.recommendation import router as recommendation_router
from app.database import Base, engine
from app.models import User, Destination
from app.models.activity import Activity
from app.models.saved_trip import SavedTrip
from app.routes.activity import router as activity_router
from app.routes.trip import router as trip_router
from app.routes.destination import router as destination_router
from app.routes.saved_trips import router as saved_trips_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Trip Optimizer API"
)

raw_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in raw_allowed_origins.split(",") if origin.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(recommendation_router)
app.include_router(destination_router)
app.include_router(activity_router)
app.include_router(trip_router)
app.include_router(saved_trips_router)


@app.get("/")
def root():
    return {"message": "Trip Optimizer API is running"}