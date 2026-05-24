"""
data/profile.py — local persistence for the traveler profile and points wallet.

───────────────────────────────────────────────────────────────────────────────
ARCHITECTURE (plain English)
───────────────────────────────────────────────────────────────────────────────

This module has one job: read and write a single JSON file on disk so that
your traveler details and points balances survive page reloads and app restarts.

It is a pure-Python module with no Streamlit imports — it only knows about
files and dicts. The UI layer (app.py) calls load() at startup and save()
when the user clicks "Save".

───────────────────────────────────────────────────────────────────────────────
WHERE THE FILE LIVES
───────────────────────────────────────────────────────────────────────────────

    <project_root>/data/traveler_profile.json

The path is computed from __file__ (this file's location), so it works
regardless of which directory you launch the app from.

The file is plain, human-readable JSON.  You can open it in any text editor,
edit it directly, and the app will pick up the changes on next load.

Add this line to .gitignore if you don't want to commit personal data:

    data/traveler_profile.json

───────────────────────────────────────────────────────────────────────────────
HOW PERSISTENCE WORKS
───────────────────────────────────────────────────────────────────────────────

Streamlit re-runs the entire app script on every user interaction, so ordinary
Python variables reset on each run.  We solve this in two layers:

  1. In-session memory  — st.session_state (managed by app.py) keeps values
                          alive for the current browser tab.

  2. Cross-session disk — this module writes to / reads from JSON so data
                          survives browser refreshes, app restarts, reboots.

Flow:
  App starts        → load() reads JSON → stored in st.session_state.profile
  User edits form   → widget values live in st.session_state during the session
  User clicks Save  → app.py calls save() → JSON updated on disk
  App restarts      → load() reads the saved JSON again  ✓
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# ── File location ──────────────────────────────────────────────────────────────
_DATA_DIR     = Path(__file__).parent          # .../europe-travel-agent/data/
_PROFILE_FILE = _DATA_DIR / "traveler_profile.json"

# ── Defaults (used the very first time, before any save) ───────────────────────
DEFAULTS: dict = {
    "name":   "",
    "origin": "SFO",
    "travelers": {
        "adults":    2,
        "kids":      2,
        "kids_ages": [14, 11],
    },
    "wallet": {
        "amex_mr":              200_000,
        "marriott_free_nights": 5,
        "bonvoy_points":        250_000,
    },
    "_saved_at": None,   # ISO timestamp, filled in on every save
}


# ── Public API ─────────────────────────────────────────────────────────────────

def load() -> dict:
    """
    Load the saved profile from disk.

    Returns a deep copy of DEFAULTS if the file doesn't exist or is corrupted.
    Any keys missing from an older saved file are filled in from DEFAULTS, so
    adding new fields in future versions won't break existing saves.
    """
    if not _PROFILE_FILE.exists():
        return _deep_copy(DEFAULTS)
    try:
        data = json.loads(_PROFILE_FILE.read_text(encoding="utf-8"))
        _fill_defaults(data, DEFAULTS)   # forward-compatible: add any new keys
        return data
    except Exception:
        return _deep_copy(DEFAULTS)


def save(data: dict) -> None:
    """
    Write the profile dict to disk as formatted JSON.

    Stamps _saved_at with the current UTC time so the UI can show
    when the profile was last updated.
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["_saved_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _PROFILE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def file_path() -> str:
    """Absolute path to the JSON file — shown in the UI so users know where data lives."""
    return str(_PROFILE_FILE.resolve())


def saved_at(data: dict) -> str:
    """Human-readable 'last saved' string, or empty string if never saved."""
    return data.get("_saved_at") or ""


# ── Internal helpers ───────────────────────────────────────────────────────────

def _deep_copy(d: dict) -> dict:
    """Deep copy via JSON round-trip (avoids importing the copy module)."""
    return json.loads(json.dumps(d))


def _fill_defaults(data: dict, defaults: dict) -> None:
    """Recursively add keys present in defaults but absent from data."""
    for key, val in defaults.items():
        if key not in data:
            data[key] = _deep_copy(val) if isinstance(val, dict) else val
        elif isinstance(val, dict) and isinstance(data.get(key), dict):
            _fill_defaults(data[key], val)
