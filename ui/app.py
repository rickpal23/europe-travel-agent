# ui/app.py — Travel Points Planner

import contextlib
import io
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import main as engine
from data import profile as profile_store

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Points Planner",
    page_icon="✈️",
    layout="centered",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
# Rules only for custom HTML elements — we do NOT override Streamlit's widget
# theme (background, input colors, label colors) because that causes dark-mode
# conflicts and unreadable text. Native widgets keep their own theme.
_CSS = """<style>

/* Narrow the centered column and tighten vertical padding */
.block-container {
    max-width: 640px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 6rem !important;
}

/* === Section label ========================================================= */
/* Dark enough to read on both light and dark Streamlit themes */
.sec-lbl {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4b5563;
    margin: 1.75rem 0 0.6rem;
}

/* === Profile / Wallet summary cards ======================================== */
/* Explicit background so cards are visible regardless of page theme */
.pcard {
    background: #f9f8f6;
    border-radius: 14px;
    padding: 14px 16px 12px;
    border: 1px solid #e0ddd8;
    margin-bottom: 2px;
}
.pcard-eyebrow {
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 5px;
}
.wcard-eyebrow { color: #16a34a; }
.pcard-main { font-size: 14px; font-weight: 600; color: #111827; line-height: 1.45; }
.pcard-sub  { font-size: 11px; color: #6b7280; margin-top: 3px; }

/* === Winner hero card ====================================================== */
.hero {
    background: linear-gradient(140deg, #eef2ff 0%, #f8faff 100%);
    border: 1.5px solid #c7d2f8;
    border-radius: 18px;
    padding: 26px 26px 22px;
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
    font-size: 24px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.025em;
    line-height: 1.15;
    margin-bottom: 4px;
}
.hero-sub  { font-size: 14px; color: #374151; margin-bottom: 20px; }
.kv-row    { display: flex; gap: 22px; flex-wrap: wrap; }
.kv        { display: flex; flex-direction: column; gap: 2px; }
.kv-l      { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #6b7280; }
.kv-v      { font-size: 17px; font-weight: 800; color: #111827; line-height: 1.2; }

/* === Comparison tile ======================================================= */
.tile {
    background: #ffffff;
    border: 1.5px solid #e0ddd8;
    border-radius: 14px;
    padding: 16px 12px 14px;
    height: 100%;
    box-sizing: border-box;
}
.tile-win  { border-color: #c7d2f8; background: #f5f7ff; }
.t-rank    { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #6b7280; margin-bottom: 4px; }
.t-name    { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 2px; line-height: 1.2; }
.t-cities  { font-size: 11px; color: #6b7280; margin-bottom: 10px; }
.t-score   { font-size: 32px; font-weight: 900; color: #111827; line-height: 1; }
.t-score-lbl { font-size: 11px; color: #6b7280; margin-bottom: 5px; }
.pills     { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.pill      { display: inline-block; background: #f3f4f6; border-radius: 100px; padding: 3px 8px; font-size: 11px; color: #374151; }
.pill-g    { background: #dcfce7; color: #166534; }
.pill-y    { background: #fef9c3; color: #713f12; }
.pill-r    { background: #fee2e2; color: #991b1b; }

/* === Seats.aero block ====================================================== */
.sa-blk { border-radius: 11px; padding: 13px 15px; line-height: 1.4; }
.sa-yes { background: #f0fdf4; border: 1px solid #86efac; }
.sa-no  { background: #fff5f5; border: 1px solid #fca5a5; }
.sa-est { background: #f9fafb; border: 1px solid #d1d5db; }
.sa-dir { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4b5563; margin-bottom: 5px; }
.sa-hl  { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 3px; }
.sa-dt  { font-size: 12px; color: #4b5563; }

/* === Research note box ===================================================== */
.note-box {
    background: #f9fafb;
    border: 1px solid #e0ddd8;
    border-radius: 11px;
    padding: 12px 13px;
    height: 100%;
    box-sizing: border-box;
}
.note-lbl { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4b5563; margin-bottom: 5px; }
.note-txt { font-size: 13px; color: #374151; line-height: 1.55; }

/* === Pros / Cons =========================================================== */
.pro { font-size: 13.5px; color: #166534; padding: 3px 0; }
.con { font-size: 13.5px; color: #991b1b;  padding: 3px 0; }

/* === Sub-label (inside result cards) ======================================= */
.sub-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4b5563;
    padding-top: 16px;
    margin-bottom: 8px;
}

/* === Web context summary =================================================== */
.wc-item { padding: 8px 0; border-bottom: 1px solid #f0ede8; }
.wc-item:last-child { border-bottom: none; }
.wc-lbl { font-size: 10px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: #4b5563; margin-bottom: 3px; }
.wc-txt { font-size: 13px; color: #374151; line-height: 1.5; }

/* === Step list (How this works) ============================================ */
.step { display: flex; gap: 14px; padding: 10px 0; border-bottom: 1px solid #f0ede8; align-items: flex-start; }
.step:last-child { border-bottom: none; }
.step-n { font-size: 11px; font-weight: 800; color: #6366f1; background: #eef2ff; border-radius: 6px; padding: 2px 8px; white-space: nowrap; margin-top: 2px; }
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
    if not text or len(text) <= n:
        return text or ""
    return text[:n].rsplit(" ", 1)[0] + "…"


def _best_sentence(results: list, keywords=None) -> str:
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
    <div class="kv"><span class="kv-l">Score</span><span class="kv-v">{w['score']}/100</span></div>
    <div class="kv"><span class="kv-l">Cash needed</span><span class="kv-v">${w['total_cash']:,}</span></div>
    <div class="kv"><span class="kv-l">Hotel changes</span><span class="kv-v">{w['moves']}</span></div>
    <div class="kv"><span class="kv-l">Award space</span><span class="kv-v">{DOT.get(avail,'')} {avail}</span></div>
    <div class="kv"><span class="kv-l">Pace</span><span class="kv-v">{w['pace'].title()}</span></div>
    <div class="kv"><span class="kv-l">Points used</span><span class="kv-v">{pts:,}</span></div>
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
  <div class="sa-hl" style="color:#4b5563;">〜 &nbsp;Estimated</div>
  <div class="sa-dt">{err}</div>
</div>""", unsafe_allow_html=True)


