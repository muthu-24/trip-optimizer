import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./TripPreferences.css";

type Recommendation = {
  destination: string;
  country: string;
  score: number;
  average_daily_cost: number;
  estimated_trip_cost: number;
  best_season: string;
  activities: string;
  rating: number;
  reasons: string[];
};

function TripPreferences() {
  const navigate = useNavigate();

  const [budget, setBudget] = useState("");
  const [tripDuration, setTripDuration] = useState("");
  const [travelStyle, setTravelStyle] = useState("");
  const [season, setSeason] = useState("");
  const [activities, setActivities] = useState<string[]>([]);

  const [recommendations, setRecommendations] = useState<
    Recommendation[]
  >([]);

  const [selectedDestination, setSelectedDestination] = useState<
    string | null
  >(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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

      setRecommendations(response.data.recommendations);
      setSelectedDestination(null);
    } catch (error) {
      console.error("Failed to get recommendations:", error);
    }
  };

  const handleSelectDestination = async (destination: string) => {
    try {
      setSelectedDestination(destination);

      const destinationIdMap: Record<string, number> = {
        Ella: 1,
        Galle: 2,
        Mirissa: 3,
        Sigiriya: 4,
        "Nuwara Eliya": 5,
        Kandy: 6,
        "Arugam Bay": 7,
        Yala: 8,
        Hikkaduwa: 9,
        Knuckles: 10,
      };

      const destinationId = destinationIdMap[destination];

      if (!destinationId) {
        console.error("Destination ID not found:", destination);
        return;
      }

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
          destination,
          tripDuration: Number(tripDuration),
          itinerary: response.data.itinerary,
        },
      });
    } catch (error) {
      console.error("Failed to generate trip plan:", error);
    }
  };

  return (
    <div className="preferences-page">
      <h1>Plan Your Trip</h1>

      <p>Tell us what kind of trip you want.</p>

      <form onSubmit={handleSubmit}>
        <label>
          Budget

          <input
            type="number"
            min="1"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            placeholder="e.g. 50000"
            required
          />
        </label>

        <label>
          Trip Duration

          <input
            type="number"
            min="1"
            value={tripDuration}
            onChange={(e) => setTripDuration(e.target.value)}
            placeholder="Number of days"
            required
          />
        </label>

        <label>
          Travel Style

          <select
            value={travelStyle}
            onChange={(e) => setTravelStyle(e.target.value)}
            required
          >
            <option value="">Select a style</option>
            <option value="adventure">Adventure</option>
            <option value="beach">Beach</option>
            <option value="culture">Culture</option>
            <option value="nature">Nature</option>
            <option value="relaxation">Relaxation</option>
          </select>
        </label>

        <div>
          <p>Preferred Activities</p>

          {availableActivities.map((activity) => (
            <label key={activity}>
              <input
                type="checkbox"
                checked={activities.includes(activity)}
                onChange={() => handleActivityChange(activity)}
              />

              {activity}
            </label>
          ))}
        </div>

        <label>
          Season

          <select
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            required
          >
            <option value="">Select a season</option>
            <option value="January-April">January-April</option>
            <option value="May-September">May-September</option>
            <option value="October-December">
              October-December
            </option>
          </select>
        </label>

        <button type="submit">
          Find My Best Destinations
        </button>
      </form>

      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>Your Recommended Destinations</h2>

          {recommendations.map((recommendation, index) => (
            <div
              className="recommendation-card"
              key={recommendation.destination}
            >
              <div className="recommendation-header">
                <h3>{recommendation.destination}</h3>

                <span className="rank">
                  #{index + 1}
                </span>
              </div>

              <p className="country">
                {recommendation.country}
              </p>

              <div className="score-row">
                <span>Match Score</span>

                <span>
                  {recommendation.score}%
                </span>
              </div>

              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{
                    width: `${recommendation.score}%`,
                  }}
                />
              </div>

              <div className="destination-details">
                <p>
                  💰 Estimated Cost:{" "}
                  <strong>
                    Rs.{" "}
                    {recommendation.estimated_trip_cost.toLocaleString()}
                  </strong>
                </p>

                <p>
                  ⭐ Rating:{" "}
                  <strong>
                    {recommendation.rating}/5
                  </strong>
                </p>

                <p>
                  🌤️ Best Season:{" "}
                  <strong>
                    {recommendation.best_season}
                  </strong>
                </p>

                <p>
                  🏄 Activities:{" "}
                  <strong>
                    {recommendation.activities}
                  </strong>
                </p>
              </div>

              <div className="recommendation-reasons">
                <h4>Why this destination?</h4>

                <ul>
                  {recommendation.reasons.map(
                    (reason, reasonIndex) => (
                      <li key={reasonIndex}>
                        ✓ {reason}
                      </li>
                    )
                  )}
                </ul>
              </div>

              <button
                type="button"
                onClick={() =>
                  handleSelectDestination(
                    recommendation.destination
                  )
                }
              >
                Select This Destination
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedDestination && (
        <div className="selected-trip">
          <h2>Your Selected Trip</h2>

          <p>
            You selected{" "}
            <strong>{selectedDestination}</strong>
          </p>
        </div>
      )}
    </div>
  );
}

export default TripPreferences;

