"""
Verification script for Sri Lanka dataset recommendation and itinerary tests.
"""

from app.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest
from app.routes.recommendation import get_recommendations
from app.routes.trip import get_personalized_activities

db = SessionLocal()

print("==================================================")
print("TEST A: Nature / Hiking (Budget: 50k, 4 Days, Dec-Apr)")
print("==================================================")
req_a = RecommendationRequest(
    budget=50000,
    trip_duration=4,
    travel_style="nature",
    preferred_activities=["hiking", "nature"],
    season="December-April",
)
res_a = get_recommendations(req_a, db)
for idx, r in enumerate(res_a["recommendations"][:5], 1):
    print(f"  #{idx} {r['destination']} ({r['region']}) | Score: {r['score']}% | Est. Cost: Rs. {r['estimated_trip_cost']:,}")
    print(f"      Reasons: {r['reasons'][:2]}")

print("\n==================================================")
print("TEST B: Beach / Swimming (Budget: 60k, 4 Days, May-Sep)")
print("==================================================")
req_b = RecommendationRequest(
    budget=60000,
    trip_duration=4,
    travel_style="beach",
    preferred_activities=["swimming", "beach"],
    season="May-September",
)
res_b = get_recommendations(req_b, db)
for idx, r in enumerate(res_b["recommendations"][:5], 1):
    print(f"  #{idx} {r['destination']} ({r['region']}) | Score: {r['score']}% | Est. Cost: Rs. {r['estimated_trip_cost']:,}")
    print(f"      Reasons: {r['reasons'][:2]}")

print("\n==================================================")
print("TEST C: Culture / Sightseeing (Budget: 30k, 2 Days, Jan-Apr)")
print("==================================================")
req_c = RecommendationRequest(
    budget=30000,
    trip_duration=2,
    travel_style="culture",
    preferred_activities=["culture", "sightseeing"],
    season="January-April",
)
res_c = get_recommendations(req_c, db)
for idx, r in enumerate(res_c["recommendations"][:5], 1):
    print(f"  #{idx} {r['destination']} ({r['region']}) | Score: {r['score']}% | Est. Cost: Rs. {r['estimated_trip_cost']:,}")
    print(f"      Reasons: {r['reasons'][:2]}")

print("\n==================================================")
print("ITINERARY GENERATION TEST: Ella (Destination ID: 1, 3 Days)")
print("==================================================")
itin_res = get_personalized_activities(
    destination_id=1,
    budget=50000,
    travel_style="nature",
    trip_duration=3,
    preferred_activities=["hiking", "nature"],
    db=db,
)
for d in itin_res["itinerary"]:
    print(f"  Day {d['day']} ({len(d['activities'])} activities, {d['total_duration']} hrs, Rs. {d['total_cost']:,}):")
    for act in d["activities"]:
        cost_str = f"Rs. {act['estimated_cost']:,}" if act["estimated_cost"] > 0 else "Free Entry"
        print(f"    - {act['name']} [{act['category']}] ({act['duration']}h, {cost_str}, Match: {act['score']}%)")

if itin_res.get("cost_breakdown"):
    cb = itin_res["cost_breakdown"]
    print("\n  Cost Breakdown for Trip:")
    print(f"    Stay: Rs. {cb['trip_accommodation']:,} | Food: Rs. {cb['trip_food']:,} | Transport: Rs. {cb['trip_transportation']:,} | Activities: Rs. {cb['trip_activities']:,}")
    print(f"    Total Estimated Trip Cost: Rs. {cb['estimated_trip_total']:,}")

db.close()
print("\n[OK] All backend test cases executed successfully.")
