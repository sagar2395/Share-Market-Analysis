"""Analysis endpoints: compute indicators and return their teaching explanations."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.data.registry import get_provider
from app.intelligence.indicators.base import Explanation
from app.intelligence.registry import available, get_indicator

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _load_frame(symbol: str, interval: str, lookback: int) -> pd.DataFrame:
    candles = get_provider().get_ohlcv(symbol, interval=interval, lookback=lookback)
    df = candles.to_frame()
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    return df


@router.get("/indicators/available", response_model=list[str])
def list_indicators() -> list[str]:
    return available()


@router.get("/indicators", response_model=list[Explanation])
def indicators(
    symbol: str = Query(..., examples=["RELIANCE.NS"]),
    keys: str = Query("ema,rsi,macd,bollinger", description="Comma-separated indicator keys"),
    interval: str = Query("1d"),
    lookback: int = Query(250, ge=30, le=2000),
) -> list[Explanation]:
    """Return a plain-language explanation per requested indicator for ``symbol``.

    This is the API behind the "what am I looking at?" teaching feature.
    """
    df = _load_frame(symbol, interval, lookback)
    out: list[Explanation] = []
    for key in [k.strip() for k in keys.split(",") if k.strip()]:
        try:
            out.append(get_indicator(key).explain(df))
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return out


@router.get("/overlays")
def overlays(
    symbol: str = Query(..., examples=["RELIANCE.NS"]),
    keys: str = Query("ema,bollinger", description="Indicators to draw as line overlays"),
    interval: str = Query("1d"),
    lookback: int = Query(250, ge=30, le=2000),
) -> dict:
    """Return time-aligned indicator line series for chart overlays (EMA, Bollinger…)."""
    df = _load_frame(symbol, interval, lookback)
    times = [t.strftime("%Y-%m-%d") for t in df.index]
    series: dict[str, list] = {}
    for key in [k.strip() for k in keys.split(",") if k.strip()]:
        try:
            result = get_indicator(key).compute(df)
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if isinstance(result, pd.Series):
            result = result.to_frame(name=key)
        for col in result.columns:
            vals = result[col]
            series[f"{key}.{col}"] = [
                {"time": t, "value": (None if pd.isna(v) else round(float(v), 2))}
                for t, v in zip(times, vals)
            ]
    return {"symbol": symbol, "interval": interval, "series": series}
