import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

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
  const response = await api.get(
    `/backhaul/decision/${truckId}`
  );

  return response.data;
};

export const getLatestTruckLocation = async (truckId) => {
  const response = await api.get(
    `/locations/truck/${truckId}/latest`
  );

  return response.data;
};

export const getAssignments = async () => {
  const response = await api.get("/assignments/");
  return response.data;
};


export const getBaselineVsAI = async (truckId) => {
  const response = await api.get(
    `/backhaul/baseline-vs-ai/${truckId}`
  );

  return response.data;
};

export default api;