def render_research_notes(notes: dict) -> None:
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
            st.markdown(f'<div style="padding:4px 0">{html_items}</div>', unsafe_allow_html=True)
        else:
            st.caption("Searches ran but no relevant snippets were found.")


# ── Profile: load from disk once per browser session ──────────────────────────
def _init_profile() -> None:
    if "profile" in st.session_state:
        return
    saved = profile_store.load()
    st.session_state.profile = saved
    seeds = {
        "p_name":   saved.get("name", ""),
        "p_origin": saved.get("origin", "SFO"),
        "p_adults": saved["travelers"]["adults"],
        "p_kids":   saved["travelers"]["kids"],
        "p_ages":   ", ".join(str(a) for a in saved["travelers"].get("kids_ages", [14, 11])),
        "w_amex":   saved["wallet"]["amex_mr"],
        "w_certs":  saved["wallet"]["marriott_free_nights"],
        "w_bonvoy": saved["wallet"]["bonvoy_points"],
    }
    for k, v in seeds.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# Session state — initialised HERE, before any rendering, so it's always ready
# ══════════════════════════════════════════════════════════════════════════════
if "results" not in st.session_state:
    st.session_state.results     = None
    st.session_state.web_context = {}
    st.session_state.log         = ""

_init_profile()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE LAYOUT — centered, top-to-bottom
#
# Rendering order:
#   1. Hero
#   2. Profile + Wallet cards (always)
#   3. RESULTS (if available) ← appear above the form so clicking the button
#      shows results here after st.rerun(), not off-screen below the fold
#   4. Form: destinations / style / duration
#   5. CTA button
#   6. Engine: runs when button clicked, then calls st.rerun()
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Hero ───────────────────────────────────────────────────────────────────
_pname    = st.session_state.profile.get("name", "").strip()
_greeting = f"Hi {_pname}" if _pname else "Plan your Europe trip"
st.markdown(f"""
<div style="padding:0.25rem 0 1.5rem">
  <div style="font-size:10px;font-weight:800;letter-spacing:0.14em;
              text-transform:uppercase;color:#6b7280;margin-bottom:14px">
    ✦ &nbsp;Travel Points Planner
  </div>
  <h1 style="font-size:32px;font-weight:800;color:#111827;
             letter-spacing:-0.03em;line-height:1.1;margin:0 0 10px">
    {_greeting}
  </h1>
  <p style="font-size:15px;color:#374151;margin:0;line-height:1.65">
    Pick your cities and style — we rank every route using your real points balance.
  </p>
</div>
""", unsafe_allow_html=True)


