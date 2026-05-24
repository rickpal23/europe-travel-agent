"""
api/main.py — FastAPI entry point for the Travel Points Planner.

Run with:
    uvicorn api.main:app --reload --port 8000

Always run from the project root so that `import main` in the routers
resolves to the planning engine (main.py), not this file.
"""

import os
import sys
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
# Insert the project root at position 0 so that `import main` in the routers
# finds the planning engine (root/main.py), not this FastAPI file.
_ROOT = str(Path(__file__).parent.parent.resolve())
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Load .env before any module that reads API keys (the engine, Seats.aero, etc.)
from dotenv import load_dotenv
load_dotenv(Path(_ROOT) / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import plan, profile

app = FastAPI(
    title="Travel Points Planner API",
    description="Wraps the Python planning engine for use by the Next.js frontend.",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server (port 3000) to call this API.
# Tighten allowed_origins before any public deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(plan.router,    prefix="/api", tags=["plan"])
app.include_router(profile.router, prefix="/api", tags=["profile"])


@app.get("/api/health", tags=["meta"])
def health():
    """Quick liveness check — confirms the server is up and the engine imported."""
    import main as engine  # noqa: F401  (validates the import resolves correctly)
    return {"status": "ok"}
