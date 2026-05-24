import contextlib
import io
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main as engine

st.set_page_config(
    page_title="Travel Points Planner",
    page_icon="✈️",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("✈️ Travel Points Planner")
st.caption(
    "Enter your points balances, travelers, and destination ideas — "
    "get back ranked itinerary options with flights, hotels, and a day-by-day plan."
)

# ── Sidebar: inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Trip Details")

    st.subheader("Destination & Dates")
    origin = st.text_input("Origin airport", value="SFO")
    year = st.number_input("Travel year", min_value=2025, max_value=2030, value=2026, step=1)
    col1, col2 = st.columns(2)
    min_days = col1.number_input("Min days", min_value=5, max_value=21, value=7)
    max_days = col2.number_input("Max days", min_value=5, max_value=21, value=10)

    st.subheader("Travelers")
    col1, col2 = st.columns(2)
    adults = col1.number_input("Adults", min_value=1, max_value=8, value=2)
    kids = col2.number_input("Kids", min_value=0, max_value=6, value=2)
    if int(kids) > 0:
        kids_ages_str = st.text_input(
            "Kids ages (comma-separated)", value="14, 11", help="Example: 14, 11"
        )
    else:
        kids_ages_str = ""

    st.subheader("Cities")
    available_cities = list(engine.CITY_DATA.keys())
    required_cities = st.multiselect(
        "Required cities", available_cities, default=["London", "Paris"]
    )
    optional_cities = st.multiselect(
        "Optional cities",
        [c for c in available_cities if c not in required_cities],
        default=[c for c in ["Rome", "Amsterdam", "Barcelona"] if c not in required_cities],
    )
    st.caption("Route templates are preset. City selection affects scoring.")

    st.subheader("Points & Certs")
    amex_mr = st.number_input("Amex MR points", min_value=0, step=10_000, value=200_000)
    col1, col2 = st.columns(2)
    free_nights = col1.number_input("Free night certs", min_value=0, max_value=30, value=5)
    bonvoy_points = col2.number_input("Bonvoy points", min_value=0, step=10_000, value=250_000)

    st.divider()
    run_clicked = st.button("🔍  Run Search", use_container_width=True, type="primary")

# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.log = ""

# ── Run agents ────────────────────────────────────────────────────────────────
if run_clicked:
    n_kids = int(kids)
    if n_kids > 0 and kids_ages_str.strip():
        try:
            kids_ages = [int(a.strip()) for a in kids_ages_str.split(",") if a.strip()]
        except ValueError:
            kids_ages = [10] * n_kids
        while len(kids_ages) < max(n_kids, 2):
            kids_ages.append(10)
    else:
        kids_ages = [10, 10]

    profile = {
        "origin": origin,
        "travel_window": "late July through early August",
        "trip_length_days": f"{int(min_days)} to {int(max_days)}",
        "travelers": {
            "adults": int(adults),
            "kids": n_kids,
            "kids_ages": kids_ages,
        },
        "trip_type": "family" if n_kids > 0 else "couple",
        "required_cities": required_cities,
        "optional_cities": optional_cities,
        "avoid_cities": [],
        "total_cities": "2 or 3",
        "points": {
            "amex_mr": int(amex_mr),
            "marriott_free_nights": int(free_nights),
            "bonvoy_points": int(bonvoy_points),
        },
        "strategy": {
            "flight": "Use Amex Membership Rewards points with strong transfer partners (Flying Blue, Virgin Atlantic, etc.)",
            "hotel": "Use Marriott free nights first, then Bonvoy points, then cash if needed",
        },
        "preferences": {
            "optimize_for": "best mix of quality, convenience, and value",
            "not_just_cheapest": True,
            "family_friendly": n_kids > 0,
            "fewer_hotel_changes": True,
            "efficient_city_flow": True,
            "preferred_departure_days": ["Friday", "Saturday", "Sunday"],
            "flexible_for_better_deal": True,
        },
        "hotel_requirements": {
            "rooms": 1,
            "room_type_preference": ["suite", "junior suite", "large room with sofa bed"],
            "prioritize_large_square_footage": True,
            "family_of_4_comfort": n_kids > 0,
            "avoid_small_rooms": True,
        },
        "travel_style": {
            "pace": "moderate to relaxed",
            "avoid_rushed_itineraries": True,
            "prefer_trains_over_short_flights": True,
        },
    }

    with st.spinner("Running travel agents..."):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ranked = engine.run_plan(profile, year=int(year))
        st.session_state.results = ranked
        st.session_state.log = buf.getvalue()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.results:
    ranked = st.session_state.results
    winner = ranked[0]

    st.success(
        f"**Winner: {winner['name']}** — {winner['score']}/100 | "
        f"{' → '.join(c for c, _ in winner['stops'])} | "
        f"{winner['dates']['label']} | ~${winner['total_cash']} cash needed"
    )

    # Quick-compare row
    st.subheader("All Options")
    medals = ["🥇", "🥈", "🥉"]
    avail_dot = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    cols = st.columns(len(ranked))
    for i, (col, itin) in enumerate(zip(cols, ranked)):
        with col:
            st.metric(
                label=f"{medals[i] if i < 3 else f'#{i+1}'} {itin['name']}",
                value=f"{itin['score']}/100",
                delta=f"-${itin['total_cash']} cash",
                delta_color="inverse",
            )
            st.caption(" → ".join(c for c, _ in itin["stops"]))
            st.caption(itin["dates"]["label"])
            st.caption(
                f"{avail_dot.get(itin['award_likelihood'], '')} "
                f"Award space: {itin['award_likelihood']}"
            )

    st.divider()

    # Detailed cards
    for i, itin in enumerate(ranked):
        label = (
            f"{medals[i] if i < 3 else f'#{i+1}'} {itin['name']} — "
            f"{itin['score']}/100 | {itin['pace'].title()} pace | ~${itin['total_cash']} cash"
        )
        with st.expander(label, expanded=(i == 0)):

            # Top metrics
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Score", f"{itin['score']}/100")
            m2.metric("Family comfort", f"{itin['family_comfort']}/10")
            m3.metric("Pace", itin["pace"].title())
            m4.metric("Hotel changes", itin["moves"])
            m5.metric("Cash needed", f"${itin['total_cash']}")

            st.markdown(
                f"**Dates:** {itin['dates']['label']}  \n"
                f"**Departure logic:** {itin['date_reason']}  \n"
                f"**Award space:** {avail_dot.get(itin['award_likelihood'], '')} {itin['award_likelihood']}"
            )

            # Pros / Cons
            st.divider()
            pc1, pc2 = st.columns(2)
            with pc1:
                st.markdown("**Pros**")
                for p in itin["pros"]:
                    st.markdown(f"- ✅ {p}")
            with pc2:
                st.markdown("**Cons**")
                for c in (itin["cons"] or ["None worth flagging"]):
                    st.markdown(f"- ⚠️ {c}")

            # Flights
            st.divider()
            st.markdown("**Flights (Amex MR)**")
            fp = itin["flight_plan"]
            st.markdown(f"- {fp['outbound']}")
            st.markdown(f"- {fp['return']}")
            if fp["intra_cash"]:
                st.markdown(f"- Intra-Europe transit: ~${fp['intra_cash']}")
            if fp["amex_short"]:
                st.warning(
                    f"⚠️ {fp['amex_short']:,} MR short — ~${fp['flight_cash_overflow']} extra cash needed"
                )

            # Hotels
            st.markdown("**Hotels (Marriott)**")
            hp = itin["hotel_plan"]
            for line in hp["lines"]:
                st.markdown(f"- {line}")
            st.caption(
                f"Certs used: {hp['certs_used']}  |  "
                f"Bonvoy points used: {hp['points_used']:,}  |  "
                f"Cash for hotels: ${hp['cash_for_hotels']}  |  "
                f"Avg room: {hp['avg_sqft']:.0f} sqft  |  "
                f"Smallest: {hp['smallest_sqft']:.0f} sqft"
            )

            # Score breakdown
            with st.expander("Score breakdown"):
                for b in itin["breakdown"]:
                    st.markdown(f"- {b}")

            # Day-by-day (winner only)
            if i == 0:
                st.divider()
                st.markdown("**Day-by-day plan**")
                for day in engine.get_day_plan(itin):
                    with st.expander(f"Day {day['day']} ({day['date_str']}) — {day['city']}"):
                        st.markdown(f"**Main:** {day['main']}")
                        st.markdown(f"**Lighter:** {day['lighter']}")
                        st.markdown(f"*{day['family']}*")
                        if day.get("points_note"):
                            st.info(day["points_note"])

    # Debug log
    with st.expander("Agent log"):
        st.code(st.session_state.log, language=None)

# ── Welcome state ─────────────────────────────────────────────────────────────
else:
    st.markdown(
        """
        Configure your trip in the sidebar and click **Run Search**.

        **What the planner does:**
        1. Generates candidate departure dates (weekends + mid-week deal-hunter)
        2. Evaluates 3 route options across 2–3 European cities
        3. Plans transatlantic flights with your Amex MR points (Flying Blue, Virgin Atlantic, etc.)
        4. Plans hotels using Marriott free-night certs → Bonvoy points → cash fallback
        5. Scores each option 0–100 on a family-tuned scale (required cities, pace, comfort, cash outlay)
        6. Returns ranked results with a full day-by-day plan for the winner

        **Scoring factors:** required cities, travel flow, Amex MR utilization, Marriott strategy,
        family comfort, pace, hotel quality, cash outlay, room-size and hotel-change penalties.
        """
    )
