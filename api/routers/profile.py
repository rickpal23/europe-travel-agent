"""
api/routers/profile.py — read and write the saved traveler profile.

Endpoints:
  GET  /api/profile  → return the current profile + wallet from disk
  PUT  /api/profile  → overwrite the profile + wallet on disk
"""

from fastapi import APIRouter, HTTPException
from data import profile as profile_store

router = APIRouter()


@router.get("/profile")
def get_profile() -> dict:
    """
    Return the saved traveler profile.
    Falls back to defaults if no file exists yet (first-time user).
    """
    return profile_store.load()


@router.put("/profile")
def save_profile(data: dict) -> dict:
    """
    Persist an updated profile to disk.
    Returns the saved state, which includes the new _saved_at timestamp.
    """
    try:
        profile_store.save(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return profile_store.load()
