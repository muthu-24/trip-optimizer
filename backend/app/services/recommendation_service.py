DESTINATION_DESCRIPTIONS = {
    "Ella": "Picturesque hill country haven renowned for misty mountain vistas, the iconic Nine Arch Bridge, lush Ceylon tea estates, and scenic hiking treks.",
    "Nuwara Eliya": "Cool-climate colonial highland retreat known as 'Little England', featuring sprawling Ceylon tea estates, serene Gregory Lake, and misty mountain air.",
    "Kandy": "Spiritual and cultural capital nestled in the central hills, home to the Sacred Temple of the Tooth Relic, royal botanical gardens, and historic traditions.",
    "Galle": "UNESCO World Heritage 17th-century fortified city combining Portuguese, Dutch, and British colonial ramparts with vibrant boutique cafes and ocean ramparts.",
    "Mirissa": "Tropical southern beach paradise popular for crescent-shaped golden shores, world-class whale watching excursions, and scenic coastal palms.",
    "Sigiriya": "Ancient 5th-century rock citadel rising 200m above jungle plains, featuring majestic palace ruins, ancient frescoes, and world-renowned landscaped gardens.",
    "Dambulla": "Hub of the Cultural Triangle, home to the UNESCO World Heritage Royal Cave Temple complex with over 150 Buddha statues and vivid Buddhist ceiling murals.",
    "Yala": "Sri Lanka's premier national park boasting the highest leopard density in the world, wild Asian elephants, sloth bears, and diverse coastal ecosystems.",
    "Udawalawe": "Spectacular wildlife haven renowned for guaranteed sightings of wild elephant herds roaming open grasslands around the Udawalawe reservoir.",
    "Arugam Bay": "World-renowned surf haven on the sun-soaked east coast with legendary point breaks, relaxed beachfront cafes, and rich wildlife lagoon excursions.",
    "Trincomalee": "East coast coastal hub boasting one of the world's finest natural deep-water harbors, pristine turquoise beaches at Nilaveli, and historic Hindu temples.",
    "Anuradhapura": "Ancient first royal capital of Sri Lanka, featuring massive sacred brick stupas, ancient monastic ruins, and the revered Jaya Sri Maha Bodhi tree.",
    "Hikkaduwa": "Vibrant south-coast beach resort renowned for protected coral reefs, marine turtle feeding, energetic surf breaks, and lively seaside dining.",
    "Bentota": "Premier coastal haven famous for golden sandspits, calm lagoon watersports, architectural garden estates, and tranquil wellness resorts.",
    "Haputale": "Quiet highland ridge town overlooking dramatic southern plains, world-renowned for Sir Thomas Lipton's historic tea seat and cloud forest walks.",
    "Jaffna": "Distinct northern cultural hub rich in vibrant Dravidian Hindu heritage, historic coastal colonial forts, unique culinary flavors, and remote islands.",
    "Negombo": "Charming coastal gateway town close to the international airport, known for lively fish markets, Dutch canal cruises, sandy beaches, and seafood dining.",
    "Knuckles": "Rugged UNESCO World Heritage mountain range featuring cloud forests, hidden villages like Meemure, cascading waterfalls, and world-class trekking.",
}


STYLE_COMPATIBILITY = {
    "adventure": {"adventure": 1.0, "nature": 0.85, "wildlife": 0.75, "beach": 0.5, "culture": 0.4, "relaxation": 0.3},
    "beach": {"beach": 1.0, "relaxation": 0.85, "nature": 0.6, "adventure": 0.5, "culture": 0.4, "wildlife": 0.35},
    "culture": {"culture": 1.0, "adventure": 0.5, "nature": 0.5, "relaxation": 0.45, "wildlife": 0.4, "beach": 0.35},
    "nature": {"nature": 1.0, "adventure": 0.85, "wildlife": 0.8, "beach": 0.55, "relaxation": 0.5, "culture": 0.45},
    "wildlife": {"wildlife": 1.0, "nature": 0.85, "adventure": 0.75, "beach": 0.4, "culture": 0.35, "relaxation": 0.3},
    "relaxation": {"relaxation": 1.0, "beach": 0.85, "nature": 0.65, "culture": 0.5, "adventure": 0.35, "wildlife": 0.3},
}

