def calculate_score(
    destination,
    budget,
    trip_duration,
    travel_style,
    preferred_activities,
    season
):
    """
    Calculate a personalized destination score out of 100.

    Weighting:
    - Budget:          30 points
    - Activities:      25 points
    - Season:           20 points
    - Travel style:     15 points
    - Rating:           10 points
    """

    score = 0.0

    # ---------------------------------------------------------
    # 1. BUDGET MATCH - 30 POINTS
    # ---------------------------------------------------------

    total_trip_cost = (
        destination.average_daily_cost * trip_duration
    )

    if total_trip_cost <= budget:
        budget_score = 30

    elif total_trip_cost <= budget * 1.10:
        budget_score = 25

    elif total_trip_cost <= budget * 1.20:
        budget_score = 20

    elif total_trip_cost <= budget * 1.50:
        budget_score = 10

    else:
        budget_score = 0

    score += budget_score

    # ---------------------------------------------------------
    # 2. ACTIVITY MATCH - 25 POINTS
    # ---------------------------------------------------------

    destination_activities = [
        activity.strip().lower()
        for activity in destination.activities.split(",")
    ]

    preferred_activities_clean = [
        activity.strip().lower()
        for activity in preferred_activities
    ]

    if preferred_activities_clean:

        matching_activities = [
            activity
            for activity in preferred_activities_clean
            if activity in destination_activities
        ]

        activity_match_ratio = (
            len(matching_activities)
            / len(preferred_activities_clean)
        )

        activity_score = activity_match_ratio * 25

        score += activity_score

    else:
        # If the user doesn't select activities,
        # don't penalize the destination.
        activity_score = 25
        score += activity_score

    # ---------------------------------------------------------
    # 3. SEASON MATCH - 20 POINTS
    # ---------------------------------------------------------

    destination_season = (
        destination.best_season.strip().lower()
    )

    selected_season = season.strip().lower()

    if selected_season == destination_season:
        season_score = 20

    elif (
        selected_season in destination_season
        or destination_season in selected_season
    ):
        season_score = 15

    else:
        season_score = 0

    score += season_score

    # ---------------------------------------------------------
    # 4. TRAVEL STYLE MATCH - 15 POINTS
    # ---------------------------------------------------------

    destination_category = (
        destination.category.strip().lower()
    )

    selected_style = travel_style.strip().lower()

    if selected_style == destination_category:
        style_score = 15

    elif (
        selected_style in destination_category
        or destination_category in selected_style
    ):
        style_score = 10

    else:
        style_score = 0

    score += style_score

    # ---------------------------------------------------------
    # 5. DESTINATION RATING - 10 POINTS
    # ---------------------------------------------------------

    rating = float(destination.rating or 0)

    rating_score = (rating / 5) * 10

    score += rating_score

    # ---------------------------------------------------------
    # FINAL SCORE
    # ---------------------------------------------------------

    return round(score, 2)


def generate_recommendation_reasons(
    destination,
    budget,
    trip_duration,
    travel_style,
    preferred_activities,
    season
):
    """
    Generate human-readable reasons explaining
    why a destination was recommended.
    """

    reasons = []

    # ---------------------------------------------------------
    # COST
    # ---------------------------------------------------------

    total_trip_cost = (
        destination.average_daily_cost * trip_duration
    )

    if total_trip_cost <= budget:
        reasons.append("Fits your budget")

    elif total_trip_cost <= budget * 1.10:
        reasons.append(
            "Slightly above your budget"
        )

    elif total_trip_cost <= budget * 1.20:
        reasons.append(
            "Within 20% of your budget"
        )

    # ---------------------------------------------------------
    # ACTIVITIES
    # ---------------------------------------------------------

    destination_activities = [
        activity.strip().lower()
        for activity in destination.activities.split(",")
    ]

    preferred_activities_clean = [
        activity.strip().lower()
        for activity in preferred_activities
    ]

    matching_activities = [
        activity
        for activity in preferred_activities_clean
        if activity in destination_activities
    ]

    if matching_activities:

        reasons.append(
            "Matches your preferred activities: "
            + ", ".join(matching_activities)
        )

    # ---------------------------------------------------------
    # SEASON
    # ---------------------------------------------------------

    destination_season = (
        destination.best_season.strip().lower()
    )

    selected_season = season.strip().lower()

    if selected_season == destination_season:

        reasons.append(
            "Suitable for your selected season"
        )

    elif (
        selected_season in destination_season
        or destination_season in selected_season
    ):

        reasons.append(
            "Partially matches your selected season"
        )

    # ---------------------------------------------------------
    # TRAVEL STYLE
    # ---------------------------------------------------------

    destination_category = (
        destination.category.strip().lower()
    )

    selected_style = travel_style.strip().lower()

    if selected_style == destination_category:

        reasons.append(
            f"Matches your {travel_style} travel style"
        )

    elif (
        selected_style in destination_category
        or destination_category in selected_style
    ):

        reasons.append(
            f"Suitable for {travel_style} travel"
        )

    # ---------------------------------------------------------
    # RATING
    # ---------------------------------------------------------

    rating = float(destination.rating or 0)

    if rating >= 4.5:

        reasons.append(
            f"Highly rated destination ({rating}/5)"
        )

    elif rating >= 4.0:

        reasons.append(
            f"Well-rated destination ({rating}/5)"
        )

    # ---------------------------------------------------------
    # RETURN REASONS
    # ---------------------------------------------------------

    return reasons

