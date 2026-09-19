"""
Phase 4 Test Suite: Itinerary Edge Cases & Route Reliability
Covers:
- Single activity (1 activity, "Main Experience" time slot, 0 distance, 0 transit)
- Two activities ("Morning" and "Afternoon & Sunset" slots, single route segment, valid distance)
- Many activities (<= 7.5 hrs/day, <= 3 acts/day, no duplicates, valid clustering)
- Insufficient activities (graceful duration reduction, no fake fillers, informative notice)
- Duplicate activity elimination (by ID and by Name)
- Haversine distance calculation accuracy against known coordinates
- Route optimization nearest-neighbor ordering & distance_to_next
"""

import sys
import pytest

from app.database import SessionLocal
from app.models.destination import Destination
from app.routes.trip import get_personalized_activities
from app.services.trip_planner import generate_itinerary
from app.services.route_optimizer import calculate_distance, optimize_route, estimate_transit_minutes


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. Single Activity Itinerary
# ---------------------------------------------------------------------------

def test_single_activity_itinerary():
    """An input of 1 activity returns a 1-day itinerary with 'Main Experience' slot, 0 distance, 0 transit."""
    mock_activity = {
        "id": 101,
        "name": "Sigiriya Rock Fortress",
        "category": "Culture",
        "estimated_cost": 5000.0,
        "duration": 3.0,
        "rating": 4.9,
        "latitude": 7.9570,
        "longitude": 80.7603,
        "score": 95.0,
    }

    itinerary = generate_itinerary([mock_activity], trip_duration=1)
    assert len(itinerary) == 1
    day_1 = itinerary[0]
    assert len(day_1["activities"]) == 1
    assert day_1["activities"][0]["id"] == 101
    assert day_1["activities"][0]["time_slot"] == "Main Experience"
    assert day_1["total_distance"] == 0.0
    assert day_1["transit_duration_minutes"] == 0


# ---------------------------------------------------------------------------
# 2. Two Activities Itinerary
# ---------------------------------------------------------------------------

def test_two_activities_itinerary():
    """An input of 2 activities assigns 'Morning' and 'Afternoon & Sunset', calculates 1 segment distance."""
    mock_act_1 = {
        "id": 201,
        "name": "Galle Fort Ramparts",
        "category": "Culture",
        "estimated_cost": 0.0,
        "duration": 2.0,
        "rating": 4.8,
        "latitude": 6.0320,
        "longitude": 80.2170,
        "score": 92.0,
    }
    mock_act_2 = {
        "id": 202,
        "name": "Maritime Museum",
        "category": "Sightseeing",
        "estimated_cost": 1200.0,
        "duration": 1.5,
        "rating": 4.5,
        "latitude": 6.0350,
        "longitude": 80.2200,
        "score": 85.0,
    }

    itinerary = generate_itinerary([mock_act_1, mock_act_2], trip_duration=1)
    assert len(itinerary) == 1
    day_1 = itinerary[0]
    assert len(day_1["activities"]) == 2

    # Check time slot labels
    assert day_1["activities"][0]["time_slot"] == "Morning"
    assert day_1["activities"][1]["time_slot"] == "Afternoon & Sunset"

    # Exactly 1 segment distance between them
    expected_dist = round(calculate_distance(6.0320, 80.2170, 6.0350, 80.2200), 2)
    assert day_1["total_distance"] == expected_dist
    assert day_1["activities"][0].get("distance_to_next") == expected_dist
    assert day_1["activities"][1].get("distance_to_next") is None


# ---------------------------------------------------------------------------
# 3. Many Activities Itinerary & Constraints
# ---------------------------------------------------------------------------

def test_many_activities_constraints():
    """Day plans must never exceed 7.5 hours or 3 activities per day."""
    mock_acts = [
        {
            "id": 300 + i,
            "name": f"Activity {i}",
            "category": "Nature" if i % 2 == 0 else "Culture",
            "estimated_cost": 500.0 * i,
            "duration": 2.5,
            "rating": 4.5,
            "latitude": 6.8 + 0.01 * i,
            "longitude": 80.5 + 0.01 * i,
            "score": 90.0 - i,
        }
        for i in range(12)
    ]

    itinerary = generate_itinerary(mock_acts, trip_duration=4)
    all_seen_ids = set()

    for day in itinerary:
        # Max 3 activities per day
        assert len(day["activities"]) <= 3, f"Day {day['day']} exceeded 3 activities ({len(day['activities'])})"
        # Max 7.5 hours activity duration per day
        assert day["total_activity_duration"] <= 7.5, f"Day {day['day']} exceeded 7.5h ({day['total_activity_duration']})"

        for act in day["activities"]:
            assert act["id"] not in all_seen_ids, f"Activity {act['id']} duplicated across days"
            all_seen_ids.add(act["id"])


# ---------------------------------------------------------------------------
# 4. Insufficient Activities Graceful Reduction
# ---------------------------------------------------------------------------

