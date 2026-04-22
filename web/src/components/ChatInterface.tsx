import React, { useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import { analyzeCompetitors, type AnalyzeResponse } from "../services/api";
import {
  localizeChangesSummary,
  localizeExecutiveSummary,
} from "../services/localization";

const DIMENSIONS = ["product", "pricing", "funding", "talent", "strategy"];
const DEFAULT_DIMENSIONS = ["product", "pricing"];

type ChartItem = Record<string, unknown>;
type ActionItem = Record<string, unknown>;

type ChatInterfaceProps = {
  language: AppLanguage;
};

export function ChatInterface({ language }: ChatInterfaceProps) {
  const [targetInput, setTargetInput] = useState("Feishu, DingTalk");
  const [selectedDimensions, setSelectedDimensions] =
    useState<string[]>(DEFAULT_DIMENSIONS);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedLabel = useMemo(() => {
    return selectedDimensions.length > 0
      ? selectedDimensions
          .map((item) => getDimensionLabel(item, language))
          .join(" / ")
          .toUpperCase()
      : "NONE";
  }, [language, selectedDimensions]);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        panelLabel: "分析控制台",
        panelTitle: "启动扫描",
        panelHelper:
          "输入一个或多个竞品，默认优先分析产品与定价两个维度，以保证响应速度和结果稳定性。",
        dimensionsLabel: "维度",
        placeholder: "输入一个或多个竞品名称，用逗号分隔",
        run: "开始分析",
        running: "分析中",
        outputHint:
          "当前默认模式先聚焦产品与定价，优先给出可执行的结构化结果。",
        reportLabel: "结果区",
        reportTitle: "当前输出",
        waiting: "等待请求",
        mode: "模式",
        alerts: "预警",
        task: "任务",
        noReport: "暂无报告",
        noReportBody:
          "触发一次分析后，结果会以结构化卡片的形式展示在这里。",
        chartLabel: "图表",
        chartTitle: "信号图表",
        chartEmpty: "本次结果还没有可展示的图表数据。",
        actionLabel: "行动",
        actionTitle: "推荐动作",
        actionEmpty: "当前没有推荐动作。",
        qualityLabel: "质量",
        qualityTitle: "数据质量说明",
        basisLabel: "依据",
        departmentLabel: "责任",
        priorityLabel: "优先级",
        fallbackError: "分析请求失败",
        dimensionSeries: "维度分布",
        timelineSeries: "时间走势",
        timelineLabel: "日期",
      };
    }

    return {
      panelLabel: "Analysis Console",
      panelTitle: "Run The Scan",
      panelHelper:
        "Feed one or more competitors into the pipeline. The default run focuses on product and pricing first for a faster, steadier response.",
      dimensionsLabel: "Dimensions",
      placeholder: "Enter one or more competitors, separated by commas",
      run: "Run Analysis",
      running: "Running Analysis",
      outputHint:
        "The default path prioritizes product and pricing first so the page stays fast and usable.",
      reportLabel: "Report Surface",
      reportTitle: "Current Output",
      waiting: "Waiting For Request",
      mode: "Mode",
      alerts: "Alerts",
      task: "Task",
      noReport: "No Report Yet",
      noReportBody:
        "Trigger a run and the result will appear here as a structured report.",
      chartLabel: "Charts",
      chartTitle: "Signal Views",
      chartEmpty: "No chart data is available for this run yet.",
      actionLabel: "Actions",
      actionTitle: "Recommended Moves",
      actionEmpty: "No recommended actions for this run.",
      qualityLabel: "Quality",
      qualityTitle: "Data Quality Note",
      basisLabel: "Basis",
      departmentLabel: "Owner",
      priorityLabel: "Priority",
      fallbackError: "Analysis request failed",
      dimensionSeries: "By Dimension",
      timelineSeries: "Over Time",
      timelineLabel: "Date",
    };
  }, [language]);

  const chartData = result?.report.chart_data ?? [];
  const recommendedActions = result?.report.recommended_actions ?? [];

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    try {
      const targets = targetInput
        .split(/[,\n]/)
        .map((item) => item.trim())
        .filter(Boolean);

      const response = await analyzeCompetitors({
        targets,
        dimensions: selectedDimensions,
        time_range: language === "zh" ? "近3个月" : "last 3 months",
      });

      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : copy.fallbackError);
    } finally {
      setLoading(false);
    }
  }

  function toggleDimension(dimension: string) {
    setSelectedDimensions((current) =>
      current.includes(dimension)
        ? current.filter((item) => item !== dimension)
        : [...current, dimension]
    );
  }

  return (
    <section className="bau-analysis">
      <div className="bau-panel bau-panel--red">
        <div className="bau-panel__header">
          <div>
            <p className="bau-label">{copy.panelLabel}</p>
            <h2 className="bau-panel__title">{copy.panelTitle}</h2>
          </div>
          <span className="bau-pill bau-pill--yellow">
            {copy.dimensionsLabel} / {selectedLabel}
          </span>
        </div>

        <div className="bau-analysis__grid">
          <div>
            <p className="bau-helper">{copy.panelHelper}</p>
          </div>
          <div>
            <textarea
              value={targetInput}
              onChange={(event) => setTargetInput(event.target.value)}
              rows={5}
              className="bau-textarea"
              placeholder={copy.placeholder}
            />
          </div>
        </div>

        <div className="bau-chip-row" style={{ marginTop: "1rem" }}>
          {DIMENSIONS.map((dimension) => {
            const isActive = selectedDimensions.includes(dimension);
            return (
              <button
                key={dimension}
                type="button"
                className={`bau-chip${isActive ? " bau-chip--active" : ""}`}
                onClick={() => toggleDimension(dimension)}
              >
                {getDimensionLabel(dimension, language)}
              </button>
            );
          })}
        </div>

        <div className="bau-hero__row">
          <button
            type="button"
            className="bau-button bau-button--yellow"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? copy.running : copy.run}
          </button>
          <span className="bau-pill bau-pill--white">{copy.outputHint}</span>
        </div>

        {error ? <p className="bau-error">{error}</p> : null}
      </div>

      <div className="bau-report">
        <div className="bau-panel__header">
          <div>
            <p className="bau-label">{copy.reportLabel}</p>
            <h2 className="bau-panel__title">{copy.reportTitle}</h2>
          </div>
          <span className="bau-pill bau-pill--blue">
            {result ? `Intel Count / ${result.intel_count}` : copy.waiting}
          </span>
        </div>

        {result ? (
          <div className="bau-report__stack">
            <div className="bau-report__grid">
              <div className="bau-report__summary">
                <h3 className="bau-report__title">{result.report.target}</h3>
                <p className="bau-report__lead">
                  {localizeExecutiveSummary(result, language)}
                </p>
                <p className="bau-report__body">
                  {localizeChangesSummary(result, language)}
                </p>
              </div>

              <div className="bau-report__stats">
                <div className="bau-stat-card bau-stat-card--yellow">
                  <p className="bau-label">{copy.mode}</p>
                  <p className="bau-stat-card__value">{result.report.report_type}</p>
                </div>
                <div className="bau-stat-card bau-stat-card--blue">
                  <p className="bau-label">{copy.alerts}</p>
                  <p className="bau-stat-card__value">{result.alerts.length}</p>
                </div>
                <div className="bau-stat-card bau-stat-card--red">
                  <p className="bau-label">{copy.task}</p>
                  <p className="bau-stat-card__value">{result.task_id.slice(-6)}</p>
                </div>
              </div>
            </div>

            <section className="bau-detail-panel bau-detail-panel--quality">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.qualityLabel}</p>
                <h4 className="bau-detail-panel__title">{copy.qualityTitle}</h4>
              </div>
              <p className="bau-quality-note">{result.report.data_quality_note}</p>
            </section>

            <div className="bau-report__detail-grid">
              <section className="bau-detail-panel bau-detail-panel--chart">
                <div className="bau-detail-panel__header">
                  <p className="bau-label">{copy.chartLabel}</p>
                  <h4 className="bau-detail-panel__title">{copy.chartTitle}</h4>
                </div>
                {chartData.length > 0 ? (
                  <div className="bau-chart-list">
                    {chartData.map((item, index) => (
                      <ChartCard
                        key={`${String(item.chart)}-${index}`}
                        item={item}
                        language={language}
                        copy={copy}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="bau-helper">{copy.chartEmpty}</p>
                )}
              </section>

              <section className="bau-detail-panel bau-detail-panel--action">
                <div className="bau-detail-panel__header">
                  <p className="bau-label">{copy.actionLabel}</p>
                  <h4 className="bau-detail-panel__title">{copy.actionTitle}</h4>
                </div>
                {recommendedActions.length > 0 ? (
                  <div className="bau-action-list">
                    {recommendedActions.map((item, index) => (
                      <ActionCard
                        key={`${String(item.priority)}-${index}`}
                        item={item}
                        language={language}
                        copy={copy}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="bau-helper">{copy.actionEmpty}</p>
                )}
              </section>
            </div>
          </div>
        ) : (
          <div className="bau-placeholder">
            <p className="bau-placeholder__title">{copy.noReport}</p>
            <p className="bau-helper">{copy.noReportBody}</p>
          </div>
        )}
      </div>
    </section>
  );
}

function ChartCard({
  item,
  language,
  copy,
}: {
  item: ChartItem;
  language: AppLanguage;
  copy: Record<string, string>;
}) {
  const chartType = String(item.chart ?? "");
  const count = Number(item.count ?? 0);
  const width = `${Math.min(100, Math.max(18, count * 24))}%`;

  if (chartType === "timeline") {
    const date = String(item.date ?? "");
    return (
      <article className="bau-chart-card bau-chart-card--blue">
        <div className="bau-chart-card__meta">
          <span className="bau-pill bau-pill--white">{copy.timelineSeries}</span>
          <strong>
            {copy.timelineLabel} / {date}
          </strong>
        </div>
        <div className="bau-chart-track">
          <div className="bau-chart-fill bau-chart-fill--blue" style={{ width }} />
        </div>
        <p className="bau-chart-value">{count}</p>
      </article>
    );
  }

  const label =
    language === "zh"
      ? String(item.label ?? getDimensionLabel(String(item.dimension ?? ""), language))
      : getDimensionLabel(String(item.dimension ?? ""), language);

  return (
    <article className="bau-chart-card bau-chart-card--yellow">
      <div className="bau-chart-card__meta">
        <span className="bau-pill bau-pill--white">{copy.dimensionSeries}</span>
        <strong>{label}</strong>
      </div>
      <div className="bau-chart-track">
        <div className="bau-chart-fill bau-chart-fill--red" style={{ width }} />
      </div>
      <p className="bau-chart-value">{count}</p>
    </article>
  );
}

function ActionCard({
  item,
  language,
  copy,
}: {
  item: ActionItem;
  language: AppLanguage;
  copy: Record<string, string>;
}) {
  const priority = String(item.priority ?? "");
  const department = String(item.department ?? "");
  const action = String(item.action ?? "");
  const basis = String(item.basis ?? "");
  const toneClass =
    priority === "ASAP"
      ? "bau-action-card--asap"
      : priority === "TODAY"
        ? "bau-action-card--today"
        : "bau-action-card--default";

  return (
    <article className={`bau-action-card ${toneClass}`}>
      <div className="bau-action-card__header">
        <span className={`bau-priority-badge bau-priority-badge--${priority.toLowerCase() || "default"}`}>
          {priority || (language === "zh" ? "待定" : "TBD")}
        </span>
        <span className="bau-action-card__owner">
          {copy.departmentLabel} / {department || (language === "zh" ? "未指定" : "Unassigned")}
        </span>
      </div>
      <p className="bau-action-card__title">{action}</p>
      {basis ? (
        <p className="bau-action-card__basis">
          <span className="bau-label">{copy.basisLabel}</span>
          {basis}
        </p>
      ) : null}
    </article>
  );
}

function getDimensionLabel(dimension: string, language: AppLanguage) {
  const zhMap: Record<string, string> = {
    product: "产品",
    pricing: "定价",
    funding: "融资",
    talent: "人才",
    strategy: "战略",
  };

  const enMap: Record<string, string> = {
    product: "Product",
    pricing: "Pricing",
    funding: "Funding",
    talent: "Talent",
    strategy: "Strategy",
  };

  return language === "zh"
    ? zhMap[dimension] ?? dimension
    : enMap[dimension] ?? dimension;
}
