from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.routes.recommendation import router as recommendation_router
from app.database import Base, engine
from app.models import User, Destination
from app.models.activity import Activity
from app.routes.activity import router as activity_router
from app.routes.trip import router as trip_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Trip Optimizer API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(recommendation_router)
app.include_router(activity_router)
app.include_router(trip_router)


@app.get("/")
def root():
    return {"message": "Trip Optimizer API is running"}