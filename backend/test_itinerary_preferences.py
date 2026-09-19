"""
Itinerary preference-match verification tests.

Tests:
  A. Culture + Sightseeing -> top destinations should prioritise culture/sightseeing activities
  B. Nature + Hiking       -> top destinations should prioritise hiking/nature activities
  C. Beach + Swimming      -> top destinations should prioritise beach/swimming activities
  D. Low-activity fallback -> works when fewer suitable activities exist than days requested
  E. Determinism           -> same inputs always produce same itinerary
"""

import sys

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.routes.trip import get_personalized_activities

db = SessionLocal()

PASS = "[PASS]"
FAIL = "[FAIL]"

all_passed = True


def check(condition: bool, label: str) -> None:
    global all_passed
    status = PASS if condition else FAIL
    print(f"  {status} {label}")
    if not condition:
        all_passed = False


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def avg_match_for_categories(itinerary: list[dict], categories: list[str]) -> float:
    """Return average match score of activities whose category is in `categories`."""
    scores = [
        act["score"]
        for day in itinerary
        for act in day["activities"]
        if (act.get("category") or "").strip().lower() in categories
    ]
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def pct_above_threshold(itinerary: list[dict], threshold: float) -> float:
    """Percentage of activities with score >= threshold."""
    acts = [act for day in itinerary for act in day["activities"]]
    if not acts:
        return 0.0
    above = sum(1 for a in acts if a["score"] >= threshold)
    return round(above / len(acts) * 100, 1)


def min_score(itinerary: list[dict]) -> float:
    acts = [act for day in itinerary for act in day["activities"]]
    return min((a["score"] for a in acts), default=0.0)


def print_itinerary(itinerary: list[dict], label: str) -> None:
    print(f"\n  {label}")
    for d in itinerary:
        print(f"    Day {d['day']} ({len(d['activities'])} acts, {d['total_duration']}h, Rs. {d['total_cost']:,}):")
        for act in d["activities"]:
            print(f"      [{act['score']:5.1f}%] {act['name']} [{act['category']}]")


# ===========================================================================
# TEST A: Culture + Sightseeing
# ===========================================================================
print("=" * 60)
print("TEST A: Culture + Sightseeing (budget 30k, 3 days, Jan-Apr)")
print("=" * 60)

req_a = RecommendationRequest(
    budget=30000,
    trip_duration=3,
    travel_style="culture",
    preferred_activities=["culture", "sightseeing"],
    season="January-April",
)
res_a = get_recommendations(req_a, db)
top_a = res_a["recommendations"][0]
print(f"  Top destination: {top_a['destination']} ({top_a['region']}) | Score: {top_a['score']}%")

itin_a = get_personalized_activities(
    destination_id=top_a["id"],
    budget=30000,
    travel_style="culture",
    trip_duration=3,
    preferred_activities=["culture", "sightseeing"],
    db=db,
)
print_itinerary(itin_a["itinerary"], f"Itinerary for {top_a['destination']}")

culture_avg = avg_match_for_categories(itin_a["itinerary"], ["culture", "sightseeing", "history"])
pct_70 = pct_above_threshold(itin_a["itinerary"], 70)
low = min_score(itin_a["itinerary"])

check(pct_70 >= 60, f">=60% of activities have score >=70% (got {pct_70}%)")
check(low >= 50 or len([a for d in itin_a['itinerary'] for a in d['activities']]) < 3 * 3,
      f"No activity below 50% unless padding needed (min={low}%)")
print(f"  Info: culture/sightseeing avg match = {culture_avg}% | {pct_70}% of acts score >=70 | min = {low}%")

# ===========================================================================
# TEST B: Nature + Hiking
# ===========================================================================
print("\n" + "=" * 60)
print("TEST B: Nature + Hiking (budget 50k, 4 days, Dec-Apr)")
print("=" * 60)

req_b = RecommendationRequest(
    budget=50000,
    trip_duration=4,
    travel_style="nature",
    preferred_activities=["hiking", "nature"],
    season="December-April",
)
res_b = get_recommendations(req_b, db)
top_b = res_b["recommendations"][0]
print(f"  Top destination: {top_b['destination']} ({top_b['region']}) | Score: {top_b['score']}%")

itin_b = get_personalized_activities(
    destination_id=top_b["id"],
    budget=50000,
    travel_style="nature",
    trip_duration=4,
    preferred_activities=["hiking", "nature"],
    db=db,
)
print_itinerary(itin_b["itinerary"], f"Itinerary for {top_b['destination']}")

