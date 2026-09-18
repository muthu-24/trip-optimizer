from app.models.activity import Activity
from app.services.route_optimizer import optimize_route, calculate_distance, estimate_transit_minutes


# ---------------------------------------------------------------------------
# Score thresholds
# ---------------------------------------------------------------------------
HIGH_MATCH_THRESHOLD = 70.0   # Preferred tier – always include when possible
LOW_MATCH_THRESHOLD = 50.0    # Acceptable tier – include for variety / padding
# Below LOW_MATCH_THRESHOLD → padding only (used when not enough above-50 activities)

# Maximum number of activities per category before we start diversifying
MAX_CATEGORY_SHARE = 0.60   # No single category can exceed 60 % of total slots





def calculate_activity_score(
    activity: Activity,
    preferred_activities: list[str],
    travel_style: str,
    budget: float
) -> float:
    """
    Calculate compatibility score (0-100) for an activity.

    Factors:
    - Preferred activity match: 40 points
    - Travel style match:       25 points
    - Budget suitability:       15 points
    - Rating:                   20 points
    """
    score = 0.0

    activity_category = (activity.category or "").strip().lower()
    preferred = [item.strip().lower() for item in preferred_activities if item.strip()]
    style = (travel_style or "").strip().lower()

    # 1. Preferred activity match — 40 points
    if preferred:
        if activity_category in preferred:
            score += 40.0
        elif any(pref in activity_category or activity_category in pref for pref in preferred):
            score += 30.0
    else:
        # Neutral if user didn't specify preferences
        score += 30.0

    # 2. Travel style match — 25 points
    travel_style_mapping = {
        "adventure": ["adventure", "hiking", "wildlife", "surfing"],
        "beach": ["beach", "swimming", "surfing", "relaxation"],
        "culture": ["culture", "sightseeing", "history"],
        "nature": ["nature", "hiking", "wildlife", "scenic"],
        "wildlife": ["wildlife", "nature", "adventure"],
        "relaxation": ["beach", "nature", "relaxation", "sightseeing"],
    }

    matching_categories = travel_style_mapping.get(style, [])

    if activity_category in matching_categories:
        score += 25.0
    elif any(cat in activity_category for cat in matching_categories):
        score += 18.0
    elif not style:
        score += 20.0

    # 3. Budget suitability — 15 points
    cost = float(activity.estimated_cost or 0.0)
    if cost == 0.0:
        score += 15.0
    elif cost <= budget * 0.10:
        score += 15.0
    elif cost <= budget * 0.20:
        score += 10.0
    elif cost <= budget * 0.35:
        score += 5.0

    # 4. Rating — 20 points
    if activity.rating:
        score += (float(activity.rating) / 5.0) * 20.0

    return round(min(score, 100.0), 1)


# ---------------------------------------------------------------------------
# Activity selection with preference-aware filtering & diversity enforcement
# ---------------------------------------------------------------------------

