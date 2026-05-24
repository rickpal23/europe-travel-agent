# europe-agent: a tiny travel agent demo to show how agents work together.
#
# How to run:
#   1. Open Terminal
#   2. cd ~/europe-agent
#   3. (optional) export TAVILY_API_KEY="your-key-here"  -> turns on real web search
#   4. python3 main.py

import os
import json
import urllib.request
from datetime import date, timedelta


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


# ---------- Sample data ----------
SAMPLE_ITINERARIES = [
    {
        "name":    "Two-City Classic",
        "stops":   [("London", 5), ("Paris", 4)],
        "transit": ["Overnight flight SFO -> LHR",
                    "Eurostar train London -> Paris (no flight)",
                    "Daytime flight CDG -> SFO"],
    },
    {
        "name":    "North Loop (train-heavy)",
        "stops":   [("London", 3), ("Amsterdam", 3), ("Paris", 3)],
        "transit": ["Overnight flight SFO -> LHR",
                    "Eurostar train London -> Amsterdam (no flight)",
                    "Thalys train Amsterdam -> Paris (no flight)",
                    "Daytime flight CDG -> SFO"],
    },
    {
        "name":    "European Triangle",
        "stops":   [("London", 3), ("Paris", 3), ("Rome", 3)],
        "transit": ["Overnight flight SFO -> LHR",
                    "Eurostar train London -> Paris (no flight)",
                    "Short flight CDG -> FCO",
                    "Daytime flight FCO -> SFO"],
    },
]

