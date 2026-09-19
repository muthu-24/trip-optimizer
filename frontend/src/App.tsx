import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import TripPreferences from "./pages/TripPreferences";
import TripPlan from "./pages/TripPlan";
import DestinationDetail from "./pages/DestinationDetail";
import SavedTrips from "./pages/SavedTrips";
import SavedTripDetail from "./pages/SavedTripDetail";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/plan-trip"
          element={
            <ProtectedRoute>
              <TripPreferences />
            </ProtectedRoute>
          }
        />

        <Route
          path="/trip-preferences"
          element={
            <ProtectedRoute>
              <TripPreferences />
            </ProtectedRoute>
          }
        />

        <Route
          path="/trip-plan"
          element={
            <ProtectedRoute>
              <TripPlan />
            </ProtectedRoute>
          }
        />

        <Route
          path="/destinations/:id"
          element={
            <ProtectedRoute>
              <DestinationDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/my-trips"
          element={
            <ProtectedRoute>
              <SavedTrips />
            </ProtectedRoute>
          }
        />

        <Route
          path="/my-trips/:id"
          element={
            <ProtectedRoute>
              <SavedTripDetail />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;