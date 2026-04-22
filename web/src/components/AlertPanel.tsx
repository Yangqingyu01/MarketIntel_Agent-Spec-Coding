import { useEffect, useState, type CSSProperties } from "react";

import { fetchAlerts, type AlertItem } from "../services/api";

export function AlertPanel() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts()
      .then((payload) => setAlerts(payload.alerts))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section style={wrapperStyle}>
      <div style={headerStyle}>
        <div>
          <p style={tagStyle}>Alert Feed</p>
          <h2 style={{ margin: 0 }}>预警面板</h2>
        </div>
        <span style={badgeStyle}>{alerts.length}</span>
      </div>
      {loading ? <p style={emptyStyle}>正在拉取最近预警...</p> : null}
      {!loading && alerts.length === 0 ? (
        <p style={emptyStyle}>当前没有新的变化预警。</p>
      ) : null}
      {alerts.map((alert) => (
        <article key={alert.alert_id} style={cardStyle}>
          <div style={pillStyle(alert.severity)}>{alert.severity}</div>
          <h3 style={{ marginBottom: "6px" }}>{alert.title}</h3>
          <p style={{ marginTop: 0 }}>{alert.description}</p>
          <small style={{ color: "#d0d5dd" }}>{alert.detected_at}</small>
        </article>
      ))}
    </section>
  );
}

const wrapperStyle: CSSProperties = {
  padding: "24px",
  borderRadius: "24px",
  background:
    "radial-gradient(circle at top left, rgba(240,162,2,0.2), transparent 24%), #112a46",
  color: "#f7fbff",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
};

const tagStyle: CSSProperties = {
  margin: "0 0 6px",
  color: "#f0a202",
  fontSize: "12px",
  textTransform: "uppercase",
  letterSpacing: "0.12em",
};

const badgeStyle: CSSProperties = {
  minWidth: "36px",
  height: "36px",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  borderRadius: "999px",
  background: "#f0a202",
  color: "#112a46",
  fontWeight: 700,
};

const cardStyle: CSSProperties = {
  marginTop: "16px",
  padding: "16px",
  borderRadius: "18px",
  background: "rgba(255, 255, 255, 0.08)",
  border: "1px solid rgba(255,255,255,0.06)",
};

const emptyStyle: CSSProperties = {
  color: "#d0d5dd",
};

const pillStyle = (severity: string): CSSProperties => ({
  display: "inline-block",
  marginBottom: "10px",
  padding: "6px 10px",
  borderRadius: "999px",
  background:
    severity === "high" ? "#d92d20" : severity === "medium" ? "#f79009" : "#98a2b3",
  color: "#fff",
  fontSize: "12px",
  textTransform: "uppercase",
});
