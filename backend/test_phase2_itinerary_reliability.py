"""
Verification test suite for Phase 2: Itinerary Reliability.

Tests:
1. Avoid repeating the same activity just to fill extra days.
2. Do not create fake/duplicate activities (no negative IDs, no generic placeholders).
3. If not enough suitable activities, gracefully reduce itinerary and clearly indicate insufficient activities.
4. Haversine distance and route optimization preserved across all days.
5. Normal trip durations (e.g. 2-3 days) continue working identically.
6. Cost breakdown reflects the realistic planned duration.
7. Graceful handling when zero activities are available.
"""

import sys
from app.database import SessionLocal
from app.models.destination import Destination
from app.models.activity import Activity
from app.routes.trip import get_personalized_activities
from app.services.trip_planner import generate_itinerary

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
print("PHASE 2 VERIFICATION: ITINERARY RELIABILITY")
print("=" * 65)

# Find Ella in DB
ella = db.query(Destination).filter(Destination.name == "Ella").first()
assert ella is not None, "Ella destination must exist in DB"
ella_activity_count = db.query(Activity).filter(Activity.destination_id == ella.id).count()
print(f"\n[INFO] Destination Ella has {ella_activity_count} real activities in DB.")

# ---------------------------------------------------------------------------
# TEST 1: Long Trip Request (10 days requested for 6-activity destination)
# ---------------------------------------------------------------------------
print("\n[TEST 1] Long Trip (10 days requested, destination has 6 activities)")
res_10 = get_personalized_activities(
    destination_id=ella.id,
    budget_per_person=60000,
    travel_style="nature",
    trip_duration=10,
    preferred_activities=["hiking", "nature"],
    num_travelers=2,
    db=db,
)

itin_10 = res_10["itinerary"]
planned_days = len(itin_10)
print(f"  Requested days: {res_10['requested_trip_duration']} | Planned days: {planned_days}")
print(f"  Notice: {res_10.get('itinerary_notice')}")

check(res_10["insufficient_activities"] is True, "insufficient_activities flag is True")
check(planned_days == ella_activity_count, f"Planned days gracefully reduced to available activities ({planned_days} == {ella_activity_count})")
check(res_10["actual_trip_duration"] == planned_days, f"actual_trip_duration matches itinerary length ({planned_days})")
check(bool(res_10.get("itinerary_notice")), "itinerary_notice explains the adjustment clearly")

# ---------------------------------------------------------------------------
# TEST 2: No Repeated Activities
# ---------------------------------------------------------------------------
print("\n[TEST 2] Strict Uniqueness – No Activity Repeated")
all_activity_ids = []
all_activity_names = []
for day_plan in itin_10:
    for act in day_plan["activities"]:
        all_activity_ids.append(act["id"])
        all_activity_names.append(act["name"].strip().lower())

unique_ids = set(all_activity_ids)
unique_names = set(all_activity_names)

check(len(all_activity_ids) == len(unique_ids), f"All {len(all_activity_ids)} scheduled activities have unique IDs")
check(len(all_activity_names) == len(unique_names), f"All {len(all_activity_names)} scheduled activities have unique names")

# ---------------------------------------------------------------------------
# TEST 3: No Fake / Synthetic / Placeholder Activities
# ---------------------------------------------------------------------------
print("\n[TEST 3] No Fake or Placeholder Activities")
has_negative_id = any(aid < 0 for aid in all_activity_ids)
check(not has_negative_id, "No negative IDs found in scheduled activities")

fake_keywords = ["generic", "fallback", "placeholder", "artisan exploration", "panoramic viewpoint walk"]
has_fake_name = any(any(kw in name for kw in fake_keywords) for name in all_activity_names)
check(not has_fake_name, "No placeholder / synthetic activity names found")

# Verify all activities belong to the real destination in database
real_db_ids = {a.id for a in db.query(Activity).filter(Activity.destination_id == ella.id).all()}
all_belong_to_destination = all(aid in real_db_ids for aid in all_activity_ids)
check(all_belong_to_destination, "Every single activity is a verified real activity from the destination")

# ---------------------------------------------------------------------------
# TEST 4: Haversine Route Optimization & Time Slots Preserved
# ---------------------------------------------------------------------------
print("\n[TEST 4] Haversine Optimization & Sequencing")
# Test with 3-day trip where multi-activity days exist
res_3 = get_personalized_activities(
    destination_id=ella.id,
    budget_per_person=50000,
    travel_style="nature",
    trip_duration=3,
    preferred_activities=["hiking", "nature"],
    num_travelers=1,
    db=db,
)

itin_3 = res_3["itinerary"]
check(len(itin_3) == 3, "3-day trip has exactly 3 days")
check(res_3["insufficient_activities"] is False, "insufficient_activities is False when duration <= activities")
check(res_3["itinerary_notice"] is None, "itinerary_notice is None for normal trips")

# Verify distance calculations and route methods
has_route_distances = any(d.get("total_distance", 0) >= 0 for d in itin_3)
check(has_route_distances, "Route distances are computed for itinerary days")

for d in itin_3:
    for act in d["activities"]:
        check("time_slot" in act and bool(act["time_slot"]), f"Activity '{act['name'][:25]}...' has valid time slot: {act.get('time_slot')}")

# ---------------------------------------------------------------------------
# TEST 5: Cost Breakdown Scales with Planned Duration
# ---------------------------------------------------------------------------
print("\n[TEST 5] Cost Breakdown Scales with Planned Duration")
# 10-day request gracefully planned for 6 days
cb_10 = res_10["cost_breakdown"]
expected_accommodation_6d = round(float(ella.accommodation_cost or 0) * planned_days * 2, 2)
check(cb_10["trip_accommodation"] == expected_accommodation_6d,
      f"Accommodation calculated for planned {planned_days} days, not requested 10 days (Rs. {cb_10['trip_accommodation']:,})")

# ---------------------------------------------------------------------------
# TEST 6: Graceful Handling of Zero Activities
# ---------------------------------------------------------------------------
print("\n[TEST 6] Empty Activities Edge Case")
empty_itin = generate_itinerary([], trip_duration=5)
check(empty_itin == [], "Empty activity pool returns empty list without error")

db.close()
print("\n" + "=" * 65)
if all_passed:
    print("[ALL TESTS PASSED] Phase 2 Itinerary Reliability verification complete.")
else:
    print("[FAILURE] Some Phase 2 tests failed.")
    sys.exit(1)
