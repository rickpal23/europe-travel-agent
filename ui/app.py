# ui/app.py — Travel Points Planner

import contextlib
import io
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import main as engine

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Points Planner",
    page_icon="✈️",
    layout="wide",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
# All visual styling lives here. Nothing below this block sets colors or
# font sizes directly — it only assigns CSS class names from this block.
_CSS = """<style>

/* Reduce Streamlit's default top padding */
.block-container { padding-top: 1.6rem !important; padding-bottom: 2rem !important; }

/* ── Winner hero card ─────────────────────────────────────────────────────── */
.hero {
    background: linear-gradient(140deg, #eef2ff 0%, #f8faff 100%);
    border: 1.5px solid #c7d2f8;
    border-radius: 20px;
    padding: 32px 36px 28px;
    margin-bottom: 10px;
}
.hero-eye {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 10px;
}
.hero-title {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.025em;
    line-height: 1.15;
    margin-bottom: 4px;
}
.hero-sub {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 24px;
}
.kv-row { display: flex; gap: 32px; flex-wrap: wrap; }
.kv     { display: flex; flex-direction: column; gap: 3px; }
.kv-l {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
}
.kv-v {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
    line-height: 1.15;
}

/* ── Option comparison tile ───────────────────────────────────────────────── */
.tile {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px 16px 18px;
    height: 100%;
    box-sizing: border-box;
}
.tile-win { border-color: #c7d2f8; background: #f5f7ff; }
.t-rank {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 4px;
}
.t-name {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 2px;
    line-height: 1.2;
}
.t-cities { font-size: 12px; color: #9ca3af; margin-bottom: 14px; }
.t-score  { font-size: 38px; font-weight: 900; color: #111827; line-height: 1; }
.t-score-lbl { font-size: 11px; color: #9ca3af; margin-bottom: 6px; }
.pills   { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.pill    { display: inline-block; background: #f3f4f6; border-radius: 100px; padding: 3px 9px; font-size: 11.5px; color: #374151; }
.pill-g  { background: #dcfce7; color: #166534; }
.pill-y  { background: #fef9c3; color: #713f12; }
.pill-r  { background: #fee2e2; color: #991b1b; }

/* ── Seats.aero block ─────────────────────────────────────────────────────── */
.sa-blk { border-radius: 12px; padding: 14px 16px; line-height: 1.4; }
.sa-yes { background: #f0fdf4; border: 1px solid #86efac; }
.sa-no  { background: #fff5f5; border: 1px solid #fca5a5; }
.sa-est { background: #f9fafb; border: 1px solid #e5e7eb; }
.sa-dir {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 5px;
}
.sa-hl  { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 3px; }
.sa-dt  { font-size: 12px; color: #6b7280; }

/* ── Research note box ────────────────────────────────────────────────────── */
.note-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px 14px;
    height: 100%;
    box-sizing: border-box;
}
.note-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 5px;
}
.note-txt { font-size: 13px; color: #374151; line-height: 1.55; }

/* ── Pros / Cons ──────────────────────────────────────────────────────────── */
.pro { font-size: 13.5px; color: #166534; padding: 3px 0; }
.con { font-size: 13.5px; color: #991b1b;  padding: 3px 0; }

/* ── Section sub-label ────────────────────────────────────────────────────── */
.sub-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    padding-top: 20px;
    margin-bottom: 8px;
}

/* ── Web context summary ──────────────────────────────────────────────────── */
.wc-item { padding: 8px 0; border-bottom: 1px solid #f3f4f6; }
.wc-item:last-child { border-bottom: none; }
.wc-lbl { font-size: 10px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: #9ca3af; margin-bottom: 3px; }
.wc-txt { font-size: 13.5px; color: #374151; line-height: 1.5; }

/* ── Welcome steps ────────────────────────────────────────────────────────── */
.step {
    display: flex;
    gap: 14px;
    padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
    align-items: flex-start;
}
.step:last-child { border-bottom: none; }
.step-n {
    font-size: 11px;
    font-weight: 800;
    color: #6366f1;
    background: #eef2ff;
    border-radius: 6px;
    padding: 2px 8px;
    white-space: nowrap;
    margin-top: 2px;
}
.step-t { font-size: 14px; color: #374151; line-height: 1.5; }

</style>"""
st.markdown(_CSS, unsafe_allow_html=True)


