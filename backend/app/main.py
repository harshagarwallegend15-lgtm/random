"""FastAPI app entrypoint."""
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.routers import analysis, photos, plan, reanalyze, users

# Top-level logging config — single source of truth for log format & level.
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("workout_app")

app = FastAPI(
    title="Workout App API",
    version="0.1.0",
    description="Personalized fitness planning with AI body analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local upload fallback (when Cloudinary creds are absent)
_uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")

app.include_router(users.router)
app.include_router(photos.router)
app.include_router(analysis.router)
app.include_router(plan.router)
app.include_router(reanalyze.router)


@app.get("/health", tags=["health"])
def health():
    """Liveness — process is up. Always 200 if the app is serving."""
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
def health_db(db: Session = Depends(get_db)):
    """Readiness — round-trips a SELECT 1 to Postgres. 503 if the DB is down.

    Use this for orchestrator readiness probes (k8s, ECS, Render) so the
    service is only marked ready after the DB is reachable.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as exc:
        log.warning("DB health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="database unreachable")
