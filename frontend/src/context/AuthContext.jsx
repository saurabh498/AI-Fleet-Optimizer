import { createContext, useContext, useEffect, useState } from "react";

import {
  getStoredUser,
  isAuthenticated,
  clearAuth,
  saveAuth,
} from "../services/auth";
import {
  loginUser as apiLogin,
  fetchCurrentUser,
} from "../services/api";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    const validateSession = async () => {
      if (!isAuthenticated()) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const freshUser = await fetchCurrentUser();
        setUser(freshUser);
      } catch {
        clearAuth();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    validateSession();
  }, []);


  const login = async (email, password) => {
    const data = await apiLogin(email, password);
    saveAuth(data);
    setUser(data.user);
    return data.user;
  };


  const logout = () => {
    clearAuth();
    setUser(null);
  };


  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
}
