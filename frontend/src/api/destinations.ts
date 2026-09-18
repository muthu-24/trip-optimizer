import { apiClient } from "./client";
import type { DestinationData } from "./types";

export async function getDestination(id: number | string): Promise<DestinationData> {
  const response = await apiClient.get<DestinationData>(`/api/destinations/${id}`);
  return response.data;
}
