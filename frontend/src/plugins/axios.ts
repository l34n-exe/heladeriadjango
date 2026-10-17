import axios from "axios";
import { useAuthStore } from "../stores/auth";

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/heladerias"
).replace(/\/+$/, "");

export function getApiErrorMessage(error: any): string {
  const payload = error?.response?.data;

  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  if (payload && typeof payload === "object") {
    const candidates = [
      payload.detail,
      payload.message,
      payload.error,
      payload.non_field_errors,
      payload.errors,
    ];

    for (const candidate of candidates) {
      if (Array.isArray(candidate) && candidate.length) {
        return String(candidate[0]);
      }

      if (typeof candidate === "string" && candidate.trim()) {
        return candidate;
      }
    }
  }

  if (error?.message) {
    return error.message;
  }

  return "No se pudo completar la solicitud.";
}

export function redirectToHomeIfNeeded() {
  if (typeof window !== "undefined" && window.location.pathname !== "/") {
    window.location.href = "/";
  }
}

export const instance = axios.create({
  baseURL: `${API_BASE_URL}/`,
  timeout: 10000,
});

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("heladeria_access_token");

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const auth = useAuthStore();

    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      auth.refreshToken
    ) {
      originalRequest._retry = true;

      try {
        const response = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          {
            refresh: auth.refreshToken,
          },
        );

        const nextAccessToken = response.data?.access;
        if (!nextAccessToken) {
          throw new Error("No se recibió el token renovado.");
        }

        auth.setToken(nextAccessToken);
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;

        return instance(originalRequest);
      } catch (refreshError) {
        auth.logout();
        redirectToHomeIfNeeded();
        return Promise.reject(refreshError);
      }
    }

    if (error.response?.status === 401) {
      auth.logout();
      redirectToHomeIfNeeded();
    }

    return Promise.reject(error);
  },
);