# ── Constants ──────────────────────────────────────────────────────────────────
MEDALS   = ["🥇", "🥈", "🥉"]
DOT      = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
PILL_CLS = {"High": "pill-g", "Medium": "pill-y", "Low": "pill-r"}
_TAVILY_KWS = {
    "point", "mile", "award", "saver", "availability",
    "seat", "marriott", "bonvoy", "transfer", "partner", "suite", "family",
}


# ── Helper functions (pure display, no planning logic) ─────────────────────────

def _trunc(text: str, n: int = 130) -> str:
    """Cut to n chars at a word boundary."""
    if not text or len(text) <= n:
        return text or ""
    return text[:n].rsplit(" ", 1)[0] + "…"


def _best_sentence(results: list, keywords=None) -> str:
    """Pick the first informative sentence from Tavily results."""
    kws = {k.lower() for k in (keywords or [])}
    for r in results:
        for s in r.get("content", "").split(". "):
            s = s.strip()
            if len(s) < 50:
                continue
            if not kws or any(k in s.lower() for k in kws):
                return s
    for r in results[:1]:
        for s in r.get("content", "").split(". "):
            if len(s.strip()) > 50:
                return s.strip()
    return ""


def render_winner_hero(w: dict) -> None:
    cities = " → ".join(c for c, _ in w["stops"])
    avail  = w["award_likelihood"]
    pts    = w["flight_plan"]["amex_used"] + w["hotel_plan"]["points_used"]
    st.markdown(f"""
<div class="hero">
  <div class="hero-eye">✦ &nbsp;Top Pick</div>
  <div class="hero-title">{w['name']}</div>
  <div class="hero-sub">{cities} &nbsp;·&nbsp; {w['dates']['label']}</div>
  <div class="kv-row">
    <div class="kv"><span class="kv-l">Score</span>
                    <span class="kv-v">{w['score']}/100</span></div>
    <div class="kv"><span class="kv-l">Cash needed</span>
                    <span class="kv-v">${w['total_cash']:,}</span></div>
    <div class="kv"><span class="kv-l">Hotel changes</span>
                    <span class="kv-v">{w['moves']}</span></div>
    <div class="kv"><span class="kv-l">Award space</span>
                    <span class="kv-v">{DOT.get(avail,'')} {avail}</span></div>
    <div class="kv"><span class="kv-l">Pace</span>
                    <span class="kv-v">{w['pace'].title()}</span></div>
    <div class="kv"><span class="kv-l">Points used</span>
                    <span class="kv-v">{pts:,}</span></div>
  </div>
</div>""", unsafe_allow_html=True)


def render_option_tile(col, itin: dict, rank: int) -> None:
    medal  = MEDALS[rank] if rank < len(MEDALS) else f"#{rank+1}"
    cities = " → ".join(c for c, _ in itin["stops"])
    avail  = itin["award_likelihood"]
    tc     = "tile tile-win" if rank == 0 else "tile"
    pc     = PILL_CLS.get(avail, "")
    col.markdown(f"""
<div class="{tc}">
  <div class="t-rank">{medal} {'Winner' if rank==0 else 'Option '+str(rank+1)}</div>
  <div class="t-name">{itin['name']}</div>
  <div class="t-cities">{cities}</div>
  <div class="t-score">{itin['score']}</div>
  <div class="t-score-lbl">/ 100</div>
  <div class="pills">
    <span class="pill">${itin['total_cash']:,}</span>
    <span class="pill {pc}">{DOT.get(avail,'')} {avail}</span>
    <span class="pill">{itin['moves']} hotel change{'s' if itin['moves']!=1 else ''}</span>
    <span class="pill">{itin['pace'].title()}</span>
  </div>
</div>""", unsafe_allow_html=True)


