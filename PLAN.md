# Share-Market-Analysis — Implementation Plan

> Personal market analysis & decision-support tool for the Indian market (NSE/BSE).
> Focus: **swing/positional trading on a ~2-week to ~6-month horizon** (no intraday),
> with a long-term sleeve. Built to be extensible.
>
> **Trading horizon (authoritative):** the owner does **not** day-trade. "Short-term"
> means holding **2 weeks–6 months**. Analysis works on **daily and weekly** timeframes;
> there is no need for intraday/minute data or real-time tick streaming. Signals target
> swing/positional setups, not scalps.
>
> **Status:** Plan for review. No code written yet.
> **Disclaimer:** This is a personal decision-support tool, not financial advice. All signals/suggestions are probabilistic aids, not guarantees.

---

## 1. Decisions locked in

| Decision | Choice |
|---|---|
| Market | Indian — NSE/BSE (Nifty/Sensex universe) |
| Data budget | Start free, abstract behind interfaces, upgrade to paid later |
| Broker integration | Manual entry first; design for Zerodha Kite / Upstox API in a later phase |
| App form factor | **Local-first web app** (browser on localhost), optional Tauri desktop wrapper later |

---

## 2. Form factor: why local web app (not native desktop)

You leaned desktop; here's why a **local-first web app** wins for *this* requirement, and how you still get the "desktop feel."

**The hard constraint:** serious market analysis lives in the **Python** ecosystem (pandas, numpy, TA-Lib/pandas-ta, scikit-learn, statsmodels, vectorbt, yfinance, nsepython). That's non-negotiable for the analytics you want. So the question isn't "Python vs not" — it's "what renders the UI."

**Why web UI over a native toolkit (PyQt/Swift):**
- **Best-in-class charting is web-native and free:** TradingView Lightweight Charts, ECharts, Plotly. Native desktop charting is years behind for financial candlesticks/overlays.
- **Fastest to extend:** adding a new screen/indicator/panel is a React component, not a native rebuild.
- **Zero packaging pain during development** — just run two processes.
- **Bonus:** reachable from your phone on the same Wi-Fi (read-only dashboard) with no extra work.

**You still get desktop:** we can wrap the exact same app in **Tauri 2.0** (Rust shell, tiny footprint, excellent on Apple Silicon / M5) in a later phase. It launches like a native `.app`, runs the Python backend as a sidecar, and feels like a desktop program — without locking us out of web tech. This is strictly better than Electron on an M-series Mac (smaller, faster, less RAM).

**Verdict:** Build a local web app now (run via one command). Add the Tauri desktop shell in Phase 5 once the app is worth packaging.

---

## 3. Tech stack

### Backend (the brain)
| Concern | Choice | Why |
|---|---|---|
| Language | **Python 3.12+** | The financial/ML ecosystem |
| API server | **FastAPI** + Uvicorn | Async REST + WebSocket (live price push), auto OpenAPI docs |
| Validation/models | **Pydantic v2** | Typed contracts shared across layers |
| DataFrames | **pandas** (+ **polars** where speed matters) | Standard for time-series |
| Technical indicators | **pandas-ta** (primary) / **TA-Lib** (optional, C-accelerated) | 150+ indicators without reinventing |
| Stats/ML | **scikit-learn**, **statsmodels**, **lightgbm** | Correlations, regression, regime/classification models |
| Backtesting | **vectorbt** (fast, vectorized) | Validate every signal/strategy on history |
| Scheduling | **APScheduler** | Periodic data pulls, EOD jobs, alert checks |
| Transactional DB | **SQLite** via **SQLAlchemy** | Zero-config local store for portfolio/watchlists/settings |
| Analytical store | **DuckDB** + **Parquet** | Fast OLAP over years of OHLCV; ideal for correlation/rolling math |
| Caching | **diskcache** / SQLite | Respect free-API rate limits |

> **Storage split rationale:** SQLite for small mutable state (your trades, watchlists, alerts). DuckDB+Parquet for the large append-only price/fundamentals history — it makes cross-stock correlation queries fast and cheap.

