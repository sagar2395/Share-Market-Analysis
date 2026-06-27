"""Signal & screener endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.intelligence.signals import analyze
from app.intelligence.signals.base import Signal
from app.services import screener

router = APIRouter(tags=["signals"])


@router.get("/signal", response_model=Signal)
def signal(symbol: str = Query(..., examples=["RELIANCE.NS"])) -> Signal:
    """Weekly+daily confluence verdict for one symbol (powers the Analyze badge)."""
    try:
        return analyze(symbol)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Signal failed: {exc}") from exc


@router.get("/screener/presets")
def screener_presets() -> list[dict]:
    return screener.list_presets()


@router.get("/screener")
def run_screener(
    preset: str = Query("all"),
    min_score: int = Query(0, ge=0, le=100),
    action: str | None = Query(None),
) -> list[dict]:
    """Scan the universe and rank swing setups by the preset/filters."""
    return screener.run(preset=preset, min_score=min_score, action=action)
