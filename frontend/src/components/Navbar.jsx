import { NavLink, useNavigate } from "react-router-dom";

const navigation = [
  { to: "/", label: "Dashboard", icon: "⌂" },
  { to: "/trucks", label: "Fleet", icon: "▣" },
  { to: "/shipments", label: "Shipments", icon: "□" },
  { to: "/ai-recommendations", label: "AI Intelligence", icon: "✦" },
  { to: "/analytics", label: "Analytics", icon: "◫" },
];

function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("fleet_optimizer_logged_in");
    navigate("/login", { replace: true });
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-brand-copy">
          <strong>AI Fleet</strong>
          <span>OPTIMIZER</span>
        </span>
      </div>

      <div className="navbar-section-label">Operations</div>

      <div className="navbar-links">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
          >
            <span className="nav-link-icon" aria-hidden="true">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>

      <div className="navbar-system-card">
        <span className="navbar-system-dot" />
        <div>
          <strong>System Online</strong>
          <span>Decision engine ready</span>
        </div>
      </div>

      <button className="logout-button" onClick={handleLogout}>
        <span aria-hidden="true">↪</span>
        Logout
      </button>
    </nav>
  );
}

export default Navbar;
