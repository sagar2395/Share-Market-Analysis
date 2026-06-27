import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Signal } from "../api";

const ACTION_COLOR: Record<Signal["action"], string> = {
  buy: "#26a69a",
  watch: "#f5a623",
  hold: "#94a3b8",
  avoid: "#ef5350",
};

// Scan the universe for swing setups, ranked by the confluence score.
export function Screener({ onSelect }: { onSelect: (symbol: string) => void }) {
  const [preset, setPreset] = useState("trend_aligned");
  const [minScore, setMinScore] = useState(0);

  const presets = useQuery({ queryKey: ["screener-presets"], queryFn: api.screenerPresets });
  const rows = useQuery({
    queryKey: ["screener", preset, minScore],
    queryFn: () => api.screener(preset, minScore),
  });

  const activePreset = presets.data?.find((p) => p.key === preset);

  return (
    <div>
      <h2>Screener</h2>

      <div className="card screener-controls">
        <div>
          <label className="muted">Preset</label>
          <select value={preset} onChange={(e) => setPreset(e.target.value)}>
            {(presets.data ?? []).map((p) => (
              <option key={p.key} value={p.key}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="muted">Min score: {minScore}</label>
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
        </div>
        {activePreset && <p className="muted">{activePreset.desc}</p>}
      </div>

      <section className="card" style={{ marginTop: 16 }}>
        {rows.isLoading && <p className="muted">Scanning the universe…</p>}
        <table className="tbl">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Setup</th>
              <th>Weekly</th>
              <th>Daily</th>
              <th className="num">Price</th>
              <th className="num">Score</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(rows.data ?? []).map((r) => (
              <tr key={r.symbol} className="clickable" onClick={() => onSelect(r.symbol)}>
                <td>
                  <strong>{r.symbol.replace(".NS", "")}</strong>
                  <div className="muted wl-name">{r.name}</div>
                </td>
                <td>{r.badge}</td>
                <td className={`tf-${r.weekly_trend}`}>{r.weekly_trend}</td>
                <td className={`tf-${r.daily_trend}`}>{r.daily_trend}</td>
                <td className="num">₹{r.price.toLocaleString("en-IN")}</td>
                <td className="num">
                  <strong>{r.score}</strong>
                </td>
                <td>
                  <span
                    style={{
                      color: ACTION_COLOR[r.action],
                      fontWeight: 700,
                      textTransform: "uppercase",
                      fontSize: 12,
                    }}
                  >
                    {r.action}
                  </span>
                </td>
              </tr>
            ))}
            {rows.data?.length === 0 && (
              <tr>
                <td colSpan={7} className="muted">
                  No matches for this preset/score. Loosen the filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
