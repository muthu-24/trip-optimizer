import { apiClient, setToken, removeToken } from "./client";
import type { LoginCredentials, RegisterData, AuthResponse, User } from "./types";

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>("/api/auth/login", credentials);
  if (response.data?.access_token) {
    setToken(response.data.access_token);
  }
  return response.data;
}

export async function register(data: RegisterData): Promise<User> {
  const response = await apiClient.post<User>("/api/auth/register", data);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>("/api/auth/me");
  return response.data;
}

export function logout(): void {
  removeToken();
}