# ── 2. Traveler profile ───────────────────────────────────────────────────────
prof = st.session_state.profile
t    = prof["travelers"]

kid_str      = f", {t['kids']} kid{'s' if t['kids']!=1 else ''}" if t["kids"] > 0 else ""
prof_summary = f"{prof['origin']} · {t['adults']} adult{'s' if t['adults']!=1 else ''}{kid_str}"
saved_ts     = profile_store.saved_at(prof)
saved_line   = f'<div class="pcard-sub">Saved {saved_ts}</div>' if saved_ts else ""

st.markdown(
    f'<div class="pcard">'
    f'<div class="pcard-eyebrow">Traveler Profile</div>'
    f'<div class="pcard-main">{prof_summary}</div>'
    f'{saved_line}'
    f'</div>',
    unsafe_allow_html=True,
)
with st.expander("Edit profile"):
    st.text_input("Your name (optional)", key="p_name")
    st.text_input("Home airport", key="p_origin", help="3-letter IATA code, e.g. SFO, JFK, LAX")
    ca, cb = st.columns(2)
    ca.number_input("Adults", min_value=1, max_value=8, step=1, key="p_adults")
    cb.number_input("Kids",   min_value=0, max_value=6, step=1, key="p_kids")
    if int(st.session_state.get("p_kids", 0)) > 0:
        st.text_input("Kids' ages (comma-separated)", key="p_ages", help="Example: 14, 11")
    if st.button("Save Profile", key="btn_save_prof", type="primary"):
        n_kids   = int(st.session_state.get("p_kids", 0))
        ages_raw = st.session_state.get("p_ages", "")
        try:
            ages = [int(a.strip()) for a in ages_raw.split(",") if a.strip().isdigit()]
        except Exception:
            ages = []
        while len(ages) < max(n_kids, 2):
            ages.append(10)
        updated = dict(st.session_state.profile)
        updated["name"]      = st.session_state.get("p_name", "").strip()
        updated["origin"]    = st.session_state.get("p_origin", "SFO").upper().strip()
        updated["travelers"] = {
            "adults":    int(st.session_state.get("p_adults", 2)),
            "kids":      n_kids,
            "kids_ages": ages[:max(n_kids, 1)],
        }
        profile_store.save(updated)
        st.session_state.profile = updated
        st.toast("Profile saved!", icon="✅")


