"""Signal model shared by the confluence engine, screener, and watchlist tags."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Action = Literal["buy", "watch", "hold", "avoid"]
Stance = Literal["bullish", "bearish", "neutral"]
Trend = Literal["up", "down", "flat"]


class Signal(BaseModel):
    symbol: str
    badge: str                 # short confluence label, e.g. "Buy-the-dip zone"
    action: Action
    stance: Stance
    score: int                 # 0–100 confidence/quality of the swing setup
    horizon: str = "swing"     # 2wk–6mo
    weekly_trend: Trend
    daily_trend: Trend
    price: float
    reasons: list[str]         # teaching: why this verdict (plain language)
    summary: str               # one-line plain-language takeaway
    caveat: str | None = None
