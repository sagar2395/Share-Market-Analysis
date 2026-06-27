"""Alerts — watch conditions against current data and fire when they're met.

Supported kinds (tuned to a swing trader):
- ``price_above`` / ``price_below`` — price crosses a level.
- ``rsi_above`` / ``rsi_below`` — momentum crosses a level.
- ``confluence_action`` — the weekly+daily confluence verdict becomes a given action
  (e.g. fire when a name turns "buy" / enters a buy-the-dip setup).

Evaluation is edge-triggered: an alert "fires" only when its condition flips from unmet
to met (tracked via ``currently_met``), so you're not spammed every poll.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.data.registry import get_provider
from app.intelligence.indicators.rsi import RSI
from app.intelligence.signals import analyze
from app.storage.db import session_scope
from app.storage.models import Alert

KINDS = ("price_above", "price_below", "rsi_above", "rsi_below", "confluence_action")


def _describe(a: Alert) -> str:
    if a.kind == "price_above":
        return f"{a.symbol} price ≥ ₹{a.threshold:g}"
    if a.kind == "price_below":
        return f"{a.symbol} price ≤ ₹{a.threshold:g}"
    if a.kind == "rsi_above":
        return f"{a.symbol} RSI ≥ {a.threshold:g}"
    if a.kind == "rsi_below":
        return f"{a.symbol} RSI ≤ {a.threshold:g}"
    if a.kind == "confluence_action":
        return f"{a.symbol} confluence becomes '{a.target}'"
    return f"{a.symbol} {a.kind}"


def _to_dict(a: Alert) -> dict:
    return {
        "id": a.id,
        "symbol": a.symbol,
        "kind": a.kind,
        "threshold": a.threshold,
        "target": a.target,
        "note": a.note,
        "active": a.active,
        "currently_met": a.currently_met,
        "last_triggered_at": a.last_triggered_at.isoformat() if a.last_triggered_at else None,
        "description": _describe(a),
    }


def create(data: dict) -> dict:
    kind = data["kind"]
    if kind not in KINDS:
        raise ValueError(f"Unknown alert kind '{kind}'. Valid: {KINDS}")
    with session_scope() as s:
        a = Alert(
            symbol=data["symbol"].strip().upper(),
            kind=kind,
            threshold=data.get("threshold"),
            target=(data.get("target") or "").strip().lower(),
            note=data.get("note", ""),
        )
        s.add(a)
        s.flush()
        return _to_dict(a)


def list_alerts() -> list[dict]:
    with session_scope() as s:
        return [_to_dict(a) for a in s.scalars(select(Alert).order_by(Alert.created_at)).all()]


def delete(alert_id: int) -> bool:
    with session_scope() as s:
        a = s.get(Alert, alert_id)
        if not a:
            return False
        s.delete(a)
        return True


def toggle(alert_id: int) -> dict | None:
    with session_scope() as s:
        a = s.get(Alert, alert_id)
        if not a:
            return None
        a.active = not a.active
        return _to_dict(a)


def _condition_met(a: Alert) -> bool:
    provider = get_provider()
    if a.kind in ("price_above", "price_below"):
        price = provider.get_quote(a.symbol).price
        return price >= a.threshold if a.kind == "price_above" else price <= a.threshold
    if a.kind in ("rsi_above", "rsi_below"):
        df = provider.get_ohlcv(a.symbol, interval="1d", lookback=120).to_frame()
        rsi = float(RSI().compute(df).iloc[-1])
        return rsi >= a.threshold if a.kind == "rsi_above" else rsi <= a.threshold
    if a.kind == "confluence_action":
        return analyze(a.symbol).action == a.target
    return False


def evaluate() -> list[dict]:
    """Check every active alert. Return results; ``newly_fired`` marks edge triggers."""
    results: list[dict] = []
    with session_scope() as s:
        alerts = s.scalars(select(Alert).where(Alert.active.is_(True))).all()
        for a in alerts:
            try:
                met = _condition_met(a)
            except Exception:  # noqa: BLE001 — a bad symbol shouldn't break evaluation
                continue
            newly_fired = met and not a.currently_met
            if newly_fired:
                a.last_triggered_at = datetime.utcnow()
            a.currently_met = met
            results.append({**_to_dict(a), "met": met, "newly_fired": newly_fired})
    return results
