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

export const getShipments = async () => {
  const response = await api.get("/shipments/");
  return response.data;
};

export default api;