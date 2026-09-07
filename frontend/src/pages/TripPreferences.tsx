import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";
import "./TripPreferences.css";

type ScoreBreakdown = {
  budget_match: number;
  activity_match: number;
  season_match: number;
  travel_style_match: number;
  rating_match?: number;
  overall_score: number;
};

type CostBreakdown = {
  accommodation: number;
  food: number;
  transportation: number;
  daily_average: number;
  estimated_trip_cost: number;
};

type Recommendation = {
  id?: number;
  destination: string;
  country: string;
  region?: string;
  category?: string;
  budget_level?: string;
  score: number;
  score_breakdown?: ScoreBreakdown;
  cost_breakdown?: CostBreakdown;
  description?: string;
  average_daily_cost: number;
  estimated_trip_cost: number;
  best_season: string;
  activities: string;
  rating: number;
  recommended_duration?: number;
  reasons: string[];
};

const ACTIVITY_METADATA: Record<string, { label: string; icon: string }> = {
  hiking: { label: "Hiking", icon: "🥾" },
  nature: { label: "Nature", icon: "🌿" },
  swimming: { label: "Swimming", icon: "🏊" },
  surfing: { label: "Surfing", icon: "🏄" },
  wildlife: { label: "Wildlife", icon: "🦁" },
  culture: { label: "Culture", icon: "🏛️" },
  sightseeing: { label: "Sightseeing", icon: "🗺️" },
  relaxation: { label: "Relaxation", icon: "🌴" },
};

function getCategoryStyle(category: string): { gradientClass: string; emoji: string } {
  const cat = (category || "").toLowerCase();
  if (cat === "beach")     return { gradientClass: "card-img-beach",     emoji: "🏖️" };
  if (cat === "culture")   return { gradientClass: "card-img-culture",   emoji: "🏛️" };
  if (cat === "nature")    return { gradientClass: "card-img-nature",    emoji: "🌿" };
  if (cat === "wildlife")  return { gradientClass: "card-img-wildlife",  emoji: "🦁" };
  if (cat === "adventure") return { gradientClass: "card-img-adventure", emoji: "⛰️" };
  if (cat === "relaxation") return { gradientClass: "card-img-relaxation", emoji: "🌴" };
  return { gradientClass: "card-img-default", emoji: "📍" };
}

