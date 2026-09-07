import { Link, useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const isDashboardActive =
    location.pathname === "/dashboard" || location.pathname === "/";
  const isPlanActive =
    location.pathname === "/plan-trip" ||
    location.pathname === "/trip-preferences" ||
    location.pathname.startsWith("/destinations");
  const isItineraryActive = location.pathname === "/trip-plan";

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          <span className="navbar-logo-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
            </svg>
          </span>
          <div className="navbar-brand-text">
            <span className="navbar-title">Trip Optimizer</span>
            <span className="navbar-tagline">AI Travel Planner</span>
          </div>
        </Link>

        <nav className="navbar-nav">
          <Link
            to="/dashboard"
            className={`navbar-link ${isDashboardActive ? "active" : ""}`}
          >
            Home
          </Link>

          <Link
            to="/plan-trip"
            className={`navbar-link ${isPlanActive ? "active" : ""}`}
          >
            Plan Trip
          </Link>

          <Link
            to="/trip-plan"
            className={`navbar-link ${isItineraryActive ? "active" : ""}`}
          >
            Itinerary
          </Link>

          <button
            type="button"
            className="navbar-logout-btn"
            onClick={handleLogout}
            title="Sign out of your account"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Logout</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
