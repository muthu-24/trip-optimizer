import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import TripPreferences from "./pages/TripPreferences";
import TripPlan from "./pages/TripPlan";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/plan-trip" element={<TripPreferences />} />
        <Route path="/trip-plan" element={<TripPlan />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;