"""Application configuration.

Settings are environment-driven (prefix ``SMA_``) so the same code runs in a
sandbox (offline, ``SMA_PROVIDER=sample``) and locally (``yfinance`` with real
NSE/BSE data). See ``docs/development.md``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMA_", env_file=".env", extra="ignore")

    app_name: str = "Share-Market-Analysis"
    debug: bool = True

    # Data provider: "yfinance" (live) or "sample" (offline synthetic).
    # On any failure the registry falls back to "sample".
    provider: str = "yfinance"

    # Local data directory for DuckDB/SQLite/Parquet stores (used from Phase 1).
    data_dir: Path = Path("./data")

    # Comma-separated list of allowed frontend origins for CORS.
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
