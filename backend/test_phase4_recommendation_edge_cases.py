"""
Phase 4 Test Suite: Recommendation Edge Cases & Explainability
Covers:
- Extreme budgets: Rs. 1,000, Rs. 50,000, Rs. 5,000,000
- Traveler scalability & score invariance (1, 2, 4, 10 travelers)
- Duration boundary testing (1 day, 7 days, 30 days)
- Complete season mismatch (0 overlap, degradation, explanatory reason)
- Complete activity mismatch (0 match, degradation, explanatory reason)
- Activity synonym mapping (trekking->hiking, safaris->wildlife, diving->swimming)
- All 6 travel styles (adventure, beach, culture, nature, wildlife, relaxation)
- Determinism: identical input yields identical output
- Explainability: reason consistency with scores
"""

import sys
import pytest

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.services.recommendation_service import (
    calculate_score_breakdown,
    generate_recommendation_reasons,
    calculate_trip_cost_breakdown,
    normalize_activity,
    match_activities,
    calculate_season_overlap,
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
# 1. Budget Edge Cases
# ---------------------------------------------------------------------------

def test_extreme_low_budget(db_session):
    """Extremely low budget (Rs. 1,000) does not crash, scores budget 0%, and generates appropriate reasons."""
    req = RecommendationRequest(
        budget_per_person=1000,
        trip_duration=3,
        travel_style="nature",
        season="December-April",
        preferred_activities=["hiking"],
    )
    res = get_recommendations(req, db_session)
    assert "recommendations" in res
    assert len(res["recommendations"]) > 0

    top = res["recommendations"][0]
    # For every destination, a 3-day trip at Rs. 1,000 per person will exceed the budget
    assert top["estimated_trip_cost_per_person"] > 1000
    assert top["score_breakdown"]["budget_match"] == 0
    # Reason should state it exceeds budget
    budget_reasons = [r for r in top["reasons"] if "budget" in r.lower()]
    assert len(budget_reasons) > 0
    assert any("above your" in r.lower() or "exceed" in r.lower() for r in budget_reasons)


def test_normal_budget(db_session):
    """Normal budget (Rs. 60,000) produces valid recommendations with positive budget scores."""
    req = RecommendationRequest(
        budget_per_person=60000,
        trip_duration=3,
        travel_style="beach",
        season="May-September",
        preferred_activities=["swimming"],
    )
    res = get_recommendations(req, db_session)
    assert len(res["recommendations"]) > 0
    # Top destination should have a high score
    assert res["recommendations"][0]["score"] > 50


def test_extreme_high_budget(db_session):
    """Extremely high budget (Rs. 5,000,000) awards 100% budget match to all destinations without overflow."""
    req = RecommendationRequest(
        budget_per_person=5_000_000,
        trip_duration=5,
        travel_style="culture",
        season="January-April",
        preferred_activities=["culture"],
    )
    res = get_recommendations(req, db_session)
    for rec in res["recommendations"]:
        assert rec["score_breakdown"]["budget_match"] == 100
        # Reasons should indicate fits within budget
        assert any("fits within your budget" in r.lower() for r in rec["reasons"])


# ---------------------------------------------------------------------------
# 2. Traveler Count Scalability & Score Invariance
# ---------------------------------------------------------------------------

def test_traveler_score_invariance(db_session):
    """Scores per destination must be identical regardless of traveler count (1, 2, 4, 10)."""
    traveler_counts = [1, 2, 4, 10]
    results = {}

    for count in traveler_counts:
        req = RecommendationRequest(
            num_travelers=count,
            budget_per_person=50000,
            trip_duration=3,
            travel_style="nature",
            preferred_activities=["hiking", "nature"],
            season="December-April",
        )
        res = get_recommendations(req, db_session)
        results[count] = {r["destination"]: r["score"] for r in res["recommendations"]}

    baseline = results[1]
    for count in [2, 4, 10]:
        for dest, score in baseline.items():
            assert results[count][dest] == score, (
                f"Score for {dest} changed with {count} travelers: {results[count][dest]} vs baseline {score}"
            )


def test_traveler_cost_scaling(db_session):
    """Estimated trip cost must scale proportionally with traveler count."""
    req_1 = RecommendationRequest(
        num_travelers=1,
        budget_per_person=50000,
        trip_duration=3,
        travel_style="nature",
    )
    req_4 = RecommendationRequest(
        num_travelers=4,
        budget_per_person=50000,
        trip_duration=3,
        travel_style="nature",
    )
    res_1 = get_recommendations(req_1, db_session)
    res_4 = get_recommendations(req_4, db_session)

    cost_1 = res_1["recommendations"][0]["estimated_trip_cost"]
    cost_4 = res_4["recommendations"][0]["estimated_trip_cost"]
    assert round(cost_4, 2) == round(cost_1 * 4, 2)


# ---------------------------------------------------------------------------
# 3. Trip Duration Boundary Cases
# ---------------------------------------------------------------------------

def test_duration_boundaries_recommendations(db_session):
    """1-day and 30-day trips execute stably without error."""
    for duration in [1, 7, 30]:
        req = RecommendationRequest(
            num_travelers=2,
            budget_per_person=100000,
            trip_duration=duration,
            travel_style="adventure",
            season="December-April",
        )
        res = get_recommendations(req, db_session)
        assert len(res["recommendations"]) > 0
        top = res["recommendations"][0]
        assert top["estimated_trip_cost"] == round(top["average_daily_cost"] * duration * 2, 2)


# ---------------------------------------------------------------------------
# 4. Season Mismatch Edge Case
# ---------------------------------------------------------------------------

def test_season_mismatch(db_session):
    """A complete season mismatch results in 0 season score and an explanatory reason."""
    ella = db_session.query(Destination).filter(Destination.name == "Ella").first()
    assert ella is not None
    assert "december-april" in ella.best_season.lower()

    # User visits in May-September (0 overlap with December-April)
    req = RecommendationRequest(
        budget_per_person=50000,
        trip_duration=3,
        travel_style="nature",
        season="May-September",
        preferred_activities=["hiking"],
    )
    res = get_recommendations(req, db_session)
    ella_rec = next(r for r in res["recommendations"] if r["destination"] == "Ella")

    assert ella_rec["score_breakdown"]["season_match"] == 0
    # Reason should mention no overlap
    assert any("no overlap" in r.lower() or "best visited in" in r.lower() for r in ella_rec["reasons"])


# ---------------------------------------------------------------------------
# 5. Activity Mismatch Edge Case
# ---------------------------------------------------------------------------

def test_activity_mismatch(db_session):
    """Zero matching activities results in 0 activity score and does not claim matching activities."""
    req = RecommendationRequest(
        budget_per_person=50000,
        trip_duration=3,
        travel_style="nature",
        season="December-April",
        preferred_activities=["snowboarding", "ice_skating"],
    )
    res = get_recommendations(req, db_session)
    for rec in res["recommendations"]:
        assert rec["score_breakdown"]["activity_match"] == 0
        # Must not claim that it matches the user's preferred activities
        assert not any("matches" in r.lower() and "preferred activities" in r.lower() for r in rec["reasons"])


# ---------------------------------------------------------------------------
# 6. Activity Synonyms & Normalization
# ---------------------------------------------------------------------------

def test_activity_synonyms():
    """Verify synonyms are properly mapped to canonical activity categories."""
    assert normalize_activity("trekking") == "hiking"
    assert normalize_activity("trek") == "hiking"
    assert normalize_activity("safaris") == "wildlife"
    assert normalize_activity("bird watching") == "wildlife"
    assert normalize_activity("diving") == "swimming"
    assert normalize_activity("water sports") == "swimming"
    assert normalize_activity("spa") == "relaxation"
    assert normalize_activity("temple") == "culture"

    dest_activities = ["hiking", "nature", "wildlife"]
    matched, ratio = match_activities(["trekking", "safaris"], dest_activities)
    assert "trekking" in matched
    assert "safaris" in matched
    assert ratio == 1.0


# ---------------------------------------------------------------------------
# 7. Travel Styles Compatibility Testing
# ---------------------------------------------------------------------------

def test_all_travel_styles(db_session):
    """Every supported travel style executes without error and computes valid scores."""
    styles = ["adventure", "beach", "culture", "nature", "wildlife", "relaxation"]
    for style in styles:
        req = RecommendationRequest(
            budget_per_person=50000,
            trip_duration=3,
            travel_style=style,
            season="December-April",
        )
        res = get_recommendations(req, db_session)
        assert len(res["recommendations"]) > 0
        for r in res["recommendations"]:
            assert 0 <= r["score_breakdown"]["travel_style_match"] <= 100
            assert 0 <= r["score"] <= 100


# ---------------------------------------------------------------------------
# 8. Determinism
# ---------------------------------------------------------------------------

def test_recommendation_determinism(db_session):
    """Running identical recommendation requests 3 times produces identical outputs."""
    req = RecommendationRequest(
        budget_per_person=45000,
        trip_duration=4,
        travel_style="culture",
        season="January-April",
        preferred_activities=["culture", "sightseeing"],
        num_travelers=2,
    )
    res_1 = get_recommendations(req, db_session)
    res_2 = get_recommendations(req, db_session)
    res_3 = get_recommendations(req, db_session)

    list_1 = [(r["id"], r["score"], r["reasons"]) for r in res_1["recommendations"]]
    list_2 = [(r["id"], r["score"], r["reasons"]) for r in res_2["recommendations"]]
    list_3 = [(r["id"], r["score"], r["reasons"]) for r in res_3["recommendations"]]

    assert list_1 == list_2 == list_3


# ---------------------------------------------------------------------------
# Direct Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHASE 4: RECOMMENDATION EDGE CASES & EXPLAINABILITY")
    print("=" * 65)
    db = SessionLocal()
    tests = [
        ("Extreme low budget (Rs. 1,000)", lambda: test_extreme_low_budget(db)),
        ("Normal budget (Rs. 60,000)", lambda: test_normal_budget(db)),
        ("Extreme high budget (Rs. 5,000,000)", lambda: test_extreme_high_budget(db)),
        ("Traveler score invariance (1, 2, 4, 10)", lambda: test_traveler_score_invariance(db)),
        ("Traveler cost scaling", lambda: test_traveler_cost_scaling(db)),
        ("Duration boundaries (1, 7, 30 days)", lambda: test_duration_boundaries_recommendations(db)),
        ("Season mismatch", lambda: test_season_mismatch(db)),
        ("Activity mismatch", lambda: test_activity_mismatch(db)),
        ("Activity synonyms", test_activity_synonyms),
        ("All 6 travel styles", lambda: test_all_travel_styles(db)),
        ("Recommendation determinism", lambda: test_recommendation_determinism(db)),
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
        print(f"[ALL TESTS PASSED] {len(tests)}/{len(tests)} recommendation edge-case tests passed.")
    else:
        print("[FAILURE] Some recommendation edge-case tests failed.")
        sys.exit(1)
