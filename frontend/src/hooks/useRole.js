import { useAuth } from "../context/AuthContext";


const WRITE_ROLES = ["manager", "admin"];


export function useRole() {
  const { user } = useAuth();
  const role = user?.role || "guest";

  return {
    role,
    isAdmin: role === "admin",
    isManager: role === "manager",
    isDriver: role === "driver",
    canWrite: WRITE_ROLES.includes(role),
    canManageUsers: role === "admin",
  };
}