def render_sa_leg(col, sa: dict, direction: str) -> None:
    """One Seats.aero leg: outbound or return."""
    with col:
        if sa.get("source") == "seats.aero" and sa.get("available"):
            pts_str  = f"{sa['lowest_points']:,} pts" if sa.get("lowest_points") else ""
            prog     = sa.get("program", "")
            dates    = ", ".join(sa.get("dates_with_space", [])[:3])
            detail   = " · ".join(p for p in [prog, pts_str] if p)
            dates_ln = f"<div class='sa-dt' style='margin-top:3px'>Sample: {dates}</div>" if dates else ""
            st.markdown(f"""
<div class="sa-blk sa-yes">
  <div class="sa-dir">{direction} &nbsp;·&nbsp; {sa['route']}</div>
  <div class="sa-hl">✅ &nbsp;{sa['seat_count']} date(s) with economy space</div>
  <div class="sa-dt">{detail}</div>
  {dates_ln}
</div>""", unsafe_allow_html=True)

        elif sa.get("source") == "seats.aero":
            st.markdown(f"""
<div class="sa-blk sa-no">
  <div class="sa-dir">{direction} &nbsp;·&nbsp; {sa['route']}</div>
  <div class="sa-hl">❌ &nbsp;No economy award space found</div>
  <div class="sa-dt">Try nearby dates or a different program.</div>
</div>""", unsafe_allow_html=True)

        else:
            err = sa.get("error") or "Set SEATS_AERO_API_KEY in .env for live data."
            st.markdown(f"""
<div class="sa-blk sa-est">
  <div class="sa-dir">{direction} &nbsp;·&nbsp; {sa.get('route', '—')}</div>
  <div class="sa-hl" style="color:#6b7280;">〜 &nbsp;Estimated</div>
  <div class="sa-dt">{err}</div>
</div>""", unsafe_allow_html=True)


def render_research_notes(notes: dict) -> None:
    """Three compact note boxes and an optional confidence badge."""
    items = [
        ("✈️ Flight award",    notes.get("flight",   "")),
        ("🏨 Hotel & family",  notes.get("hotel",    "")),
        ("💡 Points strategy", notes.get("strategy", "")),
    ]
    cols = st.columns(3)
    for col, (lbl, text) in zip(cols, items):
        with col:
            st.markdown(f"""
<div class="note-box">
  <div class="note-lbl">{lbl}</div>
  <div class="note-txt">{_trunc(text)}</div>
</div>""", unsafe_allow_html=True)

    confidence = notes.get("confidence", "")
    if confidence:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if notes.get("has_warnings"):
            st.warning(confidence)
        elif "high" in confidence.lower() and "live" in confidence.lower():
            st.success(confidence)
        else:
            st.info(confidence)


def render_pros_cons(pros: list, cons: list) -> None:
    pc, cc = st.columns(2)
    with pc:
        st.markdown('<div class="sub-lbl">Strengths</div>', unsafe_allow_html=True)
        for p in pros:
            st.markdown(f'<div class="pro">✓ &nbsp;{p}</div>', unsafe_allow_html=True)
    with cc:
        st.markdown('<div class="sub-lbl">Watch-outs</div>', unsafe_allow_html=True)
        for c in (cons or ["None worth flagging"]):
            st.markdown(f'<div class="con">· &nbsp;{c}</div>', unsafe_allow_html=True)


