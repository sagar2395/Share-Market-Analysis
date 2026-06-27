"""Candlestick patterns + nearest support/resistance — with plain-language teaching.

Pattern signals are most meaningful *in context* (a hammer after a downtrend, near
support), so the report pairs detected candles with the nearest S/R levels and explains
what each implies for a swing entry/exit. Long-only bias: bearish patterns mean
caution/exit, not "go short".
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel

Direction = Literal["bullish", "bearish", "neutral"]


class Pattern(BaseModel):
    name: str
    direction: Direction
    description: str  # what it is + what it implies (teaching)


class PatternReport(BaseModel):
    symbol: str
    interval: str
    price: float
    support: float | None
    resistance: float | None
    patterns: list[Pattern]
    summary: str
    caveat: str | None = None


def _candle_patterns(df: pd.DataFrame) -> list[Pattern]:
    if len(df) < 2:
        return []
    o, h, l, c = (df[k] for k in ("open", "high", "low", "close"))
    last, prev = -1, -2
    body = abs(c.iloc[last] - o.iloc[last])
    rng = max(h.iloc[last] - l.iloc[last], 1e-9)
    upper_wick = h.iloc[last] - max(c.iloc[last], o.iloc[last])
    lower_wick = min(c.iloc[last], o.iloc[last]) - l.iloc[last]
    out: list[Pattern] = []

    # Doji — indecision.
    if body <= 0.1 * rng:
        out.append(
            Pattern(
                name="Doji",
                direction="neutral",
                description=(
                    "Open and close are nearly equal — buyers and sellers in balance. "
                    "Often marks a pause or potential turning point; wait for the next "
                    "candle to confirm direction."
                ),
            )
        )

    # Hammer — potential bullish reversal (long lower wick, small body up top).
    if lower_wick >= 2 * body and upper_wick <= body and body > 0:
        out.append(
            Pattern(
                name="Hammer",
                direction="bullish",
                description=(
                    "A long lower wick shows sellers pushed price down but buyers reclaimed "
                    "it by the close. After a decline and near support, it hints at a bounce "
                    "— a possible swing entry if the next candle confirms."
                ),
            )
        )

    # Shooting star — potential bearish reversal (long upper wick).
    if upper_wick >= 2 * body and lower_wick <= body and body > 0:
        out.append(
            Pattern(
                name="Shooting star",
                direction="bearish",
                description=(
                    "A long upper wick shows buyers pushed up but sellers slammed it back. "
                    "After a rally, it warns of a stall — consider trimming or tightening "
                    "stops rather than adding."
                ),
            )
        )

    # Engulfing — momentum shift.
    prev_body_top = max(c.iloc[prev], o.iloc[prev])
    prev_body_bot = min(c.iloc[prev], o.iloc[prev])
    curr_up = c.iloc[last] > o.iloc[last]
    curr_down = c.iloc[last] < o.iloc[last]
    if curr_up and c.iloc[prev] < o.iloc[prev] and c.iloc[last] >= prev_body_top and o.iloc[last] <= prev_body_bot:
        out.append(
            Pattern(
                name="Bullish engulfing",
                direction="bullish",
                description=(
                    "Today's green candle fully engulfs yesterday's red one — buyers took "
                    "control. A reliable reversal hint when it appears after a pullback near "
                    "support."
                ),
            )
        )
    if curr_down and c.iloc[prev] > o.iloc[prev] and c.iloc[last] <= prev_body_bot and o.iloc[last] >= prev_body_top:
        out.append(
            Pattern(
                name="Bearish engulfing",
                direction="bearish",
                description=(
                    "Today's red candle fully engulfs yesterday's green one — sellers took "
                    "control. Near resistance or after a rally, it's a cue to protect "
                    "profits."
                ),
            )
        )
    return out


def _support_resistance(df: pd.DataFrame, order: int = 5) -> tuple[float | None, float | None]:
    """Nearest pivot low below price (support) and pivot high above price (resistance)."""
    if len(df) < 2 * order + 1:
        return None, None
    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    price = float(df["close"].iloc[-1])
    pivot_highs, pivot_lows = [], []
    for i in range(order, len(df) - order):
        window_h = highs[i - order : i + order + 1]
        window_l = lows[i - order : i + order + 1]
        if highs[i] == window_h.max():
            pivot_highs.append(highs[i])
        if lows[i] == window_l.min():
            pivot_lows.append(lows[i])
    supports = [p for p in pivot_lows if p < price]
    resistances = [p for p in pivot_highs if p > price]
    support = max(supports) if supports else (float(np.min(lows)) if len(lows) else None)
    resistance = min(resistances) if resistances else (float(np.max(highs)) if len(highs) else None)
    return (
        round(support, 2) if support is not None else None,
        round(resistance, 2) if resistance is not None else None,
    )


def detect_frame(symbol: str, interval: str, df: pd.DataFrame) -> PatternReport:
    price = float(df["close"].iloc[-1])
    patterns = _candle_patterns(df)
    support, resistance = _support_resistance(df)

    bits: list[str] = []
    if support is not None and resistance is not None:
        to_sup = (price - support) / price * 100
        to_res = (resistance - price) / price * 100
        bits.append(
            f"Price ₹{price:,.1f} sits {to_sup:.1f}% above nearest support (₹{support:,.1f}) "
            f"and {to_res:.1f}% below nearest resistance (₹{resistance:,.1f})."
        )
    if patterns:
        names = ", ".join(p.name for p in patterns)
        bits.append(f"Recent candle signal: {names}.")
    else:
        bits.append("No notable candlestick pattern on the latest bar.")
    summary = " ".join(bits)

    return PatternReport(
        symbol=symbol,
        interval=interval,
        price=round(price, 2),
        support=support,
        resistance=resistance,
        patterns=patterns,
        summary=summary,
        caveat=(
            "Candlestick patterns are hints, not triggers — they work best with the trend, "
            "near support/resistance, and confirmed by volume and the next candle."
        ),
    )


def detect(symbol: str, interval: str = "1d", lookback: int = 120) -> PatternReport:
    from app.data.registry import get_provider

    df = get_provider().get_ohlcv(symbol, interval=interval, lookback=lookback).to_frame()
    return detect_frame(symbol, interval, df)
