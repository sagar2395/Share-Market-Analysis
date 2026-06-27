# Implementation State

> **Single source of truth for "where we are."** Read this at the start of every
> session; update it at the end of every working run. See `CLAUDE.md` §2–3.

**Last updated:** 2026-06-27
**Current phase:** Phase 0 — Foundation (scaffolding) → first vertical slice

---

## Snapshot
A working backend vertical slice exists: fetch OHLCV (offline `SampleProvider`,
auto-falls back from `yfinance` when no network) → serve via FastAPI → compute
indicators (EMA, RSI, MACD) each with a plain-language `explain()` → expose over
REST. Frontend Vite/React scaffold renders a candlestick chart + indicator
explanations against the API. Docs, state tracking, and recommendations log set up.

---

## Done ✅
- [x] `PLAN.md` — full design & roadmap (phase order FROZEN).
- [x] `CLAUDE.md` — standing agent instructions (state mgmt, docs, recommendations).
- [x] Docs skeleton: `architecture.md`, `development.md`, `guides/`, this file,
      `RECOMMENDATIONS.md`.
- [x] **Backend scaffold** (`backend/app/`): config, logging, FastAPI app, CORS.
- [x] **Data layer:** `MarketDataProvider` ABC; `SampleProvider` (offline synthetic
      NSE data); `YFinanceProvider` (live, used when network available); provider
      registry with automatic fallback.
- [x] Pydantic models: `SymbolInfo`, `OHLCVBar`, `Candles`, `Quote`.
- [x] **Intelligence engine v0:** `Indicator` base with `compute()` + `explain()`;
      EMA, RSI, MACD implemented with live-value teaching text; indicator registry.
- [x] **API:** `/api/health`, `/api/market/search`, `/api/market/ohlcv`,
      `/api/market/quote`, `/api/analysis/indicators`.
- [x] **Tests** (`backend/tests/`): health, providers, indicators — passing.
- [x] **Frontend scaffold** (`frontend/`): Vite + React + TS, lightweight-charts
      candlestick view, indicator explanation panel, API client.
- [x] User guides: getting-started + dashboard/chart guide.

## In progress 🚧
- [ ] (none — Phase 0 slice complete)

## Next up ▶️ (Phase 1 — MVP: see your market)
1. Symbol search UI wired to `/api/market/search` + watchlist (SQLite-backed).
2. Multi-timeframe candlestick chart with indicator overlays (EMA/RSI/MACD/Bollinger/volume).
3. "What am I looking at?" explainer UI surfacing `explain()` on every chart/indicator.
4. Portfolio (manual entry): holdings, avg cost, live P&L — SQLite models + UI.
5. EOD ingestion job (APScheduler) → DuckDB/Parquet history store.
6. Dashboard: indices, watchlist, top movers.

## Decisions & gotchas 📌
- **Network in sandbox:** market-data hosts (Yahoo) are blocked by the remote env's
  policy; PyPI/npm are allowed. The app is built **offline-first** via `SampleProvider`
  so it runs/tests anywhere. Locally (full internet) `YFinanceProvider` is used.
- **Indicators hand-implemented** in Phase 0 (EMA/RSI/MACD) to keep deps light and
  guarantee `explain()` integration; can adopt `pandas-ta` later for breadth.
- **Storage:** DuckDB/SQLite wiring is stubbed at Phase 0 (providers serve directly);
  persistence lands in Phase 1 with the ingestion job.
- Default provider chosen by `SMA_PROVIDER` env (`sample` | `yfinance`), default
  `yfinance` with automatic fallback to `sample` on failure.

## How to run (quick)
- Backend: `cd backend && pip install -e . && uvicorn app.main:app --reload` → http://127.0.0.1:8000/docs
- Frontend: `cd frontend && npm install && npm run dev` → http://127.0.0.1:5173
- Tests: `cd backend && pytest`

See `docs/development.md` for details.
