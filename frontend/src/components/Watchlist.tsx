import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";

// Persistent watchlist sidebar. Click a row to analyse it; quotes refresh periodically.
export function Watchlist({
  selected,
  onSelect,
}: {
  selected: string;
  onSelect: (symbol: string) => void;
}) {
  const qc = useQueryClient();
  const [input, setInput] = useState("");

  const quotes = useQuery({
    queryKey: ["watchlist"],
    queryFn: api.watchlistQuotes,
    refetchInterval: 60_000,
  });

  const add = useMutation({
    mutationFn: (s: string) => api.watchlistAdd(s),
    onSuccess: () => {
      setInput("");
      qc.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });
  const remove = useMutation({
    mutationFn: (s: string) => api.watchlistRemove(s),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
  });

  return (
    <aside className="watchlist">
      <h3>Watchlist</h3>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim()) add.mutate(input.trim().toUpperCase());
        }}
        className="wl-add"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Add e.g. WIPRO.NS"
        />
        <button type="submit">+</button>
      </form>

      {quotes.isLoading && <p className="muted">Loading…</p>}
      <ul className="wl-list">
        {(quotes.data ?? []).map((q) => {
          const up = (q.change_percent ?? 0) >= 0;
          return (
            <li
              key={q.symbol}
              className={q.symbol === selected ? "wl-item active" : "wl-item"}
              onClick={() => onSelect(q.symbol)}
            >
              <div className="wl-sym">
                <strong>{q.symbol.replace(".NS", "")}</strong>
                <span className="muted wl-name">{q.name}</span>
              </div>
              <div className="wl-px">
                <span>{q.price != null ? `₹${q.price.toLocaleString("en-IN")}` : "—"}</span>
                <span className={up ? "pos" : "neg"}>
                  {q.change_percent != null ? `${up ? "+" : ""}${q.change_percent}%` : ""}
                </span>
              </div>
              <button
                className="wl-del"
                title="Remove"
                onClick={(e) => {
                  e.stopPropagation();
                  remove.mutate(q.symbol);
                }}
              >
                ×
              </button>
            </li>
          );
        })}
        {quotes.data?.length === 0 && <li className="muted">Empty — add a symbol above.</li>}
      </ul>
    </aside>
  );
}
