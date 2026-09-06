import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Trip Optimizer</h1>
      <h2>Dashboard</h2>

      <p>Welcome to your personalized trip planning dashboard.</p>

      <button onClick={() => navigate("/plan-trip")}>
        Plan a Trip
      </button>
    </div>
  );
}

export default Dashboard;