"""EMA crossover (trend) — with plain-language teaching."""

from __future__ import annotations

import pandas as pd

from app.intelligence.indicators.base import Explanation, Indicator
from app.intelligence.registry import register


@register
class EMACrossover(Indicator):
    key = "ema"
    title = "EMA Trend (20 vs 50)"

    def __init__(self, fast: int = 20, slow: int = 50) -> None:
        self.fast, self.slow = fast, slow

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                f"ema{self.fast}": df["close"].ewm(span=self.fast, adjust=False).mean(),
                f"ema{self.slow}": df["close"].ewm(span=self.slow, adjust=False).mean(),
            }
        )

    def explain(self, df: pd.DataFrame) -> Explanation:
        out = self.compute(df)
        fast = float(out[f"ema{self.fast}"].iloc[-1])
        slow = float(out[f"ema{self.slow}"].iloc[-1])
        price = float(df["close"].iloc[-1])
        gap_pct = (fast - slow) / slow * 100 if slow else 0.0

        if fast > slow:
            stance = "bullish"
            reading = (
                f"The short-term average ({self.fast}-EMA ₹{fast:,.1f}) is above the "
                f"longer one ({self.slow}-EMA ₹{slow:,.1f}) by {gap_pct:.1f}% — the "
                "trend is up."
            )
            action = (
                "Traders favour the long side: buy dips toward the 20-EMA rather than "
                "chasing, and trail a stop below it. Avoid shorting against this trend."
            )
        elif fast < slow:
            stance = "bearish"
            reading = (
                f"The short-term average ({self.fast}-EMA ₹{fast:,.1f}) is below the "
                f"longer one ({self.slow}-EMA ₹{slow:,.1f}) — the trend is down."
            )
            action = (
                "Caution on the long side. Many traders stand aside or wait for the "
                "20-EMA to cross back above the 50-EMA before fresh buying."
            )
        else:
            stance = "neutral"
            reading = "The two averages are entwined — no clear trend right now."
            action = "Range-trade or wait for a clean crossover before committing."

        return Explanation(
            indicator=self.key,
            title=self.title,
            value={"fast": round(fast, 2), "slow": round(slow, 2), "price": round(price, 2)},
            stance=stance,
            summary="Compares a fast vs slow moving average to read trend direction.",
            reading=reading,
            action=action,
            caveat=(
                "Moving averages lag price and whipsaw in sideways markets — confirm "
                "with momentum (RSI/MACD) and volume before acting."
            ),
        )
