import type { AlertItem, AnalyzeResponse } from "./api";

const REPLACEMENTS: Array<[RegExp, string]> = [
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
  [/上线/g, "launched"],
  [/发布/g, "released"],
  [/更新/g, "update"],
  [/功能/g, "feature"],
  [/能力/g, "capability"],
  [/预警/g, "alert"],
  [/变化/g, "change"],
  [/最近数量/g, "recent count"],
];

export function localizeExecutiveSummary(
  result: AnalyzeResponse,
  language: "zh" | "en"
): string {
  if (language === "zh") {
    return result.report.executive_summary;
  }

  const translated = translateKnownText(result.report.executive_summary);
  return preserveOriginalDetails(result.report.executive_summary, translated);
}

export function localizeChangesSummary(
  result: AnalyzeResponse,
  language: "zh" | "en"
): string {
  if (language === "zh") {
    return result.report.changes_summary;
  }

  const translated = translateKnownText(result.report.changes_summary);
  return preserveOriginalDetails(result.report.changes_summary, translated);
}

export function localizeAlertTitle(
  alert: AlertItem,
  language: "zh" | "en"
): string {
  if (language === "zh") {
    return alert.title;
  }

  const translated = translateKnownText(alert.title);
  return preserveOriginalDetails(alert.title, translated);
}

export function localizeAlertDescription(
  alert: AlertItem,
  language: "zh" | "en"
): string {
  if (language === "zh") {
    return alert.description;
  }

  const translated = translateKnownText(alert.description);
  return preserveOriginalDetails(alert.description, translated);
}

function translateKnownText(text: string): string {
  let output = text;
  for (const [pattern, replacement] of REPLACEMENTS) {
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
