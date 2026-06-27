# Architecture

See `PLAN.md` §4 for the full design. This is the developer-facing summary of the
**code as it exists**, updated as the app grows.

## Layers
```
Frontend (React/TS)  ──REST/WS──>  API (FastAPI)
                                      │
                                      ├─ Service layer   (watchlist ✓, portfolio ✓, ingestion ✓; screener/alerts/backtest [P2+])
                                      ├─ Intelligence    (indicators ✓ — EMA/RSI/MACD/Bollinger; signals/correlation/decisions [P2+])
                                      ├─ Data access     (provider abstraction ✓, registry+fallback ✓; cache [P2])
                                      └─ Storage         (SQLite state ✓, DuckDB history ✓)
                                                         + APScheduler EOD job ✓
```
✓ = implemented (Phase 0–1).

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
| `intelligence/indicators/*` | EMA, RSI, MACD, Bollinger (each self-registers). |
| `intelligence/registry.py` | Indicator registry (plugin discovery). |
| `intelligence/signals/confluence.py` | Weekly+daily confluence engine → `Signal`. |
| `storage/db.py` · `storage/models.py` | SQLite/SQLAlchemy state: watchlist, holdings, paper. |
| `storage/history.py` | DuckDB OHLCV history (upsert/load/stats). |
| `services/watchlist.py` · `services/portfolio.py` | Business logic for watchlist & P&L. |
| `services/screener.py` | Universe scan + presets, built on the signal engine. |
| `services/paper.py` | Paper-trading account, orders, positions, P&L. |
| `services/ingestion.py` | EOD pull of tracked symbols → DuckDB. |
| `core/scheduler.py` | APScheduler daily ingestion job (18:30 IST). |
| `api/routes/*` | Routers: health, market, analysis, signals, watchlist, portfolio, paper, admin. |
| `main.py` | App factory, CORS, lifespan (DB init + scheduler), router wiring. |

## Storage split
- **`data/app.sqlite`** (SQLAlchemy) — small mutable state: watchlist, holdings, and the
  paper-trading account/positions/trades.
- **`data/history.duckdb`** — append-only OHLCV (daily + weekly), keyed
  `(symbol, interval, time)`; fast for the correlation/backtesting phases.
- Both live under `SMA_DATA_DIR` (gitignored).

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