def test_insufficient_activities_graceful_reduction(db_session):
    """When requested duration exceeds available activities, reduce days gracefully without fake fillers."""
    ella = db_session.query(Destination).filter(Destination.name == "Ella").first()
    assert ella is not None

    res = get_personalized_activities(
        destination_id=ella.id,
        budget_per_person=60000,
        trip_duration=10,  # Requesting 10 days for Ella (only ~6 real activities)
        db=db_session,
    )

    itin = res["itinerary"]
    assert res["requested_trip_duration"] == 10
    assert res["insufficient_activities"] is True
    assert res["actual_trip_duration"] < 10
    assert len(itin) == res["actual_trip_duration"]
    assert res["itinerary_notice"] is not None
    assert "fewer than your requested 10 days" in res["itinerary_notice"]

    # Verify every activity is authentic and non-negative
    for day in itin:
        for act in day["activities"]:
            assert act["id"] > 0
            assert act["name"] not in ["", "Free Time", "Placeholder", "Explore"]


# ---------------------------------------------------------------------------
# 5. Duplicate Elimination
# ---------------------------------------------------------------------------

def test_duplicate_activity_elimination():
    """Duplicate activities by ID or by Name must be filtered out cleanly."""
    duplicates_input = [
        {"id": 1, "name": "Temple of the Tooth", "category": "Culture", "duration": 2.0, "estimated_cost": 1000, "rating": 4.8, "score": 90.0},
        {"id": 1, "name": "Temple of the Tooth", "category": "Culture", "duration": 2.0, "estimated_cost": 1000, "rating": 4.8, "score": 90.0},
        {"id": 2, "name": "temple of the tooth", "category": "Culture", "duration": 2.0, "estimated_cost": 1000, "rating": 4.8, "score": 90.0},
        {"id": 3, "name": "Royal Botanical Gardens", "category": "Nature", "duration": 2.5, "estimated_cost": 2000, "rating": 4.7, "score": 88.0},
    ]

    itinerary = generate_itinerary(duplicates_input, trip_duration=2)
    flat_acts = [act for day in itinerary for act in day["activities"]]
    assert len(flat_acts) == 2
    names = [act["name"].lower() for act in flat_acts]
    assert "temple of the tooth" in names
    assert "royal botanical gardens" in names


# ---------------------------------------------------------------------------
# 6. Haversine Distance Accuracy
# ---------------------------------------------------------------------------

def test_haversine_distance_accuracy():
    """Haversine distance between Colombo and Galle Fort (~105 km great-circle) is within +/- 2 km."""
    # Colombo: 6.9271° N, 79.8612° E
    # Galle:   6.0535° N, 80.2210° E
    dist = calculate_distance(6.9271, 79.8612, 6.0535, 80.2210)
    assert 103.0 <= dist <= 107.0

    # Same coordinate distance must be 0
    assert calculate_distance(6.0535, 80.2210, 6.0535, 80.2210) == 0.0

    # None coordinates return 0.0
    assert calculate_distance(None, None, 6.0535, 80.2210) == 0.0


# ---------------------------------------------------------------------------
# 7. Route Optimization Nearest-Neighbor Ordering
# ---------------------------------------------------------------------------

def test_route_optimization_ordering():
    """Route optimization sorts activities into a minimal-distance path."""
    # Point A -> Point B (close to A) -> Point C (far from A, close to B)
    # Give them out of order: A, C, B
    pt_a = {"id": 1, "name": "A", "latitude": 6.000, "longitude": 80.000}
    pt_b = {"id": 2, "name": "B", "latitude": 6.005, "longitude": 80.005}
    pt_c = {"id": 3, "name": "C", "latitude": 6.010, "longitude": 80.010}

    # Pass in permuted order: A, C, B
    ordered, total_dist, method = optimize_route([pt_a, pt_c, pt_b])

    # Method for <= 5 items is "exact"
    assert method == "exact"
    assert len(ordered) == 3
    # Shortest path through collinear points A(0), B(5), C(10) is A-B-C or C-B-A
    path_names = [x["name"] for x in ordered]
    assert path_names in (["A", "B", "C"], ["C", "B", "A"])
    assert total_dist > 0
    assert ordered[0]["distance_to_next"] is not None


# ---------------------------------------------------------------------------
# Direct Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHASE 4: ITINERARY EDGE CASES & ROUTE RELIABILITY")
    print("=" * 65)
    db = SessionLocal()
    tests = [
        ("Single activity itinerary (Main Experience, 0 dist)", test_single_activity_itinerary),
        ("Two activities itinerary (slots, distance)", test_two_activities_itinerary),
        ("Many activities constraints (<=7.5h, <=3/day)", test_many_activities_constraints),
        ("Insufficient activities graceful reduction", lambda: test_insufficient_activities_graceful_reduction(db)),
        ("Duplicate activity elimination", test_duplicate_activity_elimination),
        ("Haversine distance accuracy", test_haversine_distance_accuracy),
        ("Route optimization nearest-neighbor ordering", test_route_optimization_ordering),
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
        print(f"[ALL TESTS PASSED] {len(tests)}/{len(tests)} itinerary edge-case tests passed.")
    else:
        print("[FAILURE] Some itinerary edge-case tests failed.")
        sys.exit(1)