ACTIVITY_SYNONYMS = {
    "hiking": {"hiking", "trekking", "trek", "hike", "walks", "walking"},
    "swimming": {"swimming", "water sports", "snorkeling", "diving"},
    "culture": {"culture", "cultural", "history", "heritage", "temple", "temples", "museum", "museums"},
    "wildlife": {"wildlife", "safari", "safaris", "bird watching", "birdwatching", "animal"},
    "nature": {"nature", "scenic", "scenery", "waterfalls", "waterfall", "forest", "gardens", "botanical"},
    "surfing": {"surfing", "surf", "waves", "board sports"},
    "sightseeing": {"sightseeing", "touring", "exploration", "landmarks", "viewpoint", "viewpoints"},
    "relaxation": {"relaxation", "spa", "wellness", "leisure", "rest", "beach"},
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}


def parse_season_months(season_str: str) -> set:
    if not season_str:
        return set()
    s = season_str.lower().strip()
    if "-" in s:
        parts = [p.strip() for p in s.split("-")]
        if len(parts) == 2 and parts[0] in MONTHS and parts[1] in MONTHS:
            start = MONTHS[parts[0]]
            end = MONTHS[parts[1]]
            if start <= end:
                return set(range(start, end + 1))
            else:
                return set(range(start, 13)) | set(range(1, end + 1))
    return set()


def calculate_season_overlap(user_season: str, dest_season: str) -> float:
    user_set = parse_season_months(user_season)
    dest_set = parse_season_months(dest_season)
    if not user_set or not dest_set:
        return 1.0
    intersection = user_set.intersection(dest_set)
    union = user_set.union(dest_set)
    return len(intersection) / len(union) if union else 1.0


def normalize_activity(activity_name: str) -> str:
    act = activity_name.strip().lower()
    for canonical, synonyms in ACTIVITY_SYNONYMS.items():
        if act in synonyms:
            return canonical
    return act


def match_activities(user_prefs: list, dest_activities: list):
    clean_prefs = [p for p in user_prefs if p.strip()]
    if not clean_prefs:
        return [], 1.0
    
    norm_dest = {normalize_activity(a) for a in dest_activities if a.strip()}
    matched_list = []
    
    for pref in clean_prefs:
        if normalize_activity(pref) in norm_dest:
            matched_list.append(pref)
            
    ratio = len(matched_list) / len(clean_prefs)
    return matched_list, ratio


def get_destination_description(destination) -> str:
    """Return a curated or dynamically generated description for a destination."""
    if hasattr(destination, "description") and destination.description:
        return destination.description
    if destination.name in DESTINATION_DESCRIPTIONS:
        return DESTINATION_DESCRIPTIONS[destination.name]

    # Dynamic fallback based on destination properties
    return (
        f"A beautiful {destination.category.lower()} destination in {destination.country}, "
        f"offering {destination.activities.lower()} with best travel conditions during {destination.best_season}."
    )


def calculate_trip_cost_breakdown(
    destination,
    trip_duration: int,
    total_activity_costs: float = 0.0,
    num_travelers: int = 1,
) -> dict:
    """
    Calculate separated, explainable cost categories for:
    - Accommodation
    - Food
    - Transportation
    - Activities
    - Daily average & estimated trip total
    Accounts for number of travelers across all categories.
    """
    duration = max(trip_duration, 1)
    travelers = max(num_travelers, 1)
    acc_daily = float(destination.accommodation_cost or 0.0)
    food_daily = float(destination.food_cost or 0.0)
    transport_daily = float(destination.transport_cost or 0.0)

    # Fallback to general daily cost if individual breakdowns not set
    if (acc_daily + food_daily + transport_daily) == 0.0:
        daily_per_person = float(destination.average_daily_cost or 10000.0)
        acc_daily = round(daily_per_person * 0.50, 2)
        food_daily = round(daily_per_person * 0.30, 2)
        transport_daily = round(daily_per_person * 0.20, 2)
    else:
        daily_per_person = round(acc_daily + food_daily + transport_daily, 2)

    total_acc = round(acc_daily * duration * travelers, 2)
    total_food = round(food_daily * duration * travelers, 2)
    total_transport = round(transport_daily * duration * travelers, 2)
    total_activities = round(float(total_activity_costs) * travelers, 2)
    total_trip = round((daily_per_person * duration * travelers) + total_activities, 2)
    cost_per_person = round((daily_per_person * duration) + float(total_activity_costs), 2)

    return {
        "daily_accommodation": acc_daily,
        "daily_food": food_daily,
        "daily_transportation": transport_daily,
        "daily_total": daily_per_person,
        "daily_total_group": round(daily_per_person * travelers, 2),
        "trip_accommodation": total_acc,
        "trip_food": total_food,
        "trip_transportation": total_transport,
        "trip_activities": total_activities,
        "estimated_trip_total": total_trip,
        "num_travelers": travelers,
        "cost_per_person": cost_per_person,
    }


