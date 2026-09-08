import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Trucks from "./pages/Trucks";
import Navbar from "./components/Navbar";
import Shipments from "./pages/Shipments";
import AIRecommendations from "./pages/AIRecommendations";
import Analytics from "./pages/Analytics";

import "./App.css";

function App() {
  return (
    <BrowserRouter>

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
          element={<AIRecommendations />}
        />

        <Route
          path="/analytics"
          element={<Analytics />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;