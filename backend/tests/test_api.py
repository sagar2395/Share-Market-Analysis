"""End-to-end API tests against the offline sample provider."""

from __future__ import annotations

import os

os.environ["SMA_PROVIDER"] = "sample"  # force offline provider for deterministic tests

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health() -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["provider"] == "sample"


def test_search() -> None:
    r = client.get("/api/market/search", params={"q": "reli"})
    assert r.status_code == 200
    results = r.json()
    assert any(s["symbol"] == "RELIANCE.NS" for s in results)


def test_ohlcv() -> None:
    r = client.get("/api/market/ohlcv", params={"symbol": "RELIANCE.NS", "lookback": 120})
    assert r.status_code == 200
    candles = r.json()
    assert candles["symbol"] == "RELIANCE.NS"
    assert len(candles["bars"]) == 120
    bar = candles["bars"][-1]
    assert bar["high"] >= bar["low"]


def test_indicators_explanations() -> None:
    r = client.get("/api/analysis/indicators", params={"symbol": "TCS.NS", "keys": "ema,rsi,macd"})
    assert r.status_code == 200
    explanations = r.json()
    assert {e["indicator"] for e in explanations} == {"ema", "rsi", "macd"}
    for e in explanations:
        assert e["stance"] in {"bullish", "bearish", "neutral"}
        assert e["reading"] and e["action"]  # teaching text is present


def test_available_indicators() -> None:
    r = client.get("/api/analysis/indicators/available")
    assert r.status_code == 200
    assert set(r.json()) >= {"ema", "rsi", "macd"}
