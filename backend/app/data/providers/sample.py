"""Offline synthetic data provider.

Generates deterministic (seeded) random-walk OHLCV for a small NSE universe so the
app runs and tests pass with **no network** — essential for CI and sandboxed
environments. This is the safe default/fallback (see ``PLAN.md`` §5).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.data.models import Candles, Quote, SymbolInfo
from app.data.providers.base import MarketDataProvider

# A small, representative NSE universe with rough starting prices.
_UNIVERSE: dict[str, tuple[str, float]] = {
    "RELIANCE.NS": ("Reliance Industries", 2900.0),
    "TCS.NS": ("Tata Consultancy Services", 3850.0),
    "HDFCBANK.NS": ("HDFC Bank", 1650.0),
    "INFY.NS": ("Infosys", 1500.0),
    "ICICIBANK.NS": ("ICICI Bank", 1180.0),
    "SBIN.NS": ("State Bank of India", 830.0),
    "TATAMOTORS.NS": ("Tata Motors", 970.0),
    "ITC.NS": ("ITC", 430.0),
    "LT.NS": ("Larsen & Toubro", 3600.0),
    "BHARTIARTL.NS": ("Bharti Airtel", 1430.0),
}


def _seed_for(symbol: str) -> int:
    return abs(hash(symbol)) % (2**32)


def _walk(symbol: str, n: int) -> pd.DataFrame:
    """Deterministic geometric random walk with intrabar OHLC and volume."""
    name_price = _UNIVERSE.get(symbol)
    start_price = name_price[1] if name_price else 1000.0
    rng = np.random.default_rng(_seed_for(symbol))

    daily_ret = rng.normal(loc=0.0004, scale=0.015, size=n)  # slight upward drift
    close = start_price * np.exp(np.cumsum(daily_ret))
    open_ = np.empty(n)
    open_[0] = start_price
    open_[1:] = close[:-1]
    intraday = np.abs(rng.normal(0, 0.008, size=n)) * close
    high = np.maximum(open_, close) + intraday
    low = np.minimum(open_, close) - intraday
    volume = rng.integers(1_000_000, 12_000_000, size=n).astype(float)

    end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    # Business-day index ending today.
    idx = pd.bdate_range(end=end, periods=n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )


def _resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
    return df.resample("W-FRI").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()


class SampleProvider(MarketDataProvider):
    name = "sample"

    def search_symbols(self, query: str, limit: int = 20) -> list[SymbolInfo]:
        q = query.strip().lower()
        out: list[SymbolInfo] = []
        for sym, (name, _price) in _UNIVERSE.items():
            if not q or q in sym.lower() or q in name.lower():
                out.append(SymbolInfo(symbol=sym, name=name, exchange="NSE"))
            if len(out) >= limit:
                break
        return out

    def get_ohlcv(self, symbol: str, interval: str = "1d", lookback: int = 250) -> Candles:
        if interval == "1wk":
            # Build enough daily bars, then resample to weekly (swing/positional view).
            daily = _walk(symbol, lookback * 5 + 10)
            df = _resample_weekly(daily).tail(lookback)
        else:
            df = _walk(symbol, lookback)
        return Candles.from_frame(symbol, interval, df)

    def get_quote(self, symbol: str) -> Quote:
        df = _walk(symbol, 2)
        last = float(df["close"].iloc[-1])
        prev = float(df["close"].iloc[-2])
        return Quote(
            symbol=symbol,
            price=round(last, 2),
            change=round(last - prev, 2),
            change_percent=round((last - prev) / prev * 100, 2),
            previous_close=round(prev, 2),
            time=datetime.utcnow(),
        )
