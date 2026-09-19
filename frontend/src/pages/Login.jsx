import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const redirectTo = location.state?.from?.pathname || "/";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password) {
      setError("Please enter email and password.");
      return;
    }

    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        "Invalid email or password.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (role) => {
    const map = {
      admin: ["admin@fleetops.in", "admin123"],
      manager: ["manager@fleetops.in", "manager123"],
      driver: ["driver@fleetops.in", "driver123"],
    };
    const [e, p] = map[role] || ["", ""];
    setEmail(e);
    setPassword(p);
    setError("");
  };

  return (
    <div className="login-page login-control-center">
      <div className="login-ambient login-ambient-one" />
      <div className="login-ambient login-ambient-two" />

      <div className="login-shell">
        <section className="login-hero-panel">
          <div className="login-hero-brand">
            <div className="login-hero-mark">AF</div>
            <div>
              <strong>AI Fleet</strong>
              <span>OPTIMIZER</span>
            </div>
          </div>

          <div className="login-hero-content">
            <span className="login-eyebrow">INTELLIGENT LOGISTICS CONTROL</span>
            <h1>Turn every journey into a smarter decision.</h1>
            <p>
              Monitor fleet movement, discover backhaul opportunities and use
              AI-powered decision support to reduce empty kilometres.
            </p>
          </div>

          <div className="login-feature-grid">
            <div className="login-feature">
              <span className="login-feature-icon">◉</span>
              <div>
                <strong>Live Fleet</strong>
                <span>Location & status visibility</span>
              </div>
            </div>
            <div className="login-feature">
              <span className="login-feature-icon">✦</span>
              <div>
                <strong>AI Decisions</strong>
                <span>Backhaul & demand intelligence</span>
              </div>
            </div>
            <div className="login-feature">
              <span className="login-feature-icon">↗</span>
              <div>
                <strong>Optimization</strong>
                <span>Cost, profit & utilization</span>
              </div>
            </div>
          </div>
        </section>

        <section className="login-card login-modern-card">
          <div className="login-card-topline">
            <span className="login-secure-status">
              <span className="login-status-dot" />
              System Online
            </span>
            <span className="login-version">v0.1.0</span>
          </div>

          <div className="login-brand login-modern-brand">
            <div className="login-logo">🚛</div>
            <p className="dashboard-label">FLEET OPERATIONS</p>
            <h2>Welcome back</h2>
            <p className="login-subtitle">
              Sign in to continue to your AI fleet control center.
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <div className="login-input-wrap">
                <span aria-hidden="true">◎</span>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="login-input-wrap">
                <span aria-hidden="true">◆</span>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter password"
                  autoComplete="current-password"
                />
              </div>
            </div>

            {error && (
              <div className="login-error" role="alert">
                <span>⚠</span>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-button login-modern-button"
              disabled={loading}
            >
              <span>{loading ? "Signing in..." : "Sign in to control center"}</span>
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <div className="login-demo-creds">
            <p className="login-demo-label">Demo accounts</p>
            <div className="login-demo-buttons">
              <button
                type="button"
                onClick={() => fillDemo("admin")}
                className="demo-chip"
              >
                admin
              </button>
              <button
                type="button"
                onClick={() => fillDemo("manager")}
                className="demo-chip"
              >
                manager
              </button>
              <button
                type="button"
                onClick={() => fillDemo("driver")}
                className="demo-chip"
              >
                driver
              </button>
            </div>
          </div>

          <div className="login-footer">
            AI-based decision support & logistics optimization
          </div>
        </section>
      </div>
    </div>
  );
}

export default Login;
