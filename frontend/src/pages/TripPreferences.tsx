import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import {
  recommendationsApi,
  tripsApi,
  getErrorMessage,
  type Recommendation,
} from "../api";
import "./TripPreferences.css";

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

const TRAVEL_STYLES = [
  { id: "adventure", label: "Adventure", icon: "⛰️", subtitle: "Treks & Thrills" },
  { id: "beach", label: "Beach", icon: "🏖️", subtitle: "Coast & Waves" },
  { id: "culture", label: "Culture", icon: "🏛️", subtitle: "Temples & History" },
  { id: "nature", label: "Nature", icon: "🌿", subtitle: "Waterfalls & Scenery" },
  { id: "wildlife", label: "Wildlife", icon: "🦁", subtitle: "Safaris & Fauna" },
  { id: "relaxation", label: "Relaxation", icon: "🌴", subtitle: "Peace & Serenity" },
];

const TRAVELER_PRESETS = [
  { value: "1", label: "1 Traveler", tag: "Solo" },
  { value: "2", label: "2 Travelers", tag: "Couple / Pair" },
  { value: "4", label: "4 Travelers", tag: "Small Group" },
];

const BUDGET_PRESETS = [
  { value: "25000", label: "Rs. 25k", tag: "Backpacker" },
  { value: "50000", label: "Rs. 50k", tag: "Standard" },
  { value: "100000", label: "Rs. 100k", tag: "Comfort" },
  { value: "180000", label: "Rs. 180k+", tag: "Luxury" },
];

const DURATION_PRESETS = [
  { value: "3", label: "3 Days", tag: "Weekend" },
  { value: "5", label: "5 Days", tag: "Short Break" },
  { value: "7", label: "7 Days", tag: "Full Week" },
  { value: "10", label: "10 Days", tag: "Grand Tour" },
];

function getCategoryStyle(category: string): { gradientClass: string; emoji: string } {
  const cat = (category || "").toLowerCase();
  if (cat === "beach") return { gradientClass: "card-img-beach", emoji: "🏖️" };
  if (cat === "culture") return { gradientClass: "card-img-culture", emoji: "🏛️" };
  if (cat === "nature") return { gradientClass: "card-img-nature", emoji: "🌿" };
  if (cat === "wildlife") return { gradientClass: "card-img-wildlife", emoji: "🦁" };
  if (cat === "adventure") return { gradientClass: "card-img-adventure", emoji: "⛰️" };
  if (cat === "relaxation") return { gradientClass: "card-img-relaxation", emoji: "🌴" };
  return { gradientClass: "card-img-default", emoji: "📍" };
}

