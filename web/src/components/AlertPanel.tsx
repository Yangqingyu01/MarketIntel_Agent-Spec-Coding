import { useEffect, useState, type CSSProperties } from "react";

import { fetchAlerts, type AlertItem } from "../services/api";

export function AlertPanel() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    fetchAlerts()
      .then((payload) => setAlerts(payload.alerts))
      .catch(() => setAlerts([]));
  }, []);

  return (
    <section style={wrapperStyle}>
      <div style={headerStyle}>
        <h2 style={{ margin: 0 }}>预警面板</h2>
        <span style={badgeStyle}>{alerts.length}</span>
      </div>
      {alerts.length === 0 ? (
        <p style={{ color: "#5e6983" }}>当前没有新的变化预警。</p>
      ) : (
        alerts.map((alert) => (
          <article key={alert.alert_id} style={cardStyle}>
            <div style={pillStyle(alert.severity)}>{alert.severity}</div>
            <h3 style={{ marginBottom: "6px" }}>{alert.title}</h3>
            <p style={{ marginTop: 0 }}>{alert.description}</p>
            <small>{alert.detected_at}</small>
          </article>
        ))
      )}
    </section>
  );
}

const wrapperStyle: CSSProperties = {
  padding: "24px",
  borderRadius: "24px",
  background: "#112a46",
  color: "#f7fbff",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const badgeStyle: CSSProperties = {
  minWidth: "32px",
  height: "32px",
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