def render_web_context(wc: dict) -> None:
    """Collapsed plain-English research summary — no source links."""
    searches = wc.get("searches", [])
    live     = wc.get("live", False)
    count    = sum(1 for s in searches if s.get("results")) if live else 0

    header = (
        f"🌐 Research &nbsp;·&nbsp; {count} live search{'es' if count != 1 else ''} completed"
        if live else
        "🌐 Research &nbsp;·&nbsp; ⚠️ Tavily key not set — estimates only"
    )

    with st.expander(header, expanded=False):
        if not live or not searches:
            st.caption("Add TAVILY_API_KEY to your .env to enable live research.")
            return

        html_items = ""
        for s in searches:
            results = s.get("results", [])
            lbl     = s.get("label", "")
            if not results:
                continue
            sentence = _best_sentence(results, list(_TAVILY_KWS))
            if sentence:
                html_items += (
                    f'<div class="wc-item">'
                    f'<div class="wc-lbl">{lbl}</div>'
                    f'<div class="wc-txt">{_trunc(sentence, 220)}.</div>'
                    f'</div>'
                )

        if html_items:
            st.markdown(
                f'<div style="padding:4px 0">{html_items}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Searches ran but no relevant snippets were found.")


# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("## ✈️ Travel Points Planner")
st.caption("Enter your trip details on the left and click **Run Search** to rank your best Europe itinerary options.")


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Your Trip")

    st.subheader("Origin & Dates")
    origin = st.text_input(
        label="Departing from (airport code)",
        value="SFO",
        help="3-letter IATA code, e.g. SFO, JFK, LAX",
    )
    year = st.number_input(
        label="Travel year",
        min_value=2025, max_value=2030, value=2026, step=1,
    )
    col_a, col_b = st.columns(2)
    min_days = col_a.number_input("Min days", min_value=5, max_value=21, value=7)
    max_days = col_b.number_input("Max days", min_value=5, max_value=21, value=10)

    st.subheader("Travelers")
    col_a, col_b = st.columns(2)
    adults = col_a.number_input("Adults", min_value=1, max_value=8, value=2)
    kids   = col_b.number_input("Kids",   min_value=0, max_value=6, value=2)
    if int(kids) > 0:
        kids_ages_raw = st.text_input(
            label="Kids' ages (comma-separated)",
            value="14, 11",
            help="Example: 14, 11",
        )
    else:
        kids_ages_raw = ""

    st.subheader("Cities")
    all_cities = list(engine.CITY_DATA.keys())
    required_cities = st.multiselect(
        label="Must-visit cities",
        options=all_cities,
        default=["London", "Paris"],
        help="Missing a required city penalises the score.",
    )
    optional_cities = st.multiselect(
        label="Nice-to-have cities",
        options=[c for c in all_cities if c not in required_cities],
        default=[c for c in ["Rome", "Amsterdam", "Barcelona"] if c not in required_cities],
    )

    st.subheader("Trip Style")
    trip_style = st.radio(
        "How do you want to travel?",
        options=["relaxed", "balanced", "maximize"],
        index=1,
        horizontal=True,
        help=(
            "**relaxed** — up to 2 cities, 4+ nights each  \n"
            "**balanced** — up to 3 cities, good mix of depth and variety  \n"
            "**maximize** — up to 5 cities, see as much as possible"
        ),
    )
    st.caption(
        "relaxed: deep + slow · balanced: 2–3 cities · maximize: pack it in"
    )

    st.subheader("Points & Certs")
    amex_mr = st.number_input(
        label="Amex MR points",
        min_value=0, step=10_000, value=200_000,
    )
    col_a, col_b = st.columns(2)
    free_nights   = col_a.number_input("Free night certs", min_value=0, max_value=30, value=5)
    bonvoy_points = col_b.number_input("Bonvoy points",    min_value=0, step=10_000, value=250_000)

    st.divider()
    run_clicked = st.button(
        label="🔍  Run Search",
        use_container_width=True,
        type="primary",
    )


# ── Session state ──────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results     = None
    st.session_state.web_context = {}
    st.session_state.log         = ""


# ── Run agents ─────────────────────────────────────────────────────────────────
if run_clicked:
    n_kids = int(kids)
    if n_kids > 0 and kids_ages_raw.strip():
        try:
            kids_ages = [int(a.strip()) for a in kids_ages_raw.split(",") if a.strip()]
        except ValueError:
            kids_ages = [10] * n_kids
        while len(kids_ages) < max(n_kids, 2):
            kids_ages.append(10)
    else:
        kids_ages = [10, 10]

    profile = {
        "origin":           origin,
        "travel_window":    "late July through early August",
        "trip_length_days": f"{int(min_days)} to {int(max_days)}",
        "travelers": {
            "adults":    int(adults),
            "kids":      n_kids,
            "kids_ages": kids_ages,
        },
        "trip_type":       "family" if n_kids > 0 else "couple",
        "required_cities": required_cities,
        "optional_cities": optional_cities,
        "avoid_cities":    [],
        "total_cities":    "2 or 3",
        "trip_style":      trip_style,
        "points": {
            "amex_mr":              int(amex_mr),
            "marriott_free_nights": int(free_nights),
            "bonvoy_points":        int(bonvoy_points),
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
            "pace":                           "moderate to relaxed",
            "avoid_rushed_itineraries":       True,
            "prefer_trains_over_short_flights": True,
        },
    }

    with st.spinner("Running travel agents…"):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            ranked, web_context = engine.run_plan(profile, year=int(year))
        st.session_state.results     = ranked
        st.session_state.web_context = web_context
        st.session_state.log         = captured.getvalue()


# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.results:
    ranked = st.session_state.results
    winner = ranked[0]

    # 1. Winner hero card
    render_winner_hero(winner)

    # 2. Comparison tiles
    st.markdown('<div class="sub-lbl" style="padding-top:22px">All options</div>', unsafe_allow_html=True)
    tile_cols = st.columns(len(ranked))
    for i, (col, itin) in enumerate(zip(tile_cols, ranked)):
        render_option_tile(col, itin, i)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 3. Research summary (collapsed, plain English, no links)
    render_web_context(st.session_state.get("web_context", {}))

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # 4. Detailed card per itinerary
    for i, itin in enumerate(ranked):
        medal  = MEDALS[i] if i < len(MEDALS) else f"#{i+1}"
        avail  = itin["award_likelihood"]
        cities = " → ".join(c for c, _ in itin["stops"])
        header = (
            f"{medal}  {itin['name']} "
            f"— {itin['score']}/100 · "
            f"${itin['total_cash']:,} cash · "
            f"{DOT.get(avail, '')} {avail} award space"
        )
        with st.expander(header, expanded=(i == 0)):

            # ── Key metrics ───────────────────────────────────────────────────
            pts_total = itin["flight_plan"]["amex_used"] + itin["hotel_plan"]["points_used"]
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("Score",         f"{itin['score']}/100")
            m2.metric("Cash needed",   f"${itin['total_cash']:,}")
            m3.metric("Points used",   f"{pts_total:,}")
            m4.metric("Hotel changes", str(itin["moves"]))
            m5.metric("Pace",          itin["pace"].title())
            m6.metric("Award space",   itin["award_likelihood"])

            st.caption(
                f"📅 {itin['dates']['label']} &nbsp;·&nbsp; "
                f"{itin['date_reason']} &nbsp;·&nbsp; "
                f"{itin['nights']} nights"
            )

            # ── Seats.aero award availability ─────────────────────────────────
            st.markdown('<div class="sub-lbl">Award availability — Seats.aero live data</div>', unsafe_allow_html=True)
            sa_l, sa_r = st.columns(2)
            render_sa_leg(sa_l, itin.get("award_availability", {}),        "Outbound")
            render_sa_leg(sa_r, itin.get("award_availability_return", {}), "Return")

            # ── Research notes ────────────────────────────────────────────────
            notes = itin.get("research_notes", {})
            if notes:
                st.markdown('<div class="sub-lbl">Research notes</div>', unsafe_allow_html=True)
                render_research_notes(notes)

            # ── Pros / Cons ───────────────────────────────────────────────────
            render_pros_cons(itin["pros"], itin["cons"])

            # ── Flights & Hotels (collapsed) ──────────────────────────────────
            fp = itin["flight_plan"]
            hp = itin["hotel_plan"]
            with st.expander("Flights & Hotels"):
                st.markdown("**Transatlantic flights**")
                st.markdown(f"- {fp['outbound']}")
                st.markdown(f"- {fp['return']}")
                if fp["intra_cash"]:
                    st.caption(f"Intra-Europe transit: ~${fp['intra_cash']}")
                if fp["amex_short"]:
                    st.warning(
                        f"{fp['amex_short']:,} MR short — "
                        f"~${fp['flight_cash_overflow']} extra cash needed"
                    )
                st.markdown("**Hotels**")
                for line in hp["lines"]:
                    st.markdown(f"- {line}")
                st.caption(
                    f"Certs: {hp['certs_used']} &nbsp;·&nbsp; "
                    f"Bonvoy: {hp['points_used']:,} pts &nbsp;·&nbsp; "
                    f"Hotel cash: ${hp['cash_for_hotels']} &nbsp;·&nbsp; "
                    f"Avg room: {hp['avg_sqft']:.0f} sqft"
                )

            # ── Score breakdown (collapsed) ───────────────────────────────────
            with st.expander("Score breakdown"):
                for line in itin["breakdown"]:
                    st.markdown(f"- {line}")

            # ── Data quality (collapsed) ──────────────────────────────────────
            with st.expander("Data quality — live vs. config vs. estimated"):
                cities_in_route = [c for c, _ in itin["stops"]]
                intra_legs      = itin["transit"][1:-1]

                dq1, dq2, dq3 = st.columns(3)

                with dq1:
                    st.markdown("**🌐 Live (Seats.aero + Tavily)**")
                    sa_o = itin.get("award_availability", {})
                    sa_rt = itin.get("award_availability_return", {})
                    if sa_o.get("source") == "seats.aero":
                        for sa, leg in [(sa_o, "Out"), (sa_rt, "Ret")]:
                            if sa.get("available"):
                                pts_s = f" · {sa['lowest_points']:,} pts" if sa.get("lowest_points") else ""
                                st.markdown(f"- {leg} {sa['route']}: ✅ {sa['seat_count']} dates{pts_s}")
                            else:
                                st.markdown(f"- {leg} {sa['route']}: ❌ no space")
                    else:
                        st.markdown("- Award space: 〜 estimated")
                        st.caption(sa_o.get("error", ""))
                    award_r = itin.get("award_web", [])
                    st.markdown(f"- Tavily award search: {'✅ '+str(len(award_r))+' result(s)' if award_r else '⚠️ none'}")

                with dq2:
                    st.markdown("**📁 Config** (hotels.yaml)")
                    for city in cities_in_route:
                        info = engine.CITY_DATA[city]
                        st.markdown(
                            f"- **{city}:** {info['sqft']} sqft · "
                            f"{info['points_per_night']:,} pts/night · "
                            f"${info['cash_per_night']}/night"
                        )

                with dq3:
                    st.markdown("**〜 Estimated**")
                    fc = itin["stops"][0][0]
                    lc = itin["stops"][-1][0]
                    oa, opp = engine.AMEX_FLIGHT_OPTIONS[fc]
                    ra, rpp = engine.AMEX_FLIGHT_OPTIONS[lc]
                    st.markdown(f"- Out: ~{opp:,} MR/pp ({oa})")
                    st.markdown(f"- Ret: ~{rpp:,} MR/pp ({ra})")
                    for leg in intra_legs:
                        for kw, est in [
                            ("Eurostar", "$180"), ("Thalys", "$130"),
                            ("TGV", "$120"), ("Short flight", "$150"),
                        ]:
                            if kw in leg:
                                st.markdown(f"- {leg.split('(')[0].strip()}: ~{est}/person")
                                break

            # ── Day-by-day plan (winner only) ─────────────────────────────────
            if i == 0:
                st.markdown('<div class="sub-lbl">Day-by-day plan</div>', unsafe_allow_html=True)
                for day in engine.get_day_plan(itin):
                    with st.expander(
                        f"Day {day['day']} · {day['date_str']} · {day['city']}"
                    ):
                        st.markdown(f"**Main:** {day['main']}")
                        st.markdown(f"**Lighter:** {day['lighter']}")
                        st.caption(day["family"])
                        if day.get("points_note"):
                            st.info(day["points_note"])

    # Agent log
    with st.expander("Agent log"):
        st.code(st.session_state.log, language=None)


# ── Welcome / empty state ──────────────────────────────────────────────────────
else:
    st.markdown(
        "<div style='color:#6b7280;font-size:15px;margin-bottom:20px'>"
        "Fill in your trip details on the left and click <strong>Run Search</strong>."
        "</div>",
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "Date agent",      "Picks the best departure weekends in your travel window."),
        ("2", "Itinerary agent", "Builds route options from your required + nice-to-have cities."),
        ("3", "Flight agent",    "Plans transatlantic flights using your Amex MR points."),
        ("4", "Hotel agent",     "Allocates Marriott free-night certs, then Bonvoy points, then cash."),
        ("5", "Flow agent",      "Scores how smooth the city-to-city routing is."),
        ("6", "Scoring agent",   "Combines all signals into a 0–100 family-tuned score."),
        ("7", "Day-plan agent",  "Builds a full day-by-day calendar for the winning itinerary."),
    ]
    html = "".join(
        f'<div class="step">'
        f'<span class="step-n">{n}</span>'
        f'<span class="step-t"><strong>{name}</strong> — {desc}</span>'
        f'</div>'
        for n, name, desc in steps
    )
    st.markdown(
        f'<div style="max-width:580px">{html}</div>',
        unsafe_allow_html=True,
    )
