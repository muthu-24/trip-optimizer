from app.models.activity import Activity


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
    2. Tier 1 (high match ≥70 %): add all that fit within total slot budget.
    3. Tier 2 (acceptable 50–69 %): add to fill remaining slots, enforcing
       category diversity (no single category > MAX_CATEGORY_SHARE of total slots).
    4. Tier 3 (padding <50 %): fill any remaining slots if there are still not
       enough activities for the requested duration.
    5. Total slot budget = trip_duration × max_daily_activities (= trip_duration × 3).

    Returns an ordered list (high-score first) of selected activity dicts.
    """
    max_daily_activities = 3
    total_slots = trip_duration * max_daily_activities

    # Stable deterministic sort: score DESC, name ASC
    pool = sorted(scored_activities, key=lambda a: (-a["score"], a.get("name", "")))

    tier_high = [a for a in pool if a["score"] >= HIGH_MATCH_THRESHOLD]
    tier_mid = [a for a in pool if LOW_MATCH_THRESHOLD <= a["score"] < HIGH_MATCH_THRESHOLD]
    tier_low = [a for a in pool if a["score"] < LOW_MATCH_THRESHOLD]

    selected: list[dict] = []
    category_counts: dict[str, int] = {}

    def _can_add(activity: dict, current_total: int) -> bool:
        """Return True if adding this activity respects the category share cap."""
        if current_total == 0:
            return True
        cat = (activity.get("category") or "other").strip().lower()
        current_cat_count = category_counts.get(cat, 0)
        # After adding, would this category exceed the share cap?
        return (current_cat_count + 1) / (current_total + 1) <= MAX_CATEGORY_SHARE

    def _add(activity: dict) -> None:
        cat = (activity.get("category") or "other").strip().lower()
        category_counts[cat] = category_counts.get(cat, 0) + 1
        selected.append(activity)

    # ---- Tier 1: high-match activities (always preferred) ----
    for act in tier_high:
        if len(selected) >= total_slots:
            break
        if _can_add(act, len(selected)):
            _add(act)

    # ---- If diversity cap blocked some tier-1 items, do a second pass
    #       relaxing the cap slightly so we don't waste high-quality activities ----
    if len(selected) < total_slots:
        for act in tier_high:
            if act in selected:
                continue
            if len(selected) >= total_slots:
                break
            # Second pass: relax cap to 80 % to avoid wasting very high-score items
            cat = (act.get("category") or "other").strip().lower()
            current_cat_count = category_counts.get(cat, 0)
            if (current_cat_count + 1) / (len(selected) + 1) <= 0.80:
                _add(act)

    # ---- Tier 2: acceptable-match activities (fill remaining slots with variety) ----
    if len(selected) < total_slots:
        for act in tier_mid:
            if len(selected) >= total_slots:
                break
            if _can_add(act, len(selected)):
                _add(act)

    # ---- Tier 2 second pass: relax cap for mid-tier too ----
    if len(selected) < total_slots:
        for act in tier_mid:
            if act in selected:
                continue
            if len(selected) >= total_slots:
                break
            cat = (act.get("category") or "other").strip().lower()
            current_cat_count = category_counts.get(cat, 0)
            if (current_cat_count + 1) / (len(selected) + 1) <= 0.80:
                _add(act)

    # ---- Tier 3: padding — only if still not enough activities ----
    if len(selected) < total_slots:
        for act in tier_low:
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
    Generate a balanced day-by-day itinerary.

    Steps:
    1. Use select_itinerary_activities() to choose the best activities
       with preference-aware filtering and category diversity.
    2. Distribute chosen activities across days, targeting 2–3 per day,
       respecting a ~7.5 h daily cap, filling from the least-loaded day.

    The algorithm is deterministic: same scored_activities + trip_duration
    always produces the same itinerary.
    """
    if trip_duration < 1:
        trip_duration = 1

    # Select activities using preference-aware logic
    chosen = select_itinerary_activities(scored_activities, trip_duration)

    # Initialise day slots
    itinerary: list[dict] = []
    for day in range(1, trip_duration + 1):
        itinerary.append({
            "day": day,
            "activities": [],
            "total_duration": 0.0,
            "total_cost": 0.0,
        })

    max_daily_hours = 7.5
    max_daily_activities = 3

    # Distribute chosen activities round-robin by least-loaded day
    for activity in chosen:
        act_duration = float(activity.get("duration") or 2.0)
        act_cost = float(activity.get("estimated_cost") or 0.0)

        # Find the least-loaded day that can accommodate this activity
        best_day_idx = None
        min_load = float("inf")

        for idx, day_plan in enumerate(itinerary):
            current_hours = day_plan["total_duration"]
            current_count = len(day_plan["activities"])

            if current_count < max_daily_activities and (current_hours + act_duration) <= max_daily_hours:
                if current_hours < min_load:
                    min_load = current_hours
                    best_day_idx = idx

        # Fallback: find the day with the absolute minimum duration
        if best_day_idx is None:
            best_day_idx = min(
                range(len(itinerary)),
                key=lambda i: itinerary[i]["total_duration"]
            )

        itinerary[best_day_idx]["activities"].append(activity)
        itinerary[best_day_idx]["total_duration"] = round(
            itinerary[best_day_idx]["total_duration"] + act_duration, 1
        )
        itinerary[best_day_idx]["total_cost"] = round(
            itinerary[best_day_idx]["total_cost"] + act_cost, 2
        )

    return itinerary
