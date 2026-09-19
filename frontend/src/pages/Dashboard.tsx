import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import { savedTripsApi, getToken, type SavedTripSummary } from "../api";
import "./Dashboard.css";

const FEATURED_DESTINATIONS = [
  {
    id: 1,
    name: "Ella",
    region: "Central Highlands",
    category: "Nature & Hiking",
    rating: 4.8,
    dailyCost: 12000,
    bestSeason: "Dec - Apr",
    emoji: "⛰️",
    gradientClass: "feat-nature",
    highlight: "Famous for Little Adam's Peak, Nine Arch Bridge, and lush tea estates.",
  },
  {
    id: 2,
    name: "Galle Fort",
    region: "Southern Coast",
    category: "Culture & Beach",
    rating: 4.9,
    dailyCost: 15000,
    bestSeason: "Dec - Apr",
    emoji: "🏛️",
    gradientClass: "feat-culture",
    highlight: "UNESCO 17th-century fortress, coastal ramparts, and vibrant heritage streets.",
  },
  {
    id: 3,
    name: "Sigiriya",
    region: "Cultural Triangle",
    category: "Ancient Heritage",
    rating: 4.9,
    dailyCost: 14000,
    bestSeason: "Jan - Apr",
    emoji: "🦁",
    gradientClass: "feat-history",
    highlight: "Ancient 5th-century rock palace with mirror walls and panoramic summit views.",
  },
  {
    id: 4,
    name: "Mirissa",
    region: "Southern Coast",
    category: "Beach & Wildlife",
    rating: 4.7,
    dailyCost: 13000,
    bestSeason: "Nov - Apr",
    emoji: "🏄",
    gradientClass: "feat-beach",
    highlight: "World-class whale watching, coconut tree hills, and golden sunset beaches.",
  },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [savedTrips, setSavedTrips] = useState<SavedTripSummary[]>([]);
  const [loadingTrips, setLoadingTrips] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    let isMounted = true;
    savedTripsApi
      .getSavedTrips()
      .then((data) => {
        if (isMounted) {
          setSavedTrips(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setSavedTrips([]);
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoadingTrips(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard-page">
      <Navbar />

      <main className="dashboard-content">
        {/* Hero Section */}
        <section className="dashboard-hero">
          <div className="hero-top-badge">
            <span className="hero-badge-dot"></span>
            <span>Intelligent Travel Engine</span>
          </div>

          <h1 className="hero-title">
            Design Your Ideal Sri Lanka Trip with Optimized Routes
          </h1>

          <p className="hero-description">
            Discover destinations matching your budget, season, and travel style.
            Get personalized itineraries with nearest-neighbor route ordering to minimize transit time.
          </p>

          <div className="hero-btn-row">
            <button
              type="button"
              className="hero-cta-btn"
              onClick={() => navigate("/plan-trip")}
            >
              <span>Plan a New Trip</span>
              <span className="btn-arrow">→</span>
            </button>

            <button
              type="button"
              className="hero-secondary-btn"
              onClick={() => navigate("/my-trips")}
            >
              <span>My Saved Trips</span>
              {savedTrips.length > 0 && (
                <span className="hero-saved-count">{savedTrips.length}</span>
              )}
            </button>
          </div>

          <div className="hero-stat-strip">
            <div className="stat-pill">
              <span className="stat-pill-num">18+</span>
              <span className="stat-pill-text">Curated Spots</span>
            </div>
            <div className="stat-pill-divider">•</div>
            <div className="stat-pill">
              <span className="stat-pill-num">100+</span>
              <span className="stat-pill-text">Activities</span>
            </div>
            <div className="stat-pill-divider">•</div>
            <div className="stat-pill">
              <span className="stat-pill-num">100%</span>
              <span className="stat-pill-text">Geographic Route Optimization</span>
            </div>
          </div>
        </section>

        {/* Saved Trips Quick Preview Section */}
        <section className="dashboard-recent-section">
          <div className="section-header-flex">
            <div>
              <span className="sub-heading-badge">Your Itineraries</span>
              <h2 className="section-heading">Recent Saved Trips</h2>
            </div>
            <Link to="/my-trips" className="section-view-all">
              View All ({savedTrips.length}) →
            </Link>
          </div>

          {loadingTrips ? (
            <div className="recent-trips-loading">
              <div className="dash-spinner"></div>
              <span>Loading your saved trips…</span>
            </div>
          ) : savedTrips.length > 0 ? (
            <div className="recent-trips-grid">
              {savedTrips.slice(0, 3).map((trip) => (
                <div key={trip.id} className="recent-trip-card">
                  <div className="recent-trip-top">
                    <h3 className="recent-trip-dest">{trip.destination_name}</h3>
                    <span className="recent-trip-days">{trip.trip_duration} Days</span>
                  </div>

                  <div className="recent-trip-meta">
                    {trip.travel_style && (
                      <span className="recent-chip">🧭 {trip.travel_style}</span>
                    )}
                    {trip.season && (
                      <span className="recent-chip">🌤️ {trip.season}</span>
                    )}
                    {trip.total_route_distance != null && trip.total_route_distance > 0 && (
                      <span className="recent-chip dist">🗺️ {trip.total_route_distance.toFixed(1)} km</span>
                    )}
                  </div>

                  <div className="recent-trip-actions">
                    <Link to={`/my-trips/${trip.id}`} className="recent-view-link">
                      Open Full Itinerary →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-saved-prompt">
              <div className="empty-prompt-icon">🗺️</div>
              <div className="empty-prompt-text">
                <h3>No saved trips yet</h3>
                <p>
                  Create your first personalized itinerary and save it to revisit day plans, maps, and activity distances anytime.
                </p>
              </div>
              <button
                type="button"
                className="empty-prompt-cta"
                onClick={() => navigate("/plan-trip")}
              >
                Plan Your First Trip
              </button>
            </div>
          )}
        </section>

        {/* Featured Inspiration Destinations */}
        <section className="dashboard-featured-section">
          <div className="section-header-flex">
            <div>
              <span className="sub-heading-badge">Inspiration</span>
              <h2 className="section-heading">Top Sri Lankan Destinations</h2>
            </div>
            <button
              type="button"
              className="section-view-all"
              onClick={() => navigate("/plan-trip")}
            >
              Get Custom Recommendations →
            </button>
          </div>

          <div className="featured-grid">
            {FEATURED_DESTINATIONS.map((dest) => (
              <div key={dest.id} className="featured-card">
                <div className={`featured-image-strip ${dest.gradientClass}`}>
                  <span className="featured-emoji">{dest.emoji}</span>
                  <span className="featured-rating">⭐ {dest.rating.toFixed(1)}</span>
                </div>

                <div className="featured-body">
                  <div className="featured-title-row">
                    <h3 className="featured-name">{dest.name}</h3>
                    <span className="featured-category-pill">{dest.category}</span>
                  </div>

                  <p className="featured-region">📍 {dest.region}</p>
                  <p className="featured-highlight">{dest.highlight}</p>

                  <div className="featured-specs">
                    <div className="feat-spec-item">
                      <span className="feat-spec-label">Avg. Daily</span>
                      <span className="feat-spec-val">Rs. {dest.dailyCost.toLocaleString()}</span>
                    </div>
                    <div className="feat-spec-item">
                      <span className="feat-spec-label">Best Season</span>
                      <span className="feat-spec-val">{dest.bestSeason}</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="featured-plan-btn"
                    onClick={() => navigate("/plan-trip")}
                  >
                    Find Itineraries for {dest.name} →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How It Works */}
        <section className="dashboard-steps">
          <div className="steps-header">
            <span className="sub-heading-badge">Simple Process</span>
            <h2 className="steps-heading">How Trip Optimizer Works</h2>
          </div>

          <div className="steps-row">
            <div className="step-item">
              <div className="step-number">1</div>
              <h3 className="step-title">Enter Preferences</h3>
              <p className="step-text">
                Specify your budget, trip duration, favorite activities, and expected travel season.
              </p>
            </div>

            <div className="step-item">
              <div className="step-number">2</div>
              <h3 className="step-title">Get Algorithm Matches</h3>
              <p className="step-text">
                Review multi-factor match percentages and score breakdowns for every destination.
              </p>
            </div>

            <div className="step-item">
              <div className="step-number">3</div>
              <h3 className="step-title">Optimized Itinerary</h3>
              <p className="step-text">
                Receive day-by-day schedules with geographic nearest-neighbor route ordering and drive times.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}