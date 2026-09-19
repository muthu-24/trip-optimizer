import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  savedTripsApi,
  getToken,
  getErrorMessage,
  type DayPlan,
  type CostBreakdown,
  type Preferences,
} from "../api";
import "./TripPlan.css";

type DestinationDetails = {
  id?: number;
  name: string;
  country: string;
  region?: string;
  category?: string;
  budget_level?: string;
  description?: string;
  average_daily_cost?: number;
  best_season?: string;
  activities?: string;
  rating?: number;
  recommended_duration?: number;
};

type LocationState = {
  destination?: string;
  tripDuration?: number;
  requestedTripDuration?: number;
  insufficientActivities?: boolean;
  itineraryNotice?: string | null;
  itinerary?: DayPlan[];
  destinationDetails?: DestinationDetails;
  cost_breakdown?: CostBreakdown;
  preferences?: Preferences;
};

function estimateTravelTime(distanceKm?: number | null): string {
  if (!distanceKm || distanceKm <= 0) return "";
  const minutes = Math.max(3, Math.round(distanceKm * 2));
  if (minutes < 60) {
    return `~${minutes} min drive`;
  }
  const hours = Math.floor(minutes / 60);
  const rem = minutes % 60;
  return rem > 0 ? `~${hours}h ${rem}m drive` : `~${hours}h drive`;
}

function getTimeOfDaySlot(actIdx: number, totalActs: number): { label: string; icon: string } {
  if (totalActs === 1) return { label: "Main Experience", icon: "✨" };
  if (totalActs === 2) {
    return actIdx === 0
      ? { label: "Morning", icon: "🌅" }
      : { label: "Afternoon & Sunset", icon: "🌇" };
  }
  if (actIdx === 0) return { label: "Morning", icon: "🌅" };
  if (actIdx === 1) return { label: "Afternoon", icon: "☀️" };
  if (actIdx === 2) return { label: "Evening & Sunset", icon: "🌇" };
  return { label: "Bonus Attraction", icon: "🌙" };
}

