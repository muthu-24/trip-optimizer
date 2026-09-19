"""
Phase 4 Test Suite: API Validation & Error Handling
Covers:
- Recommendation & trip parameter validation
- Boundary conditions (travelers: 1-50, duration: 1-30, budget: > 0)
- Invalid & non-existent destination IDs (400, 404)
- JWT validation (missing, malformed, tampered, wrong signature, expired -> 401)
- Protected endpoints & non-existent saved trips (404)
"""

import sys
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations, get_destination_detail
from app.routes.trip import get_personalized_activities
from app.routes.saved_trips import get_saved_trip, delete_saved_trip
from app.auth.security import (
    decode_access_token,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from app.models.destination import Destination


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. Recommendation Schema & Request Validation
# ---------------------------------------------------------------------------

def test_missing_required_duration():
    """Omitting trip_duration must raise ValidationError (FastAPI 422)."""
    with pytest.raises(ValidationError) as exc_info:
        RecommendationRequest(budget_per_person=50000)
    assert "trip_duration" in str(exc_info.value)


def test_missing_budget_and_budget_per_person():
    """Omitting both budget and budget_per_person must raise ValidationError (FastAPI 422)."""
    with pytest.raises(ValidationError) as exc_info:
        RecommendationRequest(trip_duration=3)
    assert "Either budget_per_person or budget must be provided" in str(exc_info.value)


def test_zero_budget_rejected():
    """Budget of 0 must be rejected (gt=0)."""
    with pytest.raises(ValidationError):
        RecommendationRequest(budget_per_person=0, trip_duration=3)

    with pytest.raises(ValidationError):
        RecommendationRequest(budget=0, trip_duration=3)


def test_negative_budget_rejected():
    """Negative budget must be rejected."""
    with pytest.raises(ValidationError):
        RecommendationRequest(budget_per_person=-1000, trip_duration=3)


def test_traveler_boundaries():
    """Travelers must be between 1 and 50 (ge=1, le=50)."""
    # Lower boundary
    with pytest.raises(ValidationError):
        RecommendationRequest(num_travelers=0, budget_per_person=50000, trip_duration=3)

    with pytest.raises(ValidationError):
        RecommendationRequest(num_travelers=-5, budget_per_person=50000, trip_duration=3)

    # Valid min
    req_min = RecommendationRequest(num_travelers=1, budget_per_person=50000, trip_duration=3)
    assert req_min.num_travelers == 1

    # Valid max
    req_max = RecommendationRequest(num_travelers=50, budget_per_person=50000, trip_duration=3)
    assert req_max.num_travelers == 50

    # Upper boundary violation
    with pytest.raises(ValidationError):
        RecommendationRequest(num_travelers=51, budget_per_person=50000, trip_duration=3)


def test_duration_boundaries():
    """Trip duration must be between 1 and 30 days (ge=1, le=30)."""
    # Lower boundary violation
    with pytest.raises(ValidationError):
        RecommendationRequest(trip_duration=0, budget_per_person=50000)

    # Valid min
    req_min = RecommendationRequest(trip_duration=1, budget_per_person=50000)
    assert req_min.trip_duration == 1

    # Valid max
    req_max = RecommendationRequest(trip_duration=30, budget_per_person=50000)
    assert req_max.trip_duration == 30

    # Upper boundary violation
    with pytest.raises(ValidationError):
        RecommendationRequest(trip_duration=31, budget_per_person=50000)


# ---------------------------------------------------------------------------
# 2. Trip Activities Endpoint Validation (/api/trips/activities/{destination_id})
# ---------------------------------------------------------------------------

def test_trip_activities_negative_destination_id(db_session):
    """Negative or zero destination ID must return HTTP 400."""
    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=0, budget=50000, trip_duration=3, db=db_session)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=-1, budget=50000, trip_duration=3, db=db_session)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_trip_activities_nonexistent_destination(db_session):
    """Non-existent positive destination ID must return HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=999999, budget=50000, trip_duration=3, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_trip_activities_zero_or_negative_budget(db_session):
    """Zero or negative budget must return HTTP 422."""
    ella = db_session.query(Destination).first()
    dest_id = ella.id if ella else 1

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=dest_id, budget=0, budget_per_person=0, trip_duration=3, db=db_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=dest_id, budget=-500, trip_duration=3, db=db_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_trip_activities_invalid_duration(db_session):
    """Duration outside 1-30 must return HTTP 422."""
    ella = db_session.query(Destination).first()
    dest_id = ella.id if ella else 1

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=dest_id, budget=50000, trip_duration=0, db=db_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=dest_id, budget=50000, trip_duration=31, db=db_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_trip_activities_invalid_travelers(db_session):
    """Travelers < 1 must return HTTP 422."""
    ella = db_session.query(Destination).first()
    dest_id = ella.id if ella else 1

    with pytest.raises(HTTPException) as exc_info:
        get_personalized_activities(destination_id=dest_id, budget=50000, trip_duration=3, num_travelers=0, db=db_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_destination_detail_nonexistent(db_session):
    """GET /destinations/{id} with non-existent ID must return HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        get_destination_detail(destination_id=999999, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# 3. JWT Authentication Validation
# ---------------------------------------------------------------------------

def test_jwt_malformed_token():
    """Malformed token string must raise HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not-a-valid-jwt-token")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid or expired token" in exc_info.value.detail


def test_jwt_tampered_token():
    """Tampering with a valid token payload or signature must raise HTTP 401."""
    token = create_access_token("test-user-id")
    tampered = token[:-4] + "xxxx"
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(tampered)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_wrong_secret():
    """Token signed with a different secret must raise HTTP 401."""
    fake_token = jwt.encode(
        {"sub": "test-user-id", "exp": datetime.now(timezone.utc) + timedelta(minutes=10)},
        "completely-wrong-secret",
        algorithm=ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(fake_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_expired_token():
    """Token with expiration in the past must raise HTTP 401."""
    expired_token = jwt.encode(
        {"sub": "test-user-id", "exp": datetime.now(timezone.utc) - timedelta(minutes=10)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_valid_token():
    """Valid JWT decodes to correct user_id."""
    user_id = "user-12345"
    token = create_access_token(user_id)
    decoded_id = decode_access_token(token)
    assert decoded_id == user_id


# ---------------------------------------------------------------------------
# 4. Saved Trip Not Found & Unauthorized
# ---------------------------------------------------------------------------

def test_saved_trip_not_found(db_session):
    """Accessing non-existent saved trip ID must raise HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        get_saved_trip(trip_id=9999999, current_user_id="user-xyz", db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Trip not found" in exc_info.value.detail


def test_delete_saved_trip_not_found(db_session):
    """Deleting non-existent saved trip ID must raise HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        delete_saved_trip(trip_id=9999999, current_user_id="user-xyz", db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Direct Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHASE 4: API VALIDATION & ERROR HANDLING TESTS")
    print("=" * 65)
    db = SessionLocal()
    tests = [
        ("Missing required trip_duration", test_missing_required_duration),
        ("Missing budget fields", test_missing_budget_and_budget_per_person),
        ("Zero budget rejected", test_zero_budget_rejected),
        ("Negative budget rejected", test_negative_budget_rejected),
        ("Traveler boundaries (1-50)", test_traveler_boundaries),
        ("Duration boundaries (1-30)", test_duration_boundaries),
        ("Negative destination ID (400)", lambda: test_trip_activities_negative_destination_id(db)),
        ("Nonexistent destination ID (404)", lambda: test_trip_activities_nonexistent_destination(db)),
        ("Zero/negative budget in trips (422)", lambda: test_trip_activities_zero_or_negative_budget(db)),
        ("Invalid duration in trips (422)", lambda: test_trip_activities_invalid_duration(db)),
        ("Invalid travelers in trips (422)", lambda: test_trip_activities_invalid_travelers(db)),
        ("Nonexistent destination detail (404)", lambda: test_destination_detail_nonexistent(db)),
        ("JWT malformed token (401)", test_jwt_malformed_token),
        ("JWT tampered token (401)", test_jwt_tampered_token),
        ("JWT wrong secret (401)", test_jwt_wrong_secret),
        ("JWT expired token (401)", test_jwt_expired_token),
        ("JWT valid token", test_jwt_valid_token),
        ("Saved trip not found (404)", lambda: test_saved_trip_not_found(db)),
        ("Delete saved trip not found (404)", lambda: test_delete_saved_trip_not_found(db)),
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
        print(f"[ALL TESTS PASSED] {len(tests)}/{len(tests)} API validation tests passed.")
    else:
        print("[FAILURE] Some API validation tests failed.")
        sys.exit(1)
