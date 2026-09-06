import { Link, useLocation } from "react-router-dom";
import Navbar from "../components/Navbar";
import "./TripPlan.css";

type Activity = {
  id: number;
  name: string;
  category: string;
  estimated_cost: number;
  duration: number;
  rating: number;
  score: number;
};

type DayPlan = {
  day: number;
  activities: Activity[];
  total_duration: number;
  total_cost: number;
};

function TripPlan() {
  const location = useLocation();
  const { destination, tripDuration, itinerary } = location.state || {};

  if (!itinerary || itinerary.length === 0) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <main className="trip-plan-page">
          <div className="no-plan-card">
            <div className="no-plan-icon">🗺️</div>
            <h2>No Trip Plan Found</h2>
            <p>
              It looks like you haven't generated an itinerary yet or reloaded the page.
              Start by selecting your travel preferences!
            </p>
            <Link to="/plan-trip" className="primary-link-btn">
              <span>Plan a Trip</span>
              <span>→</span>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  // Calculate cumulative trip summaries
  const durationNum = Number(tripDuration) || itinerary.length;
  const totalCost = (itinerary as DayPlan[]).reduce(
    (sum, d) => sum + (d.total_cost || 0),
    0
  );
  const totalHours = (itinerary as DayPlan[]).reduce(
    (sum, d) => sum + (d.total_duration || 0),
    0
  );
  const totalActivities = (itinerary as DayPlan[]).reduce(
    (sum, d) => sum + (d.activities?.length || 0),
    0
  );

  return (
    <div className="page-wrapper">
      <Navbar />

      <main className="trip-plan-page">
        {/* Itinerary Header */}
        <header className="itinerary-header">
          <div className="header-breadcrumbs">
            <Link to="/dashboard" className="breadcrumb-link">
              Dashboard
            </Link>
            <span className="breadcrumb-separator">/</span>
            <Link to="/plan-trip" className="breadcrumb-link">
              Plan Trip
            </Link>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">Itinerary</span>
          </div>

          <div className="header-main-content">
            <div className="header-title-block">
              <span className="itinerary-badge">✨ Optimized Itinerary</span>
              <h1 className="itinerary-title">{destination}</h1>
              <p className="itinerary-subtitle">
                {durationNum} {durationNum === 1 ? "Day" : "Days"} Personalized Schedule
              </p>
            </div>

            <div className="header-action-block">
              <Link to="/plan-trip" className="plan-another-btn">
                <span>← Plan Another Destination</span>
              </Link>
            </div>
          </div>

          {/* Quick Summary Strip */}
          <div className="summary-strip">
            <div className="summary-pill">
              <span className="summary-icon">🗓️</span>
              <div className="summary-text-wrap">
                <div className="summary-val">
                  {durationNum} {durationNum === 1 ? "Day" : "Days"}
                </div>
                <div className="summary-lbl">Trip Duration</div>
              </div>
            </div>

            <div className="summary-pill">
              <span className="summary-icon">🎯</span>
              <div className="summary-text-wrap">
                <div className="summary-val">
                  {totalActivities}{" "}
                  {totalActivities === 1 ? "Activity" : "Activities"}
                </div>
                <div className="summary-lbl">Scheduled Sights</div>
              </div>
            </div>

            <div className="summary-pill">
              <span className="summary-icon">⏱️</span>
              <div className="summary-text-wrap">
                <div className="summary-val">
                  {totalHours} {totalHours === 1 ? "Hour" : "Hours"}
                </div>
                <div className="summary-lbl">Total Experience</div>
              </div>
            </div>

            <div className="summary-pill highlight">
              <span className="summary-icon">💰</span>
              <div className="summary-text-wrap">
                <div className="summary-val">
                  {totalCost > 0 ? `Rs. ${totalCost.toLocaleString()}` : "Rs. 0"}
                </div>
                <div className="summary-lbl">
                  {totalCost > 0 ? "Est. Activity Fees" : "Free Attractions"}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Day-by-Day Itinerary List */}
        <div className="days-container">
          {itinerary.map((dayPlan: DayPlan) => {
            const actCount = dayPlan.activities?.length || 0;
            const actCountLabel =
              actCount === 1 ? "1 Activity" : `${actCount} Activities`;
            const durationLabel =
              dayPlan.total_duration === 1
                ? "1 hr"
                : `${dayPlan.total_duration} hrs`;

            return (
              <section className="day-card" key={dayPlan.day}>
                {/* Day Header with prominent Day Number and clearly separated Activity Count */}
                <div className="day-card-header">
                  <div className="day-header-left">
                    <div className="day-badge-title">
                      <span className="day-number-badge">Day {dayPlan.day}</span>
                    </div>
                    <div className="day-activities-count-text">
                      {actCountLabel}
                    </div>
                  </div>

                  <div className="day-metrics">
                    <span className="day-metric-tag" title="Total Scheduled Duration">
                      <span className="metric-icon">⏱️</span>
                      <span>{durationLabel}</span>
                    </span>
                    <span
                      className={`day-metric-tag ${dayPlan.total_cost > 0 ? "cost" : "free"}`}
                      title="Estimated Activity Fees"
                    >
                      <span className="metric-icon">💰</span>
                      <span>
                        {dayPlan.total_cost > 0
                          ? `Rs. ${dayPlan.total_cost.toLocaleString()}`
                          : "Free Entry"}
                      </span>
                    </span>
                  </div>
                </div>

                {/* Day Activities List */}
                {actCount === 0 ? (
                  <div className="day-empty">
                    <p>No scheduled activities for this day. Enjoy free leisure time!</p>
                  </div>
                ) : (
                  <div className="activities-timeline">
                    {dayPlan.activities.map((activity, actIdx) => {
                      const isLast = actIdx === dayPlan.activities.length - 1;
                      const actDurationLabel =
                        activity.duration === 1
                          ? "1 hr"
                          : `${activity.duration} hrs`;

                      return (
                        <div
                          className="activity-card"
                          key={activity.id || actIdx}
                        >
                          {/* Timeline Step Indicator */}
                          <div className="activity-timeline-indicator">
                            <span className="activity-sequence-dot">
                              {actIdx + 1}
                            </span>
                            {!isLast && (
                              <span className="timeline-connector-line"></span>
                            )}
                          </div>

                          {/* Activity Details Card */}
                          <div className="activity-details">
                            <div className="activity-top-row">
                              <h3 className="activity-name">{activity.name}</h3>
                              <span className="activity-category-pill">
                                {activity.category}
                              </span>
                            </div>

                            {/* Activity Specs Grid */}
                            <div className="activity-specs-grid">
                              <div className="activity-spec">
                                <span className="spec-label">Duration</span>
                                <span className="spec-value">
                                  ⏱️ {actDurationLabel}
                                </span>
                              </div>

                              <div className="activity-spec">
                                <span className="spec-label">Est. Cost</span>
                                <span
                                  className={`spec-value ${
                                    activity.estimated_cost > 0
                                      ? "cost"
                                      : "free"
                                  }`}
                                >
                                  {activity.estimated_cost > 0
                                    ? `Rs. ${activity.estimated_cost.toLocaleString()}`
                                    : "Free Entry"}
                                </span>
                              </div>

                              <div className="activity-spec">
                                <span className="spec-label">Rating</span>
                                <span className="spec-value rating">
                                  ⭐{" "}
                                  {activity.rating
                                    ? activity.rating.toFixed(1)
                                    : "4.5"}{" "}
                                  / 5.0
                                </span>
                              </div>

                              <div className="activity-spec">
                                <span className="spec-label">
                                  Preference Match
                                </span>
                                <span className="spec-value score">
                                  🎯 {Math.round(activity.score)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Day Footer Summary */}
                <div className="day-card-footer">
                  <span className="footer-label">
                    Day {dayPlan.day} Overview:
                  </span>
                  <span className="footer-summary-highlight">
                    {dayPlan.total_duration}{" "}
                    {dayPlan.total_duration === 1 ? "hour" : "hours"} of exploration ·{" "}
                    {dayPlan.total_cost > 0
                      ? `Rs. ${dayPlan.total_cost.toLocaleString()} activity fees`
                      : "Free attraction entry"}
                  </span>
                </div>
              </section>
            );
          })}
        </div>

        {/* Footer Actions */}
        <div className="itinerary-bottom-actions">
          <Link to="/plan-trip" className="primary-link-btn">
            <span>← Plan Another Destination</span>
          </Link>
          <Link to="/dashboard" className="secondary-link-btn">
            Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}

export default TripPlan;