### Frontend (the cockpit)
| Concern | Choice | Why |
|---|---|---|
| Framework | **React + TypeScript + Vite** | Fast, huge ecosystem, type-safe |
| Financial charts | **TradingView Lightweight Charts** | Free, the gold standard for candles/overlays |
| Analytics charts | **ECharts** (or Plotly) | Heatmaps (correlation), treemaps (sector flow), network graphs |
| Data grids | **AG Grid (community)** | Screener tables, portfolio, sortable/filterable |
| Server state | **TanStack Query** | Caching, background refetch, live data |
| Client state | **Zustand** | Lightweight UI state |
| Styling/UI kit | **Tailwind CSS + shadcn/ui** | Clean, fast to build, dark-mode-first |

### Desktop wrapper (Phase 5, optional)
- **Tauri 2.0** bundling the built frontend + Python backend sidecar → native `.app` for macOS (Apple Silicon).

### Tooling
- **uv** or **Poetry** (Python deps), **ruff** + **black** (lint/format), **pytest** (tests)
- **pnpm** (frontend), **ESLint + Prettier**
- **Docker Compose** optional for one-command local run
- **Pre-commit hooks**, GitHub Actions CI (lint + tests)

---

## 4. Architecture

Layered + modular so features bolt on without touching the core. Everything analysis-related is a **plugin** conforming to a small interface.

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend (React/TS)  — dashboard, charts, screener, portfolio │
└───────────────▲──────────────────────────────────────────────┘
                │ REST + WebSocket (JSON)
┌───────────────┴──────────────────────────────────────────────┐
│  API Layer (FastAPI)  — routers, auth(local), WS price stream  │
├───────────────────────────────────────────────────────────────┤
│  Service Layer                                                 │
│   • Screener     • Portfolio     • Alerts     • Backtest       │
├───────────────────────────────────────────────────────────────┤
│  Intelligence Engine  (the differentiator)                     │
│   • Indicators registry   • Signal generators                  │
│   • Correlation/relationship engine                            │
│   • Decision/recommendation aggregator                         │
├───────────────────────────────────────────────────────────────┤
│  Data Access Layer                                             │
│   • Provider abstraction (free↔paid swappable)                 │
│   • Ingestion/normalization • Rate-limit & cache               │
├───────────────────────────────────────────────────────────────┤
│  Storage:  SQLite (state)   |   DuckDB + Parquet (history)     │
└───────────────────────────────────────────────────────────────┘
```

### Extensibility model (key requirement)
Every analytical unit implements a tiny contract and self-registers, so "add a feature later" = "drop in a new module":

```python
class Indicator(Protocol):
    name: str
    def compute(self, df: pd.DataFrame, **params) -> pd.Series | pd.DataFrame: ...
    def explain(self, ctx: AnalysisContext) -> Explanation: ...   # plain-language teaching, uses live values

class SignalGenerator(Protocol):
    name: str
    def generate(self, ctx: AnalysisContext) -> list[Signal]: ...   # each Signal carries its own "why" + action rationale

class DataProvider(Protocol):
    def ohlcv(self, symbol, interval, start, end) -> pd.DataFrame: ...
    def fundamentals(self, symbol) -> Fundamentals: ...
    def quote(self, symbol) -> Quote: ...
