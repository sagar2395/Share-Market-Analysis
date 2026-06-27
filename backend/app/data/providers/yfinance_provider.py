"""Live market data via yfinance (free).

Used when the app runs locally with internet. NSE tickers use the ``.NS`` suffix
(``RELIANCE.NS``), BSE uses ``.BO``. If a call fails (no network, rate limit), the
registry falls back to :class:`SampleProvider`.

This is the free starting point; a Zerodha Kite / Upstox provider can implement the
same :class:`MarketDataProvider` interface later (see ``PLAN.md`` §5).
"""

from __future__ import annotations

from datetime import datetime

from app.core.logging import get_logger
from app.data.models import Candles, Quote, SymbolInfo
from app.data.providers.base import MarketDataProvider
from app.data.providers.sample import _UNIVERSE

log = get_logger(__name__)

_INTERVAL_TO_PERIOD = {
    "1d": "2y",
    "1wk": "5y",
}


class YFinanceProvider(MarketDataProvider):
    name = "yfinance"

    def __init__(self) -> None:
        import yfinance  # imported lazily so the package isn't required offline

        self._yf = yfinance

    def search_symbols(self, query: str, limit: int = 20) -> list[SymbolInfo]:
        # yfinance has no clean search endpoint; for the curated NSE universe we match
        # locally. A richer symbol master can be ingested in Phase 1.
        q = query.strip().lower()
        out: list[SymbolInfo] = []
        for sym, (name, _price) in _UNIVERSE.items():
            if not q or q in sym.lower() or q in name.lower():
                out.append(SymbolInfo(symbol=sym, name=name, exchange="NSE"))
            if len(out) >= limit:
                break
        return out

    def get_ohlcv(self, symbol: str, interval: str = "1d", lookback: int = 250) -> Candles:
        period = _INTERVAL_TO_PERIOD.get(interval, "2y")
        df = self._yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
        if df.empty:
            raise RuntimeError(f"yfinance returned no data for {symbol}")
        df = df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )[["open", "high", "low", "close", "volume"]]
        df = df.tail(lookback)
        df.index = df.index.tz_localize(None) if df.index.tz is not None else df.index
        return Candles.from_frame(symbol, interval, df)

    def get_quote(self, symbol: str) -> Quote:
        candles = self.get_ohlcv(symbol, interval="1d", lookback=2)
        bars = candles.bars
        last, prev = bars[-1].close, bars[-2].close if len(bars) > 1 else bars[-1].close
        return Quote(
            symbol=symbol,
            price=round(last, 2),
            change=round(last - prev, 2),
            change_percent=round((last - prev) / prev * 100, 2) if prev else 0.0,
            previous_close=round(prev, 2),
            time=datetime.utcnow(),
        )
