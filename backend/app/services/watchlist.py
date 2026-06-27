"""Watchlist service — persistent list of symbols the owner is tracking."""

from __future__ import annotations

from sqlalchemy import select

from app.data.registry import get_provider
from app.storage.db import session_scope
from app.storage.models import WatchlistItem


def list_items() -> list[dict]:
    with session_scope() as s:
        items = s.scalars(select(WatchlistItem).order_by(WatchlistItem.added_at)).all()
        return [
            {"symbol": i.symbol, "name": i.name, "added_at": i.added_at.isoformat()}
            for i in items
        ]


def add(symbol: str) -> dict:
    symbol = symbol.strip().upper()
    provider = get_provider()
    matches = provider.search_symbols(symbol)
    name = next((m.name for m in matches if m.symbol.upper() == symbol), "")
    with session_scope() as s:
        existing = s.scalar(select(WatchlistItem).where(WatchlistItem.symbol == symbol))
        if existing:
            return {"symbol": existing.symbol, "name": existing.name, "added": False}
        item = WatchlistItem(symbol=symbol, name=name)
        s.add(item)
        return {"symbol": symbol, "name": name, "added": True}


def remove(symbol: str) -> bool:
    symbol = symbol.strip().upper()
    with session_scope() as s:
        item = s.scalar(select(WatchlistItem).where(WatchlistItem.symbol == symbol))
        if not item:
            return False
        s.delete(item)
        return True


def quotes() -> list[dict]:
    """Watchlist with a live quote per symbol (for the dashboard)."""
    provider = get_provider()
    out: list[dict] = []
    for item in list_items():
        try:
            q = provider.get_quote(item["symbol"])
            out.append(
                {
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "price": q.price,
                    "change": q.change,
                    "change_percent": q.change_percent,
                }
            )
        except Exception:  # noqa: BLE001 — a single bad symbol shouldn't break the list
            out.append(
                {
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "price": None,
                    "change": None,
                    "change_percent": None,
                }
            )
    return out
