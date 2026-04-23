import React, { useEffect, useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import {
  fetchSchedulerStatus,
  fetchSchedulerSummary,
  type SchedulerStatusResponse,
  type SchedulerSummaryResponse,
} from "../services/api";

type SchedulerPanelProps = {
  language: AppLanguage;
};

export function SchedulerPanel({ language }: SchedulerPanelProps) {
  const [status, setStatus] = useState<SchedulerStatusResponse | null>(null);
  const [daily, setDaily] = useState<SchedulerSummaryResponse["summary"] | null>(null);
  const [weekly, setWeekly] = useState<SchedulerSummaryResponse["summary"] | null>(null);

  useEffect(() => {
    fetchSchedulerStatus().then(setStatus).catch(() => setStatus(null));
    fetchSchedulerSummary("daily")
      .then((payload) => setDaily(payload.summary))
      .catch(() => setDaily(null));
    fetchSchedulerSummary("weekly")
      .then((payload) => setWeekly(payload.summary))
      .catch(() => setWeekly(null));
  }, []);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        label: "调度 / 摘要",
        title: "调度器状态",
        enabled: "调度器",
        daily: "每日",
        weekly: "每周",
        watchlist: "监测目标",
        jobs: "任务数",
        empty: "当前没有可展示的摘要预览。",
        disabledButReady: "当前未启用自动调度，但下方仍展示最近一次已生成的摘要结果。",
        reports: "报告",
        alerts: "预警",
        trigger: "触发器",
        off: "未启用",
        on: "已启用",
      };
    }

    return {
      label: "Scheduler / Digest",
      title: "Scheduler Status",
      enabled: "Scheduler",
      daily: "Daily",
      weekly: "Weekly",
      watchlist: "Watchlist",
      jobs: "Jobs",
      empty: "No digest preview is available yet.",
      disabledButReady: "Automation is off, but recent digest previews are still shown below.",
      reports: "Reports",
      alerts: "Alerts",
      trigger: "Trigger",
      off: "Off",
      on: "On",
    };
  }, [language]);

  const jobs = status?.scheduler.jobs ?? [];
  const hasDigestPreview = Boolean(daily || weekly);

  return (
    <section className="bau-panel bau-panel--white">
      <div className="bau-panel__header">
        <div>
          <p className="bau-label">{copy.label}</p>
          <h2 className="bau-panel__title">{copy.title}</h2>
        </div>
        <span className="bau-pill bau-pill--yellow">
          {copy.enabled} / {status?.scheduler.enabled ? copy.on : copy.off}
        </span>
      </div>

      <div className="bau-scheduler-grid">
        <div className="bau-scheduler-stats">
          <article className="bau-stat-card bau-stat-card--yellow">
            <p className="bau-label">{copy.watchlist}</p>
            <p className="bau-stat-card__value">{status?.competitor_count ?? 0}</p>
          </article>
          <article className="bau-stat-card bau-stat-card--blue">
            <p className="bau-label">{copy.jobs}</p>
            <p className="bau-stat-card__value">{jobs.length}</p>
          </article>
        </div>

        <div className="bau-job-list">
          {jobs.map((job) => (
            <article key={job.id} className="bau-job-card">
              <div className="bau-job-card__meta">
                <span className="bau-pill bau-pill--white">{job.id}</span>
                <span className="bau-meta">{copy.trigger}</span>
              </div>
              <h3 className="bau-job-card__title">{job.name}</h3>
              <p className="bau-job-card__text">{job.trigger}</p>
            </article>
          ))}
          {jobs.length === 0 ? (
            <article className="bau-job-card">
              <h3 className="bau-job-card__title">{copy.off}</h3>
              <p className="bau-job-card__text">
                {hasDigestPreview ? copy.disabledButReady : copy.empty}
              </p>
            </article>
          ) : null}
        </div>
      </div>

      <div className="bau-digest-grid">
        <DigestCard title={copy.daily} summary={daily} copy={copy} />
        <DigestCard title={copy.weekly} summary={weekly} copy={copy} />
      </div>
    </section>
  );
}

function DigestCard({
  title,
  summary,
  copy,
}: {
  title: string;
  summary: SchedulerSummaryResponse["summary"] | null;
  copy: Record<string, string>;
}) {
  return (
    <article className="bau-digest-card">
      <div className="bau-digest-card__header">
        <span className="bau-pill bau-pill--blue">{title}</span>
      </div>
      {summary ? (
        <>
          <p className="bau-digest-card__headline">{summary.headline}</p>
          <div className="bau-digest-card__stats">
            <span>{copy.reports}: {summary.report_count}</span>
            <span>{copy.alerts}: {summary.alert_count}</span>
          </div>
        </>
      ) : (
        <p className="bau-digest-card__headline">{copy.empty}</p>
      )}
    </article>
  );
}
