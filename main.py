# europe-agent: a tiny travel agent demo to show how agents work together.
#
# How to run:
#   1. Open Terminal
#   2. cd ~/europe-agent
#   3. (optional) export TAVILY_API_KEY="your-key-here"  -> turns on real web search
#   4. python3 main.py

import itertools
import os
import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import yaml

from dotenv import load_dotenv

# Load variables from .env into os.environ before anything else reads them.
# This means TAVILY_API_KEY in .env is now visible to os.environ.get() below.
# If the key is already set in the shell environment, load_dotenv() leaves it alone.
load_dotenv()

# ---------- Your settings ----------
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TRAVEL_YEAR = 2026

USER_PROFILE = {
    "origin": "SFO",
    "travel_window": "late July through early August",
    "trip_length_days": "7 to 10",

    "travelers": {"adults": 2, "kids": 2, "kids_ages": [14, 11]},
    "trip_type": "family",

    "required_cities": ["London", "Paris"],
    "optional_cities": ["Rome", "Amsterdam", "Barcelona"],
    "avoid_cities":    ["Lisbon"],
    "total_cities":    "2 or 3",

    "points": {"amex_mr": 200_000, "marriott_free_nights": 5, "bonvoy_points": 250_000},

    "strategy": {
        "flight": "Use Amex Membership Rewards points with strong transfer partners (Flying Blue, Virgin Atlantic, etc.)",
        "hotel":  "Use Marriott free nights first, then Bonvoy points, then cash if needed",
    },

    "preferences": {
        "optimize_for":        "best mix of quality, convenience, and value",
        "not_just_cheapest":   True,
        "family_friendly":     True,
        "fewer_hotel_changes": True,
        "efficient_city_flow": True,
        "preferred_departure_days": ["Friday", "Saturday", "Sunday"],
        "flexible_for_better_deal": True,
    },

    "hotel_requirements": {
        "rooms": 1,
        "room_type_preference": ["suite", "junior suite", "large room with sofa bed"],
        "prioritize_large_square_footage": True,
        "family_of_4_comfort": True,
        "avoid_small_rooms":   True,
    },

    "travel_style": {
        "pace": "moderate to relaxed",
        "avoid_rushed_itineraries":         True,
        "prefer_trains_over_short_flights": True,
    },
}

AMEX_FRIENDLY_AIRLINES = {"Air France", "KLM", "Virgin Atlantic", "British Airways", "Iberia", "Delta"}

# Per-person one-way Amex MR cost (off-peak Flying Blue Promo / Virgin off-peak).
AMEX_FLIGHT_OPTIONS = {
    "London":    ("Virgin Atlantic",          25_000),
    "Paris":     ("Air France (Flying Blue)", 22_500),
    "Amsterdam": ("KLM (Flying Blue)",        22_500),
    "Rome":      ("Air France (Flying Blue)", 25_000),
    "Barcelona": ("Iberia",                   22_500),
}

# Rough award-availability score per arrival city (3 = good, 1 = tight).
CITY_AVAIL = {"London": 3, "Paris": 2, "Amsterdam": 2, "Rome": 1, "Barcelona": 2}


# Preferred west-to-east travel order — used to sort cities into a logical route.
CANONICAL_CITY_ORDER = ["London", "Amsterdam", "Paris", "Barcelona", "Rome"]

# Transit strings between each city pair. Keys are frozensets so order doesn't matter.
# These strings must include keywords that city_flow_agent and flight_points_agent
# pattern-match on: "Eurostar", "Thalys", "TGV", "Short flight", "FCO", "BCN".
TRANSIT_BETWEEN = {
    frozenset({"London",    "Amsterdam"}): "Eurostar London → Amsterdam (4h, no flight)",
    frozenset({"London",    "Paris"}):     "Eurostar London → Paris (2h20, no flight)",
    frozenset({"Amsterdam", "Paris"}):     "Thalys Amsterdam → Paris (3h30, no flight)",
    frozenset({"Paris",     "Barcelona"}): "TGV Paris → Barcelona (6h30, no flight)",
    frozenset({"Paris",     "Rome"}):      "Short flight CDG → FCO (~2h)",
    frozenset({"Amsterdam", "Rome"}):      "Short flight AMS → FCO (~2.5h)",
    frozenset({"London",    "Rome"}):      "Short flight LHR → FCO (~2.5h)",
    frozenset({"London",    "Barcelona"}): "Short flight LHR → BCN (~2h)",
    frozenset({"Amsterdam", "Barcelona"}): "Short flight AMS → BCN (~2h)",
    frozenset({"Barcelona", "Rome"}):      "Short flight BCN → FCO (~2h)",
}

CITY_AIRPORTS = {
    "London": "LHR", "Paris": "CDG", "Amsterdam": "AMS",
    "Barcelona": "BCN", "Rome": "FCO",
}

_HOTELS_FILE = Path(__file__).parent / "config" / "hotels.yaml"
CITY_DATA: dict = yaml.safe_load(_HOTELS_FILE.read_text())


