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

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  health: () => get<{ status: string; provider: string; version: string }>("/api/health"),
  search: (q: string) => get<SymbolInfo[]>(`/api/market/search?q=${encodeURIComponent(q)}`),
  ohlcv: (symbol: string, lookback = 250) =>
    get<Candles>(`/api/market/ohlcv?symbol=${encodeURIComponent(symbol)}&lookback=${lookback}`),
  indicators: (symbol: string, keys = "ema,rsi,macd") =>
    get<Explanation[]>(
      `/api/analysis/indicators?symbol=${encodeURIComponent(symbol)}&keys=${keys}`,
    ),
};
