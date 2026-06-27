"""Screener — scan the universe and rank swing/positional setups.

Built on the confluence engine: every candidate gets a signal, then presets/filters
narrow the list. Fundamental filters arrive with Phase 3 data; this is the technical
(price/trend/momentum) screen.
"""

from __future__ import annotations

from app.data.registry import get_provider
from app.intelligence.signals import analyze
from app.intelligence.signals.base import Signal

# Preset → predicate over a Signal. Keys are stable API identifiers.
PRESETS: dict[str, dict] = {
    "trend_aligned": {
        "label": "Trend-aligned longs",
        "desc": "Weekly and daily both up — cleanest backdrop for a long swing.",
        "pred": lambda s: s.weekly_trend == "up" and s.daily_trend in ("up", "flat"),
    },
    "buy_the_dip": {
        "label": "Buy-the-dip (weekly up, daily pullback)",
        "desc": "Uptrend with the daily pulled back into a buyable zone.",
        "pred": lambda s: s.badge == "Buy-the-dip zone",
    },
    "oversold_bounce": {
        "label": "Oversold / basing",
        "desc": "Stretched to the downside — potential mean-reversion bounce to watch.",
        "pred": lambda s: s.badge == "Basing / oversold",
    },
    "actionable": {
        "label": "Actionable (buy-rated)",
        "desc": "Anything the engine currently rates a buy.",
        "pred": lambda s: s.action == "buy",
    },
    "all": {
        "label": "All (ranked by score)",
        "desc": "Every symbol, best swing setups first.",
        "pred": lambda _s: True,
    },
}


def universe() -> list[tuple[str, str]]:
    """(symbol, name) pairs for the tradable universe from the active provider."""
    return [(s.symbol, s.name) for s in get_provider().search_symbols("", limit=500)]


def list_presets() -> list[dict]:
    return [{"key": k, "label": v["label"], "desc": v["desc"]} for k, v in PRESETS.items()]


def _row(name: str, sig: Signal) -> dict:
    return {
        "symbol": sig.symbol,
        "name": name,
        "badge": sig.badge,
        "action": sig.action,
        "stance": sig.stance,
        "score": sig.score,
        "weekly_trend": sig.weekly_trend,
        "daily_trend": sig.daily_trend,
        "price": sig.price,
        "summary": sig.summary,
    }


def run(
    preset: str = "all",
    min_score: int = 0,
    action: str | None = None,
) -> list[dict]:
    pred = PRESETS.get(preset, PRESETS["all"])["pred"]
    rows: list[dict] = []
    for symbol, name in universe():
        try:
            sig = analyze(symbol)
        except Exception:  # noqa: BLE001 — skip a bad symbol, keep scanning
            continue
        if not pred(sig):
            continue
        if sig.score < min_score:
            continue
        if action and sig.action != action:
            continue
        rows.append(_row(name, sig))
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows
