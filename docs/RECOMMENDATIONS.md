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
