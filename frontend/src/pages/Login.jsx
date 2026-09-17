import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();

    setError("");

    if (!username.trim() || !password) {
      setError("Please enter username and password.");
      return;
    }

    setLoading(true);

    setTimeout(() => {
      if (
        username.trim() === "admin" &&
        password === "admin123"
      ) {
        localStorage.setItem(
          "fleet_optimizer_logged_in",
          "true"
        );

        navigate("/", { replace: true });
      } else {
        setError("Invalid username or password.");
      }

      setLoading(false);
    }, 500);
  };

  return (
    <div className="login-page">

      <div className="login-card">

        <div className="login-brand">
          <div className="login-logo">
            🚛
          </div>

          <p className="dashboard-label">
            AI FLEET OPTIMIZER
          </p>

          <h1>Welcome Back</h1>

          <p className="login-subtitle">
            Sign in to access the fleet management
            dashboard.
          </p>
        </div>

        <form
          className="login-form"
          onSubmit={handleSubmit}
        >

          <div className="form-group">
            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Enter username"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter password"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="login-error">
              ⚠ {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

        </form>

        <div className="login-footer">
          Fleet Management • AI Decision Support
        </div>

      </div>

    </div>
  );
}

export default Login;