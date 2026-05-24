// Types matching the FastAPI response shapes.
// Keep in sync with api/routers/plan.py and api/routers/profile.py.

export interface Travelers {
  adults: number;
  kids: number;
  kids_ages: number[];
}

export interface Wallet {
  amex_mr: number;
  marriott_free_nights: number;
  bonvoy_points: number;
}

export interface Profile {
  name: string;
  origin: string;
  travelers: Travelers;
  wallet: Wallet;
  _saved_at?: string;
}

export interface PlanRequest {
  origin: string;
  travelers: Travelers;
  points: Wallet;
  required_cities: string[];
  optional_cities: string[];
  trip_style: string;
  year: number;
  min_days: number;
  max_days: number;
}

export interface AwardAvailability {
  source: string; // "seats.aero" | "estimated"
  available: boolean;
  seat_count: number;
  lowest_points: number | null;
  program: string;
  route: string;
  error: string | null;
}

// Python tuples become JSON arrays: stops is [[city, nights], ...]
export type Stop = [string, number];

export interface Itinerary {
  name: string;
  stops: Stop[];
  score: number;
  total_cash: number;
  moves: number;
  pace: string;
  award_likelihood: "High" | "Medium" | "Low";
  dates: { label: string };
  date_reason: string;
  nights: number;
  pros: string[];
  cons: string[];
  award_availability: AwardAvailability;
  award_availability_return: AwardAvailability;
}

export interface PlanResponse {
  ranked: Itinerary[];
  web_context: Record<string, unknown>;
  log: string;
}
