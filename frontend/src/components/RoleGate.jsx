import { useRole } from "../hooks/useRole";


/**
 * Conditionally render children based on user role.
 *
 * Usage:
 *   <RoleGate allow={["admin", "manager"]}>
 *     <button>+ Add Truck</button>
 *   </RoleGate>
 *
 *   <RoleGate allow={["admin"]} fallback={<p>Read-only</p>}>
 *     <AdminPanel />
 *   </RoleGate>
 */
function RoleGate({ allow, children, fallback = null }) {
  const { role } = useRole();

  if (!allow || allow.includes(role)) {
    return children;
  }

  return fallback;
}


export default RoleGate;
