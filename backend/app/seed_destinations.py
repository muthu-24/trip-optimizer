from app.database import SessionLocal
from app.models.destination import Destination


destinations = [
    Destination(
        name="Ella",
        country="Sri Lanka",
        category="Nature",
        budget_level="Low",
        average_daily_cost=8000,
        best_season="December-April",
        activities="Hiking,Nature,Scenic",
        rating=4.8
    ),
    Destination(
        name="Galle",
        country="Sri Lanka",
        category="Culture",
        budget_level="Medium",
        average_daily_cost=10000,
        best_season="December-April",
        activities="Beach,Culture,History",
        rating=4.7
    ),
    Destination(
        name="Mirissa",
        country="Sri Lanka",
        category="Beach",
        budget_level="Medium",
        average_daily_cost=12000,
        best_season="December-March",
        activities="Beach,Surfing,Whale Watching",
        rating=4.6
    ),
    Destination(
        name="Sigiriya",
        country="Sri Lanka",
        category="Adventure",
        budget_level="Medium",
        average_daily_cost=9000,
        best_season="January-April",
        activities="Hiking,History,Culture",
        rating=4.9
    ),
    Destination(
        name="Nuwara Eliya",
        country="Sri Lanka",
        category="Nature",
        budget_level="Medium",
        average_daily_cost=9500,
        best_season="January-April",
        activities="Nature,Scenic,Hiking",
        rating=4.6
    ),
    Destination(
        name="Kandy",
        country="Sri Lanka",
        category="Culture",
        budget_level="Medium",
        average_daily_cost=8500,
        best_season="January-April",
        activities="Culture,History,Nature",
        rating=4.7
    ),
    Destination(
        name="Arugam Bay",
        country="Sri Lanka",
        category="Beach",
        budget_level="Medium",
        average_daily_cost=11000,
        best_season="May-September",
        activities="Surfing,Beach,Adventure",
        rating=4.7
    ),
    Destination(
        name="Yala",
        country="Sri Lanka",
        category="Wildlife",
        budget_level="High",
        average_daily_cost=15000,
        best_season="February-June",
        activities="Wildlife,Safari,Nature",
        rating=4.8
    ),
    Destination(
        name="Hikkaduwa",
        country="Sri Lanka",
        category="Beach",
        budget_level="Low",
        average_daily_cost=7500,
        best_season="December-March",
        activities="Beach,Surfing,Diving",
        rating=4.5
    ),
    Destination(
        name="Knuckles",
        country="Sri Lanka",
        category="Adventure",
        budget_level="Low",
        average_daily_cost=7000,
        best_season="January-April",
        activities="Hiking,Nature,Adventure",
        rating=4.8
    ),
]


db = SessionLocal()

try:
    db.add_all(destinations)
    db.commit()
    print("Destinations added successfully!")

finally:
    db.close()