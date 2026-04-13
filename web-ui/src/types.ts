export interface Preferences {
  location_city: string;
  location_area?: string;
  max_budget?: number;
  cuisines: string[];
  min_rating: number;
  notes?: string;
}

export interface Recommendation {
  restaurant_name: string;
  cuisines: string[];
  rating: number | null;
  estimated_cost_for_two: number | null;
  location_city: string;
  location_area: string | null;
  explanation: string;
  rank: number;
}

