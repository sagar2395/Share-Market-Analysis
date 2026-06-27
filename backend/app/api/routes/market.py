"""Market data endpoints: symbol search, OHLCV, quotes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.data.models import Candles, Quote, SymbolInfo
from app.data.registry import get_provider

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/search", response_model=list[SymbolInfo])
def search(q: str = Query("", description="Free-text symbol/name query")) -> list[SymbolInfo]:
    return get_provider().search_symbols(q)


@router.get("/ohlcv", response_model=Candles)
def ohlcv(
    symbol: str = Query(..., examples=["RELIANCE.NS"]),
    interval: str = Query("1d"),
    lookback: int = Query(250, ge=10, le=2000),
) -> Candles:
    try:
        return get_provider().get_ohlcv(symbol, interval=interval, lookback=lookback)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"OHLCV fetch failed: {exc}") from exc


@router.get("/quote", response_model=Quote)
def quote(symbol: str = Query(..., examples=["RELIANCE.NS"])) -> Quote:
    try:
        return get_provider().get_quote(symbol)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Quote fetch failed: {exc}") from exc