function TripPreferences() {
  const navigate = useNavigate();
  const formRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLElement>(null);

  const [budget, setBudget] = useState("");
  const [tripDuration, setTripDuration] = useState("");
  const [travelStyle, setTravelStyle] = useState("");
  const [season, setSeason] = useState("");
  const [activities, setActivities] = useState<string[]>([]);

  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [expandedCard, setExpandedCard] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [showResultsOnly, setShowResultsOnly] = useState(false);

  const availableActivities = [
    "hiking",
    "nature",
    "swimming",
    "surfing",
    "wildlife",
    "culture",
    "sightseeing",
    "relaxation",
  ];

  const handleActivityChange = (activity: string) => {
    setActivities((current) =>
      current.includes(activity)
        ? current.filter((item) => item !== activity)
        : [...current, activity]
    );
  };

  const toggleCardDetails = (destName: string) => {
    setExpandedCard((prev) => ({
      ...prev,
      [destName]: !prev[destName],
    }));
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    setIsLoading(true);
    setErrorMessage(null);
    setHasSearched(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/recommendations/",
        {
          budget: Number(budget),
          trip_duration: Number(tripDuration),
          travel_style: travelStyle,
          preferred_activities: activities,
          season: season,
        }
      );

      const recs: Recommendation[] = response.data.recommendations || [];
      // Ensure sorted by overall score descending
      recs.sort((a, b) => b.score - a.score);
      setRecommendations(recs);
      setShowResultsOnly(true);

      // Auto expand the #1 best match by default
      if (recs.length > 0) {
        setExpandedCard({ [recs[0].destination]: true });
      }

      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error: unknown) {
      console.error("Failed to get recommendations:", error);
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setErrorMessage(
        axiosError.response?.data?.detail ||
          "Could not connect to the recommendation service. Please verify the backend is running and try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartOver = () => {
    setBudget("");
    setTripDuration("");
    setTravelStyle("");
    setSeason("");
    setActivities([]);
    setRecommendations([]);
    setHasSearched(false);
    setShowResultsOnly(false);
    setErrorMessage(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleModifyPreferences = () => {
    setShowResultsOnly(false);
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  // Fix: retry without requiring a FormEvent — calls the API directly
  const handleRetry = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/recommendations/",
        {
          budget: Number(budget),
          trip_duration: Number(tripDuration),
          travel_style: travelStyle,
          preferred_activities: activities,
          season: season,
        }
      );

      const recs: Recommendation[] = response.data.recommendations || [];
      recs.sort((a, b) => b.score - a.score);
      setRecommendations(recs);
      setShowResultsOnly(true);

      if (recs.length > 0) {
        setExpandedCard({ [recs[0].destination]: true });
      }
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setErrorMessage(
        axiosError.response?.data?.detail ||
          "Could not connect to the recommendation service. Please verify the backend is running and try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDestination = async (rec: Recommendation) => {
    try {
      setIsGeneratingPlan(rec.destination);

      const destinationId = rec.id || 1;

      const response = await axios.post(
        `http://127.0.0.1:8000/api/trips/activities/${destinationId}`,
        activities,
        {
          params: {
            budget: Number(budget),
            travel_style: travelStyle,
            trip_duration: Number(tripDuration),
          },
        }
      );

      navigate("/trip-plan", {
        state: {
          destination: rec.destination,
          tripDuration: Number(tripDuration),
          itinerary: response.data.itinerary,
        },
      });
    } catch (error) {
      console.error("Failed to generate trip plan:", error);
      alert("Failed to generate trip itinerary. Please check the backend connection and try again.");
    } finally {
      setIsGeneratingPlan(null);
    }
  };

  const handleViewDetails = (rec: Recommendation) => {
    navigate(`/destinations/${rec.id ?? 0}`, {
      state: {
        recommendation: rec,
        preferences: {
          budget,
          tripDuration,
          travelStyle,
          season,
          activities,
        },
      },
    });
  };

  return (
    <div className="page-wrapper">
      <Navbar />

      <main className="preferences-page">
        {/* Top Navigation when viewing results */}
        {showResultsOnly && (
          <div className="results-top-nav">
            <button
              type="button"
              className="back-btn"
              onClick={handleModifyPreferences}
            >
              ← Modify Preferences
            </button>
            <button
              type="button"
              className="start-over-btn"
              onClick={handleStartOver}
            >
              🔄 Start Over
            </button>
          </div>
        )}

        {/* Preference Input View */}
        {!showResultsOnly && (
          <>
            <header className="page-header">
              <div className="header-badge">Sri Lanka AI Travel Engine</div>
              <h1 className="page-title">Find Your Ideal Destination</h1>
              <p className="page-subtitle">
                Set your budget, duration, travel style, and activities to receive
                algorithm-ranked recommendations with full score breakdowns.
              </p>
            </header>

            <div className="form-card" ref={formRef}>
              <form onSubmit={handleSubmit} className="trip-form">
                <div className="form-grid">
                  {/* Budget Field */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="budget-input">
                      <span className="label-icon">💰</span> Budget (LKR)
                    </label>
                    <div className="input-affix-wrapper">
                      <span className="input-prefix">Rs.</span>
                      <input
                        id="budget-input"
                        type="number"
                        min="1000"
                        step="500"
                        className="form-input with-prefix"
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        placeholder="e.g. 50000"
                        required
                      />
                    </div>
                    <span className="field-hint">Total budget for the entire trip</span>
                  </div>

                  {/* Trip Duration Field */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="duration-input">
                      <span className="label-icon">⏱️</span> Trip Duration
                    </label>
                    <div className="input-affix-wrapper">
                      <input
                        id="duration-input"
                        type="number"
                        min="1"
                        max="30"
                        className="form-input with-suffix"
                        value={tripDuration}
                        onChange={(e) => setTripDuration(e.target.value)}
                        placeholder="e.g. 3"
                        required
                      />
                      <span className="input-suffix">Days</span>
                    </div>
                    <span className="field-hint">Number of travel days</span>
                  </div>

                  {/* Travel Style Field */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="travel-style-select">
                      <span className="label-icon">🧭</span> Travel Style
                    </label>
                    <select
                      id="travel-style-select"
                      className="form-select"
                      value={travelStyle}
                      onChange={(e) => setTravelStyle(e.target.value)}
                      required
                    >
                      <option value="">Select a style</option>
                      <option value="adventure">Adventure (Thrills & Treks)</option>
                      <option value="beach">Beach (Coastal & Waves)</option>
                      <option value="culture">Culture (Heritage & History)</option>
                      <option value="nature">Nature (Scenic & Greenery)</option>
                      <option value="wildlife">Wildlife (Safaris & Fauna)</option>
                      <option value="relaxation">Relaxation (Peace & Wellness)</option>
                    </select>
                    <span className="field-hint">Preferred atmosphere & style</span>
                  </div>

                  {/* Season Field */}
                  <div className="form-group">
                    <label className="form-label" htmlFor="season-select">
                      <span className="label-icon">🌤️</span> Travel Season
                    </label>
                    <select
                      id="season-select"
                      className="form-select"
                      value={season}
                      onChange={(e) => setSeason(e.target.value)}
                      required
                    >
                      <option value="">Select a season</option>
                      <option value="December-April">December - April (Peak Dry Season / South & West & Central)</option>
                      <option value="January-April">January - April (Cultural Triangle & Central Highlands)</option>
                      <option value="May-September">May - September (East Coast & Summer Surf)</option>
                      <option value="February-June">February - June (Wildlife & Safari Season)</option>
                      <option value="December-March">December - March (South Coastal & Marine Season)</option>
                      <option value="January-September">January - September (Northern Peninsula)</option>
                      <option value="October-April">October - April (Wildlife National Parks)</option>
                    </select>
                    <span className="field-hint">Time of year you plan to travel</span>
                  </div>
                </div>

                {/* Preferred Activities Field */}
                <div className="activities-group">
                  <div className="activities-header-row">
                    <label className="form-label">
                      <span className="label-icon">🎯</span> Preferred Activities
                    </label>
                    <span className="optional-tag">
                      {activities.length === 0
                        ? "(Select any to personalize)"
                        : `(${activities.length} selected)`}
                    </span>
                  </div>

                  <div className="activity-chips-grid">
                    {availableActivities.map((activity) => {
                      const isSelected = activities.includes(activity);
                      const meta = ACTIVITY_METADATA[activity] || {
                        label: activity,
                        icon: "✨",
                      };

                      return (
                        <button
                          type="button"
                          key={activity}
                          className={`activity-chip ${isSelected ? "selected" : ""}`}
                          onClick={() => handleActivityChange(activity)}
                          aria-pressed={isSelected}
                        >
                          <span className="chip-icon">{meta.icon}</span>
                          <span className="chip-label">{meta.label}</span>
                          {isSelected && <span className="chip-check">✓</span>}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="btn-spinner"></span>
                      <span>Calculating Compatibility Scores...</span>
                    </>
                  ) : (
                    <>
                      <span>Find My Best Destinations</span>
                      <span className="btn-arrow">→</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </>
        )}

        {/* Loading State Animation */}
        {isLoading && (
          <div className="loading-state-card">
            <div className="loading-spinner-large"></div>
            <h3>Finding Your Optimal Destinations</h3>
            <p>
              Evaluating budget constraints across accommodation, food, and transport,
              matching preferred activities, checking season suitability, and sorting
              top-scoring Sri Lankan destinations...
            </p>
          </div>
        )}

        {/* API Error State */}
        {errorMessage && !isLoading && (
          <div className="error-card">
            <div className="error-icon-large">⚠️</div>
            <h3>Unable to Load Recommendations</h3>
            <p>{errorMessage}</p>
            <div className="error-actions">
              <button
                type="button"
                className="retry-btn"
                onClick={handleRetry}
              >
                🔄 Try Again
              </button>
              {showResultsOnly && (
                <button
                  type="button"
                  className="secondary-action-btn"
                  onClick={handleModifyPreferences}
                >
                  Modify Preferences
                </button>
              )}
            </div>
          </div>
        )}

        {/* Empty Results State */}
        {hasSearched &&
          recommendations.length === 0 &&
          !isLoading &&
          !errorMessage && (
            <div className="empty-results-card">
              <div className="empty-icon">🏖️</div>
              <h3>No Matching Destinations Found</h3>
              <p>
                We couldn't find destinations matching your exact filters. Try
                increasing your budget, selecting different activities, or choosing
                a different season.
              </p>
              <button
                type="button"
                className="retry-btn"
                onClick={handleModifyPreferences}
              >
                Adjust Trip Preferences
              </button>
            </div>
          )}

        {/* Recommendation Results Page / Section */}
        {showResultsOnly && recommendations.length > 0 && !isLoading && (
          <section
            id="recommendations-section"
            className="recommendations-section"
            ref={resultsRef}
          >
            {/* Header & Filter Summary Banner */}
            <div className="results-hero-banner">
              <div className="results-summary-left">
                <span className="section-badge">🎯 AI Recommendation Results</span>
                <h2 className="results-main-title">Top Sri Lankan Destinations for You</h2>
                <p className="results-summary-text">
                  Ranked by budget match, season suitability, travel style, and activity preferences.
                </p>
              </div>

              {/* Active Preferences Chips */}
              <div className="active-filters-box">
                <span className="filters-title">Your Criteria:</span>
                <div className="filter-pills">
                  <span className="filter-pill">💰 Rs. {Number(budget).toLocaleString()}</span>
                  <span className="filter-pill">⏱️ {tripDuration} {Number(tripDuration) === 1 ? "Day" : "Days"}</span>
                  <span className="filter-pill">🧭 {travelStyle}</span>
                  <span className="filter-pill">🌤️ {season}</span>
                  {activities.length > 0 && (
                    <span className="filter-pill">
                      🎯 {activities.length} {activities.length === 1 ? "activity" : "activities"}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Results Controls Bar */}
            <div className="results-controls-bar">
              <div className="results-count">
                Showing <strong>{recommendations.length}</strong> ranked{" "}
                {recommendations.length === 1 ? "destination" : "destinations"}
              </div>
              <div className="results-action-buttons">
                <button
                  type="button"
                  className="control-btn modify"
                  onClick={handleModifyPreferences}
                >
                  ✏️ Modify Preferences
                </button>
                <button
                  type="button"
                  className="control-btn start-over"
                  onClick={handleStartOver}
                >
                  🔄 Start Over
                </button>
              </div>
            </div>

            {/* Cards Grid / List */}
            <div className="recommendations-list">
              {recommendations.map((recommendation, index) => {
                const isTopMatch = index === 0;
                const isExpanded = !!expandedCard[recommendation.destination];
                const breakdown = recommendation.score_breakdown;
                const costBreakdown = recommendation.cost_breakdown;

                  return (
                  <article
                    className={`recommendation-card ${isTopMatch ? "top-match-card" : ""}`}
                    key={recommendation.destination}
                  >
                    {isTopMatch && (
                      <div className="top-match-ribbon">
                        <span>🌟 #1 Best Overall Match</span>
                      </div>
                    )}

                    {/* Category Gradient Image Strip */}
                    {(() => {
                      const { gradientClass, emoji } = getCategoryStyle(recommendation.category ?? "");
                      return (
                        <div className={`card-image-strip ${gradientClass}`}>
                          <span className="card-strip-emoji">{emoji}</span>
                          <span className="card-strip-rank">#{index + 1}</span>
                        </div>
                      );
                    })()}

                    {/* Card Main Info Area */}
                    <div className="card-header-row">
                      <div className="destination-identity">
                        <div>
                          <div className="dest-title-wrap">
                            <h3 className="destination-name">
                              {recommendation.destination}
                            </h3>
                            {recommendation.category && (
                              <span className="category-tag">
                                {recommendation.category}
                              </span>
                            )}
                            {recommendation.budget_level && (
                              <span className="budget-level-tag">
                                💰 {recommendation.budget_level}
                              </span>
                            )}
                          </div>
                          <span className="destination-country">
                            📍 {recommendation.region ? `${recommendation.region}, Sri Lanka` : `${recommendation.country}`}
                          </span>
                        </div>
                      </div>

                      {/* Prominent Match Percentage */}
                      <div className="match-score-badge">
                        <div className="score-percent-val">
                          {Math.round(recommendation.score)}%
                        </div>
                        <span className="score-percent-label">Match Score</span>
                      </div>
                    </div>

                    {/* Short Description */}
                    {recommendation.description && (
                      <p className="destination-description">
                        {recommendation.description}
                      </p>
                    )}

                    {/* Key Travel Metrics Grid */}
                    <div className="destination-meta-grid">
                      <div className="meta-item">
                        <span className="meta-label">Est. Daily Budget</span>
                        <span className="meta-value cost-value">
                          Rs. {recommendation.average_daily_cost.toLocaleString()}/day
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">Est. Total ({tripDuration}d)</span>
                        <span className="meta-value cost-value highlight">
                          Rs. {recommendation.estimated_trip_cost.toLocaleString()}
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">Rating</span>
                        <span className="meta-value rating-value">
                          ⭐ {recommendation.rating.toFixed(1)} / 5.0
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">Best Season</span>
                        <span className="meta-value season-value">
                          🌤️ {recommendation.best_season}
                        </span>
                      </div>
                    </div>

                    {/* Relevant Activities Tags */}
                    {recommendation.activities && (
                      <div className="activities-tags-row">
                        <span className="tags-label">Relevant Activities:</span>
                        <div className="tags-container">
                          {recommendation.activities.split(",").map((act, i) => {
                            const cleanAct = act.trim().toLowerCase();
                            const isUserPreferred = activities.includes(cleanAct);

                            return (
                              <span
                                key={i}
                                className={`activity-tag ${isUserPreferred ? "preferred-tag" : ""}`}
                              >
                                {isUserPreferred && <span className="tag-check">✓ </span>}
                                {act.trim()}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Simple Score Breakdown Bar Section */}
                    {breakdown && (
                      <div className="score-breakdown-card">
                        <div className="breakdown-header">
                          <h4 className="breakdown-title">📊 Match Score Breakdown</h4>
                          <span className="breakdown-total">
                            Overall: <strong>{Math.round(recommendation.score)}%</strong>
                          </span>
                        </div>

                        <div className="breakdown-bars-grid">
                          {/* Budget Match */}
                          <div className="breakdown-bar-item">
                            <div className="bar-labels">
                              <span className="bar-title">💰 Budget Match</span>
                              <span className="bar-val">{breakdown.budget_match}%</span>
                            </div>
                            <div className="bar-track">
                              <div
                                className="bar-fill budget"
                                style={{ width: `${breakdown.budget_match}%` }}
                              />
                            </div>
                          </div>

                          {/* Activity Match */}
                          <div className="breakdown-bar-item">
                            <div className="bar-labels">
                              <span className="bar-title">🎯 Activity Match</span>
                              <span className="bar-val">{breakdown.activity_match}%</span>
                            </div>
                            <div className="bar-track">
                              <div
                                className="bar-fill activity"
                                style={{ width: `${breakdown.activity_match}%` }}
                              />
                            </div>
                          </div>

                          {/* Season Match */}
                          <div className="breakdown-bar-item">
                            <div className="bar-labels">
                              <span className="bar-title">🌤️ Season Match</span>
                              <span className="bar-val">{breakdown.season_match}%</span>
                            </div>
                            <div className="bar-track">
                              <div
                                className="bar-fill season"
                                style={{ width: `${breakdown.season_match}%` }}
                              />
                            </div>
                          </div>

                          {/* Travel Style Match */}
                          <div className="breakdown-bar-item">
                            <div className="bar-labels">
                              <span className="bar-title">🧭 Style Match</span>
                              <span className="bar-val">{breakdown.travel_style_match}%</span>
                            </div>
                            <div className="bar-track">
                              <div
                                className="bar-fill style"
                                style={{ width: `${breakdown.travel_style_match}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* "Why this destination?" Expandable Explanation Box */}
                    {recommendation.reasons && recommendation.reasons.length > 0 && (
                      <div className="reasons-section-box">
                        <div
                          className="reasons-toggle-header"
                          onClick={() => toggleCardDetails(recommendation.destination)}
                          role="button"
                          tabIndex={0}
                        >
                          <h4 className="reasons-title">
                            💡 Why this destination fits your trip:
                          </h4>
                          <button
                            type="button"
                            className="view-details-toggle-btn"
                          >
                            <span>{isExpanded ? "Hide Details" : "View Details"}</span>
                            <span className={`toggle-arrow ${isExpanded ? "open" : ""}`}>
                              ▼
                            </span>
                          </button>
                        </div>

                        {isExpanded && (
                          <div className="reasons-expanded-content">
                            <ul className="reasons-list">
                              {recommendation.reasons.map((reason, reasonIndex) => (
                                <li key={reasonIndex} className="reason-item">
                                  <span className="reason-check">✓</span>
                                  <span className="reason-text">{reason}</span>
                                </li>
                              ))}
                            </ul>

                            {/* Estimated Daily Cost Breakdown Categories */}
                            {costBreakdown && (
                              <div className="cost-breakdown-substrip">
                                <span className="cost-substrip-title">Daily Category Estimates:</span>
                                <div className="cost-substrip-pills">
                                  <span className="cost-pill">
                                    🏨 Stay: Rs. {Math.round(costBreakdown.accommodation / Number(tripDuration || 1)).toLocaleString()}/day
                                  </span>
                                  <span className="cost-pill">
                                    🍽️ Food: Rs. {Math.round(costBreakdown.food / Number(tripDuration || 1)).toLocaleString()}/day
                                  </span>
                                  <span className="cost-pill">
                                    🛺 Transport: Rs. {Math.round(costBreakdown.transportation / Number(tripDuration || 1)).toLocaleString()}/day
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Card Actions */}
                    <div className="card-actions-row">
                      <button
                        type="button"
                        className="details-secondary-btn"
                        onClick={() => handleViewDetails(recommendation)}
                      >
                        👁️ View Details
                      </button>

                      <button
                        type="button"
                        className="select-destination-btn"
                        disabled={isGeneratingPlan === recommendation.destination}
                        onClick={() => handleSelectDestination(recommendation)}
                      >
                        {isGeneratingPlan === recommendation.destination ? (
                          <>
                            <span className="btn-spinner"></span>
                            <span>Building Itinerary...</span>
                          </>
                        ) : (
                          <>
                            <span>Plan My Trip</span>
                            <span className="btn-arrow">→</span>
                          </>
                        )}
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>

            {/* Bottom Footer Actions */}
            <div className="results-bottom-bar">
              <button
                type="button"
                className="control-btn modify large"
                onClick={handleModifyPreferences}
              >
                ✏️ Modify Trip Preferences
              </button>
              <button
                type="button"
                className="control-btn start-over large"
                onClick={handleStartOver}
              >
                🔄 Start a New Search
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default TripPreferences;
