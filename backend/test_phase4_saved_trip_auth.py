"""
Phase 4 Test Suite: Saved Trip Authorization & Ownership Isolation
Covers:
- Owner CRUD operations (create, list, get, delete)
- Cross-user access isolation: User B cannot GET User A's saved trip (403 Forbidden)
- Cross-user delete protection: User B cannot DELETE User A's saved trip (403 Forbidden)
- Unauthenticated requests protection (401 Unauthorized)
- Non-existent saved trips return 404 Not Found
"""

import sys
import uuid
import pytest
from fastapi import HTTPException, status

from app.database import SessionLocal
from app.models.user import User
from app.models.saved_trip import SavedTrip
from app.schemas.saved_trip import SavedTripCreate
from app.routes.saved_trips import (
    save_trip,
    list_saved_trips,
    get_saved_trip,
    delete_saved_trip,
)
from app.auth.security import hash_password, decode_access_token


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def user_a(db_session):
    user = User(
        name="User A",
        email=f"user_a_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Pass123!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="module")
def user_b(db_session):
    user = User(
        name="User B",
        email=f"user_b_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Pass123!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# 1. Owner CRUD Operations
# ---------------------------------------------------------------------------

def test_owner_can_create_and_retrieve_saved_trip(db_session, user_a):
    """User A can save a trip and retrieve it."""
    payload = SavedTripCreate(
        destination_name="Ella",
        trip_duration=3,
        budget=60000.0,
        num_travelers=2,
        travel_style="nature",
        season="December-April",
        total_route_distance=12.5,
        itinerary_data={"itinerary": [{"day": 1, "activities": []}]},
    )

    created = save_trip(payload, current_user_id=str(user_a.user_id), db=db_session)
    assert created.id is not None
    assert created.destination_name == "Ella"
    assert created.user_id == str(user_a.user_id)

    # Retrieve
    retrieved = get_saved_trip(trip_id=created.id, current_user_id=str(user_a.user_id), db=db_session)
    assert retrieved.id == created.id
    assert retrieved.num_travelers == 2


def test_owner_can_list_saved_trips(db_session, user_a):
    """User A can list all their saved trips."""
    trips = list_saved_trips(current_user_id=str(user_a.user_id), db=db_session)
    assert len(trips) >= 1
    assert any(t.destination_name == "Ella" for t in trips)


# ---------------------------------------------------------------------------
# 2. Cross-User Isolation (User B cannot access or delete User A's trip)
# ---------------------------------------------------------------------------

def test_cross_user_get_rejected(db_session, user_a, user_b):
    """User B cannot view User A's saved trip (403 Forbidden)."""
    # Create trip for User A
    payload = SavedTripCreate(
        destination_name="Galle Fort",
        trip_duration=2,
        budget=40000.0,
        num_travelers=1,
        travel_style="culture",
        season="December-April",
        total_route_distance=5.0,
        itinerary_data={"itinerary": []},
    )
    trip_a = save_trip(payload, current_user_id=str(user_a.user_id), db=db_session)

    # User B attempts GET
    with pytest.raises(HTTPException) as exc_info:
        get_saved_trip(trip_id=trip_a.id, current_user_id=str(user_b.user_id), db=db_session)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in exc_info.value.detail


def test_cross_user_delete_rejected(db_session, user_a, user_b):
    """User B cannot delete User A's saved trip (403 Forbidden)."""
    payload = SavedTripCreate(
        destination_name="Kandy",
        trip_duration=3,
        budget=45000.0,
        num_travelers=2,
        travel_style="culture",
        season="January-April",
        total_route_distance=8.0,
        itinerary_data={"itinerary": []},
    )
    trip_a = save_trip(payload, current_user_id=str(user_a.user_id), db=db_session)

    # User B attempts DELETE
    with pytest.raises(HTTPException) as exc_info:
        delete_saved_trip(trip_id=trip_a.id, current_user_id=str(user_b.user_id), db=db_session)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in exc_info.value.detail

    # Verify trip still exists in DB
    existing = db_session.query(SavedTrip).filter(SavedTrip.id == trip_a.id).first()
    assert existing is not None


# ---------------------------------------------------------------------------
# 3. Owner Can Delete Own Trip
# ---------------------------------------------------------------------------

def test_owner_can_delete_own_trip(db_session, user_a):
    """User A can successfully delete their own saved trip."""
    payload = SavedTripCreate(
        destination_name="Mirissa",
        trip_duration=2,
        budget=35000.0,
        num_travelers=2,
        travel_style="beach",
        season="December-April",
        total_route_distance=3.0,
        itinerary_data={"itinerary": []},
    )
    trip = save_trip(payload, current_user_id=str(user_a.user_id), db=db_session)
    trip_id = trip.id

    # Owner deletes
    delete_saved_trip(trip_id=trip_id, current_user_id=str(user_a.user_id), db=db_session)

    # Verify deleted
    deleted = db_session.query(SavedTrip).filter(SavedTrip.id == trip_id).first()
    assert deleted is None


# ---------------------------------------------------------------------------
# 4. Non-Existent Saved Trip
# ---------------------------------------------------------------------------

def test_nonexistent_saved_trip_lookup(db_session, user_a):
    """Looking up non-existent trip returns HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        get_saved_trip(trip_id=999999, current_user_id=str(user_a.user_id), db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_nonexistent_saved_trip_delete(db_session, user_a):
    """Deleting non-existent trip returns HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        delete_saved_trip(trip_id=999999, current_user_id=str(user_a.user_id), db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# 5. Unauthenticated Token Rejection
# ---------------------------------------------------------------------------

def test_unauthenticated_token_rejection():
    """Missing or invalid token string raises HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("Bearer invalid-token")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Direct Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHASE 4: SAVED TRIP AUTHORIZATION & ISOLATION TESTS")
    print("=" * 65)
    db = SessionLocal()

    # Create temporary users for direct execution
    ua = User(name="User A", email=f"user_a_{uuid.uuid4().hex[:8]}@test.com", password_hash=hash_password("Pass123!"))
    ub = User(name="User B", email=f"user_b_{uuid.uuid4().hex[:8]}@test.com", password_hash=hash_password("Pass123!"))
    db.add(ua)
    db.add(ub)
    db.commit()
    db.refresh(ua)
    db.refresh(ub)

    tests = [
        ("Owner can create and retrieve saved trip", lambda: test_owner_can_create_and_retrieve_saved_trip(db, ua)),
        ("Owner can list saved trips", lambda: test_owner_can_list_saved_trips(db, ua)),
        ("Cross-user GET rejected (403)", lambda: test_cross_user_get_rejected(db, ua, ub)),
        ("Cross-user DELETE rejected (403)", lambda: test_cross_user_delete_rejected(db, ua, ub)),
        ("Owner can delete own trip", lambda: test_owner_can_delete_own_trip(db, ua)),
        ("Nonexistent saved trip lookup (404)", lambda: test_nonexistent_saved_trip_lookup(db, ua)),
        ("Nonexistent saved trip delete (404)", lambda: test_nonexistent_saved_trip_delete(db, ua)),
        ("Unauthenticated token rejection (401)", test_unauthenticated_token_rejection),
    ]

    all_passed = True
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  [PASS] {name}")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            all_passed = False

    db.close()
    print("=" * 65)
    if all_passed:
        print(f"[ALL TESTS PASSED] {len(tests)}/{len(tests)} saved-trip authorization tests passed.")
    else:
        print("[FAILURE] Some saved-trip authorization tests failed.")
        sys.exit(1)