function TripPlan() {
  const location = useLocation();
  const navigate = useNavigate();

  const state = (location.state as LocationState) || {};
  const {
    destination,
    tripDuration,
    requestedTripDuration,
    insufficientActivities,
    itineraryNotice,
    itinerary,
    destinationDetails,
    cost_breakdown,
    preferences,
  } = state;

  // Save trip state
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [saveErrorMsg, setSaveErrorMsg] = useState<string | null>(null);

  const travelersCount = Number(preferences?.numTravelers) || cost_breakdown?.num_travelers || 1;
  const budgetPerPerson = Number(preferences?.budgetPerPerson ?? preferences?.budget ?? 0);
  const totalGroupBudget = preferences?.totalGroupBudget ?? (budgetPerPerson * travelersCount);

  async function handleSaveTrip() {
    if (saveStatus === "saving" || saveStatus === "saved") return;
    setSaveStatus("saving");
    setSaveErrorMsg(null);

    const token = getToken();
    if (!token) {
      navigate("/login");
      return;
    }

    // Calculate total route distance across all days
    const totalRouteDistance = itinerary
      ? itinerary.reduce((sum: number, d: DayPlan) => sum + (d.total_distance ?? 0), 0)
      : 0;

    const payload = {
      destination_name: destination ?? destinationDetails?.name ?? "Trip",
      trip_duration: Number(tripDuration) || (itinerary?.length ?? 1),
      budget: budgetPerPerson || parseFloat(preferences?.budget ?? "0") || 50000,
      num_travelers: travelersCount,
      travel_style: preferences?.travelStyle ?? destinationDetails?.category ?? null,
      season: preferences?.season ?? null,
      total_route_distance: totalRouteDistance > 0 ? Math.round(totalRouteDistance * 100) / 100 : null,
      itinerary_data: {
        itinerary: itinerary ?? [],
        cost_breakdown,
        preferences,
        num_travelers: travelersCount,
        budget_per_person: budgetPerPerson,
        total_group_budget: totalGroupBudget,
        destination_name: destination,
        destination_details: destinationDetails,
        itinerary_notice: itineraryNotice,
        requested_trip_duration: requestedTripDuration,
        actual_trip_duration: Number(tripDuration) || (itinerary?.length ?? 1),
        insufficient_activities: insufficientActivities,
      },
    };

    try {
      await savedTripsApi.saveTrip(payload);
      setSaveStatus("saved");
    } catch (err) {
      setSaveStatus("error");
      setSaveErrorMsg(getErrorMessage(err, "Unable to save this trip right now. Please try again."));
      setTimeout(() => {
        setSaveStatus("idle");
        setSaveErrorMsg(null);
      }, 5000);
    }
  }

  // If no itinerary, display the empty state.
  if (!itinerary || itinerary.length === 0) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <main className="trip-plan-page">
          <div className="no-plan-card">
            <div className="no-plan-icon">🗺️</div>
            <h2>No Trip Plan Found</h2>
            <p>
              It looks like you haven't generated an itinerary yet, or the plan session expired.
            </p>
            <div className="itinerary-bottom-actions" style={{ justifyContent: "center" }}>
              <Link to="/plan-trip" className="primary-link-btn">
                <span>Plan a New Trip</span>
              </Link>
              <button onClick={() => navigate(-1)} className="secondary-link-btn">
                Go Back
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const destCountry = destinationDetails?.country || "Sri Lanka";
  const travelStyle = preferences?.travelStyle || destinationDetails?.category || "Adventure";
  const durationNum = Number(tripDuration) || itinerary.length;

  const totalCost = cost_breakdown?.trip_activities ?? itinerary.reduce(
    (sum, d) => sum + (d.total_cost || 0),
    0
  );
  const totalHours = itinerary.reduce(
    (sum, d) => sum + (d.total_duration || 0),
    0
  );
  const totalRouteDist = itinerary.reduce(
    (sum, d) => sum + (d.total_distance || 0),
    0
  );
  const totalActivities = itinerary.reduce(
    (sum, d) => sum + (d.activities?.length || 0),
    0
  );

  return (
    <div className="page-wrapper">
      <Navbar />

      <main className="trip-plan-page">
        {/* Header Breadcrumbs */}
        <div className="header-breadcrumbs">
          <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
          <span className="breadcrumb-separator">/</span>
          <Link to="/plan-trip" className="breadcrumb-link">Plan Trip</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Itinerary</span>
        </div>

        {/* Itinerary Header */}
        <header className="itinerary-hero">
          <div className="itinerary-hero-main">
            <div className="itinerary-badge-row">
              <span className="itinerary-badge">✨ Optimized Route</span>
              {travelStyle && (
                <span className="itinerary-tag">{travelStyle.charAt(0).toUpperCase() + travelStyle.slice(1)}</span>
              )}
            </div>
            <h1 className="itinerary-title">{destination || destinationDetails?.name || "Your Trip"}</h1>
            <p className="itinerary-subtitle">
              {destCountry} • {durationNum} {durationNum === 1 ? "Day" : "Days"}
              {requestedTripDuration && requestedTripDuration !== durationNum
                ? ` (${requestedTripDuration} requested)`
                : ""} • {travelersCount} {travelersCount === 1 ? "Traveler" : "Travelers"} • {totalActivities} Scheduled Activities
              {totalRouteDist > 0 ? ` • ${totalRouteDist.toFixed(1)} km Total Route` : ""}
            </p>
            <p className="itinerary-personalized-summary">
              Activities intelligently sequenced by nearest-neighbor distance to minimize transit time.
            </p>
          </div>
          <div className="itinerary-hero-actions">
            {/* Save Trip button */}
            <button
              type="button"
              onClick={handleSaveTrip}
              disabled={saveStatus === "saving" || saveStatus === "saved"}
              className={`save-trip-btn ${saveStatus}`}
            >
              {saveStatus === "saving" && "Saving…"}
              {saveStatus === "saved" && "✓ Trip Saved!"}
              {saveStatus === "error" && "⚠ Save Failed — Retry"}
              {saveStatus === "idle" && "Save This Trip"}
            </button>
            <Link to="/plan-trip" className="primary-link-btn">
              <span>Start New Trip</span>
            </Link>
            <button type="button" onClick={() => navigate(-1)} className="secondary-link-btn">
              Back to Details
            </button>
          </div>
        </header>

        {/* Notice for Gracefully Adjusted Trips */}
        {itineraryNotice && (
          <div className="itinerary-notice-banner" role="status">
            <span className="banner-icon">ℹ️</span>
            <span className="banner-text">{itineraryNotice}</span>
          </div>
        )}

        {/* Save Status Notification Banners */}
        {saveStatus === "saved" && (
          <div className="itinerary-save-success-banner" role="status">
            <span className="banner-icon">✅</span>
            <span className="banner-text">
              Trip saved successfully to your account! You can revisit or manage it anytime in <strong>My Trips</strong>.
            </span>
            <Link to="/my-trips" className="banner-link">
              View in My Trips →
            </Link>
          </div>
        )}

        {saveErrorMsg && (
          <div className="itinerary-save-error-banner" role="alert">
            <span className="banner-icon">⚠️</span>
            <span className="banner-text">{saveErrorMsg}</span>
            <button type="button" onClick={handleSaveTrip} className="banner-retry-btn">
              Retry Save
            </button>
          </div>
        )}

        <div className="itinerary-content-grid">
          {/* Main Itinerary Timeline */}
          <div className="itinerary-timeline-section">
            <div className="section-title-wrap">
              <h2 className="section-title">Day-by-Day Route Plan</h2>
              <p className="route-optimized-text">
                ✨ Order optimized per day using geographic coordinates to reduce travel.
              </p>
            </div>

            <div className="days-container">
              {itinerary.map((dayPlan: DayPlan) => {
                const actCount = dayPlan.activities?.length || 0;
                const categories = Array.from(new Set(dayPlan.activities.map((a) => a.category)));
                const transitEstimate = estimateTravelTime(dayPlan.total_distance);

                return (
                  <section className="day-card" key={dayPlan.day}>
                    <div className="day-card-header">
                      <div className="day-header-left">
                        <span className="day-num-badge">DAY {dayPlan.day}</span>
                        <p className="day-theme-subtitle">
                          {actCount > 0 ? categories.join(" & ") : "Leisure & Free Time"}
                        </p>
                      </div>
                      <div className="day-metrics">
                        <span className="day-metric-tag" title="Total Scheduled Duration">
                          <span className="metric-icon">⏱️</span>
                          <span>{dayPlan.total_duration} hrs</span>
                        </span>
                        {dayPlan.total_distance !== undefined && dayPlan.total_distance > 0 && (
                          <span className="day-metric-tag route-distance" title="Total Route Distance">
                            <span className="metric-icon">🗺️</span>
                            <span>{dayPlan.total_distance.toFixed(1)} km</span>
                          </span>
                        )}
                        {transitEstimate && (
                          <span className="day-metric-tag transit-time-tag" title="Estimated Road Transit">
                            <span className="metric-icon">🚗</span>
                            <span>{transitEstimate}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {actCount === 0 ? (
                      <div className="day-empty">
                        <p>No scheduled activities for this day. Enjoy free leisure time!</p>
                      </div>
                    ) : (
                      <div className="activities-vertical-timeline">
                        {dayPlan.activities.map((activity, actIdx) => {
                          const isLast = actIdx === dayPlan.activities.length - 1;
                          const actDurationLabel =
                            activity.duration === 1 ? "1 hr" : `${activity.duration} hrs`;
                          const stepTravelTime = estimateTravelTime(activity.distance_to_next);
                          const slot = getTimeOfDaySlot(actIdx, dayPlan.activities.length);

                          return (
                            <div className="activity-timeline-item" key={activity.id || actIdx}>
                              {/* Timeline indicator line */}
                              <div className="timeline-indicator">
                                <div className="timeline-step-badge" title={`Stop ${actIdx + 1}`}>
                                  {actIdx + 1}
                                </div>
                                {!isLast && (
                                  <div className="timeline-line">
                                    {activity.distance_to_next !== undefined && activity.distance_to_next > 0 && (
                                      <div className="distance-travel-badge" title="Distance & drive time to next stop">
                                        <span className="distance-badge-val">↓ {activity.distance_to_next.toFixed(1)} km</span>
                                        {stepTravelTime && (
                                          <span className="travel-time-val">{stepTravelTime}</span>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>

                              <div className="activity-card">
                                <div className="activity-card-header">
                                  <div className="activity-title-wrap">
                                    <div className="activity-slot-row">
                                      <span className="activity-slot-badge">
                                        <span className="slot-icon">{slot.icon}</span>
                                        <span className="slot-label">{slot.label}</span>
                                      </span>
                                      <span className="activity-order-label">Stop {actIdx + 1}</span>
                                    </div>
                                    <h4 className="activity-name">{activity.name}</h4>
                                  </div>
                                  <div className="activity-badges-group">
                                    <span className="activity-category-pill">{activity.category}</span>
                                    {activity.score != null && (
                                      <span className="activity-match-pill">
                                        {Math.round(activity.score)}% Match
                                      </span>
                                    )}
                                  </div>
                                </div>

                                <div className="activity-specs-grid">
                                  <div className="activity-spec">
                                    <span className="spec-label">Duration</span>
                                    <span className="spec-value">⏱️ {actDurationLabel}</span>
                                  </div>
                                  <div className="activity-spec">
                                    <span className="spec-label">Est. Cost</span>
                                    <span
                                      className={`spec-value ${activity.estimated_cost > 0 ? "cost" : "free"}`}
                                    >
                                      {activity.estimated_cost > 0
                                        ? `Rs. ${activity.estimated_cost.toLocaleString()}`
                                        : "Free Entry"}
                                    </span>
                                  </div>
                                  <div className="activity-spec">
                                    <span className="spec-label">Rating</span>
                                    <span className="spec-value rating">
                                      ⭐ {activity.rating ? activity.rating.toFixed(1) : "N/A"}
                                    </span>
                                  </div>
                                </div>

                                {activity.latitude != null && activity.longitude != null && (
                                  <div className="activity-coords-pill" title="Geographic location">
                                    <span>📍</span>
                                    <span>{activity.latitude.toFixed(3)}° N, {activity.longitude.toFixed(3)}° E</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </section>
                );
              })}
            </div>
          </div>

          {/* Sidebar for Summary and Cost */}
          <aside className="itinerary-sidebar">
            <div className="sidebar-card summary-card">
              <h3>Trip Summary</h3>
              <div className="summary-stat">
                <span className="stat-value">{totalHours} hrs</span>
                <span className="stat-label">Total Activity Time</span>
              </div>
              <div className="summary-stat">
                <span className="stat-value">{totalActivities}</span>
                <span className="stat-label">Total Activities</span>
              </div>
              {totalRouteDist > 0 && (
                <div className="summary-stat">
                  <span className="stat-value">{totalRouteDist.toFixed(1)} km</span>
                  <span className="stat-label">Total Route Distance</span>
                </div>
              )}
              {totalRouteDist > 0 && (
                <div className="summary-stat">
                  <span className="stat-value">{estimateTravelTime(totalRouteDist)}</span>
                  <span className="stat-label">Est. Total Driving Time</span>
                </div>
              )}
            </div>

            {preferences && (
              <div className="sidebar-card preferences-card">
                <h3>Why This Fits You</h3>
                <ul className="reasons-list">
                  {preferences.travelStyle && (
                    <li>✓ Matches your preferred travel style ({preferences.travelStyle})</li>
                  )}
                  {preferences.activities && preferences.activities.length > 0 && (
                    <li>✓ Includes your selected activities ({preferences.activities.join(", ")})</li>
                  )}
                  <li>✓ Optimized for your {durationNum}-day duration</li>
                  {preferences.season && (
                    <li>✓ Recommended for season: {preferences.season}</li>
                  )}
                </ul>
              </div>
            )}

            <div className="sidebar-card cost-card">
              <h3>Trip Budget & Cost Breakdown</h3>

              {/* Budget & Traveler Overview */}
              <div className="cost-budget-overview">
                <div className="budget-meta-row">
                  <span>Travelers</span>
                  <strong>{travelersCount} {travelersCount === 1 ? "Person" : "People"}</strong>
                </div>
                {budgetPerPerson > 0 && (
                  <div className="budget-meta-row">
                    <span>Budget per Person</span>
                    <span>Rs. {budgetPerPerson.toLocaleString()}</span>
                  </div>
                )}
                {totalGroupBudget > 0 && (
                  <div className="budget-meta-row highlight">
                    <span>Total Group Budget</span>
                    <span>Rs. {totalGroupBudget.toLocaleString()}</span>
                  </div>
                )}
              </div>
              <hr className="cost-divider" />

              {cost_breakdown ? (
                <>
                  <div className="cost-row">
                    <span>Accommodation ({travelersCount} travelers)</span>
                    <span>Rs. {Number(cost_breakdown.trip_accommodation ?? 0).toLocaleString()}</span>
                  </div>
                  <div className="cost-row">
                    <span>Food ({travelersCount} travelers)</span>
                    <span>Rs. {Number(cost_breakdown.trip_food ?? 0).toLocaleString()}</span>
                  </div>
                  <div className="cost-row">
                    <span>Transportation ({travelersCount} travelers)</span>
                    <span>Rs. {Number(cost_breakdown.trip_transportation ?? 0).toLocaleString()}</span>
                  </div>
                  <div className="cost-row">
                    <span>Activities ({travelersCount} travelers)</span>
                    <span>Rs. {Number(cost_breakdown.trip_activities ?? totalCost * travelersCount).toLocaleString()}</span>
                  </div>
                  <hr className="cost-divider" />
                  <div className="cost-row total">
                    <span>Estimated Trip Total</span>
                    <span>
                      Rs. {Number(cost_breakdown.estimated_trip_total ?? totalCost).toLocaleString()}
                    </span>
                  </div>
                  {totalGroupBudget > 0 && (
                    <div className={`budget-balance-row ${(cost_breakdown.estimated_trip_total ?? totalCost) <= totalGroupBudget ? "under-budget" : "over-budget"}`}>
                      {(cost_breakdown.estimated_trip_total ?? totalCost) <= totalGroupBudget ? (
                        <span>✓ Within budget (Rs. {(totalGroupBudget - (cost_breakdown.estimated_trip_total ?? totalCost)).toLocaleString()} remaining)</span>
                      ) : (
                        <span>⚠️ Rs. {((cost_breakdown.estimated_trip_total ?? totalCost) - totalGroupBudget).toLocaleString()} over group budget</span>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="cost-row">
                    <span>Activities ({travelersCount} travelers)</span>
                    <span>Rs. {(totalCost * travelersCount).toLocaleString()}</span>
                  </div>
                  <hr className="cost-divider" />
                  <div className="cost-row total">
                    <span>Estimated Trip Total</span>
                    <span>Rs. {(totalCost * travelersCount).toLocaleString()}</span>
                  </div>
                </>
              )}
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default TripPlan;
