"""RSI (momentum) — with plain-language teaching."""

from __future__ import annotations

import pandas as pd

from app.intelligence.indicators.base import Explanation, Indicator
from app.intelligence.registry import register


@register
class RSI(Indicator):
    key = "rsi"
    title = "RSI (14) — Momentum"

    def __init__(self, period: int = 14) -> None:
        self.period = period

    def compute(self, df: pd.DataFrame) -> pd.Series:
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / self.period, min_periods=self.period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / self.period, min_periods=self.period, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.rename("rsi")

    def explain(self, df: pd.DataFrame) -> Explanation:
        rsi = float(self.compute(df).iloc[-1])

        if rsi >= 70:
            stance = "bearish"
            reading = (
                f"RSI is {rsi:.0f} — overbought. The stock has risen fast and may be "
                "due for a pause or pullback."
            )
            action = (
                "Short-term traders often avoid fresh buys here and consider booking "
                "partial profit. A better entry is usually a dip back toward 40–50."
            )
        elif rsi <= 30:
            stance = "bullish"
            reading = (
                f"RSI is {rsi:.0f} — oversold. Selling may be overdone and a bounce is "
                "possible."
            )
            action = (
                "Watch for a reversal signal (e.g. RSI turning back above 30 with rising "
                "volume) before buying — oversold can stay oversold in a strong downtrend."
            )
        else:
            stance = "neutral"
            reading = f"RSI is {rsi:.0f} — neutral momentum, neither stretched up nor down."
            action = (
                "No momentum extreme to trade. Lean on trend (EMA) and price structure "
                "for direction; a move above 60 favours bulls, below 40 favours bears."
            )

        return Explanation(
            indicator=self.key,
            title=self.title,
            value={"rsi": round(rsi, 2)},
            stance=stance,
            summary="Measures momentum 0–100; >70 overbought, <30 oversold.",
            reading=reading,
            action=action,
            caveat=(
                "In strong trends RSI can stay overbought/oversold for a long time — "
                "don't fade a trend on RSI alone; divergences are more reliable."
            ),
        )
