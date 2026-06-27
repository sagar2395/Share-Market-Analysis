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

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
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
};
