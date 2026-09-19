import axios from "axios";

import {
  getAccessToken,
  getRefreshToken,
  saveAuth,
  clearAuth,
} from "./auth";


const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});


// -------------------------------------------------
// Request interceptor: attach Bearer token
// -------------------------------------------------

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


// -------------------------------------------------
// Response interceptor: refresh on 401 once
// -------------------------------------------------

let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    const isAuthEndpoint =
      original?.url?.includes("/auth/login") ||
      original?.url?.includes("/auth/refresh");

    if (
      error.response?.status !== 401 ||
      original?._retry ||
      isAuthEndpoint
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearAuth();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    // De-dupe concurrent refreshes
    if (!refreshPromise) {
      refreshPromise = axios
        .post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        .then((resp) => {
          saveAuth(resp.data);
          return resp.data.access_token;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    try {
      const newToken = await refreshPromise;
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (refreshError) {
      clearAuth();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    }
  }
);


// -------------------------------------------------
// Auth endpoints
// -------------------------------------------------

export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
};

export const registerUser = async (payload) => {
  const response = await api.post("/auth/register", payload);
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};


// -------------------------------------------------
// Fleet endpoints (unchanged signatures)
// -------------------------------------------------

export const getTrucks = async () => {
  const response = await api.get("/trucks/");
  return response.data;
};

export const createTruck = async (truckData) => {
  const response = await api.post("/trucks/", truckData);
  return response.data;
};

export const getShipments = async () => {
  const response = await api.get("/shipments/");
  return response.data;
};

export const createShipment = async (shipmentData) => {
  const response = await api.post("/shipments/", shipmentData);
  return response.data;
};

export const getTruckDecision = async (truckId) => {
  const response = await api.get(`/backhaul/decision/${truckId}`);
  return response.data;
};

export const getLatestTruckLocation = async (truckId) => {
  const response = await api.get(`/locations/truck/${truckId}/latest`);
  return response.data;
};

export const getAssignments = async () => {
  const response = await api.get("/assignments/");
  return response.data;
};

export const getBaselineVsAI = async (truckId) => {
  const response = await api.get(`/backhaul/baseline-vs-ai/${truckId}`);
  return response.data;
};

export const getBackhaulMatches = async (truckId) => {
  const response = await api.get(`/backhaul/match/${truckId}`);
  return response.data;
};

export default api;
