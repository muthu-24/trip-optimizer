import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";
import {
  savedTripsApi,
  getToken,
  getErrorMessage,
  type DayPlan,
  type SavedTripDetail,
} from "../api";
import "./TripPlan.css";
import "./SavedTripDetail.css";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

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
  if (totalActs === 1) return { label: "Full Experience", icon: "✨" };
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

export default function SavedTripDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [trip, setTrip] = useState<SavedTripDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadTrigger, setReloadTrigger] = useState(0);

  const token = getToken();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    let cancelled = false;

    const load = async () => {
      if (!id) {
        setError("Invalid trip identifier.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await savedTripsApi.getSavedTrip(id);
        if (cancelled) return;
        setTrip(data);
      } catch (err: unknown) {
        if (cancelled) return;
        if (axios.isAxiosError(err)) {
          if (err.response?.status === 403 || err.response?.status === 404) {
            setError("Trip not found or you don't have permission to view it.");
            setLoading(false);
            return;
          }
        }
        setError(getErrorMessage(err, "Unable to load this saved trip. Please verify your connection and try again."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, reloadTrigger]);

  /* ── Loading ── */
  if (loading) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <main className="std-page">
          <div className="std-loading">
            <div className="std-spinner" />
            <p>Loading your saved trip details…</p>
          </div>
        </main>
      </div>
    );
  }

  /* ── Error ── */
  if (error || !trip) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <main className="std-page">
          <div className="std-error-card">
            <div className="std-error-icon">⚠️</div>
            <h2>Could Not Load Trip</h2>
            <p>{error ?? "An unexpected error occurred while loading your trip."}</p>
            <div className="std-error-actions">
              <button
                type="button"
                onClick={() => setReloadTrigger((prev) => prev + 1)}
                className="std-retry-btn"
              >
                Retry
              </button>
              <Link to="/my-trips" className="std-back-btn">
                ← Back to My Trips
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const itinerary: DayPlan[] = trip.itinerary_data?.itinerary ?? [];
  const cost_breakdown = trip.itinerary_data?.cost_breakdown;
  const preferences = trip.itinerary_data?.preferences;

  const travelersCount =
    trip.num_travelers ||
    trip.itinerary_data?.num_travelers ||
    Number(preferences?.numTravelers) ||
    cost_breakdown?.num_travelers ||
    1;
  const budgetPerPerson =
    trip.itinerary_data?.budget_per_person ||
    Number(preferences?.budgetPerPerson ?? preferences?.budget ?? trip.budget ?? 0);
  const totalGroupBudget =
    trip.itinerary_data?.total_group_budget ||
    preferences?.totalGroupBudget ||
    (budgetPerPerson * travelersCount);

  const travelStyle = trip.travel_style ?? preferences?.travelStyle ?? "";
  const itineraryNotice = trip.itinerary_data?.itinerary_notice;
  const requestedTripDuration = trip.itinerary_data?.requested_trip_duration;
  const totalHours = itinerary.reduce((s, d) => s + (d.total_duration || 0), 0);
  const totalActivities = itinerary.reduce((s, d) => s + (d.activities?.length || 0), 0);
  const totalCost = cost_breakdown?.trip_activities ?? itinerary.reduce((s, d) => s + (d.total_cost || 0), 0);
  const totalRouteDist = trip.total_route_distance ?? itinerary.reduce((s, d) => s + (d.total_distance || 0), 0);

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="std-page">
        {/* Breadcrumbs */}
        <div className="header-breadcrumbs">
          <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
          <span className="breadcrumb-separator">/</span>
          <Link to="/my-trips" className="breadcrumb-link">My Trips</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">{trip.destination_name}</span>
        </div>

        {/* Hero Header */}
        <header className="itinerary-hero">
          <div className="itinerary-hero-main">
            <div className="itinerary-badge-row">
              <span className="itinerary-badge">📌 Saved Itinerary</span>
              {travelStyle && (
                <span className="itinerary-tag">{travelStyle.charAt(0).toUpperCase() + travelStyle.slice(1)}</span>
              )}
              {trip.season && (
                <span className="itinerary-tag">🌤️ {trip.season}</span>
              )}
            </div>
            <h1 className="itinerary-title">{trip.destination_name}</h1>
            <p className="itinerary-subtitle">
              Sri Lanka • {trip.trip_duration} {trip.trip_duration === 1 ? "Day" : "Days"}
              {requestedTripDuration && requestedTripDuration !== trip.trip_duration
                ? ` (${requestedTripDuration} requested)`
                : ""} • {travelersCount} {travelersCount === 1 ? "Traveler" : "Travelers"} • {totalActivities} Scheduled Activities
              {totalRouteDist > 0 ? ` • ${totalRouteDist.toFixed(1)} km Total Route` : ""}
            </p>
            <p className="itinerary-personalized-summary">
              Saved on {formatDate(trip.created_at)} • Stored with optimized route order and distance calculations.
            </p>
          </div>
          <div className="itinerary-hero-actions">
            <Link to="/my-trips" className="secondary-link-btn">
              ← All Saved Trips
            </Link>
            <Link to="/plan-trip" className="primary-link-btn">
              <span>Plan Another Trip</span>
            </Link>
          </div>
        </header>

        {/* Notice for Gracefully Adjusted Trips */}
        {itineraryNotice && (
          <div className="itinerary-notice-banner" role="status">
            <span className="banner-icon">ℹ️</span>
            <span className="banner-text">{itineraryNotice}</span>
          </div>
        )}

        {itinerary.length === 0 ? (
          <div className="std-no-itinerary-card">
            <div className="no-plan-icon">📋</div>
            <h2>No Scheduled Activities</h2>
            <p>This saved trip does not contain scheduled activity items.</p>
            <Link to="/my-trips" className="primary-link-btn">Back to My Trips</Link>
          </div>
        ) : (
          <div className="itinerary-content-grid">
            {/* Main timeline */}
            <div className="itinerary-timeline-section">
              <div className="section-title-wrap">
                <h2 className="section-title">Day-by-Day Route & Activities</h2>
                <p className="route-optimized-text">
                  ✨ Pre-calculated nearest-neighbor sequence to optimize road travel.
                </p>
              </div>

              <div className="days-container">
                {itinerary.map((dayPlan) => {
                  const actCount = dayPlan.activities?.length || 0;
                  const categories = Array.from(new Set(dayPlan.activities.map((a) => a.category)));
                  const dayTransit = estimateTravelTime(dayPlan.total_distance);

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
                          {dayPlan.total_distance != null && dayPlan.total_distance > 0 && (
                            <span className="day-metric-tag route-distance" title="Total Route Distance">
                              <span className="metric-icon">🗺️</span>
                              <span>{dayPlan.total_distance.toFixed(1)} km</span>
                            </span>
                          )}
                          {dayTransit && (
                            <span className="day-metric-tag transit-time-tag" title="Estimated Driving Transit">
                              <span className="metric-icon">🚗</span>
                              <span>{dayTransit}</span>
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
                              <div className="activity-timeline-item" key={activity.id ?? actIdx}>
                                <div className="timeline-indicator">
                                  <div className="timeline-step-badge" title={`Stop ${actIdx + 1}`}>
                                    {actIdx + 1}
                                  </div>
                                  {!isLast && (
                                    <div className="timeline-line">
                                      {activity.distance_to_next != null && activity.distance_to_next > 0 && (
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
                                    <div className="activity-coords-pill" title="Geographic coordinates">
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

            {/* Sidebar */}
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
                  <h3>Preferences Profile</h3>
                  <ul className="reasons-list">
                    {preferences.travelStyle && (
                      <li>✓ Style: {preferences.travelStyle}</li>
                    )}
                    {preferences.activities && preferences.activities.length > 0 && (
                      <li>✓ Interests: {preferences.activities.join(", ")}</li>
                    )}
                    <li>✓ Duration: {trip.trip_duration} days</li>
                    {preferences.season && (
                      <li>✓ Season: {preferences.season}</li>
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
        )}
      </main>
    </div>
  );
}