# ---------- Activity data ----------
ACTIVITIES = {
    "London": [
        ("Tower of London + Tower Bridge walk",
         "Picnic at Tower Hill or ride the London Eye after dinner"),
        ("British Museum highlights (Egyptian + Greek galleries)",
         "Covent Garden market and street performers"),
        ("Day trip: Warner Bros. Harry Potter Studios (Watford)",
         "Hotel pool / quiet evening — it'll already be a long day"),
        ("Westminster Abbey + Churchill War Rooms",
         "Stroll through St. James's Park, watch the changing of the guard"),
        ("Natural History Museum (dinosaurs!) + Science Museum next door",
         "Hyde Park bike rentals or pedal boats on the Serpentine"),
    ],
    "Paris": [
        ("Eiffel Tower lift (book tickets in advance)",
         "Picnic on Champ de Mars at sunset"),
        ("Louvre kids' route — Egyptian wing + Mona Lisa",
         "Tuileries Garden + Berthillon ice cream on Île Saint-Louis"),
        ("Seine river cruise (open-top boat, ~1 hr)",
         "Walk through the Marais, find a creperie"),
        ("Day trip: Versailles OR Disneyland Paris (kids vote)",
         "Crepes for dinner, early bedtime to recover"),
        ("Montmartre + Sacré-Cœur (funicular up the hill)",
         "Sketching in Place du Tertre, gelato break"),
    ],
    "Rome": [
        ("Colosseum + Forum (kid-focused gladiator tour)",
         "Gelato crawl and people-watching at Piazza Navona"),
        ("Vatican Museums + St. Peter's (book early-entry skip-the-line)",
         "Trastevere walking dinner"),
        ("Day trip to Ostia Antica (easier than Pompeii for kids)",
         "Hotel pool, pizza in the neighborhood"),
    ],
    "Amsterdam": [
        ("Canal boat tour (sets the geography for the kids)",
         "Vondelpark stroll and a frites stand stop"),
        ("Anne Frank House (book ahead) + NEMO Science Museum",
         "Bike rental hour along the canals"),
        ("Day trip to Zaanse Schans (windmills)",
         "Pancake dinner at a kid-friendly spot"),
    ],
    "Barcelona": [
        ("Sagrada Família + Park Güell (book Park Güell entry)",
         "Beach time at Barceloneta"),
        ("Camp Nou stadium tour (FC Barcelona)",
         "Tapas crawl in the Gothic Quarter"),
        ("La Boqueria market + Picasso Museum",
         "Hotel pool, sunset walk"),
    ],
}