def select_itinerary_activities(
    scored_activities: list[dict],
    trip_duration: int,
) -> list[dict]:
    """
    Choose the best activities for an itinerary from a pre-scored, pre-sorted list.

    Strategy (deterministic):
    1. Sort by score DESC, then name ASC as a tiebreaker (ensures determinism).
    2. Tier 1 (high match >=70 %): add all that fit within total slot budget.
    3. Tier 2 (acceptable 50-69 %): add to fill remaining slots, enforcing
       category diversity (no single category > MAX_CATEGORY_SHARE of total slots).
    4. Tier 3 (padding <50 %): fill any remaining slots if there are still not
       enough activities for the requested duration.
    5. Strict uniqueness: No activity is ever selected more than once.
    6. Total slot budget = trip_duration * max_daily_activities (= trip_duration * 3).

    Returns an ordered list (high-score first) of unique selected activity dicts.
    """
    max_daily_activities = 3
    total_slots = trip_duration * max_daily_activities

    # Stable deterministic sort: score DESC, name ASC
    pool = sorted(scored_activities, key=lambda a: (-a.get("score", 0), a.get("name", "")))

    tier_high = [a for a in pool if a.get("score", 0) >= HIGH_MATCH_THRESHOLD]
    tier_mid = [a for a in pool if LOW_MATCH_THRESHOLD <= a.get("score", 0) < HIGH_MATCH_THRESHOLD]
    tier_low = [a for a in pool if a.get("score", 0) < LOW_MATCH_THRESHOLD]

    selected: list[dict] = []
    seen_ids: set = set()
    seen_names: set = set()
    category_counts: dict[str, int] = {}

    def _is_duplicate(activity: dict) -> bool:
        aid = activity.get("id")
        name = (activity.get("name") or "").strip().lower()
        if aid is not None and aid in seen_ids:
            return True
        if name and name in seen_names:
            return True
        return False

    def _can_add(activity: dict, current_total: int) -> bool:
        """Return True if adding this activity respects the category share cap."""
        if current_total == 0:
            return True
        cat = (activity.get("category") or "other").strip().lower()
        current_cat_count = category_counts.get(cat, 0)
        # After adding, would this category exceed the share cap?
        return (current_cat_count + 1) / (current_total + 1) <= MAX_CATEGORY_SHARE

    def _add(activity: dict) -> None:
        if _is_duplicate(activity):
            return
        aid = activity.get("id")
        name = (activity.get("name") or "").strip().lower()
        if aid is not None:
            seen_ids.add(aid)
        if name:
            seen_names.add(name)
        cat = (activity.get("category") or "other").strip().lower()
        category_counts[cat] = category_counts.get(cat, 0) + 1
        selected.append(activity)

    # ---- Tier 1: high-match activities (always preferred) ----
    for act in tier_high:
        if len(selected) >= total_slots:
            break
        if not _is_duplicate(act) and _can_add(act, len(selected)):
            _add(act)

    # ---- Tier 1 second pass: relax cap to 80 % to avoid wasting high-score items ----
    if len(selected) < total_slots:
        for act in tier_high:
            if _is_duplicate(act):
                continue
            if len(selected) >= total_slots:
                break
            cat = (act.get("category") or "other").strip().lower()
            current_cat_count = category_counts.get(cat, 0)
            if (current_cat_count + 1) / (len(selected) + 1) <= 0.80:
                _add(act)

    # ---- Tier 2: acceptable-match activities (fill remaining slots with variety) ----
    if len(selected) < total_slots:
        for act in tier_mid:
            if _is_duplicate(act):
                continue
            if len(selected) >= total_slots:
                break
            if _can_add(act, len(selected)):
                _add(act)

    # ---- Tier 2 second pass: relax cap for mid-tier too ----
    if len(selected) < total_slots:
        for act in tier_mid:
            if _is_duplicate(act):
                continue
            if len(selected) >= total_slots:
                break
            cat = (act.get("category") or "other").strip().lower()
            current_cat_count = category_counts.get(cat, 0)
            if (current_cat_count + 1) / (len(selected) + 1) <= 0.80:
                _add(act)

    # ---- Tier 3: padding with real activities from destination ----
    if len(selected) < total_slots:
        for act in tier_low:
            if _is_duplicate(act):
                continue
            if len(selected) >= total_slots:
                break
            _add(act)

    return selected


# ---------------------------------------------------------------------------
# Itinerary generation (day-by-day distribution)
# ---------------------------------------------------------------------------

