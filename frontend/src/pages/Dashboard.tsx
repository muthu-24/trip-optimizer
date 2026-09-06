import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <Navbar />

      <main className="dashboard-content">
        {/* Hero Section */}
        <section className="dashboard-hero">
          <span className="hero-tagline">✨ Smart Travel Optimization</span>
          <h1 className="hero-title">Plan Your Perfect Getaway</h1>
          <p className="hero-description">
            Discover ideal destinations tailored to your budget, travel style,
            and preferred activities with AI-driven scoring and day-by-day itineraries.
          </p>
          <button
            type="button"
            className="hero-cta-btn"
            onClick={() => navigate("/plan-trip")}
          >
            <span>Plan a New Trip</span>
            <span>→</span>
          </button>
        </section>

        {/* Feature Highlights */}
        <section className="dashboard-features">
          <h2 className="features-heading">Why Choose Trip Optimizer?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">🎯</div>
              <h3 className="feature-title">Personalized AI Scoring</h3>
              <p className="feature-desc">
                Our algorithm calculates multi-factor compatibility scores based
                on your travel style, activities, budget, and best season match.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">🗓️</div>
              <h3 className="feature-title">Day-by-Day Schedules</h3>
              <p className="feature-desc">
                Receive structured, balanced daily itineraries with estimated
                hours, activity categories, and expected entry/experience costs.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">💰</div>
              <h3 className="feature-title">Budget Optimization</h3>
              <p className="feature-desc">
                Keep your travel expenses on track with automatic daily cost
                estimates and total trip cost breakdowns.
              </p>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="dashboard-steps">
          <h2 className="steps-heading">How It Works in 3 Easy Steps</h2>
          <div className="steps-row">
            <div className="step-item">
              <div className="step-number">1</div>
              <h3 className="step-title">Set Preferences</h3>
              <p className="step-text">
                Enter your total budget, trip duration, travel style, and favorite activities.
              </p>
            </div>

            <div className="step-item">
              <div className="step-number">2</div>
              <h3 className="step-title">Explore Matches</h3>
              <p className="step-text">
                View ranked destination recommendations with detailed match reasoning and star ratings.
              </p>
            </div>

            <div className="step-item">
              <div className="step-number">3</div>
              <h3 className="step-title">Get Itinerary</h3>
              <p className="step-text">
                Select your preferred destination to instantly receive a day-by-day customized schedule.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;