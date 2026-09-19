export type User = {
  user_id: string;
  name: string;
  email: string;
};

export type LoginCredentials = {
  email: string;
  password: string;
};

export type RegisterData = {
  name: string;
  email: string;
  password: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
};

export type ScoreBreakdown = {
  budget_match: number;
  activity_match: number;
  season_match: number;
  travel_style_match: number;
  rating_match?: number;
  overall_score: number;
};

export type CostBreakdown = {
  accommodation?: number;
  food?: number;
  transportation?: number;
  daily_average?: number;
  estimated_trip_cost?: number;
  daily_accommodation?: number;
  daily_food?: number;
  daily_transportation?: number;
  daily_total?: number;
  daily_total_group?: number;
  trip_accommodation?: number;
  trip_food?: number;
  trip_transportation?: number;
  trip_activities?: number;
  estimated_trip_total?: number;
  num_travelers?: number;
  cost_per_person?: number;
};

export type DestinationData = {
  id: number;
  name: string;
  country: string;
  region: string;
  category: string;
  budget_level: string;
  description: string;
  average_daily_cost: number;
  best_season: string;
  activities: string;
  rating: number;
  recommended_duration: number;
  accommodation_cost?: number;
  food_cost?: number;
  transport_cost?: number;
};

export type Recommendation = {
  id?: number;
  destination: string;
  country: string;
  region?: string;
  category?: string;
  budget_level?: string;
  score: number;
  score_breakdown?: ScoreBreakdown;
  cost_breakdown?: CostBreakdown;
  description?: string;
  average_daily_cost: number;
  estimated_trip_cost: number;
  estimated_trip_cost_per_person?: number;
  best_season: string;
  activities: string;
  rating: number;
  recommended_duration?: number;
  reasons: string[];
};

export type RecommendationRequest = {
  num_travelers: number;
  budget_per_person: number;
  budget?: number;
  trip_duration: number;
  travel_style: string;
  preferred_activities: string[];
  season: string;
};

export type RecommendationsResponse = {
  total: number;
  recommendations: Recommendation[];
};

export type Activity = {
  id: number;
  name: string;
  category: string;
  estimated_cost: number;
  duration: number;
  rating: number;
  score: number;
  latitude?: number;
  longitude?: number;
  distance_to_next?: number;
};

export type DayPlan = {
  day: number;
  activities: Activity[];
  total_duration: number;
  total_cost: number;
  total_distance?: number;
};

export type TripPlanResponse = {
  destination: string;
  requested_trip_duration?: number;
  actual_trip_duration?: number;
  trip_duration: number;
  budget: number;
  insufficient_activities?: boolean;
  itinerary_notice?: string | null;
  itinerary: DayPlan[];
  cost_breakdown?: CostBreakdown;
};

export type PlanTripParams = {
  budget: number;
  budget_per_person?: number;
  num_travelers: number;
  travel_style: string;
  trip_duration: number;
};

export type SavedTripSummary = {
  id: number;
  destination_name: string;
  trip_duration: number;
  budget: number;
  num_travelers?: number;
  travel_style: string | null;
  season: string | null;
  total_route_distance: number | null;
  created_at: string;
};

export type Preferences = {
  budget?: string;
  budgetPerPerson?: string;
  numTravelers?: number | string;
  totalGroupBudget?: number;
  tripDuration?: string;
  travelStyle?: string;
  season?: string;
  activities?: string[];
};

export type ItineraryData = {
  itinerary: DayPlan[];
  cost_breakdown?: CostBreakdown;
  preferences?: Preferences;
  num_travelers?: number;
  budget_per_person?: number;
  total_group_budget?: number;
  destination_name?: string;
  destination_details?: unknown;
  itinerary_notice?: string | null;
  requested_trip_duration?: number;
  actual_trip_duration?: number;
  insufficient_activities?: boolean;
};

export type SavedTripDetail = {
  id: number;
  destination_name: string;
  trip_duration: number;
  budget: number;
  num_travelers?: number;
  travel_style: string | null;
  season: string | null;
  total_route_distance: number | null;
  itinerary_data: ItineraryData;
  created_at: string;
};

export type SaveTripPayload = {
  destination_name: string;
  trip_duration: number;
  budget: number;
  num_travelers: number;
  travel_style: string | null;
  season: string | null;
  total_route_distance: number | null;
  itinerary_data: ItineraryData;
};