# ── 3. Points wallet ──────────────────────────────────────────────────────────
w = prof["wallet"]
wallet_summary = (
    f"{w['amex_mr']:,} MR  ·  {w['bonvoy_points']:,} Bonvoy  ·  "
    f"{w['marriott_free_nights']} cert{'s' if w['marriott_free_nights']!=1 else ''}"
)
st.markdown(
    f'<div class="pcard" style="margin-top:6px">'
    f'<div class="pcard-eyebrow wcard-eyebrow">Points Wallet</div>'
    f'<div class="pcard-main">{wallet_summary}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
with st.expander("Edit wallet"):
    st.number_input("Amex MR points", min_value=0, step=10_000, key="w_amex")
    ca, cb = st.columns(2)
    ca.number_input("Free night certs", min_value=0, max_value=30, step=1, key="w_certs")
    cb.number_input("Bonvoy points",    min_value=0, step=10_000,            key="w_bonvoy")
    if st.button("Save Wallet", key="btn_save_wallet", type="primary"):
        updated = dict(st.session_state.profile)
        updated["wallet"] = {
            "amex_mr":              int(st.session_state.get("w_amex",   0)),
            "marriott_free_nights": int(st.session_state.get("w_certs",  0)),
            "bonvoy_points":        int(st.session_state.get("w_bonvoy", 0)),
        }
        profile_store.save(updated)
        st.session_state.profile = updated
        st.toast("Wallet saved!", icon="💳")


# ── 4. RESULTS — rendered here so they appear above the form ──────────────────
# After the engine runs (step 6 below), st.rerun() causes the script to restart.
# On that fresh run, st.session_state.results is already set, so this block
# renders the results AT THE TOP of the page — before the search form.
if st.session_state.results:
    ranked = st.session_state.results
    winner = ranked[0]

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    render_winner_hero(winner)

    st.markdown('<div class="sub-lbl" style="padding-top:20px">All options</div>', unsafe_allow_html=True)
    tile_cols = st.columns(len(ranked))
    for i, (col, itin) in enumerate(zip(tile_cols, ranked)):
        render_option_tile(col, itin, i)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    render_web_context(st.session_state.get("web_context", {}))

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    for i, itin in enumerate(ranked):
        medal  = MEDALS[i] if i < len(MEDALS) else f"#{i+1}"
        avail  = itin["award_likelihood"]
        header = (
            f"{medal}  {itin['name']} "
            f"— {itin['score']}/100 · "
            f"${itin['total_cash']:,} cash · "
            f"{DOT.get(avail, '')} {avail} award space"
        )
        with st.expander(header, expanded=(i == 0)):

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

            st.markdown('<div class="sub-lbl">Award availability — Seats.aero live data</div>', unsafe_allow_html=True)
            sa_l, sa_r = st.columns(2)
            render_sa_leg(sa_l, itin.get("award_availability", {}),        "Outbound")
            render_sa_leg(sa_r, itin.get("award_availability_return", {}), "Return")

            notes = itin.get("research_notes", {})
            if notes:
                st.markdown('<div class="sub-lbl">Research notes</div>', unsafe_allow_html=True)
                render_research_notes(notes)

            render_pros_cons(itin["pros"], itin["cons"])

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

            with st.expander("Score breakdown"):
                for line in itin["breakdown"]:
                    st.markdown(f"- {line}")

            with st.expander("Data quality — live vs. config vs. estimated"):
                cities_in_route = [c for c, _ in itin["stops"]]
                intra_legs      = itin["transit"][1:-1]
                dq1, dq2, dq3  = st.columns(3)

                with dq1:
                    st.markdown("**🌐 Live (Seats.aero + Tavily)**")
                    sa_o  = itin.get("award_availability", {})
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

            if i == 0:
                st.markdown('<div class="sub-lbl">Day-by-day plan</div>', unsafe_allow_html=True)
                for day in engine.get_day_plan(itin):
                    with st.expander(f"Day {day['day']} · {day['date_str']} · {day['city']}"):
                        st.markdown(f"**Main:** {day['main']}")
                        st.markdown(f"**Lighter:** {day['lighter']}")
                        st.caption(day["family"])
                        if day.get("points_note"):
                            st.info(day["points_note"])

    with st.expander("Agent log"):
        st.code(st.session_state.log, language=None)

    st.divider()
    st.markdown('<div class="sec-lbl">Search again</div>', unsafe_allow_html=True)


# ── 5. Trip form ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-lbl">Where do you want to go?</div>', unsafe_allow_html=True)
all_cities = list(engine.CITY_DATA.keys())
required_cities = st.multiselect(
    "Must-visit cities",
    options=all_cities,
    default=["London", "Paris"],
    help="A missing required city penalises the score.",
)
optional_cities = st.multiselect(
    "Nice-to-have cities",
    options=[c for c in all_cities if c not in required_cities],
    default=[c for c in ["Rome", "Amsterdam", "Barcelona"] if c not in required_cities],
)

st.markdown('<div class="sec-lbl">Trip style</div>', unsafe_allow_html=True)
trip_style = st.radio(
    "Trip style",
    options=["relaxed", "balanced", "maximize"],
    index=1,
    horizontal=True,
    label_visibility="collapsed",
    help=(
        "**relaxed** — up to 2 cities, 4+ nights each  \n"
        "**balanced** — up to 3 cities, good depth and variety  \n"
        "**maximize** — up to 5 cities, see as much as possible"
    ),
)

st.markdown('<div class="sec-lbl">When and how long?</div>', unsafe_allow_html=True)
dc1, dc2, dc3 = st.columns(3)
year     = dc1.number_input("Year",     min_value=2025, max_value=2030, value=2026, step=1)
min_days = dc2.number_input("Min days", min_value=5,    max_value=21,   value=7)
max_days = dc3.number_input("Max days", min_value=5,    max_value=21,   value=10)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ── 6. Primary CTA ────────────────────────────────────────────────────────────
run_clicked = st.button(
    "Find my best itinerary →",
    use_container_width=True,
    type="primary",
)

# "How this works" shown only when no results yet
if not st.session_state.results:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    steps = [
        ("1", "Date agent",      "Picks the best departure weekends in your travel window."),
        ("2", "Itinerary agent", "Builds route options from your required + nice-to-have cities."),
        ("3", "Flight agent",    "Plans transatlantic flights using your Amex MR points."),
        ("4", "Hotel agent",     "Allocates Marriott free-night certs, then Bonvoy points, then cash."),
        ("5", "Flow agent",      "Scores how smooth the city-to-city routing is."),
        ("6", "Scoring agent",   "Combines all signals into a 0–100 family-tuned score."),
        ("7", "Day-plan agent",  "Builds a full day-by-day calendar for the winning itinerary."),
    ]
    steps_html = "".join(
        f'<div class="step">'
        f'<span class="step-n">{n}</span>'
        f'<span class="step-t"><strong>{name}</strong> — {desc}</span>'
        f'</div>'
        for n, name, desc in steps
    )
    with st.expander("How this works", expanded=False):
        st.markdown(f'<div style="padding:4px 0">{steps_html}</div>', unsafe_allow_html=True)


# ── 7. Engine ────────────────────────────────────────────────────────────────
# This block is the ONLY place engine.run_plan() is called.
# When run_clicked is True:
#   1. plan_profile is built from current widget values + saved profile/wallet
#   2. engine.run_plan() executes (may take 10-30s)
#   3. Results stored in st.session_state.results
#   4. st.rerun() triggers a fresh script execution
#   5. On that fresh run, step 4 above renders results at the top of the page
if run_clicked:
    prof      = st.session_state.profile
    t         = prof["travelers"]
    w         = prof["wallet"]
    n_kids    = t["kids"]
    kids_ages = list(t.get("kids_ages", []))
    while len(kids_ages) < max(n_kids, 2):
        kids_ages.append(10)

    plan_profile = {
        "origin":           prof["origin"],
        "travel_window":    "late July through early August",
        "trip_length_days": f"{int(min_days)} to {int(max_days)}",
        "travelers": {
            "adults":    t["adults"],
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
            "amex_mr":              w["amex_mr"],
            "marriott_free_nights": w["marriott_free_nights"],
            "bonvoy_points":        w["bonvoy_points"],
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

    try:
        with st.spinner("Planning your trip…"):
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                ranked, web_context = engine.run_plan(plan_profile, year=int(year))
        st.session_state.results     = ranked
        st.session_state.web_context = web_context
        st.session_state.log         = captured.getvalue()
        st.rerun()   # ← restarts the script so results render at step 4 above
    except Exception as exc:
        import traceback
        st.error(f"Planning failed: {exc}")
        with st.expander("Error details"):
            st.code(traceback.format_exc())