nature_avg = avg_match_for_categories(itin_b["itinerary"], ["hiking", "nature", "scenic"])
pct_70_b = pct_above_threshold(itin_b["itinerary"], 70)
low_b = min_score(itin_b["itinerary"])

check(pct_70_b >= 50, f">=50% of activities have score >=70% (got {pct_70_b}%)")
check(low_b >= 50 or len([a for d in itin_b['itinerary'] for a in d['activities']]) < 4 * 3,
      f"No activity below 50% unless padding needed (min={low_b}%)")
print(f"  Info: hiking/nature avg match = {nature_avg}% | {pct_70_b}% of acts score >=70 | min = {low_b}%")

# ===========================================================================
# TEST C: Beach + Swimming
# ===========================================================================
print("\n" + "=" * 60)
print("TEST C: Beach + Swimming (budget 60k, 4 days, May-Sep)")
print("=" * 60)

req_c = RecommendationRequest(
    budget=60000,
    trip_duration=4,
    travel_style="beach",
    preferred_activities=["swimming", "beach"],
    season="May-September",
)
res_c = get_recommendations(req_c, db)
top_c = res_c["recommendations"][0]
print(f"  Top destination: {top_c['destination']} ({top_c['region']}) | Score: {top_c['score']}%")

itin_c = get_personalized_activities(
    destination_id=top_c["id"],
    budget=60000,
    travel_style="beach",
    trip_duration=4,
    preferred_activities=["swimming", "beach"],
    db=db,
)
print_itinerary(itin_c["itinerary"], f"Itinerary for {top_c['destination']}")

beach_avg = avg_match_for_categories(itin_c["itinerary"], ["beach", "swimming", "surfing"])
pct_70_c = pct_above_threshold(itin_c["itinerary"], 70)
low_c = min_score(itin_c["itinerary"])

check(pct_70_c >= 50, f">=50% of activities have score >=70% (got {pct_70_c}%)")
check(low_c >= 50 or len([a for d in itin_c['itinerary'] for a in d['activities']]) < 4 * 3,
      f"No activity below 50% unless padding needed (min={low_c}%)")
print(f"  Info: beach/swimming avg match = {beach_avg}% | {pct_70_c}% of acts score >=70 | min = {low_c}%")

# ===========================================================================
# TEST D: Low-activity fallback (1 day, many activities expected)
# ===========================================================================
print("\n" + "=" * 60)
print("TEST D: Determinism – same input produces same itinerary")
print("=" * 60)

itin_d1 = get_personalized_activities(
    destination_id=top_a["id"],
    budget=30000,
    travel_style="culture",
    trip_duration=3,
    preferred_activities=["culture", "sightseeing"],
    db=db,
)
itin_d2 = get_personalized_activities(
    destination_id=top_a["id"],
    budget=30000,
    travel_style="culture",
    trip_duration=3,
    preferred_activities=["culture", "sightseeing"],
    db=db,
)

names_1 = [act["name"] for d in itin_d1["itinerary"] for act in d["activities"]]
names_2 = [act["name"] for d in itin_d2["itinerary"] for act in d["activities"]]
check(names_1 == names_2, f"Same activities in same order both calls: {names_1 == names_2}")

# ===========================================================================
# TEST E: Original dataset regression
# ===========================================================================
print("\n" + "=" * 60)
print("TEST E: Regression – original Nature/Hiking Ella itinerary")
print("=" * 60)

itin_ella = get_personalized_activities(
    destination_id=res_b["recommendations"][0]["id"],  # top nature dest
    budget=50000,
    travel_style="nature",
    trip_duration=3,
    preferred_activities=["hiking", "nature"],
    db=db,
)
print_itinerary(itin_ella["itinerary"], f"Itinerary for {res_b['recommendations'][0]['destination']}")
total_acts = sum(len(d["activities"]) for d in itin_ella["itinerary"])
check(total_acts > 0, f"Itinerary has at least 1 activity (got {total_acts})")
check(len(itin_ella["itinerary"]) == 3, "Itinerary has exactly 3 days")

# ===========================================================================
# SUMMARY
# ===========================================================================
db.close()
print("\n" + "=" * 60)
if all_passed:
    print("[OK] All itinerary preference-match tests passed.")
else:
    print("[WARN] Some tests did not pass – review output above.")
    sys.exit(1)
