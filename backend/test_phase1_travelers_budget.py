"""
Verification test suite for Phase 1: Travelers + Budget Model.

Tests:
1. 1-traveler budget & cost calculations (baseline check).
2. Multiple travelers (2, 4 travelers) group budget calculations.
3. Estimated trip cost accounts for travelers: daily_cost_per_person * duration * travelers + activity_costs * travelers.
4. Recommendation scoring is normalized per person (not multiplied by traveler count).
5. Validation rejects invalid travelers (< 1) and invalid budget (<= 0).
6. Itinerary generation correctly scales activity costs by traveler count.
7. Backward compatibility: legacy 'budget' field without 'num_travelers' works cleanly.
"""

import sys
from pydantic import ValidationError

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.routes.trip import get_personalized_activities
from app.services.recommendation_service import (
    calculate_trip_cost_breakdown,
    calculate_score_breakdown,
)
from app.models.destination import Destination

db = SessionLocal()

PASS = "[PASS]"
FAIL = "[FAIL]"
all_passed = True


def check(condition: bool, label: str):
    global all_passed
    status = PASS if condition else FAIL
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


print("=" * 65)
print("PHASE 1 VERIFICATION: TRAVELERS + BUDGET MODEL")
print("=" * 65)

# ---------------------------------------------------------------------------
# TEST 1: One Traveler Budget & Breakdown
# ---------------------------------------------------------------------------
print("\n[TEST 1] Single Traveler Baseline")
req_1 = RecommendationRequest(
    num_travelers=1,
    budget_per_person=50000,
    trip_duration=3,
    travel_style="nature",
    preferred_activities=["hiking", "nature"],
    season="December-April",
)
check(req_1.num_travelers == 1, "Number of travelers is 1")
check(req_1.budget_per_person == 50000, "Budget per person is Rs. 50,000")
check(req_1.total_group_budget == 50000, "Total group budget is Rs. 50,000")

res_1 = get_recommendations(req_1, db)
check(res_1["num_travelers"] == 1, "Response num_travelers is 1")
check(res_1["total_group_budget"] == 50000, "Response total_group_budget is 50,000")

dest_1 = res_1["recommendations"][0]
print(f"  Top destination: {dest_1['destination']} | Score: {dest_1['score']}%")
print(f"  Estimated cost (1 traveler, 3d): Rs. {dest_1['estimated_trip_cost']:,}")
expected_cost_1 = round(dest_1["average_daily_cost"] * 3 * 1, 2)
check(dest_1["estimated_trip_cost"] == expected_cost_1, f"Estimated trip cost matches daily * 3 * 1 ({expected_cost_1})")

# ---------------------------------------------------------------------------
# TEST 2: Multiple Travelers (2 and 4 travelers)
# ---------------------------------------------------------------------------
print("\n[TEST 2] Multiple Travelers Group Budget Scaling")
req_2 = RecommendationRequest(
    num_travelers=2,
    budget_per_person=50000,
    trip_duration=3,
    travel_style="nature",
    preferred_activities=["hiking", "nature"],
    season="December-April",
)
check(req_2.total_group_budget == 100000, f"2 travelers @ 50k = Rs. 100,000 group budget (got {req_2.total_group_budget})")

res_2 = get_recommendations(req_2, db)
check(res_2["num_travelers"] == 2, "Response num_travelers is 2")
check(res_2["total_group_budget"] == 100000, "Response total_group_budget is 100,000")

dest_2 = res_2["recommendations"][0]
print(f"  Top destination (2 travelers): {dest_2['destination']} | Score: {dest_2['score']}%")
print(f"  Estimated cost (2 travelers, 3d): Rs. {dest_2['estimated_trip_cost']:,}")
expected_cost_2 = round(dest_2["average_daily_cost"] * 3 * 2, 2)
check(dest_2["estimated_trip_cost"] == expected_cost_2, f"Estimated trip cost matches daily * 3 * 2 ({expected_cost_2})")
check(dest_2["estimated_trip_cost"] == expected_cost_1 * 2, "Estimated trip cost for 2 travelers is exactly 2x of 1 traveler")

req_4 = RecommendationRequest(
    num_travelers=4,
    budget_per_person=50000,
    trip_duration=3,
    travel_style="nature",
    preferred_activities=["hiking", "nature"],
    season="December-April",
)
check(req_4.total_group_budget == 200000, f"4 travelers @ 50k = Rs. 200,000 group budget (got {req_4.total_group_budget})")
res_4 = get_recommendations(req_4, db)
dest_4 = res_4["recommendations"][0]
expected_cost_4 = round(dest_4["average_daily_cost"] * 3 * 4, 2)
check(dest_4["estimated_trip_cost"] == expected_cost_4, f"Estimated trip cost for 4 travelers matches ({expected_cost_4})")

