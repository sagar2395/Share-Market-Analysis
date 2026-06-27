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

6. 🆕 **Weekly+Daly confluence badge** (Phase 2)
   Since you'll check weekly-then-daily, compute whether both timeframes agree (e.g.
   "Weekly up + Daily pullback = buy-the-dip zone") and show it as a single badge.
   *Effort: S, high value for your style.*

_Owner: tick the ones you want and I'll fold them into the appropriate phase._
