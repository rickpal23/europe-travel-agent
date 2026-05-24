"""
Seats.aero award availability search.

How Seats.aero works:
  - Seats.aero aggregates award inventory from loyalty programs in real time.
  - The Partner API lets you query a specific route and date range and get back
    a list of dates where award seats are actually available, along with the
    mileage cost and which program holds the space.
  - Auth: pass your key in a `Partner-Authorization` HTTP header.
  - Endpoint: GET https://seats.aero/partnerapi/search
  - Key response fields (per date returned):
      YAvailable / WAvailable / JAvailable / FAvailable  — bool, is there space?
      YMileageCost / WMileageCost / ...                  — points cost for that date
      Source      — the loyalty program holding the space (e.g. "flyingblue")
      YAirlines   — which airline(s) are available for economy
      Date        — ISO date string "2026-07-25"

Cabin codes used in the response:
  Y = Economy   W = Premium Economy   J = Business   F = First

NOTE: Seats.aero sits behind Cloudflare. Requests without a browser-like
User-Agent header receive 403 Forbidden (Cloudflare error 1010). The headers
dict below includes the minimum set needed to pass through.

This module is intentionally self-contained (stdlib only, no third-party imports)
so it can be imported without installing anything extra.
"""

import json
import os
import urllib.parse
import urllib.request

_BASE = "https://seats.aero/partnerapi"

# Cloudflare blocks requests without a browser-like User-Agent.
# These headers are the minimum needed to receive a real API response.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Seats.aero cabin code → field prefix used in response JSON
_CABIN_PREFIX = {
    "economy":          "Y",
    "premium-economy":  "W",
    "business":         "J",
    "first":            "F",
}

# Seats.aero source key → human-readable program name shown in the UI
_SOURCE_LABELS = {
    "aircanada":      "Air Canada Aeroplan",
    "united":         "United MileagePlus",
    "alaska":         "Alaska Mileage Plan",
    "virginatlantic": "Virgin Atlantic Flying Club",
    "airfrance":      "Air France Flying Blue",
    "flyingblue":     "Air France/KLM Flying Blue",
    "british":        "British Airways Avios",
    "american":       "American AAdvantage",
    "delta":          "Delta SkyMiles",
    "jetblue":        "JetBlue TrueBlue",
    "aeroplan":       "Air Canada Aeroplan",
}


def query_award_availability(
    origin,
    destination,
    cabin="economy",
    start_date=None,
    end_date=None,
):
    """
    Query Seats.aero for real award seat availability on a route and date window.

    Parameters
    ----------
    origin, destination : str
        3-letter IATA airport codes, e.g. "SFO", "LHR".
    cabin : str
        One of "economy", "premium-economy", "business", "first".
    start_date, end_date : str or None
        ISO date strings "YYYY-MM-DD".  If None, Seats.aero returns its
        default rolling window (roughly next 30 days).

    Returns
    -------
    dict with keys:
        source           — "seats.aero" if we got live data, else "estimated"
        available        — True / False / None (None = API not called)
        seat_count       — number of dates in the window that have space
        lowest_points    — cheapest mileage cost found (int or None)
        program          — loyalty program with cheapest space (str or None)
        all_programs     — list of all unique programs that have space
        dates_with_space — list of ISO date strings where seats were found
        cabin            — the cabin queried
        route            — human-readable "SFO → LHR"
        error            — error message string if something went wrong, else None
    """
    route = f"{origin} → {destination}"
    fallback = {
        "source":           "estimated",
        "available":        None,
        "seat_count":       None,
        "lowest_points":    None,
        "program":          None,
        "all_programs":     [],
        "dates_with_space": [],
        "cabin":            cabin,
        "route":            route,
        "error":            None,
    }

    api_key = os.environ.get("SEATS_AERO_API_KEY", "").strip()
    if not api_key:
        fallback["error"] = "SEATS_AERO_API_KEY not set — using estimated availability"
        return fallback

    prefix    = _CABIN_PREFIX.get(cabin, "Y")
    avail_key = f"{prefix}Available"
    cost_key  = f"{prefix}MileageCost"

    params = {
        "origin_airport":      origin,
        "destination_airport": destination,
        "cabin":               cabin,
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    url = f"{_BASE}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={**_HEADERS, "Partner-Authorization": api_key},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        fallback["error"] = f"Seats.aero HTTP {e.code}: {e.reason}"
        return fallback
    except Exception as e:
        fallback["error"] = f"Seats.aero request failed: {e}"
        return fallback

    # The API returns {"data": [...], "count": N, ...}
    rows = data.get("data") or []
    if not rows:
        return {
            **fallback,
            "source":    "seats.aero",
            "available": False,
            "error":     None,
        }

    # Filter to dates where the requested cabin actually has seats.
    open_rows = [r for r in rows if r.get(avail_key)]
    dates_with_space = sorted(
        {r["Date"][:10] for r in open_rows if r.get("Date")}
    )

    # Build cost-to-program map: find the cheapest offer and who holds it.
    # Each row carries a top-level Source (the loyalty program) and a cost.
    # The API returns YMileageCost as a string (e.g. "30000"), so cast to int.
    cost_by_program: dict[str, list[int]] = {}
    for r in open_rows:
        src = (r.get("Source") or "").lower()
        raw_cost = r.get(cost_key)
        if src and raw_cost:
            try:
                cost_by_program.setdefault(src, []).append(int(raw_cost))
            except (ValueError, TypeError):
                pass

    # Sort programs by their cheapest offering.
    sorted_programs = sorted(
        cost_by_program.items(), key=lambda kv: min(kv[1])
    )
    cheapest_raw = sorted_programs[0][0] if sorted_programs else None
    lowest_points = min(sorted_programs[0][1]) if sorted_programs else None
    program = _SOURCE_LABELS.get(cheapest_raw, cheapest_raw)
    all_programs = [
        _SOURCE_LABELS.get(src, src) for src, _ in sorted_programs
    ]

    return {
        "source":           "seats.aero",
        "available":        bool(open_rows),
        "seat_count":       len(open_rows),
        "lowest_points":    lowest_points,
        "program":          program,
        "all_programs":     all_programs,
        "dates_with_space": dates_with_space[:5],  # up to 5 sample dates in UI
        "cabin":            cabin,
        "route":            route,
        "error":            None,
    }