# ---------------------------------------------------------------------------
# TEST 3: Recommendation Scoring Normalization
# ---------------------------------------------------------------------------
print("\n[TEST 3] Recommendation Score Normalization Across Group Sizes")
score_1 = dest_1["score"]
score_2 = dest_2["score"]
score_4 = dest_4["score"]
check(score_1 == score_2 == score_4, f"Scores are identical regardless of traveler count ({score_1}% == {score_2}% == {score_4}%)")

# ---------------------------------------------------------------------------
# TEST 4: Cost Breakdown with Activity Cost Scaling
# ---------------------------------------------------------------------------
print("\n[TEST 4] Cost Breakdown Category & Activity Scaling")
destination_obj = db.query(Destination).filter(Destination.id == dest_1["id"]).first()

cb_1 = calculate_trip_cost_breakdown(destination_obj, trip_duration=3, total_activity_costs=5000.0, num_travelers=1)
cb_2 = calculate_trip_cost_breakdown(destination_obj, trip_duration=3, total_activity_costs=5000.0, num_travelers=2)

check(cb_1["trip_activities"] == 5000.0, f"1 traveler activity cost = 5,000 (got {cb_1['trip_activities']})")
check(cb_2["trip_activities"] == 10000.0, f"2 travelers activity cost = 10,000 (got {cb_2['trip_activities']})")
check(cb_2["trip_accommodation"] == cb_1["trip_accommodation"] * 2, "Accommodation scales 2x for 2 travelers")
check(cb_2["trip_food"] == cb_1["trip_food"] * 2, "Food scales 2x for 2 travelers")
check(cb_2["trip_transportation"] == cb_1["trip_transportation"] * 2, "Transport scales 2x for 2 travelers")
check(cb_2["estimated_trip_total"] == cb_1["estimated_trip_total"] * 2, "Total estimated trip scales 2x for 2 travelers")

# ---------------------------------------------------------------------------
# TEST 5: Itinerary Generation with Multiple Travelers
# ---------------------------------------------------------------------------
print("\n[TEST 5] Itinerary Generation with Travelers Count")
itin_res_1 = get_personalized_activities(
    destination_id=dest_1["id"],
    budget_per_person=50000,
    travel_style="nature",
    trip_duration=3,
    preferred_activities=["hiking", "nature"],
    num_travelers=1,
    db=db,
)
itin_res_2 = get_personalized_activities(
    destination_id=dest_1["id"],
    budget_per_person=50000,
    travel_style="nature",
    trip_duration=3,
    preferred_activities=["hiking", "nature"],
    num_travelers=2,
    db=db,
)

check(itin_res_1["num_travelers"] == 1, "Itinerary 1 reports num_travelers=1")
check(itin_res_2["num_travelers"] == 2, "Itinerary 2 reports num_travelers=2")
check(itin_res_2["cost_breakdown"]["trip_activities"] == itin_res_1["cost_breakdown"]["trip_activities"] * 2,
      "Itinerary total activity cost scales by 2x for 2 travelers")

# ---------------------------------------------------------------------------
# TEST 6: Backward Compatibility (legacy 'budget' field)
# ---------------------------------------------------------------------------
print("\n[TEST 6] Backward Compatibility")
req_legacy = RecommendationRequest(
    budget=60000,
    trip_duration=4,
    travel_style="beach",
    preferred_activities=["swimming"],
    season="May-September",
)
check(req_legacy.num_travelers == 1, "Default num_travelers is 1")
check(req_legacy.budget_per_person == 60000, "budget_per_person automatically populated from legacy budget")
check(req_legacy.total_group_budget == 60000, "total_group_budget is 60,000")

# ---------------------------------------------------------------------------
# TEST 7: Validation Rejection
# ---------------------------------------------------------------------------
print("\n[TEST 7] Validation Rules")
try:
    RecommendationRequest(
        num_travelers=0,
        budget_per_person=50000,
        trip_duration=3,
    )
    check(False, "Should reject num_travelers < 1")
except ValidationError:
    check(True, "Successfully rejected num_travelers < 1")

try:
    RecommendationRequest(
        num_travelers=1,
        budget_per_person=0,
        trip_duration=3,
    )
    check(False, "Should reject budget_per_person <= 0")
except ValidationError:
    check(True, "Successfully rejected budget_per_person <= 0")

try:
    RecommendationRequest(
        num_travelers=1,
        trip_duration=3,
    )
    check(False, "Should reject missing budget")
except ValidationError:
    check(True, "Successfully rejected request missing both budget and budget_per_person")

db.close()
print("\n" + "=" * 65)
if all_passed:
    print("[ALL TESTS PASSED] Phase 1 verification complete.")
else:
    print("[FAILURE] Some Phase 1 tests failed.")
    sys.exit(1)
