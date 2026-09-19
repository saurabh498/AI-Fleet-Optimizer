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
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

import "./App.css";

function AppShell({ children }) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppShell>
                  <Dashboard />
                </AppShell>
              </ProtectedRoute>
            }
          />

          <Route
            path="/trucks"
            element={
              <ProtectedRoute>
                <AppShell>
                  <Trucks />
                </AppShell>
              </ProtectedRoute>
            }
          />

          <Route
            path="/shipments"
            element={
              <ProtectedRoute>
                <AppShell>
                  <Shipments />
                </AppShell>
              </ProtectedRoute>
            }
          />

          <Route
            path="/ai-recommendations"
            element={
              <ProtectedRoute>
                <AppShell>
                  <AIRecommendations />
                </AppShell>
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AppShell>
                  <Analytics />
                </AppShell>
              </ProtectedRoute>
            }
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