def generate_itinerary(
    scored_activities: list[dict],
    trip_duration: int
) -> list[dict]:
    """
    Generate a balanced day-by-day itinerary without duplicates or fake activities.

    Steps:
    1. Strict Deduplication of input activities.
    2. Select unique real activities using preference-aware logic.
    3. Graceful Duration Reduction: If there are fewer suitable activities than
       requested days, gracefully adjust the itinerary days to ensure every day
       has authentic, non-repeated activities.
    4. Geographic clustering onto days using Haversine distance.
    5. Daily route optimization using nearest-neighbor TSP.
    6. Transit duration calculation.
    7. Time slot assignment.
    """
    if trip_duration < 1:
        trip_duration = 1

    # 1. Strict Deduplication
    seen_ids = set()
    seen_names = set()
    unique_activities = []
    for a in scored_activities:
        aid = a.get("id")
        name = (a.get("name") or "").strip().lower()

        if (aid is not None and aid in seen_ids) or (name and name in seen_names):
            continue

        if aid is not None:
            seen_ids.add(aid)
        if name:
            seen_names.add(name)

        unique_activities.append(a)

    # 2. Select activities using preference-aware logic (no fake items)
    chosen = select_itinerary_activities(unique_activities, trip_duration)

    if not chosen:
        return []

    # 3. Graceful Duration Adjustment
    # Avoid repeating activities across days or inventing fake experiences.
    # If the destination has fewer suitable activities than requested days,
    # gracefully reduce the itinerary to the number of days that have authentic activities.
    effective_days = min(trip_duration, len(chosen))

    # 4. Geographic Clustering
    seeds = []
    unassigned = list(chosen)

    # Pick first activity as the first seed
    seeds.append(unassigned.pop(0))

    for day in range(1, effective_days):
        best_dist = -1
        best_idx = 0
        for i, act in enumerate(unassigned):
            min_to_seeds = float('inf')
            for seed in seeds:
                lat1, lon1 = act.get("latitude"), act.get("longitude")
                lat2, lon2 = seed.get("latitude"), seed.get("longitude")
                if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                    dist = calculate_distance(lat1, lon1, lat2, lon2)
                else:
                    dist = 0
                if dist < min_to_seeds:
                    min_to_seeds = dist

            if min_to_seeds > best_dist:
                best_dist = min_to_seeds
                best_idx = i

        if unassigned:
            seeds.append(unassigned.pop(best_idx))

    # Initialise day slots with seeds
    itinerary: list[dict] = []
    for i in range(len(seeds)):
        act = seeds[i]
        itinerary.append({
            "day": i + 1,
            "activities": [act],
            "total_duration": float(act.get("duration") or 2.0),
            "total_cost": float(act.get("estimated_cost") or 0.0),
        })

    max_daily_hours = 7.5
    max_daily_activities = 3

    # Distribute remaining activities based on geographic proximity
    for act in unassigned:
        act_duration = float(act.get("duration") or 2.0)
        act_cost = float(act.get("estimated_cost") or 0.0)

        best_day_idx = None
        min_dist = float('inf')

        for idx, day_plan in enumerate(itinerary):
            if len(day_plan["activities"]) >= max_daily_activities:
                continue
            if day_plan["total_duration"] + act_duration > max_daily_hours:
                continue

            # Distance to the day's seed
            seed = day_plan["activities"][0]
            lat1, lon1 = act.get("latitude"), act.get("longitude")
            lat2, lon2 = seed.get("latitude"), seed.get("longitude")
            if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                dist = calculate_distance(lat1, lon1, lat2, lon2)
            else:
                dist = 0

            if dist < min_dist:
                min_dist = dist
                best_day_idx = idx

        # Fallback if no day could geographically accommodate it based on limits
        if best_day_idx is None:
            valid_days = [
                idx for idx, dp in enumerate(itinerary)
                if len(dp["activities"]) < max_daily_activities
            ]
            if not valid_days:
                continue  # Could not fit anywhere, skip

            best_day_idx = min(
                valid_days,
                key=lambda i: itinerary[i]["total_duration"]
            )

        itinerary[best_day_idx]["activities"].append(act)
        itinerary[best_day_idx]["total_duration"] = round(
            itinerary[best_day_idx]["total_duration"] + act_duration, 1
        )
        itinerary[best_day_idx]["total_cost"] = round(
            itinerary[best_day_idx]["total_cost"] + act_cost, 2
        )

    # 5-7. Route optimization, Transit & Time Slots
    for day_plan in itinerary:
        # Route optimization per day using Haversine nearest-neighbor
        optimized_activities, total_distance, route_method = optimize_route(day_plan["activities"])
        day_plan["activities"] = optimized_activities
        day_plan["total_distance"] = total_distance
        day_plan["route_method"] = route_method

        # Transit duration
        transit_mins = estimate_transit_minutes(total_distance)
        day_plan["transit_duration_minutes"] = transit_mins
        day_plan["transit_duration_hours"] = round(transit_mins / 60.0, 1)

        act_hours = day_plan["total_duration"]
        day_plan["total_activity_duration"] = round(act_hours, 1)
        day_plan["total_duration"] = round(act_hours, 1)
        day_plan["total_day_hours"] = round(act_hours + transit_mins / 60.0, 1)

        # Assign time slots
        n_acts = len(optimized_activities)
        slots = []
        if n_acts == 1:
            slots = ["Main Experience"]
        elif n_acts == 2:
            slots = ["Morning", "Afternoon & Sunset"]
        elif n_acts >= 3:
            slots = ["Morning (08:30 - 11:30)", "Afternoon (13:00 - 15:30)", "Evening & Sunset (16:30 - 18:30)"]

        for i, act in enumerate(optimized_activities):
            if i < len(slots):
                act["time_slot"] = slots[i]
            else:
                act["time_slot"] = "Evening & Sunset (16:30 - 18:30)"

    return itinerary
