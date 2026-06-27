"""EOD ingestion — pull OHLCV for tracked symbols into the DuckDB history store.

Runs daily (APScheduler) and can be triggered manually. Persisting history locally
makes later phases (correlation, backtesting) fast and keeps us within free-API limits.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.data.registry import get_provider
from app.services import watchlist
from app.storage import history

log = get_logger(__name__)

# Intervals to keep on disk for swing/positional analysis (no intraday).
INTERVALS = ("1d", "1wk")


def symbols_to_ingest() -> list[str]:
    """Watchlist ∪ portfolio symbols (deduped)."""
    from sqlalchemy import select

    from app.storage.db import session_scope
    from app.storage.models import Holding

    syms = {i["symbol"] for i in watchlist.list_items()}
    with session_scope() as s:
        syms |= {h.symbol for h in s.scalars(select(Holding)).all()}
    return sorted(syms)


def ingest_symbol(symbol: str) -> int:
    provider = get_provider()
    written = 0
    for interval in INTERVALS:
        try:
            candles = provider.get_ohlcv(symbol, interval=interval, lookback=500)
            written += history.upsert(symbol, interval, candles.to_frame())
        except Exception as exc:  # noqa: BLE001
            log.warning("Ingest failed for %s @ %s: %s", symbol, interval, exc)
    return written


def run() -> dict:
    """Ingest all tracked symbols. Returns a small report."""
    symbols = symbols_to_ingest()
    total = 0
    for sym in symbols:
        total += ingest_symbol(sym)
    log.info("Ingestion complete: %d symbols, %d rows written.", len(symbols), total)
    return {"symbols": len(symbols), "rows_written": total, **history.stats()}
