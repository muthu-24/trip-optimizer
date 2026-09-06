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
) -> dict:
    """
    Calculate separated, explainable cost categories for:
    - Accommodation
    - Food
    - Transportation
    - Activities
    - Daily average & estimated trip total
    """
    duration = max(trip_duration, 1)
    acc_daily = float(destination.accommodation_cost or 0.0)
    food_daily = float(destination.food_cost or 0.0)
    transport_daily = float(destination.transport_cost or 0.0)

    # Fallback to general daily cost if individual breakdowns not set
    if (acc_daily + food_daily + transport_daily) == 0.0:
        daily_total = float(destination.average_daily_cost or 10000.0)
        acc_daily = round(daily_total * 0.50, 2)
        food_daily = round(daily_total * 0.30, 2)
        transport_daily = round(daily_total * 0.20, 2)
    else:
        daily_total = round(acc_daily + food_daily + transport_daily, 2)

    total_acc = round(acc_daily * duration, 2)
    total_food = round(food_daily * duration, 2)
    total_transport = round(transport_daily * duration, 2)
    total_activities = round(float(total_activity_costs), 2)
    total_trip = round((daily_total * duration) + total_activities, 2)

    return {
        "daily_accommodation": acc_daily,
        "daily_food": food_daily,
        "daily_transportation": transport_daily,
        "daily_total": daily_total,
        "trip_accommodation": total_acc,
        "trip_food": total_food,
        "trip_transportation": total_transport,
        "trip_activities": total_activities,
        "estimated_trip_total": total_trip,
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
    dest_activities = [
        act.strip().lower() for act in destination.activities.split(",") if act.strip()
    ]
    pref_activities_clean = [
        act.strip().lower() for act in preferred_activities if act.strip()
    ]

    if pref_activities_clean:
        matching_activities = [
            act for act in pref_activities_clean if act in dest_activities
        ]
        activity_match_ratio = len(matching_activities) / len(pref_activities_clean)
        activity_score = round(activity_match_ratio * 25.0, 2)
        activity_pct = round(activity_match_ratio * 100)
    else:
        activity_score = 25.0
        activity_pct = 100

    # ---------------------------------------------------------
    # 3. SEASON MATCH - 20 POINTS
    # ---------------------------------------------------------
    dest_season = destination.best_season.strip().lower()
    selected_season = season.strip().lower() if season else ""

    if selected_season and selected_season == dest_season:
        season_score = 20.0
        season_pct = 100
    elif (
        selected_season
        and (selected_season in dest_season or dest_season in selected_season)
    ):
        season_score = 15.0
        season_pct = 75
    elif not selected_season:
        season_score = 20.0
        season_pct = 100
    else:
        season_score = 0.0
        season_pct = 0

    # ---------------------------------------------------------
    # 4. TRAVEL STYLE MATCH - 15 POINTS
    # ---------------------------------------------------------
    dest_category = destination.category.strip().lower()
    selected_style = travel_style.strip().lower() if travel_style else ""

    if selected_style and selected_style == dest_category:
        style_score = 15.0
        style_pct = 100
    elif (
        selected_style
        and (selected_style in dest_category or dest_category in selected_style)
    ):
        style_score = 10.0
        style_pct = 67
    elif not selected_style:
        style_score = 15.0
        style_pct = 100
    else:
        style_score = 0.0
        style_pct = 0

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
) -> list[str]:
    """
    Generate human-readable, deterministic reasons explaining
    why a destination was recommended based on budget, duration,
    travel style, season, and activities.
    """
    reasons = []
    total_trip_cost = destination.average_daily_cost * trip_duration

    # 1. Budget & Duration explanation
    if total_trip_cost <= budget:
        reasons.append(
            f"Fits your budget (Est. Rs. {total_trip_cost:,.0f} for {trip_duration} {'day' if trip_duration == 1 else 'days'})"
        )
    elif total_trip_cost <= budget * 1.10:
        reasons.append(
            f"Close to your budget at Rs. {total_trip_cost:,.0f} (~{round(((total_trip_cost - budget) / budget) * 100)}% over)"
        )
    elif total_trip_cost <= budget * 1.20:
        reasons.append(
            f"Within 20% of your budget (Est. Rs. {total_trip_cost:,.0f} for {trip_duration} days)"
        )
    else:
        reasons.append(
            f"Estimated total trip cost is Rs. {total_trip_cost:,.0f} for {trip_duration} days"
        )

    # 2. Preferred Activities match
    dest_activities = [
        act.strip().lower() for act in destination.activities.split(",") if act.strip()
    ]
    pref_activities_clean = [
        act.strip().lower() for act in preferred_activities if act.strip()
    ]

    matching_activities = [
        act for act in pref_activities_clean if act in dest_activities
    ]

    if matching_activities:
        matched_formatted = ", ".join(act.title() for act in matching_activities)
        reasons.append(f"Matches your preferred activities: {matched_formatted}")
    elif pref_activities_clean:
        reasons.append(f"Offers popular highlights: {destination.activities}")

    # 3. Season alignment
    dest_season = destination.best_season.strip().lower()
    selected_season = season.strip().lower() if season else ""

    if selected_season:
        if selected_season == dest_season:
            reasons.append(f"Ideal climate during your selected {season} travel window")
        elif selected_season in dest_season or dest_season in selected_season:
            reasons.append(f"Good travel conditions during {season}")
        else:
            reasons.append(f"Best visited in {destination.best_season}")

    # 4. Travel style compatibility
    dest_category = destination.category.strip().lower()
    selected_style = travel_style.strip().lower() if travel_style else ""

    if selected_style:
        if selected_style == dest_category:
            reasons.append(
                f"Directly matches your {travel_style.capitalize()} travel style"
            )
        elif selected_style in dest_category or dest_category in selected_style:
            reasons.append(
                f"Well suited for {travel_style.capitalize()} style trips"
            )

    # 5. Traveler Rating
    rating = float(destination.rating or 0)
    if rating >= 4.7:
        reasons.append(f"Top-rated destination ({rating:.1f}/5.0 star traveler rating)")
    elif rating >= 4.3:
        reasons.append(f"Highly rated destination ({rating:.1f}/5.0 star traveler rating)")

    return reasons
