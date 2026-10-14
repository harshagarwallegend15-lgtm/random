import axios, { AxiosInstance } from "axios";

const baseURL = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export const api: AxiosInstance = axios.create({ baseURL });

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg = err?.response?.data?.detail || err?.message || "Request failed";
    console.error("[api]", msg);
    return Promise.reject(new Error(msg));
  }
);
