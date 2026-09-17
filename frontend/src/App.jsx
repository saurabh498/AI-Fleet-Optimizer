import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Trucks from "./pages/Trucks";
import Shipments from "./pages/Shipments";
import AIRecommendations from "./pages/AIRecommendations";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
import Navbar from "./components/Navbar";

import "./App.css";

function ProtectedRoute({ children }) {
  const isLoggedIn =
    localStorage.getItem(
      "fleet_optimizer_logged_in"
    ) === "true";

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <>
                <Navbar />

                <Routes>
                  <Route
                    path="/"
                    element={<Dashboard />}
                  />

                  <Route
                    path="/trucks"
                    element={<Trucks />}
                  />

                  <Route
                    path="/shipments"
                    element={<Shipments />}
                  />

                  <Route
                    path="/ai-recommendations"
                    element={
                      <AIRecommendations />
                    }
                  />

                  <Route
                    path="/analytics"
                    element={<Analytics />}
                  />

                  <Route
                    path="*"
                    element={
                      <Navigate
                        to="/"
                        replace
                      />
                    }
                  />
                </Routes>
              </>
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;