"""Unit tests for indicator maths and explanations."""

from __future__ import annotations

from app.data.providers.sample import SampleProvider
from app.intelligence.indicators.rsi import RSI


def _frame():
    return SampleProvider().get_ohlcv("RELIANCE.NS", lookback=200).to_frame()


def test_rsi_bounds() -> None:
    rsi = RSI().compute(_frame()).dropna()
    assert (rsi >= 0).all() and (rsi <= 100).all()


def test_rsi_explanation_shape() -> None:
    exp = RSI().explain(_frame())
    assert exp.indicator == "rsi"
    assert exp.stance in {"bullish", "bearish", "neutral"}
    assert exp.value["rsi"] is not None
    assert exp.caveat  # honest caveat present
