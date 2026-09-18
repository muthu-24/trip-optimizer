"""
Phase 4 Test Suite: Traveler & Budget Consistency
Covers:
- Formula verification: total_group_budget = budget_per_person * num_travelers
- Multi-traveler testing across 1, 2, 3, 5, 12 travelers and varied budgets
- Per-person score invariance across group sizes
- Category cost breakdown scaling (accommodation, food, transport, activities)
- Estimated trip total and cost per person mathematical consistency
- Backward compatibility for legacy requests specifying only `budget`
"""

import sys
import pytest

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.routes.trip import get_personalized_activities
from app.services.recommendation_service import calculate_trip_cost_breakdown
from app.models.destination import Destination


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. Total Group Budget Formula Verification
# ---------------------------------------------------------------------------

def test_total_group_budget_formula():
    """Verify total_group_budget == budget_per_person * num_travelers across 1, 2, 3, 5, 12 travelers."""
    test_cases = [
        (1, 25000),
        (2, 50000),
        (3, 75000),
        (5, 120000),
        (12, 150000),
    ]

    for travelers, budget_pp in test_cases:
        req = RecommendationRequest(
            num_travelers=travelers,
            budget_per_person=budget_pp,
            trip_duration=4,
            travel_style="nature",
        )
        expected = round(budget_pp * travelers, 2)
        assert req.total_group_budget == expected, (
            f"Expected total_group_budget {expected} for {travelers} travelers @ {budget_pp}, got {req.total_group_budget}"
        )


# ---------------------------------------------------------------------------
# 2. Per-Person Score Invariance
# ---------------------------------------------------------------------------

def test_score_invariance_across_diverse_group_sizes(db_session):
    """Destination preference score is invariant to group size (1, 2, 3, 5, 12)."""
    sizes = [1, 2, 3, 5, 12]
    scores_by_size = {}

    for size in sizes:
        req = RecommendationRequest(
            num_travelers=size,
            budget_per_person=60000,
            trip_duration=3,
            travel_style="culture",
            preferred_activities=["culture", "sightseeing"],
            season="January-April",
        )
        res = get_recommendations(req, db_session)
        scores_by_size[size] = {r["destination"]: r["score"] for r in res["recommendations"]}

    baseline = scores_by_size[1]
    for size in [2, 3, 5, 12]:
        for dest, score in baseline.items():
            assert scores_by_size[size][dest] == score, (
                f"Score for {dest} differed for group size {size}: {scores_by_size[size][dest]} vs {score}"
            )


# ---------------------------------------------------------------------------
# 3. Cost Breakdown Mathematical Consistency
# ---------------------------------------------------------------------------

def test_cost_breakdown_consistency(db_session):
    """Verify cost breakdown subcategories sum up correctly and scale with traveler count."""
    ella = db_session.query(Destination).filter(Destination.name == "Ella").first()
    assert ella is not None

    for travelers in [1, 2, 3, 5, 12]:
        duration = 4
        activity_costs = 3500.0

        breakdown = calculate_trip_cost_breakdown(
            destination=ella,
            trip_duration=duration,
            total_activity_costs=activity_costs,
            num_travelers=travelers,
        )

        acc = breakdown["trip_accommodation"]
        food = breakdown["trip_food"]
        trans = breakdown["trip_transportation"]
        acts = breakdown["trip_activities"]
        total = breakdown["estimated_trip_total"]
        cost_pp = breakdown["cost_per_person"]

        # Subcategories must sum to total
        assert round(acc + food + trans + acts, 2) == total

        # Activity costs must scale by travelers
        assert acts == round(activity_costs * travelers, 2)

        # Cost per person * travelers must equal total
        assert round(cost_pp * travelers, 2) == total


# ---------------------------------------------------------------------------
# 4. Itinerary Activities Cost Scaling with Travelers
# ---------------------------------------------------------------------------

def test_itinerary_activity_cost_scaling(db_session):
    """Activities total cost in itinerary scales linearly with traveler count."""
    ella = db_session.query(Destination).filter(Destination.name == "Ella").first()
    assert ella is not None

    res_1 = get_personalized_activities(
        destination_id=ella.id,
        budget_per_person=60000,
        trip_duration=3,
        num_travelers=1,
        db=db_session,
    )
    res_3 = get_personalized_activities(
        destination_id=ella.id,
        budget_per_person=60000,
        trip_duration=3,
        num_travelers=3,
        db=db_session,
    )

    cost_1 = res_1["cost_breakdown"]["trip_activities"]
    cost_3 = res_3["cost_breakdown"]["trip_activities"]
    assert round(cost_3, 2) == round(cost_1 * 3, 2)
    assert res_3["cost_breakdown"]["num_travelers"] == 3
    assert res_3["total_group_budget"] == round(60000 * 3, 2)


# ---------------------------------------------------------------------------
# 5. Backward Compatibility for Legacy 'budget' Field
# ---------------------------------------------------------------------------

def test_legacy_budget_backward_compatibility():
    """Requests with only 'budget' automatically populate budget_per_person and total_group_budget with 1 traveler."""
    req = RecommendationRequest(
        budget=80000,
        trip_duration=5,
        travel_style="relaxation",
    )
    assert req.num_travelers == 1
    assert req.budget_per_person == 80000
    assert req.total_group_budget == 80000


# ---------------------------------------------------------------------------
# Direct Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHASE 4: TRAVELER & BUDGET CONSISTENCY TESTS")
    print("=" * 65)
    db = SessionLocal()
    tests = [
        ("Total group budget formula (1, 2, 3, 5, 12 travelers)", test_total_group_budget_formula),
        ("Score invariance across group sizes", lambda: test_score_invariance_across_diverse_group_sizes(db)),
        ("Cost breakdown mathematical consistency", lambda: test_cost_breakdown_consistency(db)),
        ("Itinerary activity cost scaling", lambda: test_itinerary_activity_cost_scaling(db)),
        ("Legacy budget backward compatibility", test_legacy_budget_backward_compatibility),
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
        print(f"[ALL TESTS PASSED] {len(tests)}/{len(tests)} traveler & budget consistency tests passed.")
    else:
        print("[FAILURE] Some traveler & budget consistency tests failed.")
        sys.exit(1)
