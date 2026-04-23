import React, { useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import {
  analyzeCompetitors,
  type AlertItem,
  type AnalyzeResponse,
} from "../services/api";
import {
  localizeChangesSummary,
  localizeCompanyList,
  localizeDimensionLabel,
  localizeExecutiveSummary,
  localizeReportType,
} from "../services/localization";

const DIMENSIONS = ["product", "pricing", "funding", "talent", "strategy"];
const DEFAULT_DIMENSIONS = ["product", "pricing"];

type ActionItem = Record<string, unknown>;
type SignalEntry = Record<string, unknown> & { dimension: string };

type ChatInterfaceProps = {
  language: AppLanguage;
  onResult?: (result: AnalyzeResponse) => void;
};

export function ChatInterface({ language, onResult }: ChatInterfaceProps) {
  const [targetInput, setTargetInput] = useState("Feishu, DingTalk");
  const [selectedDimensions, setSelectedDimensions] =
    useState<string[]>(DEFAULT_DIMENSIONS);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedLabel = useMemo(() => {
    return selectedDimensions.length > 0
      ? selectedDimensions
          .map((item) => localizeDimensionLabel(item, language))
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
          "输入一个或多个竞品名称。系统会尽量保留你实际勾选的分析维度，并先输出适合答辩展示的结构化结果。",
        dimensionsLabel: "维度",
        placeholder: "输入一个或多个竞品名称，用逗号分隔",
        run: "开始分析",
        running: "分析中",
        outputHint: "结果会先给出结论，再展示结构化信号与来源证据。",
        reportLabel: "结果区",
        reportTitle: "当前输出",
        waiting: "等待请求",
        mode: "模式",
        alerts: "预警",
        task: "任务",
        noReport: "暂无报告",
        noReportBody: "触发一次分析后，结果会以结构化卡片的形式展示在这里。",
        chartLabel: "结果指标",
        chartTitle: "结果判断卡",
        chartEmpty: "当前结果还不足以形成更明确的变化判断。",
        chartNote:
          "这里展示的是结论指标卡，不是传统坐标图，重点回答“发生了什么、为什么要关心”。",
        changeFocusTitle: "重点变化图",
        insightFocusTitle: "结论型图表",
        productChange: "产品变化",
        pricingChange: "定价变化",
        alertTriggered: "是否触发预警",
        focusDimensionTitle: "最值得关注的维度",
        highConfidenceTitle: "高置信度信号数量",
        changedSinceLastRun: "是否相对上次有变化",
        countUnit: "条",
        yes: "是",
        no: "否",
        none: "暂无",
        actionLabel: "行动",
        actionTitle: "推荐动作",
        actionEmpty: "当前没有推荐动作。",
        signalsLabel: "信号",
        signalsTitle: "结构化信号",
        signalsEmpty: "这次运行还没有提取出可展示的结构化信号。",
        signalsMockOnly: "当前结果主要来自演示回退数据，示例占位来源已隐藏。",
        qualityLabel: "质量",
        qualityTitle: "数据质量说明",
        basisLabel: "依据",
        departmentLabel: "责任",
        sourceLabel: "来源",
        publishedLabel: "发布时间",
        evidenceLabel: "证据",
        openLabel: "打开来源",
        fallbackError: "分析请求失败",
        comparisonHint: "已完成跨竞品对比，请重点关注差异化动态。",
        mockSourceLabel: "演示回退来源",
        mockSourceDescription:
          "这条信号来自本地演示数据，只用于展示结果结构，不代表真实外部网页抓取结果。",
      };
    }

    return {
      panelLabel: "Analysis Console",
      panelTitle: "Run The Scan",
      panelHelper:
        "Enter one or more competitors. The system tries to preserve the dimensions you selected and render display-ready structured results first.",
      dimensionsLabel: "Dimensions",
      placeholder: "Enter one or more competitors, separated by commas",
      run: "Run Analysis",
      running: "Running Analysis",
      outputHint: "The result shows the conclusion first, then the structured signals and source evidence.",
      reportLabel: "Report Surface",
      reportTitle: "Current Output",
      waiting: "Waiting For Request",
      mode: "Mode",
      alerts: "Alerts",
      task: "Task",
      noReport: "No Report Yet",
      noReportBody: "Trigger a run and the result will appear here.",
      chartLabel: "Result Metrics",
      chartTitle: "Decision Cards",
      chartEmpty: "This run does not have enough evidence to form a stronger change view yet.",
      chartNote:
        "These are decision cards rather than classic charts. They are meant to explain what changed and why it matters.",
      changeFocusTitle: "What Changed",
      insightFocusTitle: "Why It Matters",
      productChange: "Product Changes",
      pricingChange: "Pricing Changes",
      alertTriggered: "Alert Triggered",
      focusDimensionTitle: "Most Noteworthy Dimension",
      highConfidenceTitle: "Higher-Confidence Signals",
      changedSinceLastRun: "Changed Since Last Run",
      countUnit: "items",
      yes: "Yes",
      no: "No",
      none: "None",
      actionLabel: "Actions",
      actionTitle: "Recommended Moves",
      actionEmpty: "No recommended actions for this run.",
      signalsLabel: "Signals",
      signalsTitle: "Structured Signals",
      signalsEmpty: "This run did not produce display-ready structured signals yet.",
      signalsMockOnly:
        "This run is mostly using demo fallback data, so example.com placeholder cards are hidden.",
      qualityLabel: "Quality",
      qualityTitle: "Data Quality Note",
      basisLabel: "Basis",
      departmentLabel: "Owner",
      sourceLabel: "Source",
      publishedLabel: "Published",
      evidenceLabel: "Evidence",
      openLabel: "Open source",
      fallbackError: "Analysis request failed",
      comparisonHint:
        "Cross-competitor comparison is ready. Focus on the strongest differences first.",
      mockSourceLabel: "Demo fallback source",
      mockSourceDescription:
        "This signal comes from local demo fallback data and only shows the shape of the result.",
    };
  }, [language]);

  const recommendedActions = result?.report.recommended_actions ?? [];
  const changeEvents = result?.change_events ?? [];
  const normalizedDimensions = normalizeDimensionSignals(result);
  const signalEntries = flattenSignalEntries(normalizedDimensions);
  const visibleSignalEntries = signalEntries.filter((item) => !isDemoSignal(item));
  const hasOnlyMockSignals = signalEntries.length > 0 && visibleSignalEntries.length === 0;
  const productCount = getDimensionSignalCount(normalizedDimensions, "product");
  const pricingCount = getDimensionSignalCount(normalizedDimensions, "pricing");
  const highConfidenceCount = countHighConfidenceSignals(normalizedDimensions);
  const noteworthyDimension = getMostNoteworthyDimension(normalizedDimensions, changeEvents);

  const displayActions =
    recommendedActions.length > 0
      ? recommendedActions
      : buildFallbackActions(result?.alerts ?? [], changeEvents, language);
  const actionTitle =
    language === "zh" ? "\u5efa\u8bae\u52a8\u4f5c" : "Suggested Actions";
  const actionEmpty =
    language === "zh"
      ? "\u5f53\u524d\u8fd8\u6ca1\u6709\u8db3\u591f\u660e\u786e\u7684\u540e\u7eed\u52a8\u4f5c\u5efa\u8bae\u3002"
      : "No clear next-step recommendations are available for this run yet.";
  const taskLabel =
    language === "zh" ? "\u5206\u6790\u7f16\u53f7" : "Run ID";

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
        time_range: language === "zh" ? "最近三个月" : "last 3 months",
      });

      setResult(response);
      onResult?.(response);
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
        : [...current, dimension],
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
                {localizeDimensionLabel(dimension, language)}
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
                <h3 className="bau-report__title">
                  {localizeCompanyList(result.report.target, language)}
                </h3>
                <p className="bau-report__lead">
                  {localizeExecutiveSummary(result, language)}
                </p>
                <p className="bau-report__body">
                  {result.report.report_type === "comparison"
                    ? copy.comparisonHint
                    : localizeChangesSummary(result, language)}
                </p>
              </div>

              <div className="bau-report__stats">
                <div className="bau-stat-card bau-stat-card--yellow">
                  <p className="bau-label">{copy.mode}</p>
                  <p className="bau-stat-card__value">
                    {localizeReportType(result.report.report_type, language)}
                  </p>
                </div>
                <div className="bau-stat-card bau-stat-card--blue">
                  <p className="bau-label">{copy.alerts}</p>
                  <p className="bau-stat-card__value">{result.alerts.length}</p>
                </div>
                <div className="bau-stat-card bau-stat-card--red">
                  <p className="bau-label">{taskLabel}</p>
                  <p className="bau-stat-card__value">{result.task_id.slice(-6)}</p>
                </div>
              </div>
            </div>

            <section className="bau-detail-panel bau-detail-panel--quality">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.qualityLabel}</p>
                <h4 className="bau-detail-panel__title">{copy.qualityTitle}</h4>
              </div>
              <p className="bau-quality-note">
                {normalizeQualityNote(result.report.data_quality_note, language)}
              </p>
            </section>

            <div className="bau-report__detail-grid">
              <section className="bau-detail-panel bau-detail-panel--chart">
                <div className="bau-detail-panel__header">
                  <p className="bau-label">{copy.chartLabel}</p>
                  <h4 className="bau-detail-panel__title">{copy.chartTitle}</h4>
                </div>
                <p className="bau-helper">{copy.chartNote}</p>

                <div className="bau-chart-list">
                  <InsightCard
                    tone="yellow"
                    title={copy.changeFocusTitle}
                    rows={[
                      {
                        label: copy.productChange,
                        value: formatCount(
                          Math.max(countDimensionChanges(changeEvents, "product"), productCount),
                          copy.countUnit,
                        ),
                      },
                      {
                        label: copy.pricingChange,
                        value: formatCount(
                          Math.max(countDimensionChanges(changeEvents, "pricing"), pricingCount),
                          copy.countUnit,
                        ),
                      },
                      {
                        label: copy.alertTriggered,
                        value: result.alerts.length > 0 ? copy.yes : copy.no,
                      },
                    ]}
                  />

                  <InsightCard
                    tone="blue"
                    title={copy.insightFocusTitle}
                    rows={[
                      {
                        label: copy.focusDimensionTitle,
                        value: noteworthyDimension
                          ? localizeDimensionLabel(noteworthyDimension, language)
                          : copy.none,
                      },
                      {
                        label: copy.highConfidenceTitle,
                        value: formatCount(highConfidenceCount, copy.countUnit),
                      },
                      {
                        label: copy.changedSinceLastRun,
                        value:
                          changeEvents.length > 0 || productCount > 0 || pricingCount > 0
                            ? copy.yes
                            : copy.no,
                      },
                    ]}
                  />
                </div>

                {changeEvents.length === 0 && highConfidenceCount === 0 ? (
                  <p className="bau-helper">{copy.chartEmpty}</p>
                ) : null}
              </section>

              <section className="bau-detail-panel bau-detail-panel--action">
                <div className="bau-detail-panel__header">
                  <p className="bau-label">{copy.actionLabel}</p>
                  <h4 className="bau-detail-panel__title">{actionTitle}</h4>
                </div>
                {displayActions.length > 0 ? (
                  <div className="bau-action-list">
                    {displayActions.map((item, index) => (
                      <ActionCard
                        key={`${String(item.priority)}-${index}`}
                        item={item}
                        language={language}
                        copy={copy}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="bau-helper">{actionEmpty}</p>
                )}
              </section>
            </div>

            <section className="bau-detail-panel bau-detail-panel--quality">
              <div className="bau-detail-panel__header">
                <p className="bau-label">{copy.signalsLabel}</p>
                <h4 className="bau-detail-panel__title">{copy.signalsTitle}</h4>
              </div>
              {visibleSignalEntries.length > 0 ? (
                <div className="bau-snapshot-details">
                  {visibleSignalEntries.slice(0, 8).map((item, index) => (
                    <article
                      key={`${item.dimension}-${String(item.extracted_data)}-${index}`}
                      className="bau-snapshot-item-card"
                    >
                      <div className="bau-snapshot-item-card__meta">
                        <span className="bau-pill bau-pill--white">
                          {localizeDimensionLabel(item.dimension, language)}
                        </span>
                        <span className="bau-meta">
                          {copy.publishedLabel}:{" "}
                          {formatDateLabel(String(item.publish_date || item.crawl_date || "-"))}
                        </span>
                      </div>
                      <p className="bau-snapshot-item-card__title">
                        {String(item.extracted_data || "")}
                      </p>
                      <p className="bau-snapshot-item-card__text">
                        {copy.sourceLabel}:{" "}
                        {item.source_url ? (
                          <a
                            className="bau-link"
                            href={String(item.source_url)}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {formatSourceName(item)}
                          </a>
                        ) : (
                          formatSourceName(item)
                        )}
                      </p>
                      <div className="bau-snapshot-item-card__actions">
                        {item.source_url ? (
                          <a
                            className="bau-link"
                            href={String(item.source_url)}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {copy.openLabel}
                          </a>
                        ) : isDemoSignal(item) ? (
                          <span className="bau-meta">{copy.mockSourceLabel}</span>
                        ) : null}
                      </div>
                      {item.evidence_quote ? (
                        <p className="bau-snapshot-item-card__quote">
                          <strong>{copy.evidenceLabel}: </strong>
                          {normalizeEvidenceText(String(item.evidence_quote), language)}
                        </p>
                      ) : null}
                      {isDemoSignal(item) ? (
                        <p className="bau-helper">{copy.mockSourceDescription}</p>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : hasOnlyMockSignals ? (
                <p className="bau-helper">{copy.signalsMockOnly}</p>
              ) : (
                <p className="bau-helper">{copy.signalsEmpty}</p>
              )}
            </section>
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

function InsightCard({
  title,
  rows,
  tone,
}: {
  title: string;
  rows: Array<{ label: string; value: string }>;
  tone: "yellow" | "blue";
}) {
  return (
    <article
      className={`bau-chart-card ${
        tone === "blue" ? "bau-chart-card--blue" : "bau-chart-card--yellow"
      }`}
    >
      <div className="bau-chart-card__meta">
        <span className="bau-pill bau-pill--white">{title}</span>
      </div>
      <div className="bau-insight-list">
        {rows.map((row) => (
          <div key={row.label} className="bau-insight-row">
            <span className="bau-insight-row__label">{row.label}</span>
            <strong className="bau-insight-row__value">{row.value}</strong>
          </div>
        ))}
      </div>
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
  const basis = normalizeBasisText(String(item.basis ?? ""), language);
  const toneClass =
    priority === "ASAP"
      ? "bau-action-card--asap"
      : priority === "TODAY"
        ? "bau-action-card--today"
        : "bau-action-card--default";

  return (
    <article className={`bau-action-card ${toneClass}`}>
      <div className="bau-action-card__header">
        <span
          className={`bau-priority-badge bau-priority-badge--${
            priority.toLowerCase() || "default"
          }`}
        >
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

function countDimensionChanges(
  changeEvents: AnalyzeResponse["change_events"],
  dimension: string,
) {
  return changeEvents.filter((item) => item.dimension === dimension).length;
}

function normalizeDimensionSignals(
  result: AnalyzeResponse | null,
): Record<string, Array<Record<string, unknown>>> {
  if (!result?.report.dimensions_detail) {
    return {};
  }

  const normalized: Record<string, Array<Record<string, unknown>>> = {};
  const detail = result.report.dimensions_detail;

  Object.entries(detail).forEach(([key, value]) => {
    if (!Array.isArray(value)) {
      Object.values(value as Record<string, unknown>).forEach((nested) => {
        if (nested && typeof nested === "object" && !Array.isArray(nested)) {
          Object.entries(nested as Record<string, unknown>).forEach(([nestedKey, nestedValue]) => {
            if (Array.isArray(nestedValue) && DIMENSIONS.includes(nestedKey)) {
              normalized[nestedKey] = [
                ...(normalized[nestedKey] ?? []),
                ...nestedValue,
              ];
            }
          });
        }
      });
      return;
    }

    if (DIMENSIONS.includes(key)) {
      normalized[key] = [...(normalized[key] ?? []), ...value];
    }
  });

  return normalized;
}

function getDimensionSignalCount(
  dimensionsDetail: Record<string, Array<Record<string, unknown>>>,
  dimension: string,
) {
  return (dimensionsDetail[dimension] ?? []).length;
}

function flattenSignalEntries(
  dimensionsDetail: Record<string, Array<Record<string, unknown>>>,
): SignalEntry[] {
  return Object.entries(dimensionsDetail)
    .flatMap(([dimension, items]) =>
      items.map((item) => ({
        ...item,
        dimension,
      })),
    )
    .sort((a, b) =>
      String(b.publish_date || b.crawl_date || "").localeCompare(
        String(a.publish_date || a.crawl_date || ""),
      ),
    );
}

function countHighConfidenceSignals(
  dimensionsDetail: Record<string, Array<Record<string, unknown>>>,
) {
  return Object.values(dimensionsDetail)
    .flat()
    .filter((item) => Number(item.credibility ?? 0) >= 0.6).length;
}

function getMostNoteworthyDimension(
  dimensionsDetail: Record<string, Array<Record<string, unknown>>>,
  changeEvents: AnalyzeResponse["change_events"],
) {
  const dimensionScores = new Map<string, number>();

  Object.entries(dimensionsDetail).forEach(([dimension, items]) => {
    if (DIMENSIONS.includes(dimension)) {
      dimensionScores.set(dimension, (dimensionScores.get(dimension) ?? 0) + items.length);
    }
  });

  changeEvents.forEach((item) => {
    if (DIMENSIONS.includes(item.dimension)) {
      dimensionScores.set(item.dimension, (dimensionScores.get(item.dimension) ?? 0) + 2);
    }
  });

  const ranked = [...dimensionScores.entries()].sort((a, b) => b[1] - a[1]);
  return ranked[0]?.[0] ?? "";
}

function formatCount(count: number, unit: string) {
  return `${count} ${unit}`;
}

function isDemoSignal(item: SignalEntry) {
  const sourceUrl = String(item.source_url || "");
  const sourceName = String(item.source_name || "");
  const extractedData = String(item.extracted_data || "");
  return (
    sourceUrl.includes("example.com") ||
    sourceName.includes("example.com") ||
    extractedData.includes("示例公开页面")
  );
}

function normalizeBasisText(text: string, language: AppLanguage) {
  if (!text) {
    return text;
  }
  if (text.includes("示例公开页面") || text.includes("example.com")) {
    return language === "zh"
      ? "当前动作依据来自演示回退数据。"
      : "This action is based on demo fallback data.";
  }
  return text;
}

function normalizeQualityNote(text: string, language: AppLanguage) {
  const normalized = text.replace(/\s+/g, " ").trim();
  const usesDemoFallback =
    normalized.includes("example.com") ||
    normalized.includes("mock") ||
    normalized.includes("模拟数据") ||
    normalized.includes("演示回退");
  const hasPublicIntel =
    normalized.includes("公开来源") || normalized.toLowerCase().includes("public");

  if (usesDemoFallback) {
    return language === "zh"
      ? "当前结果混入了演示回退数据，适合展示流程与页面结构，不适合直接当作真实竞品结论。"
      : "This result includes demo fallback data. It is suitable for showing the workflow, but should not be treated as a final real-world competitor conclusion.";
  }

  if (hasPublicIntel) {
    return language === "zh"
      ? "当前结果基于公开来源整理生成，可用于展示结构化分析与历史对比。"
      : "This result is generated from public-source intelligence and can be used to demonstrate structured analysis and historical comparison.";
  }

  return normalized;
}

function normalizeEvidenceText(text: string, language: AppLanguage) {
  if (text.includes("示例公开页面")) {
    return language === "zh" ? "示例公开页面（演示回退数据）" : "Sample public page (demo fallback data)";
  }
  return text;
}

function formatSourceName(item: Record<string, unknown>) {
  const sourceName = String(item.source_name || "").trim();
  const sourceUrl = String(item.source_url || "").trim();
  if (sourceName) {
    return sourceName;
  }
  if (!sourceUrl) {
    return "-";
  }
  try {
    return new URL(sourceUrl).hostname;
  } catch {
    return sourceUrl;
  }
}

function formatDateLabel(value: string) {
  if (!value || value === "-") {
    return value || "-";
  }
  const normalized = value.replace("T", " ").replace("+00:00", " UTC");
  return normalized.replace("Z", " UTC");
}

function buildFallbackActions(
  alerts: AlertItem[],
  changeEvents: AnalyzeResponse["change_events"],
  language: AppLanguage,
) {
  if (alerts.length > 0) {
    return alerts.slice(0, 2).map((alert) => ({
      priority: alert.severity === "high" ? "ASAP" : "TODAY",
      department: language === "zh" ? "\u4ea7\u54c1 / \u7b56\u7565" : "Product / Strategy",
      action:
        language === "zh"
          ? `\u4f18\u5148\u590d\u6838${alert.company}\u7684\u9884\u8b66\u53d8\u5316\uff0c\u786e\u8ba4\u662f\u5426\u9700\u8981\u8c03\u6574\u5bf9\u6807\u7b56\u7565\u3002`
          : `Review the latest ${alert.company} alert and confirm whether the benchmark plan should be adjusted.`,
      basis: alert.title,
    }));
  }

  if (changeEvents.length > 0) {
    return changeEvents.slice(0, 2).map((event) => ({
      priority: "TODAY",
      department: language === "zh" ? "\u4ea7\u54c1 / \u5e02\u573a" : "Product / Marketing",
      action:
        language === "zh"
          ? `\u68b3\u7406${event.company}\u5728${localizeDimensionLabel(
              event.dimension,
              language,
            )}\u7ef4\u5ea6\u7684\u53d8\u5316\uff0c\u8f93\u51fa\u4e00\u6761\u53ef\u76f4\u63a5\u7528\u4e8e\u5bf9\u6bd4\u7684\u7ed3\u8bba\u3002`
          : `Summarize the ${event.company} change in ${localizeDimensionLabel(
              event.dimension,
              language,
            )} and turn it into a benchmark-ready conclusion.`,
      basis: event.description,
    }));
  }

  return [];
}
