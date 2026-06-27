# CLAUDE.md — Instructions for AI agents working on this project

This file is read by every AI agent (Claude Code or otherwise) before working on
**Share-Market-Analysis**. Follow it exactly. It encodes the owner's standing
instructions so work stays consistent across sessions.

---

## 0. What this project is
A **personal** market analysis & decision-support tool for the **Indian market
(NSE/BSE)**. The owner is a short-term trader with a long-term sleeve. It must:
find/screen stocks, analyse them (technical + fundamental), surface
**correlations & money-flow** a normal user can't see, and give **explainable**
buy/sell/hold suggestions — while **teaching** the owner what every chart and
correlation means and what to do about it.

The authoritative design is **`PLAN.md`** (read it first). Phase ordering in
`PLAN.md` §7 is **FROZEN** — do not reorder phases without explicit owner
approval.

---

## 1. Standing rules (the owner's explicit instructions)

1. **Work on `main` directly.** The owner has authorized direct commits to `main`.
   Commit in logical units with clear messages. Push when a unit of work is done.
2. **Keep the state file current.** `docs/IMPLEMENTATION_STATE.md` is the source
   of truth for "where we are." At the **start** of every session, read it. At the
   **end** of every working run, update it so the next agent can resume seamlessly.
3. **Document as you build.** Developer docs live in `docs/`. Every feature ships
   with a **user guide** in `docs/guides/` (see §4) so the owner can explore the
   app and get unstuck. Documentation is part of "done," not optional.
4. **Teaching is a feature.** Per `PLAN.md` §6d, anything you build that shows data
   to the user (chart, indicator, correlation, signal) must be able to **explain
   itself in plain language using live values** and say what action it implies.
   Indicators/signals/correlation modules implement an `explain()` method.
5. **After every implementation run, produce a feature-recommendation analysis.**
   Append a dated entry to `docs/RECOMMENDATIONS.md` proposing features/improvements
   that would make the app better (with rationale + rough effort + which phase).
   The owner decides what gets adopted — **do not implement recommendations until
   the owner approves them.** Surface them in your final chat message too.
6. **Not financial advice.** All outputs are probabilistic aids. Keep a
   human-in-the-loop; never auto-trade without explicit, scoped owner approval.

---

## 2. How to start a session (resume protocol)
1. Read `PLAN.md` (design) and this file (`CLAUDE.md`).
2. Read `docs/IMPLEMENTATION_STATE.md` → find **Current Phase**, **Done**,
   **In Progress**, and **Next Up**.
3. Continue from **Next Up**. If unclear, ask the owner before large changes.

## 3. How to end a working run (handoff protocol)
1. Ensure code runs and tests pass (`backend/`: `pytest`).
2. Update `docs/IMPLEMENTATION_STATE.md`: move items between Done/In Progress/Next
   Up, bump the "Last updated" line, note any decisions/gotchas.
3. Add/refresh the relevant `docs/guides/<feature>.md` user guide.
4. Append a new dated section to `docs/RECOMMENDATIONS.md`.
5. Commit + push to `main`. Summarize what changed and surface recommendations in chat.

---

## 4. Documentation conventions
- **Developer docs** → `docs/` (`architecture.md`, `development.md`, etc.). Keep them
  truthful to the code; update when you change structure.
- **User guides** → `docs/guides/<feature>.md`. Each guide is written for the *owner
  as a user* (not a developer): what the feature does, how to open/use it, how to
  read the output, and what decisions it supports. Plain language, concrete examples.
  Index every guide in `docs/guides/README.md`.
- **State** → `docs/IMPLEMENTATION_STATE.md` (resumable progress tracker).
- **Recommendations** → `docs/RECOMMENDATIONS.md` (append-only log; owner approves).

---

## 5. Tech stack & conventions (see PLAN.md §3 for full rationale)
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, pandas/numpy, DuckDB+Parquet
  (history) + SQLite/SQLAlchemy (mutable state), APScheduler. Lint/format with
  `ruff`. Tests with `pytest`. Type-hint everything.
- **Frontend:** React + TypeScript + Vite, TradingView Lightweight Charts +
  ECharts, TanStack Query, Zustand, Tailwind + shadcn/ui.
- **Extensibility:** indicators, signals, and data providers are **plugins** behind
  small interfaces and self-register into a registry (see `PLAN.md` §4). Add features
  by dropping in a module, not by editing the core.
- **Data providers** sit behind an abstraction. `SampleProvider` (offline synthetic
  data) is the safe default/fallback so the app runs without network; real providers
  (yfinance now, Zerodha Kite/Upstox later) swap in via config. Never hard-code a
  provider in business logic.
- **Secrets** (future broker/API keys) → `.env` (gitignored), never committed.

## 6. Project layout
```
backend/   FastAPI app, providers, storage, intelligence engine, services
frontend/  React/TS app
docs/      developer docs, guides/, IMPLEMENTATION_STATE.md, RECOMMENDATIONS.md
PLAN.md    authoritative design & roadmap (phase order FROZEN)
CLAUDE.md  this file
```

## 7. Commit style
- Clear, imperative subject; body explains *why*. One logical change per commit.
- Do **not** put model identifiers or internal session details in commits/code.
