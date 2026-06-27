# Development Guide

How to set up, run, test, and extend the project.

## Prerequisites
- Python 3.11+
- Node.js 20+ (22 recommended)
- macOS (Apple Silicon fine) / Linux

## Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # recommended
pip install -e ".[dev]"
uvicorn app.main:app --reload                          # http://127.0.0.1:8000
```
Interactive API docs: http://127.0.0.1:8000/docs

### Configuration (env vars)
| Var | Default | Meaning |
|---|---|---|
| `SMA_PROVIDER` | `yfinance` | Data provider: `yfinance` or `sample`. Falls back to `sample` on error. |
| `SMA_DATA_DIR` | `./data` | Where local stores (`app.sqlite`, `history.duckdb`) live. |
| `SMA_CORS_ORIGINS` | `http://127.0.0.1:5173` | Allowed frontend origins (comma-separated). |
| `SMA_ENABLE_SCHEDULER` | `true` | Run the daily EOD ingestion job on startup. Set `false` in tests. |

> In a sandbox with no internet, set `SMA_PROVIDER=sample`. Locally, leave default
> `yfinance` for real NSE/BSE data (`RELIANCE.NS`, `TCS.NS`, ...).

### Tests
```bash
cd backend && pytest
```

## Frontend
```bash
cd frontend
npm install
npm run dev        # http://127.0.0.1:5173
npm run build      # production build
```
Set the API base via `VITE_API_BASE` (default `http://127.0.0.1:8000`).

## How to extend (the important part)

### Add an indicator
1. Create `backend/app/intelligence/indicators/<name>.py`.
2. Subclass `Indicator`; implement `compute(df)` and `explain(ctx)` (plain-language,
   uses live values — this is required, see `PLAN.md` §6d).
3. Register it (the registry auto-discovers registered indicators).
4. It appears in `/api/analysis/indicators` automatically. Add a test.

### Add a data provider
1. Create `backend/app/data/providers/<name>_provider.py`.
2. Subclass `MarketDataProvider`; implement `search_symbols`, `get_ohlcv`, `get_quote`.
3. Wire it into `data/registry.py`. Select via `SMA_PROVIDER`.

### Add an API route
Add a router under `backend/app/api/routes/`, include it in `main.py`.

## Conventions
- Type-hint everything; format/lint with `ruff`.
- Keep business logic provider-agnostic (always go through the registry).
- Every user-facing feature gets a guide in `docs/guides/` and a state update in
  `docs/IMPLEMENTATION_STATE.md` (see `CLAUDE.md`).
