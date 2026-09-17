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
              <label htmlFor="username">Username</label>
              <div className="login-input-wrap">
                <span aria-hidden="true">◎</span>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="Enter username"
                  autoComplete="username"
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

          <div className="login-demo-note">
            <span className="login-demo-dot" />
            <span>Demo environment · Fleet management access</span>
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
