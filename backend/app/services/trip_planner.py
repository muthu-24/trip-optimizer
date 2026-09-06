from app.models.activity import Activity


def calculate_activity_score(
    activity: Activity,
    preferred_activities: list[str],
    travel_style: str,
    budget: float
) -> float:

    score = 0.0

    activity_category = activity.category.lower()
    preferred = [item.lower() for item in preferred_activities]
    style = travel_style.lower()

    # 1. Preferred activity match — 40 points
    if activity_category in preferred:
        score += 40

    # 2. Travel style match — 25 points
    travel_style_mapping = {
        "adventure": ["adventure", "hiking", "wildlife"],
        "beach": ["beach", "swimming", "surfing"],
        "culture": ["culture", "sightseeing"],
        "nature": ["nature", "hiking", "wildlife"],
        "relaxation": ["beach", "nature", "relaxation"],
    }

    matching_categories = travel_style_mapping.get(style, [])

    if activity_category in matching_categories:
        score += 25

    # 3. Budget suitability — 15 points
    if activity.estimated_cost == 0:
        score += 15
    elif activity.estimated_cost <= budget * 0.1:
        score += 15
    elif activity.estimated_cost <= budget * 0.2:
        score += 8

    # 4. Rating — 20 points
    if activity.rating:
        score += (activity.rating / 5) * 20

    return round(score, 2)


def generate_itinerary(
    scored_activities: list[dict],
    trip_duration: int
) -> list[dict]:

    itinerary = []

    # Create one day for each trip day
    for day in range(1, trip_duration + 1):
        itinerary.append({
            "day": day,
            "activities": [],
            "total_duration": 0,
            "total_cost": 0
        })

    # Distribute activities across the available days
    for index, activity in enumerate(scored_activities):

        day_index = index % trip_duration

        itinerary[day_index]["activities"].append(activity)

        itinerary[day_index]["total_duration"] += activity["duration"] or 0
        itinerary[day_index]["total_cost"] += activity["estimated_cost"]

    return itinerary