CITY_DATA = {
    "London": {
        "hotel": "London Marriott Hotel County Hall",
        "room_type": "1-Bedroom Suite (king + sofa bed for kids)",
        "sqft": 650, "fits_family_of_4": True,
        "cash_per_night": 580, "points_per_night": 100_000,
        "rating": 4.6, "brand": "Marriott",
        "kid_notes": "Right next to the London Eye and Big Ben. Easy walks to Tower of London. Day trip to Warner Bros. Harry Potter Studios is a hit with both 11 and 14.",
    },
    "Paris": {
        "hotel": "Paris Marriott Opera Ambassador",
        "room_type": "Junior Suite with sofa bed",
        "sqft": 480, "fits_family_of_4": True,
        "cash_per_night": 520, "points_per_night": 90_000,
        "rating": 4.5, "brand": "Marriott",
        "kid_notes": "Eiffel Tower picnic on Champ de Mars, Louvre kids' trail (Egyptian wing has the lowest crowds), Seine boat ride. Disneyland Paris is a possible day trip.",
    },
    "Rome": {
        "hotel": "The Westin Excelsior, Rome",
        "room_type": "Deluxe Suite",
        "sqft": 700, "fits_family_of_4": True,
        "cash_per_night": 620, "points_per_night": 110_000,
        "rating": 4.7, "brand": "Marriott",
        "kid_notes": "Book a kid-focused Colosseum + Forum tour. Trastevere evenings = gelato and quiet piazzas. Ostia Antica is an easy half-day for the 14yo.",
    },
    "Amsterdam": {
        "hotel": "Renaissance Amsterdam Hotel",
        "room_type": "Family Room (1 king + 2 singles)",
        "sqft": 380, "fits_family_of_4": True,
        "cash_per_night": 460, "points_per_night": 75_000,
        "rating": 4.4, "brand": "Marriott",
        "kid_notes": "Canal boat tour first day. Anne Frank House is heavy — better for the 14yo, book ahead. NEMO Science Museum is a hit for both. Easy bike rentals.",
    },
    "Barcelona": {
        "hotel": "W Barcelona",
        "room_type": "Wonderful Suite",
        "sqft": 580, "fits_family_of_4": True,
        "cash_per_night": 700, "points_per_night": 120_000,
        "rating": 4.5, "brand": "Marriott",
        "kid_notes": "Hotel is on the beach — instant kid win. Park Güell + Sagrada Família morning, Camp Nou tour for the soccer fan, tapas in the Gothic Quarter.",
    },
}


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
    print(f"   [searching the web for: \"{query}\"]")
    if not TAVILY_API_KEY:
        print("   [no TAVILY_API_KEY set — skipping web search]")
        return []
    body = json.dumps({"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}).encode("utf-8")
    req = urllib.request.Request("https://api.tavily.com/search", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return [r.get("content", "") for r in data.get("results", [])]
    except Exception as e:
        print(f"   [web search failed: {e}]")
        return []


def summarize(snippets, limit=3):
    for s in snippets[:limit]:
        first = s.split(". ")[0].strip()
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


def itinerary_builder_agent(date_options):
    print("itinerary_builder_agent: building 3 candidate itineraries (minimizing hotel changes)...")
    print(f"   {len(date_options)} candidate date ranges available — flight agent will pick best per itinerary\n")

    built = []
    for sample in SAMPLE_ITINERARIES:
        cities = [c for c, _ in sample["stops"]]
        nights = sum(n for _, n in sample["stops"])
        moves  = len(cities) - 1
        pace   = classify_pace(nights, len(cities))

        print(f"--- {sample['name']} ---")
        print(f"   {len(cities)} cities, {nights} nights, {moves} hotel change(s), pace: {pace}")

        days, day_num = [], 1
        for stop_idx, (city, n) in enumerate(sample["stops"]):
            for i in range(n):
                if day_num == 1:
                    note = f"Arrive in {city} (overnight flight from SFO), settle in"
                elif i == 0:
                    note = f"Travel to {city} (HOTEL CHANGE), check in"
                else:
                    note = f"Explore {city}"
                days.append({"day": day_num, "city": city, "note": note})
                day_num += 1
        days.append({"day": day_num, "city": cities[-1], "note": "Fly home to SFO"})

        for d in days:
            print(f"   Day {d['day']:>2}: {d['city']:<10} - {d['note']}")

        ages = USER_PROFILE["travelers"]["kids_ages"]
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

    # Real web search informed by the dates and route.
    tips = search_web(f"best award availability SFO to {first_city} August dates Flying Blue Virgin Atlantic")
    print("   award availability tips from the web:")
    summarize(tips, limit=2)

    # Per-date-range availability for this itinerary.
    print(f"   availability per date range (route: SFO -> {first_city} ... {last_city} -> SFO):")
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

    intra_cash = 0
    for t in itin["transit"]:
        if "Eurostar" in t:        intra_cash += 180 * pax
        elif "Thalys" in t:        intra_cash += 130 * pax
        elif "Short flight" in t:  intra_cash += 150 * pax

    plan = {
        "outbound":             f"SFO -> {first_city} on {out_airline} x {pax} pax ({out_pts_total:,} MR), depart {fmt_date(chosen['depart'])}",
        "return":               f"{last_city} -> SFO on {ret_airline} x {pax} pax ({ret_pts_total:,} MR), depart {fmt_date(chosen['return'])}",
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
    has_eurostar = any("Eurostar" in t for t in itin["transit"])
    has_thalys   = any("Thalys"   in t for t in itin["transit"])
    has_short_flight = any("Short flight" in t for t in itin["transit"])
    long_intra_hop = any("FCO" in t or "BCN" in t for t in itin["transit"])

    if n == 2:
        score, note = 10, "2 cities only, 1 train hop — minimal transit"
    elif n == 3 and has_eurostar and has_thalys and not long_intra_hop:
        score, note = 10, "3 cities, all train-connected — efficient"
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

        if all(c in cities for c in USER_PROFILE["required_cities"]):
            score += 20
            breakdown.append("+20 includes London and Paris (required)")
        else:
            missing = [c for c in USER_PROFILE["required_cities"] if c not in cities]
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
            main    = f"Fly {city} -> SFO on {airline} using Amex MR points"
            lighter = "Pastry / souvenir stop near the hotel before heading to the airport"
            family  = "Build in extra time to the airport — kids and luggage move slow."
            points_note = f"Return: 4 x Amex MR transfers to {airline}."
        elif is_change:
            main    = f"Eurostar from {prev_city} to {city} (~2.5 hrs, no flight)"
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

    # 2) Web context
    print("trip_planner_agent: pulling fresh web context for your strategies...")
    flight_tips = search_web("Amex Membership Rewards transfer partners SFO Europe family of 4 summer")
    print("   flight strategy tips:")
    summarize(flight_tips)
    hotel_tips = search_web("best Marriott Bonvoy hotels Europe family of 4 suites London Paris")
    print("   hotel strategy tips:")
    summarize(hotel_tips)
    print()

    # 3) Itinerary skeletons
    itineraries = itinerary_builder_agent(date_options)

    # 4) Per-itinerary planning (flight agent picks dates here)
    print("Per-itinerary planning:\n")
    for itin in itineraries:
        print(f"=== {itin['name']} ===")
        itin["flight_plan"] = flight_points_agent(itin, date_options)
        itin["hotel_plan"]  = hotel_points_agent(itin)
        itin["flow"]        = city_flow_agent(itin)
        pros, cons = build_pros_cons(itin)
        itin["pros"] = pros
        itin["cons"] = cons
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

    return ranked


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
