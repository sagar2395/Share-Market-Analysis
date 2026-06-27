"""DuckDB + Parquet — append-only OHLCV history.

Fast analytical store for years of daily/weekly bars across the whole universe. Kept
separate from the SQLite state DB so heavy correlation/rolling queries (later phases)
stay cheap. Phase 1 uses it to persist EOD history pulled by the ingestion job.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from app.core.config import get_settings

_TABLE = "ohlcv"


def _db_path() -> str:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return str(settings.data_dir / "history.duckdb")


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(_db_path())
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_TABLE} (
            symbol   VARCHAR,
            interval VARCHAR,
            time     TIMESTAMP,
            open     DOUBLE,
            high     DOUBLE,
            low      DOUBLE,
            close    DOUBLE,
            volume   DOUBLE,
            PRIMARY KEY (symbol, interval, time)
        )
        """
    )
    return con


def upsert(symbol: str, interval: str, df: pd.DataFrame) -> int:
    """Insert/replace OHLCV rows for a symbol. ``df`` is indexed by time."""
    if df.empty:
        return 0
    rows = df.reset_index()
    rows = rows.rename(columns={rows.columns[0]: "time"})
    rows["symbol"] = symbol
    rows["interval"] = interval
    rows = rows[["symbol", "interval", "time", "open", "high", "low", "close", "volume"]]
    con = _connect()
    try:
        con.register("incoming", rows)
        con.execute(
            f"DELETE FROM {_TABLE} t USING incoming i "
            "WHERE t.symbol=i.symbol AND t.interval=i.interval AND t.time=i.time"
        )
        con.execute(f"INSERT INTO {_TABLE} SELECT * FROM incoming")
        con.unregister("incoming")
        return len(rows)
    finally:
        con.close()


def load(symbol: str, interval: str = "1d", lookback: int | None = None) -> pd.DataFrame:
    """Load stored OHLCV for a symbol as a time-indexed DataFrame."""
    con = _connect()
    try:
        q = (
            f"SELECT time, open, high, low, close, volume FROM {_TABLE} "
            "WHERE symbol=? AND interval=? ORDER BY time"
        )
        df = con.execute(q, [symbol, interval]).fetch_df()
    finally:
        con.close()
    if df.empty:
        return df
    df = df.set_index("time")
    return df.tail(lookback) if lookback else df


def stats() -> dict:
    con = _connect()
    try:
        n_rows = con.execute(f"SELECT count(*) FROM {_TABLE}").fetchone()[0]
        n_syms = con.execute(f"SELECT count(DISTINCT symbol) FROM {_TABLE}").fetchone()[0]
    finally:
        con.close()
    return {"rows": int(n_rows), "symbols": int(n_syms)}
