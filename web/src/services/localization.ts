import type { AlertItem, AnalyzeResponse } from "./api";

const ZH_TO_EN_REPLACEMENTS: Array<[RegExp, string]> = [
  [/本次分析覆盖/g, "This analysis covers "],
  [/公开情报/g, "public intelligence"],
  [/共提取/g, "with "],
  [/条结构化信息/g, " structured records"],
  [/已结合历史基线完成变化对比/g, "Historical baseline comparison is included"],
  [/当前为冷启动或暂无可用历史基线/g, "No historical baseline is available yet"],
  [/已识别并生成/g, "Generated "],
  [/条变化预警/g, " change alerts"],
  [/已完成与历史基线对比，当前没有新增预警/g, "Historical comparison completed and no new alerts were generated"],
  [/暂无历史对比结果/g, "No historical comparison is available yet"],
  [/产品/g, "product"],
  [/定价/g, "pricing"],
  [/融资/g, "funding"],
  [/人才/g, "talent"],
  [/战略/g, "strategy"],
  [/最近数量/g, "recent count"],
];

const EN_ALERT_TITLE_TO_ZH: Array<[RegExp, string]> = [
  [/^FEISHU PRODUCT CHANGE ALERT$/i, "飞书产品变化预警"],
  [/^FEISHU STRATEGY CHANGE ALERT$/i, "飞书战略变化预警"],
  [/^FEISHU PRICING CHANGE ALERT$/i, "飞书定价变化预警"],
  [/^DINGTALK PRODUCT CHANGE ALERT$/i, "钉钉产品变化预警"],
  [/^DINGTALK STRATEGY CHANGE ALERT$/i, "钉钉战略变化预警"],
  [/^DINGTALK PRICING CHANGE ALERT$/i, "钉钉定价变化预警"],
];

const EN_ALERT_DESC_TO_ZH: Array<[RegExp, string]> = [
  [
    /Feishu launched the OpenClaw official plugin and exposed direct work-scene integration capabilities\./i,
    "飞书上线了 OpenClaw 官方插件，并开放了更直接的工作场景集成能力。",
  ],
  [
    /Feishu introduced MCP Server for AI Agent workflows, indicating a stronger AI ecosystem push\./i,
    "飞书推出了面向 AI Agent 工作流的 MCP Server，说明其正在加强 AI 生态布局。",
  ],
  [
    /Feishu updated Lark Base pricing and clarified higher-tier capacity expansion\./i,
    "飞书更新了 Lark Base 定价，并明确了更高阶套餐的容量扩展方案。",
  ],
];

const DIMENSION_ZH: Record<string, string> = {
  product: "产品",
  pricing: "定价",
  funding: "融资",
  talent: "人才",
  strategy: "战略",
};

const DIMENSION_EN: Record<string, string> = {
  product: "Product",
  pricing: "Pricing",
  funding: "Funding",
  talent: "Talent",
  strategy: "Strategy",
};

export function localizeExecutiveSummary(
  result: AnalyzeResponse,
  language: "zh" | "en",
): string {
  if (language === "zh") {
    return result.report.executive_summary;
  }

  const translated = translateKnownText(result.report.executive_summary);
  return preserveOriginalDetails(result.report.executive_summary, translated);
}

export function localizeChangesSummary(
  result: AnalyzeResponse,
  language: "zh" | "en",
): string {
  if (language === "zh") {
    return result.report.changes_summary;
  }

  const translated = translateKnownText(result.report.changes_summary);
  return preserveOriginalDetails(result.report.changes_summary, translated);
}

export function localizeAlertTitle(
  alert: AlertItem,
  language: "zh" | "en",
): string {
  if (language === "zh") {
    for (const [pattern, replacement] of EN_ALERT_TITLE_TO_ZH) {
      if (pattern.test(alert.title)) {
        return replacement;
      }
    }
    return alert.title;
  }

  const translated = translateKnownText(alert.title);
  return preserveOriginalDetails(alert.title, translated);
}

export function localizeAlertDescription(
  alert: AlertItem,
  language: "zh" | "en",
): string {
  if (language === "zh") {
    for (const [pattern, replacement] of EN_ALERT_DESC_TO_ZH) {
      if (pattern.test(alert.description)) {
        return replacement;
      }
    }
    return alert.description;
  }

  const translated = translateKnownText(alert.description);
  return preserveOriginalDetails(alert.description, translated);
}

export function localizeDimensionLabel(
  dimension: string,
  language: "zh" | "en",
): string {
  return language === "zh"
    ? DIMENSION_ZH[dimension] ?? dimension
    : DIMENSION_EN[dimension] ?? dimension;
}

export function localizeReportType(
  reportType: string,
  language: "zh" | "en",
): string {
  const normalized = String(reportType || "").toLowerCase();
  if (language === "zh") {
    if (normalized === "comparison") {
      return "对比分析";
    }
    if (normalized === "single") {
      return "单目标分析";
    }
    return reportType;
  }

  if (normalized === "comparison") {
    return "Comparison";
  }
  if (normalized === "single") {
    return "Single Target";
  }
  return reportType;
}

export function localizeSeverity(
  severity: string,
  language: "zh" | "en",
): string {
  const normalized = String(severity || "").toLowerCase();
  if (language === "zh") {
    if (normalized === "high") {
      return "高";
    }
    if (normalized === "medium") {
      return "中";
    }
    if (normalized === "low") {
      return "低";
    }
  }
  return severity.toUpperCase();
}

export function localizeCompanyName(
  company: string,
  language: "zh" | "en",
): string {
  const normalized = String(company || "").toLowerCase();
  if (language === "zh") {
    if (normalized === "feishu") {
      return "飞书";
    }
    if (normalized === "dingtalk") {
      return "钉钉";
    }
  }
  return company;
}

export function localizeCompanyList(
  companies: string,
  language: "zh" | "en",
): string {
  return companies
    .split(",")
    .map((item) => localizeCompanyName(item.trim(), language))
    .join(language === "zh" ? "、" : ", ");
}

function translateKnownText(text: string): string {
  let output = text;
  for (const [pattern, replacement] of ZH_TO_EN_REPLACEMENTS) {
    output = output.replace(pattern, replacement);
  }
  return output.replace(/\s+/g, " ").trim();
}

function preserveOriginalDetails(original: string, translated: string): string {
  if (!containsChinese(translated)) {
    return translated;
  }

  if (translated !== original) {
    return `${translated} (${original})`;
  }

  return original;
}

function containsChinese(text: string): boolean {
  return /[\u4e00-\u9fff]/.test(text);
}
