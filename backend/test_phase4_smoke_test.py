"""
Phase 4 Verification: End-to-End Smoke Test Workflow
Covers complete user journey:
Register -> Login -> Dashboard/Me -> Preferences/Recommendations ->
Itinerary Generation -> Save Trip -> List Saved Trips ->
Get Saved Trip -> Delete Saved Trip -> Verify Deletion -> Re-login
"""

import sys
import uuid

from app.database import SessionLocal
from app.auth.routes import register, login, get_current_user_info
from app.schemas.user import UserCreate, UserLogin
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.routes.trip import get_personalized_activities
from app.routes.saved_trips import save_trip, list_saved_trips, get_saved_trip, delete_saved_trip
from app.schemas.saved_trip import SavedTripCreate


def run_smoke_test():
    print("=" * 65)
    print("PHASE 4: END-TO-END MANUAL SMOKE TEST WORKFLOW")
    print("=" * 65)

    db = SessionLocal()

    try:
        # Step 1: Register
        email = f"smoke_user_{uuid.uuid4().hex[:6]}@example.com"
        password = "Password123!"
        name = "Smoke Traveler"
        reg_res = register(UserCreate(name=name, email=email, password=password), db=db)
        uid = str(reg_res.user_id)
        print(f"  [PASS] 1. Register: User created (ID: {uid}, Email: {email})")

        # Step 2: Login
        login_res = login(UserLogin(email=email, password=password), db=db)
        token = login_res.access_token
        assert token and len(token) > 20
        print("  [PASS] 2. Login: JWT token generated successfully")

        # Step 3: Current User Info / Dashboard
        me_res = get_current_user_info(user_id=uid, db=db)
        assert me_res["email"] == email
        assert me_res["name"] == name
        print(f"  [PASS] 3. Dashboard Profile: Verified user {me_res['name']}")

        # Step 4: Plan Trip & Get Recommendations
        rec_req = RecommendationRequest(
            num_travelers=2,
            budget_per_person=65000,
            trip_duration=3,
            travel_style="nature",
            preferred_activities=["hiking", "nature"],
            season="December-April",
        )
        rec_res = get_recommendations(rec_req, db=db)
        assert len(rec_res["recommendations"]) > 0
        top_dest = rec_res["recommendations"][0]
        print(f"  [PASS] 4. Recommendations: Top destination is '{top_dest['destination']}' (Score: {top_dest['score']}%)")

        # Step 5: Generate Itinerary
        itin_res = get_personalized_activities(
            destination_id=top_dest["id"],
            budget_per_person=65000,
            trip_duration=3,
            travel_style="nature",
            preferred_activities=["hiking", "nature"],
            num_travelers=2,
            db=db,
        )
        itinerary = itin_res["itinerary"]
        assert len(itinerary) > 0
        print(f"  [PASS] 5. Itinerary: Generated {len(itinerary)} day(s), total route distance: {itin_res['total_route_distance']} km")

        # Step 6: Save Trip
        trip_create = SavedTripCreate(
            destination_name=top_dest["destination"],
            trip_duration=len(itinerary),
            budget=itin_res["total_group_budget"],
            num_travelers=2,
            travel_style="nature",
            season="December-April",
            total_route_distance=itin_res["total_route_distance"],
            itinerary_data=itin_res,
        )
        saved = save_trip(trip_create, current_user_id=uid, db=db)
        trip_id = saved.id
        print(f"  [PASS] 6. Save Trip: Saved trip ID {trip_id}")

        # Step 7: List Saved Trips
        trips = list_saved_trips(current_user_id=uid, db=db)
        assert any(t.id == trip_id for t in trips)
        print(f"  [PASS] 7. Saved Trips List: Found {len(trips)} trip(s) for user")

        # Step 8: Open Saved Trip Detail
        opened = get_saved_trip(trip_id=trip_id, current_user_id=uid, db=db)
        assert opened.destination_name == top_dest["destination"]
        assert opened.num_travelers == 2
        print(f"  [PASS] 8. Saved Trip Detail: Retrieved trip #{trip_id} ({opened.destination_name})")

        # Step 9: Delete Saved Trip
        delete_saved_trip(trip_id=trip_id, current_user_id=uid, db=db)
        print(f"  [PASS] 9. Delete Saved Trip: Deleted trip #{trip_id}")

        # Step 10: Verify Deletion
        trips_after = list_saved_trips(current_user_id=uid, db=db)
        assert not any(t.id == trip_id for t in trips_after)
        print("  [PASS] 10. Deletion Verified: Trip no longer exists in saved trips")

        # Step 11: Re-login (Simulate Logout -> Login Again)
        relogin_res = login(UserLogin(email=email, password=password), db=db)
        assert relogin_res.access_token is not None
        print("  [PASS] 11. Logout & Re-login: Authentication cycle successful")

        print("=" * 65)
        print("[ALL SMOKE TEST WORKFLOW STEPS PASSED SUCCESSFULLY]")
        return True

    except Exception as e:
        print(f"\n[FAIL] Smoke test failed at step: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_smoke_test()
    if not success:
        sys.exit(1)
