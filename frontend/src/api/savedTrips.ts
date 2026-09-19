import { apiClient } from "./client";
import type { SavedTripSummary, SavedTripDetail, SaveTripPayload } from "./types";

export async function getSavedTrips(signal?: AbortSignal): Promise<SavedTripSummary[]> {
  const response = await apiClient.get<SavedTripSummary[]>("/api/saved-trips", { signal });
  return response.data;
}

export async function getSavedTrip(tripId: number | string, signal?: AbortSignal): Promise<SavedTripDetail> {
  const response = await apiClient.get<SavedTripDetail>(`/api/saved-trips/${tripId}`, { signal });
  return response.data;
}

export async function saveTrip(payload: SaveTripPayload): Promise<SavedTripSummary> {
  const response = await apiClient.post<SavedTripSummary>("/api/saved-trips", payload);
  return response.data;
}

export async function deleteSavedTrip(tripId: number | string): Promise<void> {
  await apiClient.delete(`/api/saved-trips/${tripId}`);
}
