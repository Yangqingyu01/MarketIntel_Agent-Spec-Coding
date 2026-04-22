import React, { useEffect, useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import { fetchAlerts, type AlertItem } from "../services/api";
import {
  localizeAlertDescription,
  localizeAlertTitle,
} from "../services/localization";

type AlertPanelProps = {
  language: AppLanguage;
};

export function AlertPanel({ language }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts()
      .then((payload) => setAlerts(payload.alerts))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  }, []);

  const grouped = useMemo(() => alerts.slice(0, 4), [alerts]);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        label: "信号登记",
        title: "预警",
        recentCount: "最近数量",
        loading: "正在载入最近的预警信号。",
        empty: "当前还没有超过阈值的新变化，预警区保持安静。",
      };
    }

    return {
      label: "Signal Register",
      title: "Alerts",
      recentCount: "Recent Count",
      loading: "Loading the latest alert signals.",
      empty:
        "No fresh changes have crossed the alert threshold yet. The register remains intentionally quiet.",
    };
  }, [language]);

  return (
    <section className="bau-panel bau-panel--blue">
      <div className="bau-panel__header">
        <div>
          <p className="bau-label">{copy.label}</p>
          <h2 className="bau-panel__title">{copy.title}</h2>
        </div>
        <span className="bau-pill bau-pill--yellow">
          {copy.recentCount} / {loading ? "..." : alerts.length}
        </span>
      </div>

      {loading ? <p className="bau-helper">{copy.loading}</p> : null}

      {!loading && grouped.length === 0 ? <p className="bau-helper">{copy.empty}</p> : null}

      <div className="bau-alerts__grid">
        {grouped.map((alert) => (
          <article
            key={alert.alert_id}
            className={`bau-alert-card bau-alert-card--${alert.severity}`}
          >
            <div className="bau-config-card__meta">
              <span className="bau-pill bau-pill--white">{alert.severity}</span>
              <span className="bau-meta">{alert.company}</span>
            </div>
            <h3 className="bau-alert-card__title">
              {localizeAlertTitle(alert, language)}
            </h3>
            <p className="bau-alert-card__text">
              {localizeAlertDescription(alert, language)}
            </p>
            <p className="bau-meta" style={{ marginTop: "1rem" }}>
              {alert.detected_at}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
