import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type NewAlert } from "../api";

const KIND_LABEL: Record<string, string> = {
  price_above: "Price ≥",
  price_below: "Price ≤",
  rsi_above: "RSI ≥",
  rsi_below: "RSI ≤",
  confluence_action: "Confluence becomes",
};
const ACTIONS = ["buy", "watch", "hold", "avoid"];

export function Alerts({ onSelect }: { onSelect: (symbol: string) => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<NewAlert>({ symbol: "", kind: "price_above", threshold: 0 });
  const isConfluence = form.kind === "confluence_action";

  const alerts = useQuery({ queryKey: ["alerts"], queryFn: api.alerts });

  // Poll evaluation; on a newly-fired alert show a browser notification.
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
    const tick = async () => {
      try {
        const results = await api.alertEvaluate();
        const fired = results.filter((r) => r.newly_fired);
        if (fired.length) {
          qc.invalidateQueries({ queryKey: ["alerts"] });
          if ("Notification" in window && Notification.permission === "granted") {
            fired.forEach((f) => new Notification("Alert triggered", { body: f.description }));
          }
        }
      } catch {
        /* ignore transient errors */
      }
    };
    tick();
    const id = window.setInterval(tick, 60_000);
    return () => window.clearInterval(id);
  }, [qc]);

  const create = useMutation({
    mutationFn: (a: NewAlert) => api.alertCreate(a),
    onSuccess: () => {
      setForm({ symbol: form.symbol, kind: form.kind, threshold: 0 });
      qc.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
  const toggle = useMutation({
    mutationFn: (id: number) => api.alertToggle(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });
  const remove = useMutation({
    mutationFn: (id: number) => api.alertDelete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const submit = () => {
    if (!form.symbol.trim()) return;
    const payload: NewAlert = isConfluence
      ? { symbol: form.symbol, kind: form.kind, target: form.target || "buy" }
      : { symbol: form.symbol, kind: form.kind, threshold: form.threshold };
    create.mutate(payload);
  };

  return (
    <div>
      <h2>Alerts</h2>
      <p className="muted">
        Watched against current data; checked every minute while this tab is open. Browser
        notifications fire when a condition is first met.
      </p>

      <div className="card holding-form">
        <input
          placeholder="Symbol (RELIANCE.NS)"
          value={form.symbol}
          onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
        />
        <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
          {Object.entries(KIND_LABEL).map(([k, label]) => (
            <option key={k} value={k}>
              {label}
            </option>
          ))}
        </select>
        {isConfluence ? (
          <select
            value={form.target ?? "buy"}
            onChange={(e) => setForm({ ...form, target: e.target.value })}
          >
            {ACTIONS.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        ) : (
          <input
            type="number"
            step="any"
            placeholder="Level"
            value={form.threshold ?? ""}
            onChange={(e) => setForm({ ...form, threshold: Number(e.target.value) })}
          />
        )}
        <button onClick={submit}>Add alert</button>
      </div>

      <section className="card" style={{ marginTop: 16 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th>Condition</th>
              <th>Status</th>
              <th>Last triggered</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(alerts.data ?? []).map((a) => (
              <tr key={a.id}>
                <td className="clickable" onClick={() => onSelect(a.symbol)}>
                  {a.description}
                </td>
                <td>
                  {!a.active ? (
                    <span className="muted">paused</span>
                  ) : a.currently_met ? (
                    <span className="pos">● met</span>
                  ) : (
                    <span className="muted">watching</span>
                  )}
                </td>
                <td className="muted">
                  {a.last_triggered_at
                    ? new Date(a.last_triggered_at).toLocaleString("en-IN")
                    : "—"}
                </td>
                <td style={{ display: "flex", gap: 8 }}>
                  <button className="tab" onClick={() => toggle.mutate(a.id)}>
                    {a.active ? "Pause" : "Resume"}
                  </button>
                  <button className="wl-del" onClick={() => remove.mutate(a.id)}>
                    ×
                  </button>
                </td>
              </tr>
            ))}
            {alerts.data?.length === 0 && (
              <tr>
                <td colSpan={4} className="muted">
                  No alerts yet. Add one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
