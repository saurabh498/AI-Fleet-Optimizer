import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


const ALL_NAV = [
  { to: "/", label: "Dashboard", icon: "⌂", roles: ["admin", "manager", "driver"] },
  { to: "/trucks", label: "Fleet", icon: "▣", roles: ["admin", "manager", "driver"] },
  { to: "/shipments", label: "Shipments", icon: "□", roles: ["admin", "manager", "driver"] },
  { to: "/ai-recommendations", label: "AI Intelligence", icon: "✦", roles: ["admin", "manager", "driver"] },
  { to: "/analytics", label: "Analytics", icon: "◫", roles: ["admin", "manager"] },
];


function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const role = user?.role || "driver";

  const navigation = ALL_NAV.filter((item) =>
    item.roles.includes(role)
  );

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const roleLabel = role.charAt(0).toUpperCase() + role.slice(1);

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((s) => s[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "?";

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
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <span className="nav-link-icon" aria-hidden="true">
              {item.icon}
            </span>
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

      {user && (
        <div className="navbar-user" title={user.email}>
          <div className="navbar-user-avatar">{initials}</div>
          <div className="navbar-user-info">
            <strong>{user.full_name}</strong>
            <span>{roleLabel}</span>
          </div>
        </div>
      )}

      <button className="logout-button" onClick={handleLogout}>
        <span aria-hidden="true">↪</span>
        Logout
      </button>
    </nav>
  );
}

export default Navbar;
