import { apiClient } from "./client";
import type { PlanTripParams, TripPlanResponse } from "./types";

export async function generateTripItinerary(
  destinationId: number,
  preferredActivities: string[],
  params: PlanTripParams
): Promise<TripPlanResponse> {
  const queryParams = {
    budget: params.budget,
    budget_per_person: params.budget_per_person ?? params.budget,
    num_travelers: params.num_travelers,
    travel_style: params.travel_style,
    trip_duration: params.trip_duration,
  };

  const response = await apiClient.post<TripPlanResponse>(
    `/api/trips/activities/${destinationId}`,
    preferredActivities,
    {
      params: queryParams,
    }
  );
  return response.data;
}
