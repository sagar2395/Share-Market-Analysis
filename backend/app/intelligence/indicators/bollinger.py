"""Bollinger Bands (volatility + mean-reversion) — with plain-language teaching."""

from __future__ import annotations

import pandas as pd

from app.intelligence.indicators.base import Explanation, Indicator
from app.intelligence.registry import register


@register
class Bollinger(Indicator):
    key = "bollinger"
    title = "Bollinger Bands (20, 2σ)"

    def __init__(self, period: int = 20, num_std: float = 2.0) -> None:
        self.period, self.num_std = period, num_std

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        mid = df["close"].rolling(self.period).mean()
        std = df["close"].rolling(self.period).std()
        upper = mid + self.num_std * std
        lower = mid - self.num_std * std
        return pd.DataFrame({"mid": mid, "upper": upper, "lower": lower})

    def explain(self, df: pd.DataFrame) -> Explanation:
        out = self.compute(df)
        price = float(df["close"].iloc[-1])
        upper = float(out["upper"].iloc[-1])
        lower = float(out["lower"].iloc[-1])
        mid = float(out["mid"].iloc[-1])
        width = (upper - lower) / mid * 100 if mid else 0.0
        # Bandwidth percentile over the visible window → squeeze detection.
        bw = ((out["upper"] - out["lower"]) / out["mid"] * 100).dropna()
        squeeze = bool(width <= bw.quantile(0.2)) if len(bw) > 5 else False
        pos = (price - lower) / (upper - lower) if upper > lower else 0.5

        if squeeze:
            stance = "neutral"
            reading = (
                f"The bands are unusually tight (width {width:.1f}%) — a 'squeeze'. "
                "Volatility is compressed and a bigger move often follows."
            )
            action = (
                "Don't predict direction from the squeeze itself; wait for a breakout "
                "(close outside a band on rising volume) and trade in that direction."
            )
        elif price >= upper:
            stance = "bearish"
            reading = (
                f"Price (₹{price:,.1f}) is at/above the upper band (₹{upper:,.1f}) — "
                "stretched above its recent average."
            )
            action = (
                "In a range, this favours mean-reversion (avoid chasing, consider trimming). "
                "In a strong uptrend, 'riding the band' can continue — confirm with trend."
            )
        elif price <= lower:
            stance = "bullish"
            reading = (
                f"Price (₹{price:,.1f}) is at/below the lower band (₹{lower:,.1f}) — "
                "stretched below its recent average."
            )
            action = (
                "In a range, a bounce toward the midline (₹{:,.1f}) is common — watch for a "
                "reversal candle before buying. In a downtrend, wait for confirmation."
            ).format(mid)
        else:
            stance = "neutral"
            reading = (
                f"Price is mid-band (about {pos*100:.0f}% of the way up), width {width:.1f}% — "
                "no volatility extreme."
            )
            action = "Use the midline as dynamic support/resistance; trade with the trend."

        return Explanation(
            indicator=self.key,
            title=self.title,
            value={
                "price": round(price, 2),
                "upper": round(upper, 2),
                "mid": round(mid, 2),
                "lower": round(lower, 2),
                "width_pct": round(width, 2),
            },
            stance=stance,
            summary="Shows volatility as bands around a 20-day average; squeezes precede big moves.",
            reading=reading,
            action=action,
            caveat=(
                "Touching a band is not a signal by itself — in trends price hugs the band. "
                "Combine with trend (EMA) and volume."
            ),
        )
