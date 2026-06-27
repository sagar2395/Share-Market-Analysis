"""MACD (trend + momentum) — with plain-language teaching."""

from __future__ import annotations

import pandas as pd

from app.intelligence.indicators.base import Explanation, Indicator
from app.intelligence.registry import register


@register
class MACD(Indicator):
    key = "macd"
    title = "MACD (12,26,9)"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        self.fast, self.slow, self.signal = fast, slow, signal

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        ema_fast = df["close"].ewm(span=self.fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=self.slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal, adjust=False).mean()
        hist = macd - signal
        return pd.DataFrame({"macd": macd, "signal": signal, "hist": hist})

    def explain(self, df: pd.DataFrame) -> Explanation:
        out = self.compute(df)
        macd = float(out["macd"].iloc[-1])
        signal = float(out["signal"].iloc[-1])
        hist = float(out["hist"].iloc[-1])
        prev_hist = float(out["hist"].iloc[-2]) if len(out) > 1 else hist
        rising = hist > prev_hist

        if macd > signal:
            stance = "bullish"
            reading = (
                f"MACD ({macd:.2f}) is above its signal line ({signal:.2f}) and the "
                f"histogram is {'expanding' if rising else 'fading'} — "
                f"{'momentum is building' if rising else 'upside momentum is slowing'}."
            )
            action = (
                "Bias is to the upside; a fresh cross above the signal is a common buy "
                "trigger. Fading histogram warns the move may be tiring — tighten stops."
            )
        elif macd < signal:
            stance = "bearish"
            reading = (
                f"MACD ({macd:.2f}) is below its signal line ({signal:.2f}) and the "
                f"histogram is {'deepening' if not rising else 'recovering'} — "
                f"{'downside momentum' if not rising else 'selling may be easing'}."
            )
            action = (
                "Bias is to the downside; avoid fresh longs until MACD crosses back above "
                "the signal. A recovering histogram can be an early bottoming hint."
            )
        else:
            stance = "neutral"
            reading = "MACD and signal are level — momentum is balanced."
            action = "Wait for a clear cross before acting."

        return Explanation(
            indicator=self.key,
            title=self.title,
            value={"macd": round(macd, 3), "signal": round(signal, 3), "hist": round(hist, 3)},
            stance=stance,
            summary="Tracks trend + momentum via the gap between two moving averages.",
            reading=reading,
            action=action,
            caveat="MACD lags and gives false crosses in choppy markets; confirm with price/volume.",
        )
