import { apiClient } from "./client";
import type { RecommendationRequest, RecommendationsResponse } from "./types";

export async function getRecommendations(params: RecommendationRequest): Promise<RecommendationsResponse> {
  const payload = {
    ...params,
    budget: params.budget ?? params.budget_per_person,
  };
  const response = await apiClient.post<RecommendationsResponse>("/api/recommendations/", payload);
  return response.data;
}
