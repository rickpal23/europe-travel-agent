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
  all_programs: string[];
  dates_with_space: string[];
  cabin: string;
  route: string;
  error: string | null;
}

// Python tuples become JSON arrays: stops is [[city, nights], ...]
export type Stop = [string, number];

export interface DayEntry {
  day: number;
  city: string;
  note: string;
}

export interface DayPlanEntry {
  day: number;
  city: string;
  date_str: string;
  main: string;
  lighter: string;
  family: string;
  points_note: string | null;
}

export interface FlightPlan {
  outbound: string;
  return: string;
  amex_used: number;
  amex_short: number;
  flight_cash_overflow: number;
  intra_cash: number;
}

export interface HotelPlan {
  lines: string[];
  certs_used: number;
  points_used: number;
  cash_for_hotels: number;
  avg_sqft: number;
  smallest_sqft: number;
  all_fit_family: boolean;
  small_room_count: number;
}

export interface ResearchNotes {
  flight: string;
  hotel: string;
  strategy: string;
  confidence: string;
  has_warnings: boolean;
}

export interface Itinerary {
  name: string;
  stops: Stop[];
  score: number;
  total_cash: number;
  moves: number;
  pace: string;
  award_likelihood: "High" | "Medium" | "Low";
  dates: {
    depart: string;
    return: string;
    depart_day: string;
    is_deal_hunter: boolean;
    label: string;
  };
  date_reason: string;
  nights: number;
  pros: string[];
  cons: string[];
  transit: string[];
  days: DayEntry[];
  day_plan?: DayPlanEntry[];
  flight_plan?: FlightPlan;
  hotel_plan?: HotelPlan;
  research_notes?: ResearchNotes;
  family_comfort: number;
  breakdown: string[];
  award_availability: AwardAvailability;
  award_availability_return: AwardAvailability;
}

export interface PlanResponse {
  ranked: Itinerary[];
  web_context: Record<string, unknown>;
  log: string;
}
