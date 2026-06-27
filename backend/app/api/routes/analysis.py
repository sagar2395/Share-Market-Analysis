"""Analysis endpoints: compute indicators and return their teaching explanations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.data.registry import get_provider
from app.intelligence.indicators.base import Explanation
from app.intelligence.registry import available, get_indicator

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/indicators/available", response_model=list[str])
def list_indicators() -> list[str]:
    return available()


@router.get("/indicators", response_model=list[Explanation])
def indicators(
    symbol: str = Query(..., examples=["RELIANCE.NS"]),
    keys: str = Query("ema,rsi,macd", description="Comma-separated indicator keys"),
    interval: str = Query("1d"),
    lookback: int = Query(250, ge=30, le=2000),
) -> list[Explanation]:
    """Return a plain-language explanation per requested indicator for ``symbol``.

    This is the API behind the "what am I looking at?" teaching feature.
    """
    candles = get_provider().get_ohlcv(symbol, interval=interval, lookback=lookback)
    df = candles.to_frame()
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")

    out: list[Explanation] = []
    for key in [k.strip() for k in keys.split(",") if k.strip()]:
        try:
            out.append(get_indicator(key).explain(df))
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return out
