import React, { useEffect, useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import {
  fetchCompanyHistory,
  fetchCompetitors,
  fetchHistoryOverview,
  type AlertItem,
  type HistoryOverviewResponse,
  type HistoryResponse,
} from "../services/api";

type HistoryPanelProps = {
  language: AppLanguage;
};

type SnapshotItem =
  HistoryResponse["history"]["snapshots"][number]["items"][number];

type HistoryOverviewRow = HistoryOverviewResponse["overview"]["rows"][number];

export function HistoryPanel({ language }: HistoryPanelProps) {
  const [companies, setCompanies] = useState<string[]>(["Feishu"]);
  const [selectedCompany, setSelectedCompany] = useState("Feishu");
  const [history, setHistory] = useState<HistoryResponse["history"] | null>(null);
  const [overviewRows, setOverviewRows] = useState<HistoryOverviewRow[]>([]);
  const [expandedSnapshotId, setExpandedSnapshotId] = useState("");
  const [expandedItemKey, setExpandedItemKey] = useState("");

  useEffect(() => {
    fetchCompetitors()
      .then((payload) => {
        const names = payload.competitors
          .map((item) => String(item.name ?? "").trim())
          .filter(Boolean);
        const next = names.length > 0 ? names : ["Feishu"];
        setCompanies(next);
        setSelectedCompany((current) => (next.includes(current) ? current : next[0]));
      })
      .catch(() => {
        setCompanies(["Feishu"]);
        setSelectedCompany("Feishu");
      });
  }, []);

  useEffect(() => {
    fetchHistoryOverview(companies)
      .then((payload) => setOverviewRows(payload.overview.rows))
      .catch(() => setOverviewRows([]));
  }, [companies]);

  useEffect(() => {
    if (!selectedCompany) {
      setHistory(null);
      return;
    }
    fetchCompanyHistory(selectedCompany)
      .then((payload) => {
        setHistory(payload.history);
        setExpandedSnapshotId(payload.history.snapshots[0]?.snapshot_id ?? "");
        setExpandedItemKey("");
      })
      .catch(() => {
        setHistory(null);
        setExpandedSnapshotId("");
        setExpandedItemKey("");
      });
  }, [selectedCompany]);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        label: "历史 / 时间线",
        title: "历史对比",
        company: "竞品",
        overview: "多竞品横向时间线",
        snapshots: "历史快照",
        timeline: "趋势图",
        comparisons: "快照 Diff",
        alerts: "预警串联",
        sourceCount: "来源数",
        confidence: "可信度",
        product: "产品",
        pricing: "定价",
        empty: "当前还没有足够的真实历史记录。",
        descending: "最新预警",
        details: "展开详情",
        collapse: "收起",
        source: "来源",
        published: "发布时间",
        open: "打开来源",
        quote: "证据摘录",
        noHighlight: "暂无新增亮点",
        noRemoved: "暂无移除信号",
        noAlerts: "当前没有可展示的真实预警。",
        evidence: "展开证据",
        hideEvidence: "收起证据",
        added: "新增",
        removed: "移除",
        productTrend: "产品趋势",
        pricingTrend: "定价趋势",
        sourcesTrend: "来源趋势",
      };
    }

    return {
      label: "History / Timeline",
      title: "Historical View",
      company: "Company",
      overview: "Cross-Competitor Timeline",
      snapshots: "Snapshots",
      timeline: "Trend View",
      comparisons: "Snapshot Diff",
      alerts: "Alert Stream",
      sourceCount: "Sources",
      confidence: "Confidence",
      product: "Product",
      pricing: "Pricing",
      empty: "There is not enough real historical data yet.",
      descending: "Latest Alerts",
      details: "View details",
      collapse: "Collapse",
      source: "Source",
      published: "Published",
      open: "Open source",
      quote: "Evidence",
      noHighlight: "No new highlights",
      noRemoved: "No removed signals",
      noAlerts: "No real alerts are available yet.",
      evidence: "Show evidence",
      hideEvidence: "Hide evidence",
      added: "Added",
      removed: "Removed",
      productTrend: "Product Trend",
      pricingTrend: "Pricing Trend",
      sourcesTrend: "Source Trend",
    };
  }, [language]);

  return (
    <section className="bau-panel bau-panel--white">
      <div className="bau-panel__header">
        <div>
          <p className="bau-label">{copy.label}</p>
          <h2 className="bau-panel__title">{copy.title}</h2>
        </div>
        <div className="bau-history-select">
          <span className="bau-meta">{copy.company}</span>
          <select
            className="bau-field"
            value={selectedCompany}
            onChange={(event) => setSelectedCompany(event.target.value)}
          >
            {companies.map((company) => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>
        </div>
      </div>

      {history ? (
        <div className="bau-history-stack">
          <section className="bau-history-block bau-history-block--wide">
            <div className="bau-detail-panel__header">
              <p className="bau-label">{copy.overview}</p>
            </div>
            <div className="bau-overview-timeline">
              {overviewRows.map((row) => (
                <article key={`${row.company}-${row.snapshot_id}`} className="bau-overview-row">
                  <div className="bau-overview-row__head">
                    <span className="bau-pill bau-pill--white">{row.company}</span>
                    <span className="bau-meta">{row.snapshot_date}</span>
                  </div>
                  <div className="bau-overview-row__bars">
                    <div>
                      <span>{copy.product}</span>
                      <div className="bau-mini-track">
                        <div
                          className="bau-mini-fill bau-mini-fill--red"
                          style={{ width: `${Math.max(10, row.product_count * 24)}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <span>{copy.pricing}</span>
                      <div className="bau-mini-track">
                        <div
                          className="bau-mini-fill bau-mini-fill--blue"
                          style={{ width: `${Math.max(10, row.pricing_count * 24)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <div className="bau-history-grid">
            <section className="bau-history-block">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.snapshots}</p>
              </div>
              <div className="bau-snapshot-list">
                {history.snapshots.map((snapshot) => {
                  const expanded = expandedSnapshotId === snapshot.snapshot_id;
                  return (
                    <article key={snapshot.snapshot_id} className="bau-snapshot-card">
                      <div className="bau-snapshot-card__header">
                        <div>
                          <p className="bau-meta">{snapshot.snapshot_date}</p>
                          <p className="bau-snapshot-card__text">
                            {copy.sourceCount}: {snapshot.source_count}
                          </p>
                          <p className="bau-snapshot-card__text">
                            {copy.confidence}:{" "}
                            {Number(snapshot.overall_confidence ?? 0).toFixed(2)}
                          </p>
                        </div>
                        <button
                          type="button"
                          className="bau-button bau-button--white bau-button--compact"
                          onClick={() =>
                            setExpandedSnapshotId((current) =>
                              current === snapshot.snapshot_id ? "" : snapshot.snapshot_id,
                            )
                          }
                        >
                          {expanded ? copy.collapse : copy.details}
                        </button>
                      </div>
                      {expanded ? (
                        <div className="bau-snapshot-details">
                          {snapshot.items.map((item, index) => {
                            const itemKey = `${snapshot.snapshot_id}-${index}`;
                            return (
                              <SnapshotDetailCard
                                key={itemKey}
                                item={item}
                                copy={copy}
                                expanded={expandedItemKey === itemKey}
                                onToggle={() =>
                                  setExpandedItemKey((current) =>
                                    current === itemKey ? "" : itemKey,
                                  )
                                }
                              />
                            );
                          })}
                        </div>
                      ) : null}
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="bau-history-block">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.timeline}</p>
              </div>
              <div className="bau-trend-stack">
                <TrendCard
                  title={copy.productTrend}
                  tone="red"
                  values={history.timeline.map((point) => point.product_count)}
                  labels={history.timeline.map((point) => point.snapshot_date)}
                />
                <TrendCard
                  title={copy.pricingTrend}
                  tone="blue"
                  values={history.timeline.map((point) => point.pricing_count)}
                  labels={history.timeline.map((point) => point.snapshot_date)}
                />
                <TrendCard
                  title={copy.sourcesTrend}
                  tone="yellow"
                  values={history.timeline.map((point) => point.source_count)}
                  labels={history.timeline.map((point) => point.snapshot_date)}
                />
              </div>
            </section>

            <section className="bau-history-block">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.comparisons}</p>
              </div>
              <div className="bau-compare-list">
                {history.comparisons.map((comparison) => (
                  <article key={comparison.snapshot_id} className="bau-compare-card">
                    <p className="bau-meta">{comparison.snapshot_date}</p>
                    <DimensionDiff
                      label={copy.product}
                      data={comparison.product}
                      emptyLabel={copy.noHighlight}
                      removedLabel={copy.noRemoved}
                      addedCopy={copy.added}
                      removedCopy={copy.removed}
                    />
                    <DimensionDiff
                      label={copy.pricing}
                      data={comparison.pricing}
                      emptyLabel={copy.noHighlight}
                      removedLabel={copy.noRemoved}
                      addedCopy={copy.added}
                      removedCopy={copy.removed}
                    />
                  </article>
                ))}
              </div>
            </section>

            <section className="bau-history-block">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.descending}</p>
              </div>
              <div className="bau-history-alerts">
                {history.alerts.length > 0 ? (
                  history.alerts.map((alert) => (
                    <HistoryAlertCard key={alert.alert_id} alert={alert} copy={copy} />
                  ))
                ) : (
                  <p className="bau-helper">{copy.noAlerts}</p>
                )}
              </div>
            </section>
          </div>
        </div>
      ) : (
        <p className="bau-helper">{copy.empty}</p>
      )}
    </section>
  );
}

function SnapshotDetailCard({
  item,
  copy,
  expanded,
  onToggle,
}: {
  item: SnapshotItem;
  copy: Record<string, string>;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <article className="bau-snapshot-item-card">
      <div className="bau-snapshot-item-card__meta">
        <span className="bau-pill bau-pill--white">{item.dimension}</span>
        <span className="bau-meta">
          {copy.published}: {item.publish_date || item.crawl_date || "-"}
        </span>
      </div>
      <p className="bau-snapshot-item-card__title">{item.extracted_data}</p>
      <p className="bau-snapshot-item-card__text">
        {copy.source}: {item.source_name || item.source_url}
      </p>
      <div className="bau-snapshot-item-card__actions">
        {item.source_url ? (
          <a className="bau-link" href={item.source_url} target="_blank" rel="noreferrer">
            {copy.open}
          </a>
        ) : null}
        {item.evidence_quote ? (
          <button
            type="button"
            className="bau-button bau-button--white bau-button--compact"
            onClick={onToggle}
          >
            {expanded ? copy.hideEvidence : copy.evidence}
          </button>
        ) : null}
      </div>
      {expanded && item.evidence_quote ? (
        <p className="bau-snapshot-item-card__quote">
          <strong>{copy.quote}: </strong>
          {item.evidence_quote}
        </p>
      ) : null}
    </article>
  );
}

function TrendCard({
  title,
  tone,
  values,
  labels,
}: {
  title: string;
  tone: "red" | "blue" | "yellow";
  values: number[];
  labels: string[];
}) {
  const maxValue = Math.max(...values, 1);
  return (
    <article className={`bau-trend-card bau-trend-card--${tone}`}>
      <div className="bau-chart-card__meta">
        <strong>{title}</strong>
        <span>{values[values.length - 1] ?? 0}</span>
      </div>
      <div className="bau-trend-card__bars">
        {values.map((value, index) => (
          <div key={`${title}-${labels[index]}`} className="bau-trend-card__bar-wrap">
            <div
              className={`bau-trend-card__bar bau-trend-card__bar--${tone}`}
              style={{ height: `${Math.max(12, (value / maxValue) * 100)}%` }}
            />
            <span className="bau-trend-card__label">{index + 1}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

function DimensionDiff({
  label,
  data,
  emptyLabel,
  removedLabel,
  addedCopy,
  removedCopy,
}: {
  label: string;
  data: { count: number; delta: number; highlights: string[]; removed: string[] };
  emptyLabel: string;
  removedLabel: string;
  addedCopy: string;
  removedCopy: string;
}) {
  return (
    <div className="bau-diff-row">
      <div className="bau-diff-row__header">
        <strong>{label}</strong>
        <span>
          {data.count} / {data.delta >= 0 ? `+${data.delta}` : data.delta}
        </span>
      </div>
      <div className="bau-diff-panels">
        <div className="bau-diff-panel bau-diff-panel--added">
          <span className="bau-meta">{addedCopy}</span>
          {data.highlights.length > 0 ? (
            <ul className="bau-diff-list">
              {data.highlights.map((item, index) => (
                <li key={`${label}-added-${index}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="bau-meta">{emptyLabel}</p>
          )}
        </div>
        <div className="bau-diff-panel bau-diff-panel--removed">
          <span className="bau-meta">{removedCopy}</span>
          {data.removed.length > 0 ? (
            <ul className="bau-diff-list">
              {data.removed.map((item, index) => (
                <li key={`${label}-removed-${index}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="bau-meta">{removedLabel}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function HistoryAlertCard({
  alert,
  copy,
}: {
  alert: AlertItem;
  copy: Record<string, string>;
}) {
  return (
    <article className="bau-history-alert-card">
      <div className="bau-history-alert-card__meta">
        <span className="bau-pill bau-pill--white">{alert.severity}</span>
        <span className="bau-meta">{alert.detected_at}</span>
      </div>
      <h3 className="bau-alert-card__title">{alert.title}</h3>
      <p className="bau-alert-card__text">{alert.description}</p>
      {alert.source_url ? (
        <a className="bau-link" href={alert.source_url} target="_blank" rel="noreferrer">
          {copy.open}
        </a>
      ) : null}
    </article>
  );
}
