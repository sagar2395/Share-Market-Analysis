"""Admin/ops endpoints — trigger ingestion, inspect the history store."""

from __future__ import annotations

from fastapi import APIRouter

from app.services import ingestion
from app.storage import history

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/ingest")
def trigger_ingest() -> dict:
    """Manually run EOD ingestion for all tracked symbols (also runs on a daily schedule)."""
    return ingestion.run()


@router.get("/history/stats")
def history_stats() -> dict:
    return history.stats()
