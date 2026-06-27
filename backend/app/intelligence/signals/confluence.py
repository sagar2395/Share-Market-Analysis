"""Weekly + Daily confluence engine.

The core swing/positional signal: read the **weekly** trend (the tide) and the **daily**
setup (the timing), and combine them into one explainable verdict + badge — e.g.
"Weekly up + Daily pullback = buy-the-dip zone". Because the owner trades long-only on a
2wk–6mo horizon, a bearish read means "stand aside" (avoid), not "short".

Used by the Analyze badge, watchlist tags, and the screener.
"""

from __future__ import annotations

import pandas as pd

from app.data.registry import get_provider
from app.intelligence.indicators.bollinger import Bollinger
from app.intelligence.indicators.macd import MACD
from app.intelligence.indicators.rsi import RSI
from app.intelligence.signals.base import Signal, Trend


def _trend(df: pd.DataFrame) -> Trend:
    ema20 = df["close"].ewm(span=20, adjust=False).mean().iloc[-1]
    ema50 = df["close"].ewm(span=50, adjust=False).mean().iloc[-1]
    price = df["close"].iloc[-1]
    if ema20 > ema50 and price > ema50:
        return "up"
    if ema20 < ema50 and price < ema50:
        return "down"
    return "flat"


def _clamp(x: float) -> int:
    return int(max(0, min(100, round(x))))


def analyze_frames(symbol: str, daily: pd.DataFrame, weekly: pd.DataFrame) -> Signal:
    """Pure function (no I/O) so it's easy to test and reuse."""
    price = float(daily["close"].iloc[-1])
    wk = _trend(weekly)
    dl = _trend(daily)

    rsi = float(RSI().compute(daily).iloc[-1])
    macd_df = MACD().compute(daily)
    macd_bull = bool(macd_df["macd"].iloc[-1] > macd_df["signal"].iloc[-1])
    bb = Bollinger().compute(daily)
    upper = float(bb["upper"].iloc[-1])
    ema20_d = float(daily["close"].ewm(span=20, adjust=False).mean().iloc[-1])
    extended = rsi >= 70 or price >= upper
    pullback = price <= ema20_d or 38 <= rsi <= 55

    # ---- score (long-bias quality of a swing entry) ----
    score = 50.0
    score += 20 if wk == "up" else (-20 if wk == "down" else 0)
    score += 12 if dl == "up" else (-12 if dl == "down" else 0)
    score += 8 if macd_bull else -8
    if rsi < 35:
        score += 6
    elif rsi > 70:
        score -= 10
    elif 45 <= rsi <= 62:
        score += 4
    if extended:
        score -= 6

    reasons: list[str] = [
        f"Weekly trend is {wk} (the bigger tide for a 2wk–6mo trade).",
        f"Daily trend is {dl} (your entry-timing view).",
        f"Daily RSI {rsi:.0f} ({'oversold' if rsi<30 else 'overbought' if rsi>70 else 'neutral'}); "
        f"MACD is {'bullish' if macd_bull else 'bearish'}.",
    ]
    caveat = (
        "Confluence improves odds, not certainty. Confirm with volume and define your "
        "stop before entering."
    )

    # ---- badge + action decision tree ----
    if wk == "up" and not extended and pullback:
        badge, action, stance = "Buy-the-dip zone", "buy", "bullish"
        summary = (
            "Uptrend on the weekly with the daily pulled back — the kind of dip swing "
            "traders look to buy. Watch for a reversal candle and set a stop below the dip."
        )
    elif wk == "up" and extended:
        badge, action, stance = "Extended — wait", "watch", "neutral"
        summary = (
            "Trend is up but the daily is stretched (overbought / at the upper band). "
            "Chasing here is poor risk-reward — wait for a pullback toward the 20-EMA."
        )
    elif wk == "up" and dl in ("up", "flat"):
        badge, action, stance = "Trend aligned ↑", "buy", "bullish"
        summary = (
            "Weekly and daily both point up — the cleanest backdrop for a long swing. "
            "Buy strength or the next minor dip; trail a stop under the 20-EMA."
        )
    elif wk == "down" and dl == "up":
        badge, action, stance = "Counter-trend bounce — caution", "watch", "neutral"
        summary = (
            "The daily is bouncing but the weekly is still down — bounces in downtrends "
            "often fail. For a swing trade, wait for the weekly to turn before committing."
        )
    elif wk == "down":
        badge, action, stance = "Downtrend — avoid", "avoid", "bearish"
        summary = (
            "Weekly trend is down. You trade long-only, so the edge is to stand aside "
            "until the weekly trend repairs — don't try to catch the falling knife."
        )
    else:  # weekly flat / mixed
        if rsi < 32:
            badge, action, stance = "Basing / oversold", "watch", "neutral"
            summary = (
                "No clear weekly trend, but the daily is oversold — a bounce is possible. "
                "Treat as a watch until a trend establishes."
            )
        else:
            badge, action, stance = "Range / mixed — wait", "hold", "neutral"
            summary = (
                "Timeframes disagree or there's no trend. Best action is usually patience "
                "until weekly and daily line up."
            )

    return Signal(
        symbol=symbol,
        badge=badge,
        action=action,
        stance=stance,
        score=_clamp(score),
        weekly_trend=wk,
        daily_trend=dl,
        price=round(price, 2),
        reasons=reasons,
        summary=summary,
        caveat=caveat,
    )


def analyze(symbol: str) -> Signal:
    """Fetch daily + weekly bars and produce the confluence signal."""
    provider = get_provider()
    daily = provider.get_ohlcv(symbol, interval="1d", lookback=250).to_frame()
    weekly = provider.get_ohlcv(symbol, interval="1wk", lookback=160).to_frame()
    return analyze_frames(symbol, daily, weekly)
