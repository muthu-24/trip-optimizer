import { Link, useLocation } from "react-router-dom";

type Activity = {
  id: number;
  name: string;
  category: string;
  estimated_cost: number;
  duration: number;
  rating: number;
  score: number;
};

type DayPlan = {
  day: number;
  activities: Activity[];
  total_duration: number;
  total_cost: number;
};

function TripPlan() {
  const location = useLocation();

  const { destination, tripDuration, itinerary } = location.state || {};

  if (!itinerary) {
    return (
      <div>
        <h1>No Trip Plan Found</h1>
        <p>Please create a trip plan first.</p>

        <Link to="/plan-trip">
          <button>Plan a Trip</button>
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Your Trip Plan</h1>

      <h2>{destination}</h2>

      <p>
        Trip Duration: {tripDuration} days
      </p>

      {itinerary.map((dayPlan: DayPlan) => (
        <div key={dayPlan.day}>
          <h2>Day {dayPlan.day}</h2>

          {dayPlan.activities.length === 0 ? (
            <p>No activities planned for this day.</p>
          ) : (
            dayPlan.activities.map((activity) => (
              <div key={activity.id}>
                <h3>{activity.name}</h3>

                <p>Category: {activity.category}</p>
                <p>Duration: {activity.duration} hours</p>
                <p>Estimated Cost: Rs. {activity.estimated_cost}</p>
                <p>Rating: {activity.rating}</p>
                <p>Personalized Score: {activity.score}</p>
              </div>
            ))
          )}

          <p>
            <strong>Total Duration:</strong>{" "}
            {dayPlan.total_duration} hours
          </p>

          <p>
            <strong>Total Cost:</strong>{" "}
            Rs. {dayPlan.total_cost}
          </p>

          <hr />
        </div>
      ))}

      <Link to="/plan-trip">
        <button>Plan Another Trip</button>
      </Link>
    </div>
  );
}

export default TripPlan;