def calculate_score_breakdown(
    destination,
    budget: float,
    trip_duration: int,
    travel_style: str,
    preferred_activities: list,
    season: str,
):
    """
    Calculate a detailed, explainable multi-factor score breakdown.

    Weighting (Total 100 points):
    - Budget Match:       30 points
    - Activity Match:     25 points
    - Season Match:       20 points
    - Travel Style Match: 15 points
    - Rating Match:       10 points
    """
    # ---------------------------------------------------------
    # 1. BUDGET MATCH - 30 POINTS
    # ---------------------------------------------------------
    total_trip_cost = destination.average_daily_cost * trip_duration

    if total_trip_cost <= budget:
        budget_score = 30.0
        budget_pct = 100
    elif total_trip_cost <= budget * 1.10:
        budget_score = 25.0
        budget_pct = 83
    elif total_trip_cost <= budget * 1.20:
        budget_score = 20.0
        budget_pct = 67
    elif total_trip_cost <= budget * 1.50:
        budget_score = 10.0
        budget_pct = 33
    else:
        budget_score = 0.0
        budget_pct = 0

    # ---------------------------------------------------------
    # 2. ACTIVITY MATCH - 25 POINTS
    # ---------------------------------------------------------
    dest_activities = destination.activities.split(",") if destination.activities else []
    matched_activities, activity_match_ratio = match_activities(preferred_activities, dest_activities)
    
    activity_score = round(activity_match_ratio * 25.0, 2)
    activity_pct = round(activity_match_ratio * 100)

    # ---------------------------------------------------------
    # 3. SEASON MATCH - 20 POINTS
    # ---------------------------------------------------------
    dest_season = destination.best_season or ""
    season_overlap = calculate_season_overlap(season, dest_season)
    
    season_score = round(season_overlap * 20.0, 2)
    season_pct = round(season_overlap * 100)

    # ---------------------------------------------------------
    # 4. TRAVEL STYLE MATCH - 15 POINTS
    # ---------------------------------------------------------
    dest_category = destination.category.strip().lower() if destination.category else ""
    selected_style = travel_style.strip().lower() if travel_style else ""

    style_ratio = 1.0 # Default to 100% if no style provided
    if selected_style:
        if selected_style in STYLE_COMPATIBILITY and dest_category in STYLE_COMPATIBILITY[selected_style]:
            style_ratio = STYLE_COMPATIBILITY[selected_style][dest_category]
        elif selected_style == dest_category:
            style_ratio = 1.0
        else:
            style_ratio = 0.0
            
    style_score = round(style_ratio * 15.0, 2)
    style_pct = round(style_ratio * 100)

    # ---------------------------------------------------------
    # 5. DESTINATION RATING - 10 POINTS
    # ---------------------------------------------------------
    rating = float(destination.rating or 0)
    rating_score = round((rating / 5.0) * 10.0, 2)
    rating_pct = round((rating / 5.0) * 100)

    # ---------------------------------------------------------
    # OVERALL SCORE
    # ---------------------------------------------------------
    total_score = round(
        budget_score + activity_score + season_score + style_score + rating_score, 1
    )

    return {
        "budget_score": budget_score,
        "budget_pct": budget_pct,
        "activity_score": activity_score,
        "activity_pct": activity_pct,
        "season_score": season_score,
        "season_pct": season_pct,
        "style_score": style_score,
        "style_pct": style_pct,
        "rating_score": rating_score,
        "rating_pct": rating_pct,
        "overall_score": total_score,
    }


def calculate_score(
    destination,
    budget: float,
    trip_duration: int,
    travel_style: str,
    preferred_activities: list,
    season: str,
) -> float:
    """Calculate overall destination score out of 100 for backward compatibility."""
    breakdown = calculate_score_breakdown(
        destination, budget, trip_duration, travel_style, preferred_activities, season
    )
    return breakdown["overall_score"]


