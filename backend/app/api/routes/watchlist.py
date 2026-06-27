"""Watchlist endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.intelligence.signals import analyze
from app.services import watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class SymbolIn(BaseModel):
    symbol: str


@router.get("")
def get_watchlist() -> list[dict]:
    return watchlist.list_items()


@router.get("/quotes")
def get_quotes() -> list[dict]:
    return watchlist.quotes()


@router.get("/signals")
def get_signals() -> list[dict]:
    """Confluence badge/score per watchlist symbol (for inline triage tags)."""
    out: list[dict] = []
    for item in watchlist.list_items():
        try:
            sig = analyze(item["symbol"])
            out.append(
                {
                    "symbol": sig.symbol,
                    "badge": sig.badge,
                    "action": sig.action,
                    "stance": sig.stance,
                    "score": sig.score,
                }
            )
        except Exception:  # noqa: BLE001
            out.append({"symbol": item["symbol"], "badge": None, "action": None,
                        "stance": None, "score": None})
    return out


@router.post("")
def add_symbol(body: SymbolIn) -> dict:
    return watchlist.add(body.symbol)


@router.delete("/{symbol}")
def remove_symbol(symbol: str) -> dict:
    return {"removed": watchlist.remove(symbol)}
