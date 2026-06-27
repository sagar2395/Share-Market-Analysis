"""Shared data models (the contracts that flow between layers)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field


class SymbolInfo(BaseModel):
    symbol: str = Field(..., description="Ticker, e.g. RELIANCE.NS")
    name: str
    exchange: str = "NSE"


class OHLCVBar(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Candles(BaseModel):
    symbol: str
    interval: str = "1d"
    bars: list[OHLCVBar] = Field(default_factory=list)

    def to_frame(self) -> pd.DataFrame:
        """Return an indexed OHLCV DataFrame (used by the intelligence engine)."""
        if not self.bars:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        df = pd.DataFrame([b.model_dump() for b in self.bars])
        df = df.set_index("time").sort_index()
        return df

    @classmethod
    def from_frame(cls, symbol: str, interval: str, df: pd.DataFrame) -> "Candles":
        bars = [
            OHLCVBar(
                time=idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else idx,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
            for idx, row in df.iterrows()
        ]
        return cls(symbol=symbol, interval=interval, bars=bars)


class Quote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    previous_close: float
    time: datetime
