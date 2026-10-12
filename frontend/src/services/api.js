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


api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = "Bearer " + token;
  }
  return config;
});


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

    if (!refreshPromise) {
      refreshPromise = axios
        .post(BASE_URL + "/auth/refresh", {
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
      original.headers.Authorization = "Bearer " + newToken;
      return api(original);
    } catch (refreshError) {
      clearAuth();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    }
  }
);


// -------------------------------------------------
// Auth
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
// Trucks
// -------------------------------------------------

export const getTrucks = async () => {
  const response = await api.get("/trucks/");
  return response.data;
};

export const createTruck = async (truckData) => {
  const response = await api.post("/trucks/", truckData);
  return response.data;
};

export const updateTruck = async (truckId, truckData) => {
  const response = await api.put("/trucks/" + truckId, truckData);
  return response.data;
};

export const deleteTruck = async (truckId) => {
  const response = await api.delete("/trucks/" + truckId);
  return response.data;
};


// -------------------------------------------------
// Shipments
// -------------------------------------------------

export const getShipments = async () => {
  const response = await api.get("/shipments/");
  return response.data;
};

export const createShipment = async (shipmentData) => {
  const response = await api.post("/shipments/", shipmentData);
  return response.data;
};

export const updateShipment = async (loadId, shipmentData) => {
  const response = await api.put("/shipments/" + loadId, shipmentData);
  return response.data;
};

export const deleteShipment = async (loadId) => {
  const response = await api.delete("/shipments/" + loadId);
  return response.data;
};


// -------------------------------------------------
// Assignments
// -------------------------------------------------

export const getAssignments = async () => {
  const response = await api.get("/assignments/");
  return response.data;
};


// -------------------------------------------------
// Locations
// -------------------------------------------------

export const getLatestTruckLocation = async (truckId) => {
  const response = await api.get("/locations/truck/" + truckId + "/latest");
  return response.data;
};


// -------------------------------------------------
// Backhaul / decisions
// -------------------------------------------------

export const getTruckDecision = async (truckId) => {
  const response = await api.get("/backhaul/decision/" + truckId);
  return response.data;
};

export const getBaselineVsAI = async (truckId) => {
  const response = await api.get("/backhaul/baseline-vs-ai/" + truckId);
  return response.data;
};

export const getBackhaulMatches = async (truckId) => {
  const response = await api.get("/backhaul/match/" + truckId);
  return response.data;
};


// -------------------------------------------------
// Simulator
// -------------------------------------------------

export const runSimulator = async () => {
  const response = await api.post("/simulator/run");
  return response.data;
};

export const getSimulatorStatus = async () => {
  const response = await api.get("/simulator/status");
  return response.data;
};


// -------------------------------------------------
// Drivers
// -------------------------------------------------

export const getDrivers = async () => {
  const response = await api.get("/drivers/");
  return response.data;
};

export const createDriver = async (driverData) => {
  const response = await api.post("/drivers/", driverData);
  return response.data;
};

export const updateDriver = async (driverId, driverData) => {
  const response = await api.put("/drivers/" + driverId, driverData);
  return response.data;
};

export const deleteDriver = async (driverId) => {
  const response = await api.delete("/drivers/" + driverId);
  return response.data;
};

export const assignDriverToTruck = async (driverId, truckId) => {
  const response = await api.put(
    "/drivers/" + driverId + "/assign-truck",
    { truck_id: truckId }
  );
  return response.data;
};

export const unassignDriverFromTruck = async (driverId) => {
  const response = await api.delete(
    "/drivers/" + driverId + "/assign-truck"
  );
  return response.data;
};

export const markRestTaken = async (driverId) => {
  const response = await api.post("/drivers/" + driverId + "/rest-taken");
  return response.data;
};


// -------------------------------------------------
// Rest Facilities
// -------------------------------------------------

export const getRestFacilities = async () => {
  const response = await api.get("/rest-facilities/");
  return response.data;
};

export const createRestFacility = async (payload) => {
  const response = await api.post("/rest-facilities/", payload);
  return response.data;
};

export const importRestFacilitiesCsv = async (filename) => {
  const response = await api.post(
    "/rest-facilities/import-csv",
    { filename }
  );
  return response.data;
};

export const deleteRestFacility = async (facilityId) => {
  const response = await api.delete("/rest-facilities/" + facilityId);
  return response.data;
};


export default api;
