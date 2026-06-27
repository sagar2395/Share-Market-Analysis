# Architecture

See `PLAN.md` §4 for the full design. This is the developer-facing summary of the
**code as it exists**, updated as the app grows.

## Layers
```
Frontend (React/TS)  ──REST/WS──>  API (FastAPI)
                                      │
                                      ├─ Service layer   (screener, portfolio, alerts, backtest)   [Phase 2+]
                                      ├─ Intelligence    (indicators ✓, signals, correlation, decisions)
                                      ├─ Data access     (provider abstraction ✓, ingestion, cache)
                                      └─ Storage         (SQLite state, DuckDB+Parquet history)      [Phase 1]
```
✓ = implemented in Phase 0.

## Backend module map (`backend/app/`)
| Module | Responsibility |
|---|---|
| `core/config.py` | App settings (Pydantic `Settings`), env-driven. |
| `core/logging.py` | Logging setup. |
| `data/models.py` | Shared Pydantic models (`SymbolInfo`, `OHLCVBar`, `Candles`, `Quote`). |
| `data/providers/base.py` | `MarketDataProvider` ABC — the data contract. |
| `data/providers/sample.py` | Offline synthetic NSE data (default fallback). |
| `data/providers/yfinance_provider.py` | Live data via `yfinance`. |
| `data/registry.py` | `get_provider()` — selects provider from config, falls back to sample. |
| `intelligence/indicators/base.py` | `Indicator` ABC: `compute()` + `explain()` (teaching). |
| `intelligence/indicators/*` | EMA, RSI, MACD (each self-registers). |
| `intelligence/registry.py` | Indicator registry (plugin discovery). |
| `api/routes/*` | FastAPI routers: health, market, analysis. |
| `main.py` | App factory, CORS, router wiring. |

## Key design principles
- **Plugins over edits.** New indicator/signal/provider = new module that registers
  itself; the core doesn't change. This is what makes the app extensible.
- **Provider abstraction.** Business logic never imports a concrete provider; it asks
  the registry. Enables free→paid and broker swaps without rewrites.
- **Offline-first.** `SampleProvider` guarantees the app runs and tests pass without
  network (essential for CI and sandboxed environments).
- **Explainability is built in.** Every `Indicator.explain()` returns plain-language
  teaching text computed from live values (see `PLAN.md` §6d).

## Data flow (vertical slice)
1. UI requests `/api/market/ohlcv?symbol=RELIANCE.NS`.
2. Router → `get_provider()` → `get_ohlcv()` returns `Candles`.
3. UI requests `/api/analysis/indicators?symbol=...&indicators=rsi,ema,macd`.
4. Router loads candles, runs each `Indicator.compute()` + `explain()`, returns values
   and teaching text.
5. UI renders candlesticks (lightweight-charts) + an explanation panel.
