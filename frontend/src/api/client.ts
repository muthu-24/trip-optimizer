import axios, { type AxiosError } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// Request Interceptor: Attach JWT Bearer token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Optional centralized response/error hook
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Helper for extracting clean user-friendly error messages from API responses
export function getErrorMessage(error: unknown, defaultMessage = "An unexpected error occurred. Please try again."): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ detail?: string | Array<{ msg: string }> }>;
    if (!axiosErr.response) {
      return "Unable to connect to the server. Please verify the backend is running and try again.";
    }
    const data = axiosErr.response.data;
    if (data && typeof data === "object") {
      if (typeof data.detail === "string") {
        return data.detail;
      }
      if (Array.isArray(data.detail) && data.detail.length > 0) {
        return data.detail.map((item) => item.msg || JSON.stringify(item)).join(", ");
      }
    }
    if (axiosErr.response.status === 401) {
      return "Session expired or unauthorized. Please sign in again.";
    }
    if (axiosErr.response.status === 403) {
      return "You do not have permission to perform this action.";
    }
    if (axiosErr.response.status === 404) {
      return "The requested resource was not found.";
    }
    if (axiosErr.response.status >= 500) {
      return "Server error occurred. Please try again shortly.";
    }
  } else if (error instanceof Error) {
    return error.message;
  }
  return defaultMessage;
}
