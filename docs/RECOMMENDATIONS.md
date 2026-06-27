# Feature Recommendations (append-only log)

> After every implementation run, the AI appends a dated section proposing features
> or improvements. **The owner decides what gets adopted** — nothing here is built
> until approved (see `CLAUDE.md` §1.5). Mark each item's status as it changes.
>
> Status legend: 🆕 proposed · ✅ approved · 🔨 in progress · ✔️ done · ❌ declined

---

## 2026-06-27 — after Phase 0 (foundation)

1. 🆕 **Watchlist-driven daily "pre-open brief"** (Phase 1–2)
   A one-screen morning summary: Gift Nifty cue, US close, prior-day FII/DII, overnight
   news on your watchlist, and any fresh signals. High value for a short-term trader who
   needs a fast read before market open. *Effort: M.*

2. 🆕 **Keyboard-first command palette** (⌘K) (Phase 1)
   Jump to any stock/screen/indicator instantly. Makes a power-user tool feel fast.
   *Effort: S.*

3. 🆕 **Explanation quality: add "confidence" + "what would change my mind"** (Phase 3+)
   Extend `explain()` output to always include a reliability note and the invalidation
   level for any signal. Trains judgment, not blind following. *Effort: S, high value.*

4. 🆕 **Provider health dashboard** (Phase 1)
   Small status panel showing which data provider is live, last successful fetch, and
   rate-limit headroom — so you immediately know when data is stale/falling back.
   *Effort: S.*

5. 🆕 **Snapshot/replay mode for learning** (Phase 4)
   Save a market snapshot and "replay" how signals/correlations evolved — a safe way to
   study setups without risking capital, complementing the paper-trading sandbox.
   *Effort: M.*

6. 🆕 **Local-only auth + encrypted secrets store** (before broker phase)
   When broker API keys arrive (Phase 5), store them in the OS keychain and gate the app
   with a local passphrase. Worth scaffolding the secrets abstraction early. *Effort: S–M.*

_Owner: tick the ones you want and I'll fold them into the appropriate phase._

---

## 2026-06-27 — after Phase 1 (MVP: watchlist, portfolio, dashboard, ingestion)

Now that data, charting, watchlist, and portfolio exist, these would add the most value
next (without touching the frozen phase order — these slot *into* their phases):

1. 🆕 **Swing-trade setup scanner on the watchlist** (Phase 2, core)
   Tag each watchlist name with a one-word setup ("pullback-in-uptrend", "breakout",
   "overbought", "squeeze") computed from the indicators we already have. This is the
   natural bridge into the Phase 2 screener and fits the 2wk–6mo horizon directly.
   *Effort: M.*

2. 🆕 **Position-risk readout on each holding** (Phase 2)
   Using the target/stop already captured: show R-multiple (reward:risk), % to stop, and
   % to target per holding, and flag positions sitting beyond their stop. Turns the
   portfolio from record-keeping into decision support. *Effort: S.*

3. 🆕 **52-week range + distance-from-high/low context** (Phase 1.5)
   A small strip on Analyze showing where price sits in its 1-year range — cheap, and
   very useful for positional entries/exits. *Effort: S.*

4. 🆕 **Fuller NSE symbol universe + autocomplete search** (Phase 1.5)
   Replace the curated large-cap list with the full NSE symbol master so search/watchlist
   cover everything you trade. *Effort: M (needs a symbol-master source).*

5. 🆕 **"Explain my portfolio" summary** (Phase 3, teaching)
   One plain-language paragraph: concentration, sector tilt, biggest risk, what the trend
   says about your holdings — the teaching layer applied to *your* book. *Effort: M.*

6. ✅ **Weekly+Daily confluence badge** (Phase 2) — **APPROVED 2026-06-27, building now.**
   Since you'll check weekly-then-daily, compute whether both timeframes agree (e.g.
   "Weekly up + Daily pullback = buy-the-dip zone") and show it as a single badge.
   *Effort: S, high value for your style.*

**Also approved 2026-06-27 (building now):** **Paper-trading sandbox** (from `PLAN.md` §8 /
Phase 5, pulled forward to Phase 2) — simulated cash account to practise the engine's
calls risk-free.

---

## 2026-06-27 — after Phase 2 core (signals, confluence, screener, paper trading)

Both approved features shipped (✔️ confluence badge, ✔️ paper trading), plus the screener.
Highest-value next steps (all within the frozen phase order):

1. 🆕 **Send paper trades straight from a signal** (Phase 2)
   A "Paper-buy this setup" button on the Analyze badge / screener row that pre-fills the
   order with a risk-based quantity (using a default % risk + the suggested stop). Closes
   the loop scan → study → practise. *Effort: S.*

2. 🆕 **Auto-suggested stop & target on each signal** (Phase 2)
   Extend the confluence `Signal` with a concrete stop (recent swing low / ATR) and 1–2
   targets, so the badge gives a full plan, not just a direction. Feeds risk sizing.
   *Effort: M.*

3. 🆕 **Inline confluence tag on every watchlist row** (Phase 2, S)
   Show each watchlist name's badge/score in the sidebar so the whole list is triaged at
   a glance. *Effort: S.*

4. 🆕 **Alerts on confluence change** (Phase 2)
   Notify when a watchlist name flips into "Buy-the-dip zone" or "Trend aligned" (or out
   of them). This is the natural Phase 2 alerts feature, tuned to your style. *Effort: M.*

5. 🆕 **Backtest a preset** (Phase 4 preview)
   "How would 'buy-the-dip, sell at target/stop' have done on this universe?" — even a
   simple historical hit-rate would build trust in the scores. *Effort: M–L.*

6. 🆕 **Paper-trading realism toggle** (Phase 2, S)
   Optional brokerage + slippage so paper P&L isn't over-optimistic. *Effort: S.*

_Owner: tick the ones you want and I'll fold them into the appropriate phase._

---

## 2026-06-27 — after Phase 2 complete (alerts, patterns, watchlist tags)

Phase 2 is fully done (signals/confluence, screener, paper trading, alerts, pattern
recognition, inline watchlist tags). Highest-value next steps:

1. 🆕 **Background alert evaluation** (Phase 2.5)
   Alerts currently only check while the Alerts tab is open. Move evaluation into the
   APScheduler loop (and/or a lightweight always-on poll) so you're notified even when the
   tab is closed — pairs naturally with a future email/Telegram push. *Effort: S–M.*

2. 🆕 **Fold patterns + S/R into the confluence score & suggested stop** (Phase 3)
   Use nearest support as the suggested stop and let a bullish-pattern-at-support nudge the
   score up — makes the badge a complete, risk-defined plan. *Effort: M.*

3. 🆕 **"Paper-buy this setup" button** (carried over, still recommended) — one click from
   the badge/screener to a risk-sized paper order. *Effort: S.*

4. 🆕 **Volume-confirmation flag on patterns** (Phase 3)
   Mark whether a pattern formed on above-average volume — the single biggest filter for
   pattern reliability. *Effort: S.*

_Owner: tick the ones you want and I'll fold them into the appropriate phase._
