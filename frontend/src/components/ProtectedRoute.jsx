import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Checking session...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}


export default ProtectedRoute;
