"""Provider selection with automatic fallback.

Business logic calls :func:`get_provider` — never a concrete provider. The active
provider is chosen by ``SMA_PROVIDER``; if the requested one can't initialise
(e.g. no network for yfinance), we transparently fall back to the offline
:class:`SampleProvider` so the app always works.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import get_logger
from app.data.providers.base import MarketDataProvider
from app.data.providers.sample import SampleProvider

log = get_logger(__name__)

_cached: MarketDataProvider | None = None


def _build(name: str) -> MarketDataProvider:
    if name == "yfinance":
        from app.data.providers.yfinance_provider import YFinanceProvider

        return YFinanceProvider()
    return SampleProvider()


def get_provider(force: str | None = None) -> MarketDataProvider:
    """Return the active data provider (cached), falling back to ``sample``."""
    global _cached
    if force is not None:
        return _build(force)
    if _cached is not None:
        return _cached

    name = get_settings().provider
    try:
        _cached = _build(name)
    except Exception as exc:  # noqa: BLE001 — any init failure → safe fallback
        log.warning("Provider %r unavailable (%s); falling back to 'sample'.", name, exc)
        _cached = SampleProvider()
    return _cached


def reset_provider_cache() -> None:
    global _cached
    _cached = None