def generate_recommendation_reasons(
    destination,
    budget: float,
    trip_duration: int,
    travel_style: str,
    preferred_activities: list,
    season: str,
    num_travelers: int = 1,
) -> list[str]:
    """
    Generate human-readable, deterministic reasons explaining
    why a destination was recommended based on budget, duration,
    travel style, season, and activities.
    """
    reasons = []
    travelers = max(num_travelers, 1)
    total_trip_cost = destination.average_daily_cost * trip_duration

    # 1. Budget & Duration explanation
    if total_trip_cost <= budget:
        remaining = budget - total_trip_cost
        if travelers > 1:
            group_remaining = remaining * travelers
            reasons.append(
                f"Fits within your budget with Rs. {remaining:,.0f} per person remaining (Rs. {group_remaining:,.0f} group savings)"
            )
        else:
            reasons.append(
                f"Fits within your budget with Rs. {remaining:,.0f} remaining"
            )
    elif total_trip_cost <= budget * 1.50:
        pct_above = round(((total_trip_cost - budget) / budget) * 100)
        if travelers > 1:
            reasons.append(
                f"Estimated cost Rs. {total_trip_cost:,.0f}/person is {pct_above}% above your Rs. {budget:,.0f} per person budget"
            )
        else:
            reasons.append(
                f"Estimated cost Rs. {total_trip_cost:,.0f} is {pct_above}% above your Rs. {budget:,.0f} budget"
            )
    else:
        pct_above = round(((total_trip_cost - budget) / budget) * 100)
        if travelers > 1:
            reasons.append(
                f"Estimated cost Rs. {total_trip_cost:,.0f}/person is {pct_above}% above your Rs. {budget:,.0f} per person budget"
            )
        else:
            reasons.append(
                f"Estimated cost Rs. {total_trip_cost:,.0f} is {pct_above}% above your Rs. {budget:,.0f} budget"
            )

    # 2. Season alignment
    dest_season = destination.best_season or ""
    season_overlap = calculate_season_overlap(season, dest_season)
    
    if season:
        if season_overlap == 1.0:
            reasons.append(f"Ideal seasonal match (100% overlap)")
        elif season_overlap > 0.0:
            reasons.append(f"Partial seasonal overlap ({round(season_overlap * 100)}%)")
        else:
            reasons.append(f"Best visited in {dest_season} (no overlap with your travel window)")

    # 3. Travel style compatibility
    dest_category = destination.category.strip().lower() if destination.category else ""
    selected_style = travel_style.strip().lower() if travel_style else ""

    if selected_style:
        style_ratio = 0.0
        if selected_style in STYLE_COMPATIBILITY and dest_category in STYLE_COMPATIBILITY[selected_style]:
            style_ratio = STYLE_COMPATIBILITY[selected_style][dest_category]
        elif selected_style == dest_category:
            style_ratio = 1.0

        if style_ratio >= 0.8:
            reasons.append(f"Strong match for your {selected_style} preference ({round(style_ratio * 100)}% compatibility)")
        elif style_ratio >= 0.5:
            reasons.append(f"Moderate fit for your {selected_style} preference ({round(style_ratio * 100)}% compatibility)")
        else:
            reasons.append(f"Weak fit for your {selected_style} preference ({round(style_ratio * 100)}% compatibility)")

    # 4. Preferred Activities match
    dest_activities = destination.activities.split(",") if destination.activities else []
    matched_activities, _ = match_activities(preferred_activities, dest_activities)
    
    clean_prefs = [p for p in preferred_activities if p.strip()]
    if matched_activities:
        matched_formatted = ", ".join(act.title() for act in matched_activities)
        reasons.append(f"Matches {len(matched_activities)} of your preferred activities: {matched_formatted}")
    elif clean_prefs:
        reasons.append(f"Offers popular highlights: {destination.activities}")

    # 5. Traveler Rating
    rating = float(destination.rating or 0)
    if rating >= 4.7:
        reasons.append(f"Top-rated destination ({rating:.1f}/5.0)")
    elif rating >= 4.3:
        reasons.append(f"Highly rated ({rating:.1f}/5.0)")

    return reasons
