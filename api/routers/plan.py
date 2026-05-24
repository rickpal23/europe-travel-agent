"""
api/routers/plan.py — the main planning endpoint.

POST /api/plan
  Accepts a PlanRequest, runs the Python planning engine, and returns
  ranked itineraries as JSON.

  Takes 10–30 seconds depending on whether Seats.aero and Tavily keys
  are set. The client should show a loading state.

  ⚠️  Thread-safety note: the engine uses module-level globals
  (USER_PROFILE, TRAVEL_YEAR). This is fine for single-user local dev.
  For multi-user production, wrap in a threading.Lock or refactor the
  engine to accept profile as a pure argument with no globals.
"""

import contextlib
import io

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

import main as engine

router = APIRouter()


# ── Request schema ─────────────────────────────────────────────────────────────

class Travelers(BaseModel):
    adults:    int       = 2
    kids:      int       = 0
    kids_ages: list[int] = []


class Points(BaseModel):
    amex_mr:              int = 200_000
    marriott_free_nights: int = 5
    bonvoy_points:        int = 250_000


class PlanRequest(BaseModel):
    # Identity — comes from the saved profile
    origin:    str      = "SFO"
    travelers: Travelers = Field(default_factory=Travelers)
    points:    Points    = Field(default_factory=Points)

    # Trip intent — set per search
    required_cities: list[str] = ["London", "Paris"]
    optional_cities: list[str] = []
    trip_style:      str       = "balanced"   # relaxed | balanced | maximize

    # Duration
    year:     int = 2026
    min_days: int = 7
    max_days: int = 10


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_profile(body: PlanRequest) -> dict:
    """Translate the API request into the dict shape the engine expects."""
    n_kids    = body.travelers.kids
    kids_ages = list(body.travelers.kids_ages)
    # Engine expects at least 2 ages; pad with a sensible default.
    while len(kids_ages) < max(n_kids, 2):
        kids_ages.append(10)

    return {
        "origin":           body.origin,
        "travel_window":    "late July through early August",
        "trip_length_days": f"{body.min_days} to {body.max_days}",
        "travelers": {
            "adults":    body.travelers.adults,
            "kids":      n_kids,
            "kids_ages": kids_ages,
        },
        "trip_type":       "family" if n_kids > 0 else "couple",
        "required_cities": list(body.required_cities),
        "optional_cities": list(body.optional_cities),
        "avoid_cities":    [],
        "total_cities":    "2 or 3",
        "trip_style":      body.trip_style,
        "points": {
            "amex_mr":              body.points.amex_mr,
            "marriott_free_nights": body.points.marriott_free_nights,
            "bonvoy_points":        body.points.bonvoy_points,
        },
        "strategy": {
            "flight": "Use Amex Membership Rewards points with strong transfer partners",
            "hotel":  "Use Marriott free nights first, then Bonvoy points, then cash",
        },
        "preferences": {
            "optimize_for":             "best mix of quality, convenience, and value",
            "not_just_cheapest":        True,
            "family_friendly":          n_kids > 0,
            "fewer_hotel_changes":      True,
            "efficient_city_flow":      True,
            "preferred_departure_days": ["Friday", "Saturday", "Sunday"],
            "flexible_for_better_deal": True,
        },
        "hotel_requirements": {
            "rooms":                           1,
            "room_type_preference":            ["suite", "junior suite", "large room with sofa bed"],
            "prioritize_large_square_footage":  True,
            "family_of_4_comfort":             n_kids > 0,
            "avoid_small_rooms":               True,
        },
        "travel_style": {
            "pace":                            "moderate to relaxed",
            "avoid_rushed_itineraries":        True,
            "prefer_trains_over_short_flights": True,
        },
    }


# ── Endpoint ───────────────────────────────────────────────────────────────────

@router.post("/plan")
def run_plan(body: PlanRequest):
    """
    Run the travel planning engine.

    Returns:
      ranked      — list of itinerary dicts, best first.
                    Each itinerary has: name, score, total_cash, moves, pace,
                    award_likelihood, stops (list of [city, nights]),
                    dates, flight_plan, hotel_plan, award_availability,
                    research_notes, pros, cons, breakdown, transit.
                    The first (winning) itinerary also has day_plan.
      web_context — live Tavily search summaries used during planning.
      log         — captured stdout from the engine (agent trace).
    """
    plan_profile = _build_profile(body)

    # Capture the engine's print output so the client can display it
    # as an agent log if desired (mirrors what the Streamlit app showed).
    log_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(log_buf):
            ranked, web_context = engine.run_plan(plan_profile, year=body.year)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Attach the day-by-day plan to the winner only (same as Streamlit behaviour).
    if ranked:
        ranked[0]["day_plan"] = list(engine.get_day_plan(ranked[0]))

    # jsonable_encoder converts Python tuples → JSON arrays (stops field),
    # datetimes → ISO strings, and any other non-JSON-native types.
    return jsonable_encoder({
        "ranked":      ranked,
        "web_context": web_context,
        "log":         log_buf.getvalue(),
    })
