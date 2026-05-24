# ui/app.py — Travel Points Planner
#
# HOW STREAMLIT WORKS (read this first):
#   Streamlit re-runs this entire file from top to bottom every time the
#   user interacts with any input.  That means normal variables reset on
#   every run.  Use st.session_state (a persistent dict) to keep data
#   across runs — like search results.
#
# HOW THIS FILE CONNECTS TO THE AGENTS:
#   All the planning logic lives in main.py one folder up.  We import it
#   as "engine" and call two functions:
#     engine.run_plan(profile, year)  → runs all agents, returns ranked list
#     engine.get_day_plan(itinerary)  → returns day-by-day list for one itinerary

import contextlib  # lets us redirect print() output away from the terminal
import io          # gives us an in-memory string buffer to catch that output
import os
import sys

import streamlit as st

# Add the parent folder to Python's module search path so we can import main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import main as engine  # all the agent logic lives here

# ── Page config ───────────────────────────────────────────────────────────────
# This must be the first Streamlit call in the file.
st.set_page_config(
    page_title="Travel Points Planner",
    page_icon="✈️",
    layout="wide",  # uses the full browser width instead of a narrow column
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("✈️ Travel Points Planner")
st.caption("Tell us your trip details and points balances. We'll rank your best itinerary options.")

# ── Sidebar: all the input fields ────────────────────────────────────────────
# Everything inside `with st.sidebar:` appears in the left panel.
# Each st.* input widget immediately returns its current value as a Python variable.
# When the user changes a field, Streamlit reruns the script and these variables
# hold the new values automatically — no form submission needed.

with st.sidebar:
    st.header("Your Trip")

    # --- Destination ---
    st.subheader("Destination & Dates")

    origin = st.text_input(
        label="Departing from (airport code)",
        value="SFO",
        help="3-letter airport code, e.g. SFO, JFK, LAX",
    )

    year = st.number_input(
        label="Travel year",
        min_value=2025, max_value=2030, value=2026, step=1,
    )

    # Two number inputs side by side using st.columns
    col_a, col_b = st.columns(2)
    min_days = col_a.number_input("Min days", min_value=5, max_value=21, value=7)
    max_days = col_b.number_input("Max days", min_value=5, max_value=21, value=10)

    # --- Family size ---
    st.subheader("Travelers")

    col_a, col_b = st.columns(2)
    adults = col_a.number_input("Adults", min_value=1, max_value=8, value=2)
    kids   = col_b.number_input("Kids",   min_value=0, max_value=6, value=2)

    # Only show the ages field when there are actually kids.
    # Streamlit re-evaluates this every run, so if the user sets kids to 0
    # this field disappears automatically.
    if int(kids) > 0:
        kids_ages_raw = st.text_input(
            label="Kids' ages (comma-separated)",
            value="14, 11",
            help="Example: 14, 11",
        )
    else:
        kids_ages_raw = ""

    # --- Cities ---
    st.subheader("Cities")

    # engine.CITY_DATA is a dict in main.py — its keys are the city names.
    # We pull them dynamically so adding a city to main.py automatically
    # shows up here.
    all_cities = list(engine.CITY_DATA.keys())

    required_cities = st.multiselect(
        label="Must-visit cities",
        options=all_cities,
        default=["London", "Paris"],
        help="These cities are required. Missing one penalises the score.",
    )

    # Exclude already-required cities from the optional list
    optional_cities = st.multiselect(
        label="Nice-to-have cities",
        options=[c for c in all_cities if c not in required_cities],
        default=[c for c in ["Rome", "Amsterdam", "Barcelona"] if c not in required_cities],
    )

    st.caption("Route templates are fixed for now — city selection affects scoring.")

    # --- Points ---
    st.subheader("Points & Certs")

    amex_mr = st.number_input(
        label="Amex MR points",
        min_value=0, step=10_000, value=200_000,
    )

    col_a, col_b = st.columns(2)
    free_nights   = col_a.number_input("Free night certs", min_value=0, max_value=30, value=5)
    bonvoy_points = col_b.number_input("Bonvoy points",    min_value=0, step=10_000, value=250_000)

    # --- Run button ---
    st.divider()
    run_clicked = st.button(
        label="🔍  Run Search",
        use_container_width=True,  # stretches button to full sidebar width
        type="primary",            # renders as a filled button instead of outline
    )

# ── Session state: persist results across Streamlit reruns ────────────────────
# Without this, results would vanish every time the user adjusts any input field.
if "results" not in st.session_state:
    st.session_state.results     = None  # holds the ranked itinerary list
    st.session_state.web_context = {}    # holds the global web research results
    st.session_state.log         = ""    # holds the agents' print output

# ── Run the agents when the button is clicked ─────────────────────────────────
if run_clicked:

    # Parse the kids-ages text ("14, 11") into a list of ints ([14, 11]).
    n_kids = int(kids)
    if n_kids > 0 and kids_ages_raw.strip():
        try:
            kids_ages = [int(a.strip()) for a in kids_ages_raw.split(",") if a.strip()]
        except ValueError:
            kids_ages = [10] * n_kids          # fallback if the user types something odd
        # Pad to at least 2 entries so the agents don't crash on index access
        while len(kids_ages) < max(n_kids, 2):
            kids_ages.append(10)
    else:
        kids_ages = [10, 10]                   # safe default when there are no kids

    # Build the profile dict that main.py's agents expect.
    # This is the same shape as USER_PROFILE in main.py — we're just filling
    # it from the sidebar inputs instead of a hardcoded dict.
    profile = {
        "origin":           origin,
        "travel_window":    "late July through early August",
        "trip_length_days": f"{int(min_days)} to {int(max_days)}",
        "travelers": {
            "adults":    int(adults),
            "kids":      n_kids,
            "kids_ages": kids_ages,
        },
        "trip_type":      "family" if n_kids > 0 else "couple",
        "required_cities": required_cities,
        "optional_cities": optional_cities,
        "avoid_cities":    [],
        "total_cities":    "2 or 3",
        "points": {
            "amex_mr":               int(amex_mr),
            "marriott_free_nights":  int(free_nights),
            "bonvoy_points":         int(bonvoy_points),
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
            "rooms":                          1,
            "room_type_preference":           ["suite", "junior suite", "large room with sofa bed"],
            "prioritize_large_square_footage": True,
            "family_of_4_comfort":            n_kids > 0,
            "avoid_small_rooms":              True,
        },
        "travel_style": {
            "pace":                          "moderate to relaxed",
            "avoid_rushed_itineraries":      True,
            "prefer_trains_over_short_flights": True,
        },
    }

    # Show a spinner while the agents run.
    # We redirect stdout so the agents' print() calls don't appear in the terminal
    # or break the UI — they're captured and shown in the debug log below.
    with st.spinner("Running travel agents…"):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            ranked, web_context = engine.run_plan(profile, year=int(year))
        st.session_state.results     = ranked
        st.session_state.web_context = web_context
        st.session_state.log         = captured.getvalue()

# ── Display results ───────────────────────────────────────────────────────────
if st.session_state.results:
    ranked = st.session_state.results
    winner = ranked[0]

    # --- Winner banner ---
    # st.success renders a green highlighted box.
    st.success(
        f"**Winner: {winner['name']}** — {winner['score']}/100 · "
        f"{' → '.join(c for c, _ in winner['stops'])} · "
        f"{winner['dates']['label']} · ~${winner['total_cash']} cash needed"
    )

    # --- Quick-compare tiles ---
    # st.columns(n) returns n equal-width containers placed side by side.
    st.subheader("All Options")

    MEDALS   = ["🥇", "🥈", "🥉"]
    DOT      = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    cols     = st.columns(len(ranked))

    for i, (col, itin) in enumerate(zip(cols, ranked)):
        with col:
            medal = MEDALS[i] if i < len(MEDALS) else f"#{i + 1}"
            # st.metric shows a big number with a label above and a delta below.
            # delta_color="inverse" makes negative deltas green (less cash = good).
            st.metric(
                label=f"{medal} {itin['name']}",
                value=f"{itin['score']}/100",
                delta=f"-${itin['total_cash']} cash",
                delta_color="inverse",
            )
            st.caption(" → ".join(c for c, _ in itin["stops"]))
            st.caption(itin["dates"]["label"])
            st.caption(f"{DOT.get(itin['award_likelihood'], '')} Award space: {itin['award_likelihood']}")

    st.divider()

    # ── Live Web Context Used ─────────────────────────────────────────────────
    # This section is always shown and expanded so users can see what real-world
    # data was used — or wasn't — when building this plan.
    wc = st.session_state.get("web_context", {})

    if wc.get("live"):
        search_count = len([s for s in wc.get("searches", []) if s.get("results")])
        ctx_header   = f"🌐 Live Web Context Used  ·  ✅ Tavily API active  ·  {search_count} searches ran"
    else:
        ctx_header   = "🌐 Live Web Context Used  ·  ⚠️ Tavily API key not set — no live searches ran"

    with st.expander(ctx_header, expanded=True):
        searches = wc.get("searches", [])

        if not searches:
            st.info("No web searches were run. Add a TAVILY_API_KEY to your .env file to enable live search.")
        else:
            KEYWORDS = {"point", "mile", "award", "saver", "availability", "seat",
                        "marriott", "bonvoy", "transfer", "partner", "suite", "family"}

            for idx, search in enumerate(searches, 1):
                results = search.get("results", [])
                label   = search.get("label", f"Search {idx}")
                query   = search.get("query", "")

                # Section header + query pill
                st.markdown(f"**{idx}. {label}**")
                st.code(query, language=None)

                if not results:
                    st.caption("No results returned (API may be offline or key invalid).")
                else:
                    for r in results:
                        title   = r.get("title", "").strip()
                        url     = r.get("url", "")
                        content = r.get("content", "")

                        # Pick the most informative sentence — prefer ones with travel keywords
                        sentences = [s.strip() for s in content.split(". ") if len(s.strip()) > 50]
                        snippet   = next(
                            (s for s in sentences if any(k in s.lower() for k in KEYWORDS)),
                            sentences[0] if sentences else content[:150],
                        )

                        # Source line: linked title + snippet below
                        if url:
                            st.markdown(f"&nbsp;&nbsp;📄 [{title or url}]({url})")
                        else:
                            st.markdown(f"&nbsp;&nbsp;📄 {title or '(no title)'}")
                        st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{snippet}.")

                if idx < len(searches):
                    st.markdown("---")

    st.divider()

    # --- Detailed card for each itinerary ---
    # st.expander creates a collapsible section.
    # expanded=True means the winner starts open; others start collapsed.
    for i, itin in enumerate(ranked):
        medal = MEDALS[i] if i < len(MEDALS) else f"#{i + 1}"
        header = (
            f"{medal} {itin['name']} — "
            f"{itin['score']}/100 · {itin['pace'].title()} pace · ~${itin['total_cash']} cash"
        )
        with st.expander(header, expanded=(i == 0)):

            # Five key numbers in a row
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Score",          f"{itin['score']}/100")
            c2.metric("Family comfort", f"{itin['family_comfort']}/10")
            c3.metric("Pace",           itin["pace"].title())
            c4.metric("Hotel changes",  itin["moves"])
            c5.metric("Cash needed",    f"${itin['total_cash']}")

            st.markdown(
                f"**Dates:** {itin['dates']['label']}  \n"
                f"**Why these dates:** {itin['date_reason']}  \n"
                f"**Award space:** {DOT.get(itin['award_likelihood'], '')} {itin['award_likelihood']}"
            )

            # Pros and cons side by side
            st.divider()
            pro_col, con_col = st.columns(2)
            with pro_col:
                st.markdown("**Pros**")
                for p in itin["pros"]:
                    st.markdown(f"- ✅ {p}")
            with con_col:
                st.markdown("**Cons**")
                for c in (itin["cons"] or ["None worth flagging"]):
                    st.markdown(f"- ⚠️ {c}")

            # Flights
            st.divider()
            st.markdown("**Flights**")
            fp = itin["flight_plan"]
            st.markdown(f"- {fp['outbound']}")
            st.markdown(f"- {fp['return']}")
            if fp["intra_cash"]:
                st.markdown(f"- Intra-Europe transit: ~${fp['intra_cash']}")
            if fp["amex_short"]:
                st.warning(f"{fp['amex_short']:,} MR short — ~${fp['flight_cash_overflow']} extra cash needed")

            # Hotels
            st.markdown("**Hotels**")
            hp = itin["hotel_plan"]
            for line in hp["lines"]:
                st.markdown(f"- {line}")
            st.caption(
                f"Certs used: {hp['certs_used']}  ·  "
                f"Bonvoy pts: {hp['points_used']:,}  ·  "
                f"Hotel cash: ${hp['cash_for_hotels']}  ·  "
                f"Avg room: {hp['avg_sqft']:.0f} sqft"
            )

            # Score breakdown — one more nested expander inside the card
            with st.expander("How the score was calculated"):
                for line in itin["breakdown"]:
                    st.markdown(f"- {line}")

            # Data quality — honest labelling of where each number comes from
            with st.expander("Data quality — live vs. config vs. estimated"):
                cities_in_route = [c for c, _ in itin["stops"]]
                fp = itin["flight_plan"]
                intra_legs = itin["transit"][1:-1]  # skip transatlantic outbound/return

                dq_live, dq_config, dq_est = st.columns(3)

                with dq_live:
                    st.markdown("**🌐 Live web (Tavily)**")
                    award_results = itin.get("award_web", [])
                    if award_results:
                        st.markdown(
                            f"- Award availability search: "
                            f"✅ {len(award_results)} result(s)"
                        )
                        st.caption(f"_{itin.get('award_web_query', '')}_")
                    else:
                        st.markdown("- Award availability: ⚠️ no live data")
                        st.caption("Set TAVILY_API_KEY in .env to enable")
                    st.markdown("- Flight & hotel strategy tips: see *Live Web Context* above")

                with dq_config:
                    st.markdown("**📁 Config** (`config/hotels.yaml`)")
                    for city in cities_in_route:
                        info = engine.CITY_DATA[city]
                        st.markdown(
                            f"- **{city}:** {info['hotel']}  \n"
                            f"  {info['sqft']} sqft · "
                            f"{info['points_per_night']:,} pts/night · "
                            f"${info['cash_per_night']}/night cash"
                        )

                with dq_est:
                    st.markdown("**〜 Estimated / rule-of-thumb**")
                    # Amex MR award rates
                    first_city = itin["stops"][0][0]
                    last_city  = itin["stops"][-1][0]
                    out_airline, out_pp = engine.AMEX_FLIGHT_OPTIONS[first_city]
                    ret_airline, ret_pp = engine.AMEX_FLIGHT_OPTIONS[last_city]
                    st.markdown(
                        f"- Outbound award: ~{out_pp:,} MR/person "
                        f"({out_airline}, typical off-peak — not live)"
                    )
                    st.markdown(
                        f"- Return award: ~{ret_pp:,} MR/person "
                        f"({ret_airline}, typical off-peak — not live)"
                    )
                    # Intra-Europe transit cash estimates
                    transit_estimates = {
                        "Eurostar": "$180/person",
                        "Thalys":   "$130/person",
                        "TGV":      "$120/person",
                        "Short flight": "$150/person",
                    }
                    for leg in intra_legs:
                        for keyword, est in transit_estimates.items():
                            if keyword in leg:
                                leg_short = leg.split("(")[0].strip()
                                st.markdown(f"- {leg_short}: ~{est} (estimate)")
                                break
                    st.markdown(
                        "- Award space likelihood: formula using a 1–3 "
                        "city score + departure-day adjustment (not live inventory)"
                    )

            # Day-by-day plan — only for the winner to keep the page manageable
            if i == 0:
                st.divider()
                st.markdown("**Day-by-day plan**")
                for day in engine.get_day_plan(itin):
                    with st.expander(f"Day {day['day']} · {day['date_str']} · {day['city']}"):
                        st.markdown(f"**Main activity:** {day['main']}")
                        st.markdown(f"**Lighter option:** {day['lighter']}")
                        st.markdown(f"*{day['family']}*")
                        if day.get("points_note"):
                            st.info(day["points_note"])

    # --- Agent log ---
    with st.expander("Agent log (what happened behind the scenes)"):
        st.code(st.session_state.log, language=None)

# ── Welcome / empty state ─────────────────────────────────────────────────────
# This block only runs when there are no results yet.
else:
    st.info("Fill in your trip details on the left and click **Run Search** to get started.")

    st.markdown("""
    **What happens when you search:**

    1. **Date agent** — picks the best departure weekends in your travel window
    2. **Itinerary agent** — builds 3 route options (2-city, 3-city train loop, 3-city triangle)
    3. **Flight agent** — plans transatlantic flights using your Amex MR points
    4. **Hotel agent** — allocates Marriott free-night certs, then Bonvoy points, then cash
    5. **Flow agent** — scores how smooth the city-to-city travel is
    6. **Scoring agent** — combines everything into a 0–100 family-tuned score
    7. **Day-plan agent** — builds a full day-by-day calendar for the winner

    All 7 agents run in sequence and hand their output to the next one.
    """)
