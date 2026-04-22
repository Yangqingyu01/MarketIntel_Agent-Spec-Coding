"""Report agent for concise structured intelligence output."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from tools.report_builder import utc_now_iso


def build_report(
    task_id: str,
    target: str,
    analysis_results: list[dict[str, Any]],
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in analysis_results:
        grouped[item.get("dimension", "product")].append(item)

    key_insights = [item.get("extracted_data", "") for item in analysis_results[:5]]
    executive_summary = (
        f"本次分析覆盖 {target} 的公开情报，共提取 {len(analysis_results)} 条结构化信息。"
    )
    if baseline:
        executive_summary += " 已结合历史基线进行对比。"
    else:
        executive_summary += " 当前为冷启动或无可用历史基线。"

    recommended_actions = []
    if key_insights:
        recommended_actions.append(
            {
                "priority": "ASAP",
                "department": "产品部",
                "action": "复核本次竞品核心动态与我方路线图的差异",
                "basis": key_insights[0],
            }
        )

    return {
        "report_id": f"RPT-{task_id}",
        "report_type": "single",
        "target": target,
        "generated_at": utc_now_iso(),
        "executive_summary": executive_summary,
        "dimensions_detail": grouped,
        "changes_summary": "初始版本未生成专门变化摘要" if baseline else "暂无历史对比",
        "chart_data": [],
        "recommended_actions": recommended_actions,
        "key_insights": key_insights,
        "data_quality_note": f"结果基于 {len(analysis_results)} 条公开来源情报生成",
    }
