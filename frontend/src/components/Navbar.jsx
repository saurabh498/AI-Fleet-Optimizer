import { NavLink } from "react-router-dom";

function Navbar() {
    return (
        <nav className="navbar">

            <div className="navbar-brand">
                🚛 AI Fleet Optimizer
            </div>

            <div className="navbar-links">

                <NavLink
                    to="/"
                    className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                    }
                >
                    🏠 Dashboard
                </NavLink>

                <NavLink
                    to="/trucks"
                    className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                    }
                >
                    🚛 Trucks
                </NavLink>

                <NavLink
                    to="/shipments"
                    className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                    }
                >
                    📦 Shipments
                </NavLink>

                <NavLink
                    to="/ai-recommendations"
                    className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                    }
                >
                    🤖 AI Recommendations
                </NavLink>

                <NavLink
                    to="/analytics"
                    className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                    }
                >
                    📊 Analytics
                </NavLink>

            </div>

        </nav>
    );
}

export default Navbar;