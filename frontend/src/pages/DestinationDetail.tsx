import { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate, Link } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";
import "./DestinationDetail.css";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

type ScoreBreakdown = {
  budget_match: number;
  activity_match: number;
  season_match: number;
  travel_style_match: number;
  rating_match?: number;
  overall_score: number;
};

type LocationState = {
  recommendation?: {
    id?: number;
    destination: string;
    country: string;
    region?: string;
    category?: string;
    budget_level?: string;
    score: number;
    score_breakdown?: ScoreBreakdown;
    description?: string;
    average_daily_cost: number;
    estimated_trip_cost: number;
    best_season: string;
    activities: string;
    rating: number;
    recommended_duration?: number;
    reasons: string[];
  };
  // Preferences carried from TripPreferences so "Plan My Trip" can generate itinerary
  preferences?: {
    budget: string;
    tripDuration: string;
    travelStyle: string;
    season: string;
    activities: string[];
  };
};

type DestinationData = {
  id: number;
  name: string;
  country: string;
  region: string;
  category: string;
  budget_level: string;
  description: string;
  average_daily_cost: number;
  best_season: string;
  activities: string;
  rating: number;
  recommended_duration: number;
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

const ACTIVITY_META: Record<string, { label: string; icon: string }> = {
  hiking: { label: "Hiking", icon: "🥾" },
  nature: { label: "Nature", icon: "🌿" },
  swimming: { label: "Swimming", icon: "🏊" },
  surfing: { label: "Surfing", icon: "🏄" },
  wildlife: { label: "Wildlife", icon: "🦁" },
  culture: { label: "Culture", icon: "🏛️" },
  sightseeing: { label: "Sightseeing", icon: "🗺️" },
  relaxation: { label: "Relaxation", icon: "🌴" },
};

function getCategoryGradient(category: string): string {
  const cat = (category || "").toLowerCase();
  if (cat === "beach") return "hero-gradient-beach";
  if (cat === "culture") return "hero-gradient-culture";
  if (cat === "nature") return "hero-gradient-nature";
  if (cat === "wildlife") return "hero-gradient-wildlife";
  if (cat === "adventure") return "hero-gradient-adventure";
  if (cat === "relaxation") return "hero-gradient-relaxation";
  return "hero-gradient-default";
}

function getCategoryEmoji(category: string): string {
  const cat = (category || "").toLowerCase();
  if (cat === "beach") return "🏖️";
  if (cat === "culture") return "🏛️";
  if (cat === "nature") return "🌿";
  if (cat === "wildlife") return "🦁";
  if (cat === "adventure") return "⛰️";
  if (cat === "relaxation") return "🌴";
  return "📍";
}

function getRatingStars(rating: number): string {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5 ? 1 : 0;
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(Math.max(0, 5 - full - half));
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export default function DestinationDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState | null;

  const [fetchedDestination, setFetchedDestination] = useState<DestinationData | null>(null);
  const [isLoading, setIsLoading] = useState(!state?.recommendation);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Derive destination data directly from navigation state if present
  const destination: DestinationData | null = state?.recommendation
    ? {
        id: state.recommendation.id ?? Number(id),
        name: state.recommendation.destination,
        country: state.recommendation.country,
        region: state.recommendation.region ?? "Sri Lanka",
        category: state.recommendation.category ?? "",
        budget_level: state.recommendation.budget_level ?? "",
        description: state.recommendation.description ?? "",
        average_daily_cost: state.recommendation.average_daily_cost,
        best_season: state.recommendation.best_season,
        activities: state.recommendation.activities,
        rating: state.recommendation.rating,
        recommended_duration: state.recommendation.recommended_duration ?? 3,
      }
    : fetchedDestination;

  const score: number | null = state?.recommendation?.score ?? null;
  const scoreBreakdown: ScoreBreakdown | null = state?.recommendation?.score_breakdown ?? null;
  const rawReasons: string[] = state?.recommendation?.reasons ?? [];
  const preferredActivities: string[] = state?.preferences?.activities ?? [];

  // Fallback: Fetch destination details from API when visiting directly via URL
  useEffect(() => {
    if (state?.recommendation) {
      return;
    }

    let isMounted = true;

    async function loadDestination() {
      setIsLoading(true);
      setErrorMsg(null);
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/api/destinations/${id}`
        );
        if (isMounted) {
          setFetchedDestination(response.data);
        }
      } catch {
        if (isMounted) {
          setErrorMsg("Could not load destination details. Please go back and try again.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadDestination();

    return () => {
      isMounted = false;
    };
  }, [id, state?.recommendation]);

  const handlePlanMyTrip = async () => {
    if (!destination) return;

    if (state?.preferences) {
      try {
        setIsGeneratingPlan(true);
        const prefs = state.preferences;
        const activitiesList =
          prefs.activities && prefs.activities.length > 0
            ? prefs.activities
            : destination.activities
                .split(",")
                .map((a) => a.trim().toLowerCase())
                .filter(Boolean);

        const response = await axios.post(
          `http://127.0.0.1:8000/api/trips/activities/${destination.id}`,
          activitiesList,
          {
            params: {
              budget: Number(prefs.budget) || 50000,
              travel_style: prefs.travelStyle || "adventure",
              trip_duration: Number(prefs.tripDuration) || 3,
            },
          }
        );

        navigate("/trip-plan", {
          state: {
            destination: destination.name,
            tripDuration: Number(prefs.tripDuration) || 3,
            itinerary: response.data.itinerary,
          },
        });
      } catch (err) {
        console.error("Failed to generate itinerary:", err);
        navigate("/trip-plan");
      } finally {
        setIsGeneratingPlan(false);
      }
    } else {
      // Direct navigation fallback: navigate to trip preferences
      navigate("/plan-trip");
    }
  };

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="dd-page">
        <Navbar />
        <div className="dd-loading">
          <div className="dd-spinner" />
          <p>Loading destination details…</p>
        </div>
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────
  if (errorMsg) {
    return (
      <div className="dd-page">
        <Navbar />
        <div className="dd-error-card">
          <div className="dd-error-icon">⚠️</div>
          <h2>Unable to Load Destination</h2>
          <p>{errorMsg}</p>
          <button type="button" className="dd-back-btn" onClick={() => navigate(-1)}>
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  // ── No data yet ──────────────────────────────────────────────────────────
  if (!destination) {
    return (
      <div className="dd-page">
        <Navbar />
        <div className="dd-error-card">
          <div className="dd-error-icon">🗺️</div>
          <h2>Destination Not Found</h2>
          <p>We couldn't find information for this destination.</p>
          <Link to="/plan-trip" className="dd-cta-btn">
            ← Back to Trip Planner
          </Link>
        </div>
      </div>
    );
  }

  const activityList = destination.activities
    ? destination.activities.split(",").map((a) => a.trim()).filter(Boolean)
    : [];

  const gradientClass = getCategoryGradient(destination.category);
  const catEmoji = getCategoryEmoji(destination.category);

  // Use recommendation reasons or provide smart destination highlights if accessed directly
  const displayReasons =
    rawReasons.length > 0
      ? rawReasons
      : [
          `Top-rated Sri Lankan destination with a ${destination.rating.toFixed(1)} / 5.0 traveler rating`,
          `Best experienced during the optimal ${destination.best_season} weather season`,
          `Offers diverse traveler activities including ${destination.activities}`,
          `Accredited for ${destination.budget_level.toLowerCase()} travel budgets (Rs. ${destination.average_daily_cost.toLocaleString()}/day average)`,
        ];

  return (
    <div className="dd-page">
      <Navbar />

      <main className="dd-main">
        {/* ── Breadcrumb ─────────────────────────────────────────────────── */}
        <nav className="dd-breadcrumb">
          <Link to="/dashboard" className="dd-breadcrumb-link">Dashboard</Link>
          <span className="dd-breadcrumb-sep">/</span>
          <Link to="/plan-trip" className="dd-breadcrumb-link">Plan Trip</Link>
          <span className="dd-breadcrumb-sep">/</span>
          <span className="dd-breadcrumb-current">{destination.name}</span>
        </nav>

        {/* ── Hero Section ───────────────────────────────────────────────── */}
        <section className={`dd-hero ${gradientClass}`}>
          <button
            type="button"
            className="dd-back-hero-btn"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>

          <div className="dd-hero-content">
            <div className="dd-hero-emoji">{catEmoji}</div>

            {score !== null && (
              <div className="dd-match-badge">
                <span className="dd-match-pct">{Math.round(score)}%</span>
                <span className="dd-match-label">Match</span>
              </div>
            )}

            <h1 className="dd-hero-title">{destination.name}</h1>
            <p className="dd-hero-location">
              📍 {destination.region && destination.region !== "Sri Lanka"
                ? `${destination.region}, Sri Lanka`
                : destination.country}
            </p>

            <div className="dd-hero-meta">
              {destination.rating > 0 && (
                <span className="dd-hero-meta-pill">
                  ⭐ {destination.rating.toFixed(1)} / 5.0
                </span>
              )}
              {destination.budget_level && (
                <span className="dd-hero-meta-pill">
                  💰 {destination.budget_level}
                </span>
              )}
              {destination.best_season && (
                <span className="dd-hero-meta-pill">
                  🌤️ {destination.best_season}
                </span>
              )}
              {destination.category && (
                <span className="dd-hero-meta-pill dd-category-pill">
                  {destination.category}
                </span>
              )}
            </div>
          </div>
        </section>

        <div className="dd-body">
          {/* ── Score Breakdown Strip (when arrived via recommendation) ───── */}
          {scoreBreakdown && (
            <section className="dd-section dd-score-strip">
              <h2 className="dd-section-title">📊 Match Score Breakdown</h2>
              <div className="dd-breakdown-grid">
                {[
                  { label: "💰 Budget", val: scoreBreakdown.budget_match },
                  { label: "🎯 Activities", val: scoreBreakdown.activity_match },
                  { label: "🌤️ Season", val: scoreBreakdown.season_match },
                  { label: "🧭 Travel Style", val: scoreBreakdown.travel_style_match },
                ].map(({ label, val }) => (
                  <div key={label} className="dd-breakdown-item">
                    <div className="dd-breakdown-labels">
                      <span className="dd-breakdown-name">{label}</span>
                      <span className="dd-breakdown-val">{val}%</span>
                    </div>
                    <div className="dd-bar-track">
                      <div
                        className="dd-bar-fill"
                        style={{ width: `${val}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* ── About ───────────────────────────────────────────────────── */}
          {destination.description && (
            <section className="dd-section">
              <h2 className="dd-section-title">🌍 About {destination.name}</h2>
              <p className="dd-description">{destination.description}</p>
            </section>
          )}

          {/* ── Key Details ─────────────────────────────────────────────── */}
          <section className="dd-section">
            <h2 className="dd-section-title">📋 Key Details</h2>
            <div className="dd-details-grid">
              <div className="dd-detail-card">
                <span className="dd-detail-icon">⭐</span>
                <div>
                  <div className="dd-detail-label">Traveler Rating</div>
                  <div className="dd-detail-value">
                    {destination.rating.toFixed(1)} / 5.0
                    <span className="dd-stars"> {getRatingStars(destination.rating)}</span>
                  </div>
                </div>
              </div>
              <div className="dd-detail-card">
                <span className="dd-detail-icon">💰</span>
                <div>
                  <div className="dd-detail-label">Budget Level</div>
                  <div className="dd-detail-value">{destination.budget_level || "Moderate"}</div>
                </div>
              </div>
              <div className="dd-detail-card">
                <span className="dd-detail-icon">🌤️</span>
                <div>
                  <div className="dd-detail-label">Best Season</div>
                  <div className="dd-detail-value">{destination.best_season}</div>
                </div>
              </div>
              <div className="dd-detail-card">
                <span className="dd-detail-icon">🗓️</span>
                <div>
                  <div className="dd-detail-label">Recommended Stay</div>
                  <div className="dd-detail-value">{destination.recommended_duration} Days</div>
                </div>
              </div>
              <div className="dd-detail-card">
                <span className="dd-detail-icon">📊</span>
                <div>
                  <div className="dd-detail-label">Est. Daily Cost</div>
                  <div className="dd-detail-value">
                    Rs. {destination.average_daily_cost.toLocaleString()} / day
                  </div>
                </div>
              </div>
              <div className="dd-detail-card">
                <span className="dd-detail-icon">🏷️</span>
                <div>
                  <div className="dd-detail-label">Category</div>
                  <div className="dd-detail-value dd-category-text">{destination.category}</div>
                </div>
              </div>
            </div>
          </section>

          {/* ── Activities ──────────────────────────────────────────────── */}
          {activityList.length > 0 && (
            <section className="dd-section">
              <h2 className="dd-section-title">🎯 Activities at {destination.name}</h2>
              <div className="dd-activities-grid">
                {activityList.map((act) => {
                  const key = act.toLowerCase();
                  const meta = ACTIVITY_META[key];
                  const isPreferred = preferredActivities.includes(key);
                  return (
                    <span
                      key={act}
                      className={`dd-activity-chip ${isPreferred ? "dd-activity-preferred" : ""}`}
                    >
                      {meta ? (
                        <>
                          <span className="dd-chip-icon">{meta.icon}</span>
                          <span>{meta.label}</span>
                        </>
                      ) : (
                        <span>{act}</span>
                      )}
                      {isPreferred && <span className="dd-chip-check">✓</span>}
                    </span>
                  );
                })}
              </div>
              {preferredActivities.length > 0 && (
                <p className="dd-activity-note">
                  ✓ Highlighted activities match your preferences
                </p>
              )}
            </section>
          )}

          {/* ── Why We Recommend This ───────────────────────────────────── */}
          {displayReasons.length > 0 && (
            <section className="dd-section dd-reasons-section">
              <h2 className="dd-section-title">💡 Why We Recommend This</h2>
              <ul className="dd-reasons-list">
                {displayReasons.map((reason, i) => (
                  <li key={i} className="dd-reason-item">
                    <span className="dd-reason-check">✓</span>
                    <span className="dd-reason-text">{reason}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* ── CTA ─────────────────────────────────────────────────────── */}
          <section className="dd-cta-section">
            <div className="dd-cta-card">
              <div className="dd-cta-icon">✈️</div>
              <h2 className="dd-cta-title">Ready to visit {destination.name}?</h2>
              <p className="dd-cta-text">
                Generate a personalized day-by-day itinerary tailored to your budget, travel style, and activity preferences.
              </p>
              <div className="dd-cta-actions">
                <button
                  type="button"
                  className="dd-cta-btn-primary"
                  onClick={handlePlanMyTrip}
                  disabled={isGeneratingPlan}
                >
                  {isGeneratingPlan ? (
                    <span>Generating Itinerary…</span>
                  ) : (
                    <>
                      <span>Plan My Trip</span>
                      <span className="dd-btn-arrow">→</span>
                    </>
                  )}
                </button>
                <button
                  type="button"
                  className="dd-cta-btn-secondary"
                  onClick={() => navigate(-1)}
                >
                  ← Back
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
