// Typed client for the backend API.
const BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export interface SymbolInfo {
  symbol: string;
  name: string;
  exchange: string;
}

export interface OHLCVBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Candles {
  symbol: string;
  interval: string;
  bars: OHLCVBar[];
}

export type Stance = "bullish" | "bearish" | "neutral";

export interface Explanation {
  indicator: string;
  title: string;
  value: Record<string, number | null>;
  stance: Stance;
  summary: string;
  reading: string;
  action: string;
  caveat: string | null;
}

export interface LinePoint {
  time: string;
  value: number | null;
}
export interface Overlays {
  symbol: string;
  interval: string;
  series: Record<string, LinePoint[]>;
}

export interface WatchQuote {
  symbol: string;
  name: string;
  price: number | null;
  change: number | null;
  change_percent: number | null;
}

export interface Holding {
  id: number;
  symbol: string;
  name: string;
  quantity: number;
  avg_cost: number;
  target_price: number | null;
  stop_loss: number | null;
  horizon: string;
  notes: string;
  current_price: number | null;
  invested: number;
  market_value: number | null;
  pnl: number | null;
  pnl_percent: number | null;
}
export interface PortfolioSummary {
  holdings: Holding[];
  totals: { invested: number; market_value: number; pnl: number; pnl_percent: number };
}

export interface NewHolding {
  symbol: string;
  quantity: number;
  avg_cost: number;
  target_price?: number | null;
  stop_loss?: number | null;
  horizon?: string;
  notes?: string;
}

export type Trend = "up" | "down" | "flat";
export interface Signal {
  symbol: string;
  badge: string;
  action: "buy" | "watch" | "hold" | "avoid";
  stance: Stance;
  score: number;
  horizon: string;
  weekly_trend: Trend;
  daily_trend: Trend;
  price: number;
  reasons: string[];
  summary: string;
  caveat: string | null;
}

export interface ScreenerPreset {
  key: string;
  label: string;
  desc: string;
}
export interface ScreenerRow {
  symbol: string;
  name: string;
  badge: string;
  action: Signal["action"];
  stance: Stance;
  score: number;
  weekly_trend: Trend;
  daily_trend: Trend;
  price: number;
  summary: string;
}

export interface PaperPosition {
  symbol: string;
  name: string;
  quantity: number;
  avg_cost: number;
  current_price: number | null;
  market_value: number | null;
  unrealized_pnl: number | null;
}
export interface PaperSummary {
  starting_cash: number;
  cash: number;
  holdings_value: number;
  equity: number;
  realized_pnl: number;
  total_return_pct: number;
  positions: PaperPosition[];
}
export interface PaperTrade {
  id: number;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
  realized_pnl: number;
  traded_at: string;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    // Surface FastAPI's {detail: "..."} message when present.
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore non-JSON bodies */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ status: string; provider: string; version: string }>("/api/health"),
  search: (q: string) => req<SymbolInfo[]>(`/api/market/search?q=${encodeURIComponent(q)}`),
  ohlcv: (symbol: string, interval = "1d", lookback = 250) =>
    req<Candles>(
      `/api/market/ohlcv?symbol=${encodeURIComponent(symbol)}&interval=${interval}&lookback=${lookback}`,
    ),
  indicators: (symbol: string, interval = "1d", keys = "ema,rsi,macd,bollinger") =>
    req<Explanation[]>(
      `/api/analysis/indicators?symbol=${encodeURIComponent(symbol)}&interval=${interval}&keys=${keys}`,
    ),
  overlays: (symbol: string, interval = "1d", keys = "ema,bollinger") =>
    req<Overlays>(
      `/api/analysis/overlays?symbol=${encodeURIComponent(symbol)}&interval=${interval}&keys=${keys}`,
    ),

  // Watchlist
  watchlistQuotes: () => req<WatchQuote[]>("/api/watchlist/quotes"),
  watchlistAdd: (symbol: string) =>
    req("/api/watchlist", { method: "POST", body: JSON.stringify({ symbol }) }),
  watchlistRemove: (symbol: string) =>
    req(`/api/watchlist/${encodeURIComponent(symbol)}`, { method: "DELETE" }),

  // Portfolio
  portfolio: () => req<PortfolioSummary>("/api/portfolio"),
  portfolioAdd: (h: NewHolding) =>
    req("/api/portfolio", { method: "POST", body: JSON.stringify(h) }),
  portfolioRemove: (id: number) => req(`/api/portfolio/${id}`, { method: "DELETE" }),

  // Signals & screener
  signal: (symbol: string) => req<Signal>(`/api/signal?symbol=${encodeURIComponent(symbol)}`),
  screenerPresets: () => req<ScreenerPreset[]>("/api/screener/presets"),
  screener: (preset: string, minScore = 0) =>
    req<ScreenerRow[]>(`/api/screener?preset=${preset}&min_score=${minScore}`),

  // Paper trading
  paper: () => req<PaperSummary>("/api/paper"),
  paperTrades: () => req<PaperTrade[]>("/api/paper/trades"),
  paperOrder: (symbol: string, side: "BUY" | "SELL", quantity: number) =>
    req<{ executed: unknown; summary: PaperSummary }>("/api/paper/order", {
      method: "POST",
      body: JSON.stringify({ symbol, side, quantity }),
    }),
  paperReset: (starting_cash: number) =>
    req<PaperSummary>("/api/paper/reset", {
      method: "POST",
      body: JSON.stringify({ starting_cash }),
    }),
};
