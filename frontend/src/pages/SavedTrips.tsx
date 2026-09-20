import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  savedTripsApi,
  getToken,
  getErrorMessage,
  type SavedTripSummary,
} from "../api";
import "./SavedTrips.css";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
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

export default function SavedTrips() {
  const navigate = useNavigate();
  const location = useLocation();
  const [trips, setTrips] = useState<SavedTripSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const token = getToken();

  // Handle incoming deletion or save notice from navigation state
  useEffect(() => {
    if (location.state?.notice) {
      setSuccessNotice(location.state.notice as string);
      navigate(location.pathname, { replace: true, state: {} });
      const timer = setTimeout(() => setSuccessNotice(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  async function fetchTrips() {
    setLoading(true);
    setError(null);
    try {
      const data = await savedTripsApi.getSavedTrips();
      setTrips(data);
    } catch (err) {
      setError(getErrorMessage(err, "Unable to load your saved trips. Please try again."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    const controller = new AbortController();
    savedTripsApi
      .getSavedTrips(controller.signal)
      .then((data) => {
        setTrips(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err?.name === "CanceledError" || err?.name === "AbortError") return;
        setError(getErrorMessage(err, "Unable to load your saved trips. Please try again."));
        setLoading(false);
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(tripId: number) {
    setDeletingId(tripId);
    try {
      await savedTripsApi.deleteSavedTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setConfirmId(null);
      setSuccessNotice("Trip deleted successfully.");
      setTimeout(() => setSuccessNotice(null), 4000);
    } catch (err) {
      setError(getErrorMessage(err, "Unable to delete the trip. Please verify your connection and try again."));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="saved-trips-page">
        {/* Breadcrumbs */}
        <div className="header-breadcrumbs">
          <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">My Trips</span>
        </div>

        {/* Page Header */}
        <header className="st-page-header">
          <div>
            <h1 className="st-page-title">My Saved Trips</h1>
            <p className="st-page-subtitle">Your saved itineraries with optimized routes and distances.</p>
          </div>
          <Link to="/plan-trip" className="st-plan-btn">+ Plan a New Trip</Link>
        </header>

        {/* Success Notice Banner */}
        {successNotice && (
          <div className="st-success-banner" role="status">
            <span>✅ {successNotice}</span>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="st-loading">
            <div className="st-spinner" />
            <p>Loading your saved trips…</p>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="st-error-box" role="alert">
            <div className="st-error-text">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
            <button type="button" onClick={fetchTrips} className="st-retry-btn">
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && trips.length === 0 && (
          <div className="st-empty">
            <div className="st-empty-icon">🗺️</div>
            <h2>No saved trips yet</h2>
            <p>Plan your first trip and save the optimized itinerary here for easy access later.</p>
            <Link to="/plan-trip" className="st-plan-btn">
              Plan a Trip
            </Link>
          </div>
        )}

        {/* Saved Trips Grid */}
        {!loading && !error && trips.length > 0 && (
          <div className="st-grid">
            {trips.map((trip) => {
              const transitEstimate = estimateTravelTime(trip.total_route_distance);

              return (
                <div key={trip.id} className="st-card">
                  <div className="st-card-body">
                    <div className="st-card-header-row">
                      <h2 className="st-card-dest">{trip.destination_name}</h2>
                      <span className="st-days-badge">
                        {trip.trip_duration} {trip.trip_duration === 1 ? "Day" : "Days"}
                      </span>
                    </div>

                    <div className="st-card-meta">
                      <span className="st-meta-pill">
                        👥 {trip.num_travelers || 1} {(trip.num_travelers || 1) === 1 ? "Traveler" : "Travelers"}
                      </span>
                      <span className="st-meta-pill">
                        💰 Rs. {Number(trip.budget).toLocaleString()}{(trip.num_travelers || 1) > 1 ? " / person" : ""}
                      </span>
                      {(trip.num_travelers || 1) > 1 && (
                        <span className="st-meta-pill group-budget">
                          💵 Group: Rs. {(Number(trip.budget) * (trip.num_travelers || 1)).toLocaleString()}
                        </span>
                      )}
                      {trip.travel_style && (
                        <span className="st-meta-pill">
                          🧭 {trip.travel_style.charAt(0).toUpperCase() + trip.travel_style.slice(1)}
                        </span>
                      )}
                      {trip.season && (
                        <span className="st-meta-pill">
                          🌤️ {trip.season}
                        </span>
                      )}
                      {trip.total_route_distance != null && trip.total_route_distance > 0 && (
                        <span className="st-meta-pill route">
                          🗺️ {trip.total_route_distance.toFixed(1)} km
                        </span>
                      )}
                      {transitEstimate && (
                        <span className="st-meta-pill transit">
                          🚗 {transitEstimate}
                        </span>
                      )}
                    </div>

                    <p className="st-card-date">Saved on {formatDate(trip.created_at)}</p>
                  </div>

                  <div className="st-card-actions">
                    <Link to={`/my-trips/${trip.id}`} className="st-view-btn">
                      <span>View Trip</span>
                      <span>→</span>
                    </Link>
                    <button
                      type="button"
                      className="st-delete-btn"
                      onClick={() => setConfirmId(trip.id)}
                      title="Delete this saved trip"
                    >
                      Delete
                    </button>
                  </div>

                  {/* Inline delete confirmation modal */}
                  {confirmId === trip.id && (
                    <div className="st-confirm-overlay">
                      <div className="st-confirm-box">
                        <p className="st-confirm-title">Delete this saved trip?</p>
                        <p className="st-confirm-sub">
                          Are you sure you want to delete your trip to <strong>{trip.destination_name}</strong>? This action cannot be undone.
                        </p>
                        <div className="st-confirm-actions">
                          <button
                            type="button"
                            className="st-cancel-btn"
                            onClick={() => setConfirmId(null)}
                            disabled={deletingId === trip.id}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            className="st-confirm-delete-btn"
                            onClick={() => handleDelete(trip.id)}
                            disabled={deletingId === trip.id}
                          >
                            {deletingId === trip.id ? "Deleting…" : "Yes, Delete"}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
