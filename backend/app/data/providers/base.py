"""The data provider contract.

All business logic depends on this ABC, never on a concrete provider. This is what
lets us swap free sources (yfinance) for paid/broker sources (Zerodha Kite, Upstox)
later without touching the rest of the app. See ``PLAN.md`` §4–5.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.data.models import Candles, Quote, SymbolInfo


class MarketDataProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search_symbols(self, query: str, limit: int = 20) -> list[SymbolInfo]:
        """Return symbols matching a free-text query."""

    @abstractmethod
    def get_ohlcv(self, symbol: str, interval: str = "1d", lookback: int = 250) -> Candles:
        """Return OHLCV candles for ``symbol`` (most recent ``lookback`` bars)."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """Return the latest quote for ``symbol``."""