function TripPreferences() {
  const navigate = useNavigate();
  const formRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLElement>(null);

  const [numTravelers, setNumTravelers] = useState("1");
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
  const [validationError, setValidationError] = useState<string | null>(null);
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
    if (e) e.preventDefault();
    setErrorMessage(null);
    setValidationError(null);

    const t = Number(numTravelers);
    const b = Number(budget);
    const d = Number(tripDuration);

    if (!t || t < 1 || t > 50) {
      setValidationError("Please enter a valid number of travelers (between 1 and 50).");
      return;
    }
    if (!b || b < 1000) {
      setValidationError("Please enter a valid budget per person of at least Rs. 1,000.");
      return;
    }
    if (!d || d < 1 || d > 30) {
      setValidationError("Please enter a trip duration between 1 and 30 days.");
      return;
    }
    if (!travelStyle) {
      setValidationError("Please select your preferred travel style.");
      return;
    }
    if (!season) {
      setValidationError("Please choose a planned travel season.");
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      const data = await recommendationsApi.getRecommendations({
        num_travelers: t,
        budget_per_person: b,
        trip_duration: d,
        travel_style: travelStyle,
        preferred_activities: activities,
        season: season,
      });

      const recs: Recommendation[] = data.recommendations || [];
      recs.sort((a, b) => b.score - a.score);
      setRecommendations(recs);
      setShowResultsOnly(true);

      if (recs.length > 0) {
        setExpandedCard({ [recs[0].destination]: true });
      }

      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error: unknown) {
      console.error("Failed to get recommendations:", error);
      setErrorMessage(
        getErrorMessage(
          error,
          "Could not connect to the recommendation service. Please verify the backend is running and try again."
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartOver = () => {
    setNumTravelers("1");
    setBudget("");
    setTripDuration("");
    setTravelStyle("");
    setSeason("");
    setActivities([]);
    setRecommendations([]);
    setHasSearched(false);
    setShowResultsOnly(false);
    setErrorMessage(null);
    setValidationError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleModifyPreferences = () => {
    setShowResultsOnly(false);
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const handleRetry = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const data = await recommendationsApi.getRecommendations({
        num_travelers: Number(numTravelers) || 1,
        budget_per_person: Number(budget),
        trip_duration: Number(tripDuration),
        travel_style: travelStyle,
        preferred_activities: activities,
        season: season,
      });

      const recs: Recommendation[] = data.recommendations || [];
      recs.sort((a, b) => b.score - a.score);
      setRecommendations(recs);
      setShowResultsOnly(true);

      if (recs.length > 0) {
        setExpandedCard({ [recs[0].destination]: true });
      }
    } catch (error: unknown) {
      setErrorMessage(
        getErrorMessage(
          error,
          "Could not connect to the recommendation service. Please verify backend connection and try again."
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDestination = async (rec: Recommendation) => {
    try {
      setIsGeneratingPlan(rec.destination);
      setErrorMessage(null);

      const destinationId = rec.id || 1;

      const planData = await tripsApi.generateTripItinerary(
        destinationId,
        activities,
        {
          budget: Number(budget),
          budget_per_person: Number(budget),
          num_travelers: Number(numTravelers) || 1,
          travel_style: travelStyle,
          trip_duration: Number(tripDuration),
        }
      );

      navigate("/trip-plan", {
        state: {
          destination: rec.destination,
          tripDuration: planData.actual_trip_duration || Number(tripDuration),
          requestedTripDuration: planData.requested_trip_duration || Number(tripDuration),
          insufficientActivities: planData.insufficient_activities,
          itineraryNotice: planData.itinerary_notice,
          itinerary: planData.itinerary,
          destinationDetails: {
            id: rec.id,
            name: rec.destination,
            country: rec.country,
            region: rec.region || "Sri Lanka",
            category: rec.category || travelStyle,
            budget_level: rec.budget_level || "",
            description: rec.description || "",
            average_daily_cost: rec.average_daily_cost,
            best_season: rec.best_season,
            activities: rec.activities,
            rating: rec.rating,
            recommended_duration: rec.recommended_duration || Number(tripDuration),
          },
          cost_breakdown: planData.cost_breakdown,
          preferences: {
            budget,
            budgetPerPerson: budget,
            numTravelers: Number(numTravelers) || 1,
            totalGroupBudget: Number(budget) * (Number(numTravelers) || 1),
            tripDuration,
            travelStyle,
            season,
            activities,
          },
        },
      });
    } catch (error) {
      console.error("Failed to generate trip plan:", error);
      setErrorMessage(
        "Failed to generate your trip itinerary. Please verify backend connection and try again."
      );
      window.scrollTo({ top: 0, behavior: "smooth" });
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
          budgetPerPerson: budget,
          numTravelers: Number(numTravelers) || 1,
          totalGroupBudget: Number(budget) * (Number(numTravelers) || 1),
          tripDuration,
          travelStyle,
          season,
          activities,
        },
      },
    });
  };

  const isCriteriaConfigured = numTravelers && budget && tripDuration && travelStyle && season;

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
              <div className="header-badge">AI Recommendation Engine</div>
              <h1 className="page-title">Personalize Your Sri Lanka Adventure</h1>
              <p className="page-subtitle">
                Configure your budget, timeframe, and favorite experiences.
                Our algorithm evaluates scores across multiple factors to rank the best destinations for you.
              </p>
            </header>

            {validationError && (
              <div className="pref-alert warning" role="alert">
                <span className="pref-alert-icon">ℹ️</span>
                <span>{validationError}</span>
              </div>
            )}

            {errorMessage && (
              <div className="pref-alert error" role="alert">
                <span className="pref-alert-icon">⚠️</span>
                <span style={{ flex: 1 }}>{errorMessage}</span>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="preset-btn"
                  style={{ background: "var(--danger)", color: "#fff", borderColor: "var(--danger)" }}
                >
                  Retry
                </button>
              </div>
            )}

            <div className="form-card" ref={formRef}>
              <form onSubmit={handleSubmit} className="trip-form" noValidate>
                <div className="form-grid">
                  {/* Number of Travelers Field */}
                  <div className="form-group">
                    <div className="form-label-row">
                      <label className="form-label" htmlFor="travelers-input">
                        <span className="label-icon">👥</span> Number of Travelers
                      </label>
                      <span className="field-hint-tag">People</span>
                    </div>

                    <div className="input-affix-wrapper">
                      <input
                        id="travelers-input"
                        type="number"
                        min="1"
                        max="50"
                        className="form-input with-suffix"
                        value={numTravelers}
                        onChange={(e) => {
                          setNumTravelers(e.target.value);
                          if (validationError) setValidationError(null);
                        }}
                        placeholder="e.g. 2"
                        required
                      />
                      <span className="input-suffix">Travelers</span>
                    </div>

                    {/* Quick Traveler Presets */}
                    <div className="quick-presets-row">
                      {TRAVELER_PRESETS.map((p) => (
                        <button
                          key={p.value}
                          type="button"
                          className={`preset-btn ${numTravelers === p.value ? "active" : ""}`}
                          onClick={() => {
                            setNumTravelers(p.value);
                            if (validationError) setValidationError(null);
                          }}
                        >
                          <span>{p.label}</span>
                          <span className="preset-tag">{p.tag}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Budget per Person Field */}
                  <div className="form-group">
                    <div className="form-label-row">
                      <label className="form-label" htmlFor="budget-input">
                        <span className="label-icon">💰</span> Budget per Person (LKR)
                      </label>
                      <span className="field-hint-tag">Rs. / person</span>
                    </div>

                    <div className="input-affix-wrapper">
                      <span className="input-prefix">Rs.</span>
                      <input
                        id="budget-input"
                        type="number"
                        min="1000"
                        step="1000"
                        className="form-input with-prefix"
                        value={budget}
                        onChange={(e) => {
                          setBudget(e.target.value);
                          if (validationError) setValidationError(null);
                        }}
                        placeholder="e.g. 50000"
                        required
                      />
                    </div>

                    {/* Quick Budget Presets */}
                    <div className="quick-presets-row">
                      {BUDGET_PRESETS.map((p) => (
                        <button
                          key={p.value}
                          type="button"
                          className={`preset-btn ${budget === p.value ? "active" : ""}`}
                          onClick={() => {
                            setBudget(p.value);
                            if (validationError) setValidationError(null);
                          }}
                        >
                          <span>{p.label}</span>
                          <span className="preset-tag">{p.tag}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Live Group Budget Summary Box */}
                <div className="group-budget-summary-box">
                  <div className="group-budget-item">
                    <span className="gb-label">Budget per Person</span>
                    <span className="gb-value">
                      {budget ? `Rs. ${Number(budget).toLocaleString()}` : "Rs. 0"}
                    </span>
                  </div>
                  <div className="group-budget-operator">×</div>
                  <div className="group-budget-item">
                    <span className="gb-label">Travelers</span>
                    <span className="gb-value">{numTravelers || 1}</span>
                  </div>
                  <div className="group-budget-operator">=</div>
                  <div className="group-budget-item highlight">
                    <span className="gb-label">Total Group Budget</span>
                    <span className="gb-value">
                      Rs. {(Number(budget || 0) * (Number(numTravelers) || 1)).toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Trip Duration and Season Row */}
                <div className="form-grid">
                  {/* Trip Duration Field */}
                  <div className="form-group">
                    <div className="form-label-row">
                      <label className="form-label" htmlFor="duration-input">
                        <span className="label-icon">⏱️</span> Trip Duration
                      </label>
                      <span className="field-hint-tag">Days</span>
                    </div>

                    <div className="input-affix-wrapper">
                      <input
                        id="duration-input"
                        type="number"
                        min="1"
                        max="30"
                        className="form-input with-suffix"
                        value={tripDuration}
                        onChange={(e) => {
                          setTripDuration(e.target.value);
                          if (validationError) setValidationError(null);
                        }}
                        placeholder="e.g. 3"
                        required
                      />
                      <span className="input-suffix">Days</span>
                    </div>

                    {/* Quick Duration Presets */}
                    <div className="quick-presets-row">
                      {DURATION_PRESETS.map((d) => (
                        <button
                          key={d.value}
                          type="button"
                          className={`preset-btn ${tripDuration === d.value ? "active" : ""}`}
                          onClick={() => {
                            setTripDuration(d.value);
                            if (validationError) setValidationError(null);
                          }}
                        >
                          <span>{d.label}</span>
                          <span className="preset-tag">{d.tag}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Visual Travel Style Selection Cards */}
                <div className="form-section-block">
                  <div className="form-label-row">
                    <label className="form-label">
                      <span className="label-icon">🧭</span> Primary Travel Style
                    </label>
                    <span className="field-hint-tag">
                      {travelStyle ? travelStyle.toUpperCase() : "Select one"}
                    </span>
                  </div>

                  <div className="travel-style-cards-grid">
                    {TRAVEL_STYLES.map((style) => {
                      const isSelected = travelStyle === style.id;
                      return (
                        <button
                          key={style.id}
                          type="button"
                          className={`travel-style-card ${isSelected ? "selected" : ""}`}
                          onClick={() => {
                            setTravelStyle(style.id);
                            if (validationError) setValidationError(null);
                          }}
                        >
                          <span className="style-card-icon">{style.icon}</span>
                          <span className="style-card-title">{style.label}</span>
                          <span className="style-card-sub">{style.subtitle}</span>
                          {isSelected && <span className="style-card-check">✓</span>}
                        </button>
                      );
                    })}
                  </div>

                  {/* Accessible fallback select */}
                  <select
                    id="travel-style-select"
                    className="visually-hidden"
                    value={travelStyle}
                    onChange={(e) => setTravelStyle(e.target.value)}
                    tabIndex={-1}
                    aria-hidden="true"
                  >
                    <option value="">Select a style</option>
                    {TRAVEL_STYLES.map((s) => (
                      <option key={s.id} value={s.id}>{s.label}</option>
                    ))}
                  </select>
                </div>

                {/* Season Field */}
                <div className="form-section-block">
                  <label className="form-label" htmlFor="season-select">
                    <span className="label-icon">🌤️</span> Planned Travel Season
                  </label>
                  <select
                    id="season-select"
                    className="form-select"
                    value={season}
                    onChange={(e) => {
                      setSeason(e.target.value);
                      if (validationError) setValidationError(null);
                    }}
                    required
                  >
                    <option value="">Choose a travel window</option>
                    <option value="December-April">
                      December - April (Peak Season / South & West Coast, Central Highlands)
                    </option>
                    <option value="January-April">
                      January - April (Cultural Triangle, Ancient Cities & Tea Country)
                    </option>
                    <option value="May-September">
                      May - September (East Coast Beaches, Arugam Bay Surf & Summer Sun)
                    </option>
                    <option value="February-June">
                      February - June (Wildlife Parks, Safaris & Bird Watching)
                    </option>
                    <option value="December-March">
                      December - March (Marine Life, Whale Watching & Coastal Relaxation)
                    </option>
                    <option value="January-September">
                      January - September (Northern Peninsula & Jaffna Heritage)
                    </option>
                    <option value="October-April">
                      October - April (Yala & Wilpattu National Parks)
                    </option>
                  </select>
                  <span className="field-hint">
                    Sri Lanka experiences distinct regional monsoon cycles. Select your target months for best weather compatibility.
                  </span>
                </div>

                {/* Preferred Activities Field */}
                <div className="activities-group">
                  <div className="activities-header-row">
                    <label className="form-label">
                      <span className="label-icon">🎯</span> Preferred Activities & Interests
                    </label>
                    <span className="optional-tag">
                      {activities.length === 0
                        ? "(Select any to boost match scores)"
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

                {/* Live Criteria Summary Bar */}
                <div className="criteria-summary-bar">
                  <span className="criteria-summary-label">Configured Search:</span>
                  <div className="criteria-badges">
                    <span className="crit-badge active">
                      👥 {numTravelers} {Number(numTravelers) === 1 ? "Traveler" : "Travelers"}
                    </span>
                    <span className={`crit-badge ${budget ? "active" : ""}`}>
                      💰 {budget ? `Rs. ${Number(budget).toLocaleString()} / person` : "Budget unset"}
                    </span>
                    {budget && Number(numTravelers) > 1 && (
                      <span className="crit-badge active">
                        💵 Total: Rs. {(Number(budget) * Number(numTravelers)).toLocaleString()}
                      </span>
                    )}
                    <span className={`crit-badge ${tripDuration ? "active" : ""}`}>
                      ⏱️ {tripDuration ? `${tripDuration} Days` : "Duration unset"}
                    </span>
                    <span className={`crit-badge ${travelStyle ? "active" : ""}`}>
                      🧭 {travelStyle ? travelStyle.charAt(0).toUpperCase() + travelStyle.slice(1) : "Style unset"}
                    </span>
                    <span className={`crit-badge ${season ? "active" : ""}`}>
                      🌤️ {season ? season.split(" ")[0] : "Season unset"}
                    </span>
                    {activities.length > 0 && (
                      <span className="crit-badge active">
                        🎯 {activities.length} activities
                      </span>
                    )}
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={isLoading || !isCriteriaConfigured}
                >
                  {isLoading ? (
                    <>
                      <span className="btn-spinner"></span>
                      <span>Matching Destinations...</span>
                    </>
                  ) : (
                    <>
                      <span>Find Best Destination Matches</span>
                      <span className="btn-arrow">→</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </>
        )}

        {/* High Quality Loading State */}
        {isLoading && (
          <div className="loading-state-card" role="status">
            <div className="loader-compass-wrapper">
              <div className="loader-compass-ring"></div>
              <span className="loader-compass-icon">🧭</span>
            </div>
            <h3 className="loading-title">Finding Your Perfect Sri Lankan Destinations</h3>
            <p className="loading-subtext">
              Evaluating multi-factor scores for budget compatibility, seasonal climate, and activity proximity...
            </p>
            <div className="loading-pulse-steps">
              <span className="pulse-step active">✓ Analyzing budget limits</span>
              <span className="pulse-step active">✓ Matching monsoon seasons</span>
              <span className="pulse-step active">✓ Ranking 18+ destinations</span>
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
                We couldn't find destinations matching your exact filter combination. Try
                adjusting your budget, selecting broader activities, or exploring a different season.
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
                <span className="section-badge">🎯 Algorithm Recommendation Results</span>
                <h2 className="results-main-title">Top Sri Lankan Destinations for You</h2>
                <p className="results-summary-text">
                  Ranked by budget match, season suitability, travel style, and activity relevance.
                </p>
              </div>

              {/* Active Preferences Chips */}
              <div className="active-filters-box">
                <span className="filters-title">Your Criteria:</span>
                <div className="filter-pills">
                  <span className="filter-pill">👥 {numTravelers} {Number(numTravelers) === 1 ? "Traveler" : "Travelers"}</span>
                  <span className="filter-pill">💰 Rs. {Number(budget).toLocaleString()} / person</span>
                  {Number(numTravelers) > 1 && (
                    <span className="filter-pill">
                      💵 Group Total: Rs. {(Number(budget) * Number(numTravelers)).toLocaleString()}
                    </span>
                  )}
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

            {/* Cards List */}
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
                          <span className="card-strip-rank">Rank #{index + 1}</span>
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
                          </div>
                          <p className="destination-location">
                            📍 {recommendation.region && recommendation.region !== "Sri Lanka"
                              ? `${recommendation.region}, Sri Lanka`
                              : recommendation.country}
                          </p>
                        </div>
                      </div>

                      <div className="score-badge-wrapper">
                        <div className="score-circular-badge">
                          <span className="score-value-large">
                            {Math.round(recommendation.score)}%
                          </span>
                          <span className="score-label-small">Match Score</span>
                        </div>
                      </div>
                    </div>

                    {/* Meta Highlights Strip */}
                    <div className="card-meta-strip">
                      <div className="meta-item">
                        <span className="meta-label">Est. Daily Cost</span>
                        <span className="meta-value cost-value">
                          Rs. {recommendation.average_daily_cost.toLocaleString()} / person
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">
                          Est. Total ({tripDuration}d, {numTravelers} {Number(numTravelers) === 1 ? "traveler" : "travelers"})
                        </span>
                        <span className="meta-value cost-value highlight">
                          Rs. {recommendation.estimated_trip_cost.toLocaleString()}
                        </span>
                        {Number(numTravelers) > 1 && (
                          <span style={{ fontSize: "11px", color: "var(--text-secondary)", fontWeight: 500, marginTop: "2px" }}>
                            (Rs. {Math.round(recommendation.estimated_trip_cost / Number(numTravelers)).toLocaleString()} / person)
                          </span>
                        )}
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

                    {/* Match Score Breakdown Bar Section */}
                    {breakdown && (
                      <div className="score-breakdown-card">
                        <div className="breakdown-header">
                          <h4 className="breakdown-title">📊 Match Score Breakdown</h4>
                          <span className="breakdown-total">
                            Overall: <strong>{Math.round(recommendation.score)}%</strong>
                          </span>
                        </div>

                        <div className="breakdown-bars-grid">
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

                          <div className="breakdown-bar-item">
                            <div className="bar-labels">
                              <span className="bar-title">🧭 Travel Style</span>
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
                                    🏨 Stay: Rs. {Math.round((costBreakdown.accommodation ?? 0) / Number(tripDuration || 1)).toLocaleString()}/day
                                  </span>
                                  <span className="cost-pill">
                                    🍽️ Food: Rs. {Math.round((costBreakdown.food ?? 0) / Number(tripDuration || 1)).toLocaleString()}/day
                                  </span>
                                  <span className="cost-pill">
                                    🛺 Transport: Rs. {Math.round((costBreakdown.transportation ?? 0) / Number(tripDuration || 1)).toLocaleString()}/day
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
