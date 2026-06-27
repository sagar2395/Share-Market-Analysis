import type { Signal, Trend } from "../api";

const ACTION_COLOR: Record<Signal["action"], string> = {
  buy: "#26a69a",
  watch: "#f5a623",
  hold: "#94a3b8",
  avoid: "#ef5350",
};
const ARROW: Record<Trend, string> = { up: "↑", down: "↓", flat: "→" };

// The weekly+daily confluence verdict: one badge + the reasoning behind it (teaching).
export function ConfluenceBadge({ signal }: { signal: Signal }) {
  const color = ACTION_COLOR[signal.action];
  return (
    <div className="card" style={{ borderColor: color }}>
      <div className="row-between" style={{ marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            style={{
              background: color,
              color: "#0f1117",
              borderRadius: 8,
              padding: "4px 12px",
              fontWeight: 800,
            }}
          >
            {signal.badge}
          </span>
          <span style={{ textTransform: "uppercase", fontWeight: 700, color }}>
            {signal.action}
          </span>
        </div>
        <div className="conf-score" title="Setup quality 0–100">
          <strong>{signal.score}</strong>
          <span className="muted">/100</span>
        </div>
      </div>

      <div className="conf-tf">
        <span>
          Weekly <strong className={`tf-${signal.weekly_trend}`}>{ARROW[signal.weekly_trend]} {signal.weekly_trend}</strong>
        </span>
        <span>
          Daily <strong className={`tf-${signal.daily_trend}`}>{ARROW[signal.daily_trend]} {signal.daily_trend}</strong>
        </span>
      </div>

      <p style={{ marginBottom: 6 }}>{signal.summary}</p>
      <ul className="conf-reasons">
        {signal.reasons.map((r, i) => (
          <li key={i} className="muted">
            {r}
          </li>
        ))}
      </ul>
      {signal.caveat && (
        <p className="muted" style={{ fontStyle: "italic", margin: 0 }}>
          ⚠ {signal.caveat}
        </p>
      )}
    </div>
  );
}
