"""Portfolio service — manually-entered holdings with live P&L.

Tailored to a swing/positional trader: each holding can carry a target and stop, and a
horizon tag (swing vs long). P&L is computed live from the active data provider.
"""

from __future__ import annotations

from sqlalchemy import select

from app.data.registry import get_provider
from app.storage.db import session_scope
from app.storage.models import Holding


def _to_dict(h: Holding) -> dict:
    return {
        "id": h.id,
        "symbol": h.symbol,
        "name": h.name,
        "quantity": h.quantity,
        "avg_cost": h.avg_cost,
        "target_price": h.target_price,
        "stop_loss": h.stop_loss,
        "horizon": h.horizon,
        "notes": h.notes,
    }


def add(data: dict) -> dict:
    symbol = data["symbol"].strip().upper()
    provider = get_provider()
    name = data.get("name") or next(
        (m.name for m in provider.search_symbols(symbol) if m.symbol.upper() == symbol), ""
    )
    with session_scope() as s:
        existing = s.scalar(select(Holding).where(Holding.symbol == symbol))
        if existing:
            # Average-in: combine quantities and weighted average cost.
            total_qty = existing.quantity + data["quantity"]
            existing.avg_cost = (
                existing.avg_cost * existing.quantity + data["avg_cost"] * data["quantity"]
            ) / total_qty
            existing.quantity = total_qty
            existing.target_price = data.get("target_price", existing.target_price)
            existing.stop_loss = data.get("stop_loss", existing.stop_loss)
            existing.horizon = data.get("horizon", existing.horizon)
            existing.notes = data.get("notes", existing.notes)
            return _to_dict(existing)
        h = Holding(
            symbol=symbol,
            name=name,
            quantity=data["quantity"],
            avg_cost=data["avg_cost"],
            target_price=data.get("target_price"),
            stop_loss=data.get("stop_loss"),
            horizon=data.get("horizon", "swing"),
            notes=data.get("notes", ""),
        )
        s.add(h)
        s.flush()
        return _to_dict(h)


def remove(holding_id: int) -> bool:
    with session_scope() as s:
        h = s.get(Holding, holding_id)
        if not h:
            return False
        s.delete(h)
        return True


def summary() -> dict:
    """Return every holding enriched with live price + P&L, plus portfolio totals."""
    provider = get_provider()
    with session_scope() as s:
        holdings = s.scalars(select(Holding)).all()
        rows = [_to_dict(h) for h in holdings]

    total_invested = 0.0
    total_value = 0.0
    enriched: list[dict] = []
    for r in rows:
        invested = r["quantity"] * r["avg_cost"]
        try:
            price = provider.get_quote(r["symbol"]).price
        except Exception:  # noqa: BLE001
            price = None
        value = r["quantity"] * price if price is not None else None
        pnl = (value - invested) if value is not None else None
        pnl_pct = (pnl / invested * 100) if (pnl is not None and invested) else None
        enriched.append(
            {
                **r,
                "current_price": price,
                "invested": round(invested, 2),
                "market_value": round(value, 2) if value is not None else None,
                "pnl": round(pnl, 2) if pnl is not None else None,
                "pnl_percent": round(pnl_pct, 2) if pnl_pct is not None else None,
            }
        )
        total_invested += invested
        if value is not None:
            total_value += value

    total_pnl = total_value - total_invested
    return {
        "holdings": enriched,
        "totals": {
            "invested": round(total_invested, 2),
            "market_value": round(total_value, 2),
            "pnl": round(total_pnl, 2),
            "pnl_percent": round(total_pnl / total_invested * 100, 2) if total_invested else 0.0,
        },
    }