# ---------- Helpers ----------
def search_web(query):
    """Return up to 3 results as dicts with content, url, and title.
    Falls back to [] if the key is missing or the request fails."""
    print(f"   [searching the web for: \"{query}\"]")
    if not TAVILY_API_KEY:
        print("   [no TAVILY_API_KEY set — skipping web search]")
        return []
    body = json.dumps({"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.tavily.com/search", data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return [
            {
                "content": r.get("content", ""),
                "url":     r.get("url", ""),
                "title":   r.get("title", ""),
            }
            for r in data.get("results", [])
        ]
    except Exception as e:
        print(f"   [web search failed: {e}]")
        return []


def best_snippet(results, keywords=None):
    """Pick the most informative single sentence from a list of search results.
    Prefers sentences that contain at least one of the given keywords.
    Skips markdown headings (lines starting with #) and very short fragments."""
    keywords = [k.lower() for k in (keywords or [])]

    def _is_usable(s):
        s = s.strip()
        return len(s) >= 40 and not s.startswith("#")

    for r in results:
        for sentence in r["content"].split(". "):
            s = sentence.strip()
            if not _is_usable(s):
                continue
            if not keywords or any(k in s.lower() for k in keywords):
                return s
    # Fallback: first non-trivial sentence of the first result
    if results:
        for sentence in results[0]["content"].split(". "):
            if _is_usable(sentence):
                return sentence.strip()
    return ""


def summarize(results, limit=3):
    for r in results[:limit]:
        content = r["content"] if isinstance(r, dict) else r
        first = content.split(". ")[0].strip()
        if first:
            print(f"     - {first}.")


def total_travelers():
    t = USER_PROFILE["travelers"]
    return t["adults"] + t["kids"]


def classify_pace(nights, n_cities):
    avg = nights / n_cities
    if avg >= 3.5: return "relaxed"
    if avg >= 2.5: return "moderate"
    return "rushed"


def fmt_date(d):
    return d.strftime("%a %b ") + str(d.day)


def availability_for(itin, date_range):
    """Estimate award-space likelihood (High / Medium / Low) for an itinerary on a given date range."""
    out = itin["stops"][0][0]
    ret = itin["stops"][-1][0]
    base = (CITY_AVAIL[out] + CITY_AVAIL[ret]) / 2
    if date_range["is_deal_hunter"]:
        adj = +1.0
    elif date_range["depart_day"] == "Friday":
        adj = -1.0
    elif date_range["depart_day"] == "Saturday":
        adj = -0.5
    else:
        adj = 0.0
    score = base + adj
    if score >= 2.5: return "High",   score
    if score >= 1.5: return "Medium", score
    return "Low", score


def pick_date_for_itinerary(itin, date_options):
    """Prefer Fri/Sat/Sun; switch to the deal-hunter only if it's *much* better (>=1.5 score gap)."""
    rated = [(opt, *availability_for(itin, opt)) for opt in date_options]
    weekend = [r for r in rated if not r[0]["is_deal_hunter"]]
    deal    = [r for r in rated if r[0]["is_deal_hunter"]]

    best_wknd = max(weekend, key=lambda r: r[2])
    best_deal = max(deal,    key=lambda r: r[2]) if deal else None

    if best_deal and best_deal[2] - best_wknd[2] >= 1.5:
        return best_deal[0], best_deal[1], "switched to deal-hunter dates — award availability is much better"
    return best_wknd[0], best_wknd[1], f"{best_wknd[0]['depart_day']} departure matches your weekend preference"


# ---------- The agents ----------

def date_selection_agent():
    """Generate 3 weekend candidate date ranges + 1 mid-week 'deal-hunter' option."""
    print("date_selection_agent: generating candidate date ranges (10-day trips)...")
    print(f"   travel window: {USER_PROFILE['travel_window']} {TRAVEL_YEAR}")
    print(f"   preferred departure days: {', '.join(USER_PROFILE['preferences']['preferred_departure_days'])}")

    # Walk late July through early August looking for Fri/Sat/Sun departures.
    weekend_options = []
    d = date(TRAVEL_YEAR, 7, 24)
    end = date(TRAVEL_YEAR, 8, 10)
    while d <= end and len(weekend_options) < 3:
        if d.weekday() in (4, 5, 6):  # Fri=4, Sat=5, Sun=6
            weekend_options.append({
                "depart":         d,
                "return":         d + timedelta(days=9),
                "depart_day":     d.strftime("%A"),
                "is_deal_hunter": False,
            })
        d += timedelta(days=1)

    # One mid-week deal-hunter option (Tuesday around the same window).
    deal_d = date(TRAVEL_YEAR, 7, 28)
    while deal_d.weekday() != 1:  # Tuesday
        deal_d += timedelta(days=1)
    deal_option = {
        "depart":         deal_d,
        "return":         deal_d + timedelta(days=9),
        "depart_day":     deal_d.strftime("%A"),
        "is_deal_hunter": True,
    }

    options = weekend_options + [deal_option]
    for o in options:
        o["label"] = f"{o['depart_day']} {fmt_date(o['depart'])} -> {fmt_date(o['return'])}"

    print("   candidate date ranges:")
    for o in options:
        marker = "  (deal-hunter — flexible)" if o["is_deal_hunter"] else ""
        print(f"     - {o['label']}{marker}")
    print()
    return options


def _order_cities(city_set):
    """Sort cities into a logical west-to-east travel order."""
    ordered = [c for c in CANONICAL_CITY_ORDER if c in city_set]
    extras  = [c for c in city_set if c not in CANONICAL_CITY_ORDER]
    return ordered + extras


def _allocate_nights(cities, total_nights):
    """Distribute nights across cities; first city gets extras for jet lag."""
    n        = len(cities)
    base     = total_nights // n
    nights   = [base] * n
    nights[0] += total_nights % n  # jet-lag buffer goes to the first stop
    return list(zip(cities, nights))


def _route_name(cities, required):
    """Human-readable name for a candidate route."""
    if len(cities) == 2:
        return " + ".join(cities)
    return " → ".join(cities)


def generate_itineraries(required_cities, optional_cities, trip_length_str):
    """
    Build 3–5 candidate itineraries from the user's required + optional cities.

    Strategy:
    - Always include required cities (in geographic order).
    - Try adding 0, 1, and 2 optional cities (all combinations).
    - Cap at 5 candidates; deduplicate identical city sets.
    """
    try:
        parts = [int(p.strip()) for p in trip_length_str.split("to") if p.strip().isdigit()]
        total_nights = (parts[0] + parts[1]) // 2 if len(parts) == 2 else (parts[0] if parts else 9)
    except Exception:
        total_nights = 9

    valid_req = [c for c in required_cities if c in CITY_DATA]
    valid_opt = [c for c in optional_cities if c in CITY_DATA]

    candidate_sets, seen = [], []
    for extra_count in range(3):                          # 0, 1, or 2 optional cities added
        for combo in itertools.combinations(valid_opt, extra_count):
            city_set = frozenset(valid_req) | frozenset(combo)
            if city_set not in seen:
                seen.append(city_set)
                candidate_sets.append(city_set)
            if len(candidate_sets) == 5:
                break
        if len(candidate_sets) == 5:
            break

    origin = USER_PROFILE["origin"]
    itineraries = []
    for city_set in candidate_sets:
        ordered   = _order_cities(city_set)
        stops     = _allocate_nights(ordered, total_nights)
        first_apt = CITY_AIRPORTS.get(ordered[0],  ordered[0])
        last_apt  = CITY_AIRPORTS.get(ordered[-1], ordered[-1])

        transit = [f"Overnight flight {origin} -> {first_apt}"]
        for i in range(len(ordered) - 1):
            key = frozenset({ordered[i], ordered[i + 1]})
            transit.append(TRANSIT_BETWEEN.get(key, f"Transit {ordered[i]} → {ordered[i + 1]}"))
        transit.append(f"Daytime flight {last_apt} -> {origin}")

        itineraries.append({
            "name":    _route_name(ordered, valid_req),
            "stops":   stops,
            "transit": transit,
        })

    return itineraries


def itinerary_builder_agent(date_options):
    required  = USER_PROFILE.get("required_cities", ["London", "Paris"])
    optional  = USER_PROFILE.get("optional_cities", [])
    trip_len  = USER_PROFILE.get("trip_length_days", "7 to 10")
    origin    = USER_PROFILE["origin"]
    candidates = generate_itineraries(required, optional, trip_len)

    print(f"itinerary_builder_agent: generated {len(candidates)} candidate itinerary/ies...")
    print(f"   required cities: {', '.join(required)}")
    print(f"   optional cities: {', '.join(optional) if optional else 'none'}")
    print(f"   trip length: {trip_len} nights\n")

    built = []
    for sample in candidates:
        cities = [c for c, _ in sample["stops"]]
        nights = sum(n for _, n in sample["stops"])
        moves  = len(cities) - 1
        pace   = classify_pace(nights, len(cities))

        print(f"--- {sample['name']} ---")
        print(f"   {len(cities)} cities, {nights} nights, {moves} hotel change(s), pace: {pace}")

        days, day_num = [], 1
        for city, n in sample["stops"]:
            for i in range(n):
                if day_num == 1:
                    note = f"Arrive in {city} (overnight flight from {origin}), settle in"
                elif i == 0:
                    note = f"Travel to {city} (HOTEL CHANGE), check in"
                else:
                    note = f"Explore {city}"
                days.append({"day": day_num, "city": city, "note": note})
                day_num += 1
        days.append({"day": day_num, "city": cities[-1], "note": f"Fly home to {origin}"})

        for d in days:
            print(f"   Day {d['day']:>2}: {d['city']:<10} - {d['note']}")

        ages = USER_PROFILE["travelers"].get("kids_ages", [])
        if len(ages) >= 2:
            print(f"   Notes for kids ages {ages[0]} and {ages[1]}:")
        for city in cities:
            print(f"     - {city}: {CITY_DATA[city]['kid_notes']}")
        print()

        sample["days"]   = days
        sample["nights"] = nights
        sample["moves"]  = moves
        sample["pace"]   = pace
        built.append(sample)

    return built


def flight_points_agent(itin, date_options):
    """Plan flights using Amex MR; pick best date range; report award-space likelihood."""
    print(f"   flight_points_agent: planning flights for '{itin['name']}'...")

    pax = total_travelers()
    first_city = itin["stops"][0][0]
    last_city  = itin["stops"][-1][0]

    # Use the actual airline the planner would book (from AMEX_FLIGHT_OPTIONS)
    # so the query matches real redemption-path content on points blogs.
    airline, _  = AMEX_FLIGHT_OPTIONS[first_city]
    award_query = (
        f"{airline} award seat availability {USER_PROFILE['origin']} {first_city} "
        f"August {TRAVEL_YEAR} economy miles Amex transfer how to find book"
    )
    tips = search_web(award_query)
    itin["award_web"]       = tips         # results saved for UI display
    itin["award_web_query"] = award_query  # query saved so UI can show what was asked
    print("   award availability tips from the web:")
    summarize(tips, limit=2)

    # Per-date-range availability for this itinerary.
    print(f"   availability per date range (route: {USER_PROFILE['origin']} -> {first_city} ... {last_city} -> {USER_PROFILE['origin']}):")
    for opt in date_options:
        avail, _ = availability_for(itin, opt)
        marker = "  (deal-hunter)" if opt["is_deal_hunter"] else ""
        print(f"     - {opt['label']}{marker}: {avail} likelihood of award space")

    chosen, chosen_avail, reason = pick_date_for_itinerary(itin, date_options)
    print(f"   -> selected: {chosen['label']}  ({chosen_avail} availability) — {reason}")

    itin["dates"]            = chosen
    itin["award_likelihood"] = chosen_avail
    itin["date_reason"]      = reason

    out_airline, out_pp = AMEX_FLIGHT_OPTIONS[first_city]
    ret_airline, ret_pp = AMEX_FLIGHT_OPTIONS[last_city]
    out_pts_total = out_pp * pax
    ret_pts_total = ret_pp * pax
    total_pts = out_pts_total + ret_pts_total

    mr_balance = USER_PROFILE["points"]["amex_mr"]
    if total_pts > mr_balance:
        pts_used = mr_balance
        pts_short = total_pts - mr_balance
        flight_cash_overflow = round(pts_short * 0.013)
    else:
        pts_used = total_pts
        pts_short = 0
        flight_cash_overflow = 0

    origin = USER_PROFILE["origin"]
    intra_cash = 0
    for t in itin["transit"][1:-1]:   # only count intra-Europe legs
        if "Eurostar" in t:        intra_cash += 180 * pax
        elif "Thalys" in t:        intra_cash += 130 * pax
        elif "TGV" in t:           intra_cash += 120 * pax
        elif "Short flight" in t:  intra_cash += 150 * pax

    plan = {
        "outbound":             f"{origin} -> {first_city} on {out_airline} x {pax} pax ({out_pts_total:,} MR), depart {fmt_date(chosen['depart'])}",
        "return":               f"{last_city} -> {origin} on {ret_airline} x {pax} pax ({ret_pts_total:,} MR), depart {fmt_date(chosen['return'])}",
        "amex_used":            pts_used,
        "amex_short":           pts_short,
        "flight_cash_overflow": flight_cash_overflow,
        "intra_cash":           intra_cash,
    }

    print(f"     - outbound:  {plan['outbound']}")
    print(f"     - return:    {plan['return']}")
    if pts_short:
        print(f"     - {pts_short:,} MR short -> ~${flight_cash_overflow} cash to top up")
    print(f"     - intra-Europe transit for {pax} pax: ~${intra_cash}")
    print(f"     - total Amex MR used: {pts_used:,} of {mr_balance:,}")
    return plan


def hotel_points_agent(itin):
    print(f"   hotel_points_agent: planning family-friendly hotels for '{itin['name']}'...")

    certs_left  = USER_PROFILE["points"]["marriott_free_nights"]
    points_left = USER_PROFILE["points"]["bonvoy_points"]

    lines = []
    cash_for_hotels = 0
    certs_used = 0
    points_used = 0
    sqft_total = 0
    smallest_sqft = float("inf")
    all_fit_family = True
    small_room_count = 0

    for city, nights in itin["stops"]:
        info = CITY_DATA[city]
        if not info["fits_family_of_4"]:
            all_fit_family = False
        if info["sqft"] < 400:
            small_room_count += 1
        sqft_total += info["sqft"]
        smallest_sqft = min(smallest_sqft, info["sqft"])

        use_certs = min(certs_left, nights)
        certs_left -= use_certs
        certs_used += use_certs

        nights_left = nights - use_certs
        max_pt_nights = points_left // info["points_per_night"]
        use_pt_nights = min(nights_left, max_pt_nights)
        cost_in_pts = use_pt_nights * info["points_per_night"]
        points_left -= cost_in_pts
        points_used += cost_in_pts

        cash_nights = nights_left - use_pt_nights
        cash_amount = cash_nights * info["cash_per_night"]
        cash_for_hotels += cash_amount

        bits = []
        if use_certs:     bits.append(f"{use_certs} free-night cert(s)")
        if use_pt_nights: bits.append(f"{use_pt_nights} night(s) on Bonvoy ({cost_in_pts:,} pts)")
        if cash_nights:   bits.append(f"{cash_nights} night(s) cash (~${cash_amount})")

        family_marker = "fits family of 4" if info["fits_family_of_4"] else "TIGHT for family of 4"
        line = f"{city}: {nights} nights — {info['hotel']} ({info['room_type']}, {info['sqft']} sqft, {family_marker})"
        if bits:
            line += " — " + ", ".join(bits)
        lines.append(line)
        print(f"     - {line}")

    n_hotels = len(itin["stops"])
    avg_sqft = sqft_total / n_hotels

    print(f"     - certs used: {certs_used} of {USER_PROFILE['points']['marriott_free_nights']}")
    print(f"     - Bonvoy points used: {points_used:,} of {USER_PROFILE['points']['bonvoy_points']:,}")
    print(f"     - cash for hotels: ${cash_for_hotels}")
    print(f"     - avg room size: {avg_sqft:.0f} sqft, smallest: {smallest_sqft:.0f} sqft")

    return {
        "lines":            lines,
        "certs_used":       certs_used,
        "points_used":      points_used,
        "cash_for_hotels":  cash_for_hotels,
        "avg_sqft":         avg_sqft,
        "smallest_sqft":    smallest_sqft,
        "all_fit_family":   all_fit_family,
        "small_room_count": small_room_count,
    }


def city_flow_agent(itin):
    print(f"   city_flow_agent: evaluating travel flow for '{itin['name']}'...")

    n = len(itin["stops"])
    # Skip the transatlantic outbound/return — only evaluate intra-Europe legs.
    intra = itin["transit"][1:-1]
    has_eurostar     = any("Eurostar"     in t for t in intra)
    has_thalys       = any("Thalys"       in t for t in intra)
    has_tgv          = any("TGV"          in t for t in intra)
    has_short_flight = any("Short flight" in t for t in intra)
    long_intra_hop   = any("FCO" in t or "BCN" in t for t in intra)
    all_rail         = not has_short_flight and (has_eurostar or has_thalys or has_tgv)

    if n == 2:
        score, note = 10, "2 cities only, 1 train hop — minimal transit"
    elif n == 3 and has_eurostar and has_thalys and not long_intra_hop:
        score, note = 10, "3 cities, all classic rail (Eurostar + Thalys) — efficient"
    elif n == 3 and all_rail:
        score, note = 9,  "3 cities, all train-connected — smooth flow"
    elif n == 3 and long_intra_hop:
        score, note = 5,  "3 cities but a long flight south breaks the flow"
    elif n == 3 and has_short_flight:
        score, note = 7,  "3 cities with one short intra-Europe flight"
    else:
        score, note = 6,  "mixed transit"

    print(f"     - {note}")
    print(f"     - flow score: {score}/10")
    return {"score": score, "note": note}


def family_comfort_score(itin):
    h = itin["hotel_plan"]
    s = 0
    if h["all_fit_family"]:    s += 4
    if h["avg_sqft"] >= 600:   s += 3
    elif h["avg_sqft"] >= 500: s += 2
    elif h["avg_sqft"] >= 400: s += 1
    s += {"relaxed": 3, "moderate": 2, "rushed": 0}[itin["pace"]]
    s -= max(0, itin["moves"] - 1)
    return max(1, min(10, s))


def build_pros_cons(itin):
    cities = [c for c, _ in itin["stops"]]
    pros, cons = [], []

    if len(cities) == 2:
        pros.append("Only 1 hotel change — easy with 11- and 14-year-olds")
    else:
        cons.append(f"{itin['moves']} hotel changes — more packing/unpacking with kids")

    if itin["pace"] == "relaxed":
        pros.append("Relaxed pace — kids stay sane, parents do too")
    elif itin["pace"] == "rushed":
        cons.append("Rushed pace — likely to wear out the 11-year-old")

    if itin["hotel_plan"]["all_fit_family"]:
        pros.append("All hotels fit the family of 4 in one room")
    if itin["hotel_plan"]["smallest_sqft"] < 400:
        cons.append(f"One hotel is on the small side ({itin['hotel_plan']['smallest_sqft']} sqft)")

    if "Rome" in cities:
        pros.append("Mediterranean weather — fun in late July")
        cons.append("Rome adds a south-bound flight")
    if "Amsterdam" in cities:
        pros.append("Train-connected to London/Paris — smooth with kids")

    if itin["flight_plan"]["amex_short"] == 0:
        pros.append("Amex MR points cover all 4 transatlantic tickets")

    if itin["award_likelihood"] == "High":
        pros.append("High likelihood of finding award space on the chosen dates")
    elif itin["award_likelihood"] == "Low":
        cons.append("Low likelihood of award space — be ready to pivot dates")

    return pros, cons


def research_notes(itin, flight_tips, hotel_tips):
    """
    Derive four short plain-English notes from Tavily search results.

    Each note picks the single most useful sentence from the relevant
    result set (using best_snippet) and falls back to an honest
    'no live data' message when Tavily wasn't available.

    Stored as itin["research_notes"] so the UI can display them and
    the agent log captures them without any duplication of logic.
    """
    award_web  = itin.get("award_web", [])
    award_lh   = itin.get("award_likelihood", "Medium")
    fp         = itin.get("flight_plan", {})
    hp         = itin.get("hotel_plan", {})
    first_city = itin["stops"][0][0]
    last_city  = itin["stops"][-1][0]
    cities     = [c for c, _ in itin["stops"]]

    # ── 1. Flight award insight ───────────────────────────────────────────────
    # Uses the per-itinerary Tavily search (award_web), which targets the
    # actual airline + route the planner would book.
    flight_note = best_snippet(
        award_web,
        keywords=["award", "miles", "availability", "seat", "transfer",
                  "economy", "redemption", "points"],
    )
    if not flight_note:
        airline, pts = AMEX_FLIGHT_OPTIONS[first_city]
        flight_note = (
            f"No live award data. Using estimated rate of {pts:,} MR/person "
            f"to {first_city} on {airline} — verify on the airline portal."
        )

    # ── 2. Hotel / family-fit insight ────────────────────────────────────────
    # Uses the global Marriott hotel search, filtered for family-relevant terms.
    hotel_note = best_snippet(
        hotel_tips,
        keywords=["suite", "family", "sofa", "bed", "certificate",
                  "free night", "kids", "children", "room"],
    )
    if not hotel_note:
        smallest = hp.get("smallest_sqft", 0)
        hotel_note = (
            f"No live hotel data. All hotels in this route fit a family of 4; "
            f"smallest room is {smallest:.0f} sqft."
        ) if smallest else "No live hotel data — using config estimates."

    # ── 3. Points strategy insight ───────────────────────────────────────────
    # Uses the global Flying Blue / Amex MR search for transfer-strategy tips.
    strategy_note = best_snippet(
        flight_tips,
        keywords=["Flying Blue", "promo", "transfer", "Amex", "bonus",
                  "partner", "sweet spot", "miles"],
    )
    if not strategy_note:
        strategy_note = (
            "No live strategy tips. Transfer Amex MR to Flying Blue or "
            "Virgin Atlantic — watch for Flying Blue monthly promo awards."
        )

    # ── 4. Confidence / warnings ─────────────────────────────────────────────
    # Synthesised from the itinerary's own data rather than web results.
    warnings = []
    pts_short = fp.get("amex_short", 0)
    if pts_short:
        warnings.append(
            f"{pts_short:,} MR short — budget ~${fp['flight_cash_overflow']} "
            f"extra cash to top up flights."
        )
    if award_lh == "Low":
        warnings.append(
            "Award space rated Low — book as soon as the calendar opens "
            "(typically 330 days out)."
        )
    if hp.get("smallest_sqft", 999) < 400:
        warnings.append(
            f"One hotel room is under 400 sqft — snug for a family of 4; "
            f"request a connecting room or upgrade at check-in."
        )
    if not TAVILY_API_KEY:
        warnings.append(
            "No Tavily key set — flight and hotel data is estimated, not verified live."
        )

    if warnings:
        confidence = " · ".join(warnings)
    elif award_lh == "High" and TAVILY_API_KEY:
        confidence = "Live search supports good availability for this route."
    elif award_lh == "High":
        confidence = (
            "Estimated high availability based on city patterns — "
            "confirm on the airline portal before transferring points."
        )
    else:
        confidence = (
            "Medium confidence — check award space 11 months out when "
            "the booking calendar opens."
        )

    notes = {
        "flight":     flight_note,
        "hotel":      hotel_note,
        "strategy":   strategy_note,
        "confidence": confidence,
        "has_warnings": bool(warnings),
    }

    print(f"   research_notes for '{itin['name']}':")
    print(f"     flight:     {flight_note[:80]}{'…' if len(flight_note) > 80 else ''}")
    print(f"     hotel:      {hotel_note[:80]}{'…' if len(hotel_note) > 80 else ''}")
    print(f"     strategy:   {strategy_note[:80]}{'…' if len(strategy_note) > 80 else ''}")
    print(f"     confidence: {confidence[:80]}{'…' if len(confidence) > 80 else ''}")

    return notes


def deal_scorer_agent(itineraries):
    print("deal_scorer_agent: scoring each itinerary out of 100 (family-tuned)...\n")

    for itin in itineraries:
        cities = [c for c, _ in itin["stops"]]
        flight = itin["flight_plan"]
        hotel  = itin["hotel_plan"]
        flow   = itin["flow"]
        comfort = family_comfort_score(itin)
        itin["family_comfort"] = comfort

        score = 0
        breakdown = []

        req = USER_PROFILE["required_cities"]
        if all(c in cities for c in req):
            score += 20
            breakdown.append(f"+20 includes {' and '.join(req)} (required)")
        else:
            missing = [c for c in req if c not in cities]
            breakdown.append(f"+0 missing required cities: {', '.join(missing)}")

        score += flow["score"]
        breakdown.append(f"+{flow['score']} travel flow ({flow['note']})")

        amex_used  = flight["amex_used"]
        amex_avail = USER_PROFILE["points"]["amex_mr"]
        ratio = amex_used / amex_avail
        if flight["amex_short"] == 0 and ratio >= 0.7:
            amex_pts, amex_note = 15, f"strong family use ({amex_used:,} of {amex_avail:,})"
        elif flight["amex_short"] == 0:
            amex_pts, amex_note = 12, f"using points but room left ({amex_used:,} of {amex_avail:,})"
        else:
            amex_pts, amex_note = 8, f"short by {flight['amex_short']:,} MR — needs cash top-up"
        score += amex_pts
        breakdown.append(f"+{amex_pts} Amex strategy: {amex_note}")

        certs_used  = hotel["certs_used"]
        certs_avail = USER_PROFILE["points"]["marriott_free_nights"]
        cert_ratio  = certs_used / certs_avail if certs_avail else 0
        bonvoy_used = hotel["points_used"]
        if cert_ratio >= 0.6 and bonvoy_used > 0:
            mar_pts, mar_note = 15, f"great mix ({certs_used} certs + {bonvoy_used:,} Bonvoy pts)"
        elif cert_ratio >= 0.4:
            mar_pts, mar_note = 11, f"decent ({certs_used} certs used)"
        else:
            mar_pts, mar_note = 6,  f"only {certs_used} cert(s) used"
        score += mar_pts
        breakdown.append(f"+{mar_pts} Marriott strategy: {mar_note}")

        comfort_pts = round(comfort * 1.5)
        score += comfort_pts
        breakdown.append(f"+{comfort_pts} family comfort score: {comfort}/10")

        pace_pts = {"relaxed": 10, "moderate": 8, "rushed": 3}[itin["pace"]]
        score += pace_pts
        breakdown.append(f"+{pace_pts} pace ({itin['pace']})")

        ratings = [CITY_DATA[c]["rating"] for c in cities]
        avg_rating = sum(ratings) / len(ratings)
        quality_pts = max(0, min(10, round((avg_rating - 4.0) * 20)))
        score += quality_pts
        breakdown.append(f"+{quality_pts} hotel quality (avg rating {avg_rating:.2f}/5)")

        total_cash = hotel["cash_for_hotels"] + flight["intra_cash"] + flight["flight_cash_overflow"]
        if   total_cash <= 1000: cash_pts = 5
        elif total_cash <= 2500: cash_pts = 4
        elif total_cash <= 5000: cash_pts = 3
        elif total_cash <= 8000: cash_pts = 2
        else:                    cash_pts = 1
        score += cash_pts
        breakdown.append(f"+{cash_pts} cash outlay (~${total_cash})")

        small_rooms = hotel["small_room_count"]
        if small_rooms:
            score -= 5 * small_rooms
            breakdown.append(f"-{5 * small_rooms} small-room penalty ({small_rooms} hotel(s) under 400 sqft)")
        if itin["moves"] > 1:
            extra_moves = itin["moves"] - 1
            score -= 5 * extra_moves
            breakdown.append(f"-{5 * extra_moves} hotel-change penalty ({itin['moves']} total changes)")

        score = max(0, score)
        itin["score"]      = score
        itin["breakdown"]  = breakdown
        itin["total_cash"] = total_cash

        print(f"   {itin['name']}: {score}/100  (family comfort {comfort}/10, "
              f"{itin['moves']} hotel change(s), pace {itin['pace']}, "
              f"award space {itin['award_likelihood']})")
        for b in breakdown:
            print(f"     • {b}")
        print()

    return itineraries


def day_by_day_itinerary_agent(winner):
    """Print a moderate-pace day-by-day plan for the winning itinerary, with real calendar dates."""
    chosen = winner["dates"]
    depart_date = chosen["depart"]
    print(f"day_by_day_itinerary_agent: building day-by-day plan for '{winner['name']}'...")
    print(f"   dates: {chosen['label']}")
    print(f"   award space likelihood: {winner['award_likelihood']}\n")

    days = winner["days"]
    city_day_idx = {}

    print(f"Day-by-day plan ({len(days)} days, pace: {winner['pace']}, "
          f"family of {total_travelers()} including kids ages "
          f"{USER_PROFILE['travelers']['kids_ages'][0]} and "
          f"{USER_PROFILE['travelers']['kids_ages'][1]}):\n")

    for i, day in enumerate(days):
        d = day["day"]
        city = day["city"]
        is_first = (d == 1)
        is_last  = (i == len(days) - 1)
        prev_city = days[i - 1]["city"] if i > 0 else None
        is_change = (i > 0 and not is_first and not is_last and city != prev_city)

        actual_date = depart_date + timedelta(days=d - 1)
        date_str = fmt_date(actual_date)

        overnight = "(overnight flight home)" if is_last else city
        points_note = None

        if is_first:
            airline, _ = AMEX_FLIGHT_OPTIONS[city]
            main    = f"Fly {USER_PROFILE['origin']} -> {city} on {airline} using Amex MR points (overnight flight)"
            lighter = "Easy first evening — light dinner near the hotel, early bedtime to beat jet lag"
            family  = "Day 1 is just for arriving and resting. Don't try to do anything big."
            points_note = (f"Outbound: 4 x Amex MR transfers to {airline}. "
                           f"Check into {CITY_DATA[city]['hotel']} on a Marriott free-night cert.")
        elif is_last:
            airline, _ = AMEX_FLIGHT_OPTIONS[city]
            main    = f"Fly {city} -> {USER_PROFILE['origin']} on {airline} using Amex MR points"
            lighter = "Pastry / souvenir stop near the hotel before heading to the airport"
            family  = "Build in extra time to the airport — kids and luggage move slow."
            points_note = f"Return: {total_travelers()} x Amex MR transfers to {airline}."
        elif is_change:
            transit_str = next(
                (t for t in winner["transit"] if prev_city in t and city in t),
                f"Transit from {prev_city} to {city}",
            )
            main    = transit_str
            lighter = "Settle into the new hotel, dinner near the property, walk-only afternoon"
            family  = "Travel day — keep it light, no museums."
            points_note = (f"Check into {CITY_DATA[city]['hotel']} "
                           f"({CITY_DATA[city]['room_type']}, {CITY_DATA[city]['sqft']} sqft) "
                           f"using Bonvoy points / free-night cert.")
        else:
            idx = city_day_idx.get(city, 0)
            options = ACTIVITIES.get(city, [("Free exploration", "Hotel relaxation")])
            main, lighter = options[idx % len(options)]
            family  = f"Pace stays {winner['pace']} — one main activity, one optional lighter one."
            city_day_idx[city] = idx + 1

        print(f"Day {d:>2} ({date_str}) | {city:<10} | overnight: {overnight}")
        print(f"             Main:    {main}")
        print(f"             Lighter: {lighter}")
        print(f"             Family:  {family}")
        if points_note:
            print(f"             Points:  {points_note}")
        print()


def trip_planner_agent():
    print("trip_planner_agent: starting up. I will coordinate the other agents.\n")
    print(f"   trip type: {USER_PROFILE['trip_type']}, "
          f"{USER_PROFILE['travelers']['adults']} adults + "
          f"{USER_PROFILE['travelers']['kids']} kids "
          f"(ages {USER_PROFILE['travelers']['kids_ages']})")
    print(f"   travel window: {USER_PROFILE['travel_window']} {TRAVEL_YEAR}, "
          f"trip length: {USER_PROFILE['trip_length_days']} days\n")

    # 1) Date candidates
    date_options = date_selection_agent()

    # 2) Web context — targeted queries built from the actual user profile
    print("trip_planner_agent: pulling fresh web context for your strategies...")

    origin     = USER_PROFILE["origin"]
    cities_str = " and ".join(USER_PROFILE.get("required_cities", ["London", "Paris"]))
    n_pax      = USER_PROFILE["travelers"]["adults"] + USER_PROFILE["travelers"]["kids"]

    # Flying Blue promo awards are the main Amex MR sweet spot for transatlantic.
    # "promo award" and "sweet spot" are the phrases that appear on points blogs.
    flight_query = (
        f"Flying Blue promo award {origin} {cities_str} economy {TRAVEL_YEAR} "
        f"Amex Membership Rewards transfer miles cost how many points"
    )
    flight_tips = search_web(flight_query)
    print("   flight strategy tips:")
    summarize(flight_tips)

    # Hotel query asks about the actual redemption strategy (certs, points value)
    # and the specific room requirement (suite / sofa bed for families).
    hotel_query = (
        f"Marriott Bonvoy {cities_str} family of {n_pax} suite {TRAVEL_YEAR} "
        f"free night certificate points redemption sofa bed review"
    )
    hotel_tips = search_web(hotel_query)
    print("   hotel strategy tips:")
    summarize(hotel_tips)
    print()

    # 3) Itinerary skeletons
    itineraries = itinerary_builder_agent(date_options)

    # 4) Per-itinerary planning (flight agent picks dates here)
    print("Per-itinerary planning:\n")
    for itin in itineraries:
        print(f"=== {itin['name']} ===")
        itin["flight_plan"]     = flight_points_agent(itin, date_options)
        itin["hotel_plan"]      = hotel_points_agent(itin)
        itin["flow"]            = city_flow_agent(itin)
        pros, cons              = build_pros_cons(itin)
        itin["pros"]            = pros
        itin["cons"]            = cons
        itin["research_notes"]  = research_notes(itin, flight_tips, hotel_tips)
        print()

    # 5) Score
    deal_scorer_agent(itineraries)

    # 6) Final ranking with dates
    ranked = sorted(itineraries, key=lambda i: i["score"], reverse=True)

    print("=" * 64)
    print("FINAL RANKING (best to worst, with dates)")
    print("=" * 64)
    for i, itin in enumerate(ranked, 1):
        dates = itin["dates"]
        print(f"\n#{i}: {itin['name']} — {itin['score']}/100")
        print(f"   Cities:           {' -> '.join(c for c, _ in itin['stops'])}")
        print(f"   Dates:            {dates['label']}")
        print(f"   Departure day:    {dates['depart_day']} ({fmt_date(dates['depart'])})")
        print(f"   Return date:      {fmt_date(dates['return'])}")
        print(f"   Award space:      {itin['award_likelihood']} likelihood — {itin['date_reason']}")
        print(f"   Length:           {itin['nights']} nights ({itin['nights'] + 1} days)")
        print(f"   Hotel changes:    {itin['moves']}")
        print(f"   Pace:             {itin['pace']}")
        print(f"   Family comfort:   {itin['family_comfort']}/10")
        print(f"   Cash needed:      ~${itin['total_cash']}")
        print(f"   Pros:             " + "; ".join(itin["pros"]))
        print(f"   Cons:             " + ("; ".join(itin["cons"]) if itin["cons"] else "none worth flagging"))

    # 7) Why these dates were chosen
    print("\n" + "=" * 64)
    print("WHY THESE DATES")
    print("=" * 64)
    print(f"Your weekend preference: {', '.join(USER_PROFILE['preferences']['preferred_departure_days'])}")
    print("The flight agent picked the best date for each itinerary based on award-space likelihood,")
    print("only switching off the weekend if the deal-hunter dates were *much* better.\n")
    for itin in ranked:
        print(f"   {itin['name']}: {itin['dates']['label']}")
        print(f"     -> {itin['date_reason']} (award space: {itin['award_likelihood']})")

    # 8) Why the winner won
    winner = ranked[0]
    print("\n" + "=" * 64)
    print(f"WINNER: {winner['name']} — {winner['score']}/100")
    print("=" * 64)
    print("\nWhy this itinerary won:")
    for b in winner["breakdown"]:
        print(f"   • {b}")
    print(f"\nIt fits your stated preferences: \"{USER_PROFILE['preferences']['optimize_for']}\"")
    print(f"and your family travel style: pace = \"{USER_PROFILE['travel_style']['pace']}\".\n")

    # 9) Day-by-day for winner
    print("=" * 64)
    print("DAY-BY-DAY PLAN FOR THE WINNER")
    print("=" * 64 + "\n")
    day_by_day_itinerary_agent(winner)

    winner = ranked[0]
    web_context = {
        "live":     bool(TAVILY_API_KEY),
        "searches": [
            {
                "label":   "Amex MR flight strategy",
                "query":   flight_query,
                "results": flight_tips,
            },
            {
                "label":   "Marriott hotel options",
                "query":   hotel_query,
                "results": hotel_tips,
            },
            {
                "label":   f"Award availability ({' → '.join(c for c, _ in winner['stops'][:2])}…)",
                "query":   winner.get("award_web_query", ""),
                "results": winner.get("award_web", []),
            },
        ],
    }
    return ranked, web_context


def get_day_plan(winner):
    """Return day-by-day plan as structured dicts (no printing)."""
    chosen = winner["dates"]
    depart_date = chosen["depart"]
    days = winner["days"]
    city_day_idx = {}
    result = []

    for i, day in enumerate(days):
        d = day["day"]
        city = day["city"]
        is_first = (d == 1)
        is_last  = (i == len(days) - 1)
        prev_city = days[i - 1]["city"] if i > 0 else None
        is_change = (i > 0 and not is_first and not is_last and city != prev_city)

        actual_date = depart_date + timedelta(days=d - 1)
        date_str = fmt_date(actual_date)
        points_note = None

        if is_first:
            airline, _ = AMEX_FLIGHT_OPTIONS[city]
            main    = f"Fly {USER_PROFILE['origin']} -> {city} on {airline} using Amex MR points (overnight flight)"
            lighter = "Easy first evening — light dinner near the hotel, early bedtime to beat jet lag"
            family  = "Day 1 is just for arriving and resting. Don't try to do anything big."
            points_note = (f"Outbound: {total_travelers()} x Amex MR transfers to {airline}. "
                           f"Check into {CITY_DATA[city]['hotel']} on a Marriott free-night cert.")
        elif is_last:
            airline, _ = AMEX_FLIGHT_OPTIONS[city]
            main    = f"Fly {city} -> {USER_PROFILE['origin']} on {airline} using Amex MR points"
            lighter = "Pastry / souvenir stop near the hotel before heading to the airport"
            family  = "Build in extra time to the airport — kids and luggage move slow."
            points_note = f"Return: {total_travelers()} x Amex MR transfers to {airline}."
        elif is_change:
            main    = f"Train from {prev_city} to {city}, check in"
            lighter = "Settle into the new hotel, dinner near the property, walk-only afternoon"
            family  = "Travel day — keep it light, no museums."
            points_note = (f"Check into {CITY_DATA[city]['hotel']} "
                           f"({CITY_DATA[city]['room_type']}, {CITY_DATA[city]['sqft']} sqft) "
                           f"using Bonvoy points / free-night cert.")
        else:
            idx = city_day_idx.get(city, 0)
            options = ACTIVITIES.get(city, [("Free exploration", "Hotel relaxation")])
            main, lighter = options[idx % len(options)]
            family  = f"Pace stays {winner['pace']} — one main activity, one optional lighter one."
            city_day_idx[city] = idx + 1

        result.append({
            "day": d, "city": city, "date_str": date_str,
            "main": main, "lighter": lighter, "family": family,
            "points_note": points_note,
        })

    return result


def run_plan(profile, year=2026):
    """Entry point for the Streamlit UI. Sets globals and returns ranked itineraries."""
    global USER_PROFILE, TRAVEL_YEAR
    USER_PROFILE = profile
    TRAVEL_YEAR = year
    return trip_planner_agent()


if __name__ == "__main__":
    trip_planner_agent()