```
- Swap **DataProvider** (yfinance → Kite) without touching analysis.
- New strategies, indicators, and correlation studies register into a registry and appear in the UI automatically.

---

## 5. Data layer (India-first, free → paid)

All providers sit behind the `DataProvider` interface. Free now, paid drop-in later.

### Free sources (Phase 1)
| Data | Source | Notes |
|---|---|---|
| OHLCV history (EOD + intraday) | **yfinance** (`RELIANCE.NS`, `.BO`) | Free, rate-limited; good for daily history |
| Live quotes, indices, option chain | **nsepython / jugaad-data / nsetools** | Scrapes NSE India; fragile but rich (FII/DII, OI, deals) |
| BSE data | **bsedata** | BSE quotes/indices |
| Fundamentals | **screener.in** / Tickertape (scrape) + yfinance | Ratios, P&L, balance sheet |
| **FII/DII flows** | NSE/BSE daily reports | *High-signal for Indian market* |
| Index & sectoral indices | NSE (Nifty 50, Bank Nifty, sectoral) | Sector rotation analysis |
| Macro cues | yfinance: USD/INR, crude, gold, Gift Nifty, US indices, India VIX | Cross-asset correlation |
| News/sentiment | Moneycontrol/ET RSS, NewsAPI (free tier) | Headline sentiment vs price |
| Corporate actions / results calendar | NSE | Event-aware analysis |

### Paid upgrade path (later, behind same interface)
- **Zerodha Kite Connect** (~₹2000/mo): reliable live + historical data **and** order placement (doubles as broker integration).
- **Upstox API**: low-cost alternative.
- **FMP / Polygon / Alpha Vantage premium**: cleaner fundamentals.

### Ingestion strategy
- Nightly EOD job (APScheduler): pull/append OHLCV + fundamentals + FII/DII → DuckDB/Parquet.
- Intraday polling for watchlist symbols (respecting rate limits), pushed to UI via WebSocket.
- Aggressive caching; exponential backoff; provider failover (if NSE scrape fails, fall back to yfinance).

---

## 6. The Intelligence Engine — the differentiator

This is what makes the tool more than "info a normal user has." It hunts for **relationships and money-flow** the casual investor never sees, then converts them into decisions.

### 6a. Correlation & relationship engine
- **Rolling correlation matrices** across your universe (which stocks move together; detect breakdowns in correlation = early signal).
- **Lead–lag detection:** does stock/sector A reliably move *before* B? (cross-correlation at lags) → anticipatory trades.
- **Sector rotation map:** money flowing between Nifty sectoral indices (treemap + flow over time) → ride the rotation.
- **Macro factor exposure:** each stock's sensitivity (beta) to Nifty, **USD/INR**, **crude**, gold, US markets, India VIX → know *why* something moves.
- **FII/DII flow vs price:** correlate daily institutional flows with index/stock moves (a genuinely India-specific edge).
- **Delivery % analysis** (NSE): separate "real" accumulation from intraday churn — high delivery + price up = conviction.
- **Options-derived signals:** PCR (Put-Call Ratio), OI buildup, max-pain, Bank Nifty positioning → sentiment & support/resistance.
- **Regime detection:** classify market state (trending/ranging/high-vol) so signals are weighted by context.
- **Breadth indicators:** advance/decline, % above 200-DMA → is the rally healthy?

### 6b. Technical analysis
- Full indicator suite (EMA/SMA, RSI, MACD, Bollinger, ATR, ADX, Supertrend, VWAP, Stochastic, Ichimoku, etc.).
- **Candlestick & chart-pattern recognition** (engulfing, hammer, breakouts, flags, support/resistance, trendlines).
- **Multi-timeframe confluence** (weekly trend + daily entry/timing) — core to swing/positional trading. No intraday timeframes.
- Volume profile, pivot points, Fibonacci levels.

### 6c. Fundamental analysis
- Key ratios (P/E, P/B, ROE, ROCE, debt/equity, margins, growth), peer comparison within sector.
- Quality scores (Piotroski F-score, Altman Z), promoter holding & **pledging** trends, earnings surprises.
- Quick health scorecard per stock.

### 6d. Learning & explainability layer (teach me as I use it)
A cross-cutting feature, not a separate screen: **every chart, indicator, and correlation explains itself in plain language and tells you what to *do* with it.** You know the basics — this turns the tool into a tutor that levels you up while you trade.

- **"What am I looking at?" on everything** — an info/expand control on every chart, indicator, heatmap, and signal that explains, in 2–3 plain sentences: *what it measures → what the current reading means → what it typically implies for a buy/sell/hold*. Example for RSI: *"Measures momentum 0–100. Right now it's 78 = overbought, meaning the stock has run up fast and may be due for a pullback. Short-term traders often avoid fresh buys here or book partial profits; wait for a dip toward 40–50 for a better entry."*
- **Plain-language reading of each correlation** — e.g. *"RELIANCE and the energy sector are 0.85 correlated this month, but that just dropped from 0.95. A breaking correlation often means something stock-specific is happening — worth checking news before trading on the sector view."* Or for FII/DII: *"FIIs sold ₹3,000 cr today while the index held up — domestic buying is absorbing foreign selling. Historically this is a sign of underlying strength, but watch if FII selling persists for several days."*
- **Live interpretation, not static glossary** — explanations use the *current* numbers for *this* stock, so the lesson is always concrete and contextual, not a textbook definition.
- **"Why this signal" breakdown** — every Buy/Sell/Hold expands into the exact factors that produced it, each with a one-line rationale, so you learn the reasoning pattern over time.
- **Chart-reading guidance** — pattern annotations are labeled and explained ("this is a bullish flag — a brief pause in an uptrend that often resolves upward; traders watch for a breakout above the upper line"), with the suggested action and where the idea fails (invalidation level).
- **Glossary + concept cards** — a searchable, linked glossary (RSI, PCR, delivery %, beta, max-pain, etc.); any term in the UI is clickable to its card. Optional "explain like I'm learning" toggle for more detail.
- **Progressive depth** — concise by default, with an "explain more" expansion that goes deeper (the math/history) when you want it, so it never clutters but is always available.
- **Confidence & caveats stated honestly** — explanations include when a signal is unreliable (e.g. "low volume makes this breakout less trustworthy"), training good judgment rather than blind following.

> Implementation note: explanations are generated from a **rule/template engine over live values** (deterministic, fast, free) for everyday readings, with an optional LLM layer later for free-form "explain this chart to me" Q&A. Each indicator/correlation module ships its own `explain(context) -> str` method, so the teaching content grows automatically as features are added.

### 6e. Decision / recommendation engine
Combines the above into an actionable, *explainable* call. **Never a black box** — every suggestion shows its reasons.

- **Composite scoring:** weighted blend of technical, fundamental, flow, sentiment, and correlation signals → score per stock.
- **Two profiles, your two styles:**
  - *Swing/positional (2wk–6mo):* momentum, breakout, pullback-in-trend, volume/delivery surge — multi-day to multi-week setups with defined risk.
  - *Long-term:* fundamental quality + value + trend.
- **Output per idea:** action (Buy/Add/Hold/Trim/Exit/Avoid), conviction %, suggested **entry / stop-loss / targets**, position-size hint (risk-based), time horizon, and **"why" bullet list**.
- **ML layer (Phase 4):** lightgbm/logistic models predicting probability of an N-day favorable move, trained on historical features — surfaced as one input, **always backtested** before trust.
- **Every strategy is backtested** (vectorbt): win rate, expectancy, max drawdown, Sharpe — so you trust signals based on evidence, not vibes.

---

## 7. Feature roadmap (phased)

### Phase 0 — Foundation (scaffolding)
- Monorepo (`backend/`, `frontend/`), tooling, CI, config, SQLite+DuckDB setup, provider abstraction stub, health-check endpoint, one end-to-end "hello data" flow (fetch RELIANCE.NS → chart it).

### Phase 1 — MVP: see your market
- Symbol search (NSE/BSE universe), watchlists.
- Interactive candlestick charts (multi-timeframe) with core indicators (EMA, RSI, MACD, Bollinger, volume).
- **Learning layer (from day one):** "what am I looking at?" explainers on every chart/indicator + clickable glossary — so the teaching grows with each feature instead of being bolted on at the end.
- **Portfolio (manual entry):** holdings, avg cost, live P&L, allocation.
- EOD ingestion job + local history store.
- Dashboard: indices, your watchlist, top movers.

### Phase 2 — Screener & signals
- **Stock screener** (technical + fundamental filters; presets like "momentum breakout", "oversold quality").
- Signal engine: indicator-based buy/sell/hold tags on watchlist.
- Alerts (price/indicator thresholds) with desktop/browser notifications.
- Pattern recognition (candles + S/R).

### Phase 3 — Fundamentals & the correlation engine
- Fundamental data + per-stock scorecard + peer comparison.
- **Correlation engine:** rolling correlation heatmap, sector-rotation map, macro-factor exposure, **FII/DII flow** dashboard, delivery % analysis.
- Options data: PCR / OI / max-pain (Nifty & Bank Nifty).

### Phase 4 — Decisions & backtesting
- **Composite recommendation engine** (short-term + long-term profiles) with explainable output and risk-based position sizing.
- **Backtesting** of every strategy (vectorbt) + performance analytics.
- ML probability model as an input signal.
- News/sentiment ingestion + sentiment-vs-price correlation.

### Phase 5 — Polish, alerts, packaging
- Live-ish EOD/delayed quote refresh (WebSocket) for the watchlist — no intraday tick streaming needed.
- Trade journal & analytics (your win rate, what setups work *for you*).
- **Broker integration** (Zerodha Kite/Upstox): auto portfolio sync, optional order placement.
- **Tauri desktop packaging** for macOS (M5).
- Optional: paper-trading mode, export/reporting (PDF/Excel).

---

## 8. Value-add features I'm proposing (beyond your ask)

- **Built-in tutor (learning & explainability layer)** — every chart, indicator, and correlation explains what it means *and what to do about it* using live values for the stock you're viewing, plus a clickable glossary and progressive "explain more" depth. Turns the tool into something that levels up your market understanding as you use it. *(Detailed in §6e.)*
- **Trade journal with self-analytics** — the tool learns *which setups make money for you specifically*, not just generic signals. Huge for a short-term trader.
- **Risk-first position sizing** — every idea sized to a fixed % portfolio risk via stop distance (protects quick-win capital).
- **"Why did it move?" explainer** — for any move, auto-attribute it to sector/macro/flow/news factors.
- **Pre-open prep brief** — daily auto-generated morning note: Gift Nifty, US close, FII/DII, your watchlist signals, events today.
- **Event-aware mode** — flags upcoming results/ex-dates so you're not blindsided.
- **Paper-trading sandbox** — test the engine's calls with fake money before risking real capital.
- **Regime-adaptive signals** — suppress mean-reversion signals in strong trends and vice versa.

---

## 9. Repository structure (proposed)

```
Share-Market-Analysis/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers (REST + WS)
│   │   ├── core/           # config, logging, scheduler
│   │   ├── data/           # providers (yfinance, nse, ...), ingestion, cache
│   │   ├── storage/        # SQLite models, DuckDB access
│   │   ├── intelligence/   # indicators, signals, correlation, decisions
│   │   ├── services/       # screener, portfolio, alerts, backtest
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── features/       # dashboard, charts, screener, portfolio, ...
│   │   ├── components/ ui/ lib/ store/
│   │   └── main.tsx
│   └── package.json
├── data/                   # local parquet/duckdb/sqlite (gitignored)
├── docker-compose.yml
├── PLAN.md
└── README.md
```

---

## 10. Risks & considerations
- **Free NSE scraping is fragile** (NSE changes/blocks). Mitigation: provider abstraction + failover + clear path to Kite Connect.
- **Rate limits** on free APIs → caching + scheduled batch pulls, not on-demand hammering.
- **Data quality/gaps** → validation layer, multi-source cross-check.
- **Overfitting ML/strategies** → mandatory walk-forward backtesting; treat ML as *one* input, not gospel.
- **Not financial advice** — keep human-in-the-loop; the tool suggests, you decide.
- **Secrets** (future broker keys) → `.env`, never committed; local OS keychain when packaged.

---

## 11. Immediate next steps (after you approve)
1. Scaffold the monorepo (Phase 0) on `main`.
2. Wire one vertical slice end-to-end: search RELIANCE.NS → fetch via yfinance → store → candlestick chart in the UI.
3. Stand up the EOD ingestion job + DuckDB store.
4. Iterate into Phase 1 (watchlists, indicators, manual portfolio).

> **Open question for you:** confirm the phase ordering matches your priorities — e.g., do you want the **screener (Phase 2)** or the **correlation/FII-DII engine (Phase 3)** pulled earlier? I can reorder so your highest-value feature lands sooner.
