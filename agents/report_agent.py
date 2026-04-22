"""Report agent for concise structured intelligence output."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

from feishu.cards import build_report_card
from tools.chart_generator import build_report_charts
from tools.report_builder import utc_now_iso


def build_report(
    task_id: str,
    target: str,
    analysis_results: List[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]] = None,
    alerts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in analysis_results:
        grouped[item.get("dimension", "product")].append(item)

    key_insights = [item.get("extracted_data", "") for item in analysis_results[:5]]
    executive_summary = "本次分析覆盖 {target} 的公开情报，共提取 {count} 条结构化信息。".format(
        target=target,
        count=len(analysis_results),
    )
    if baseline:
        executive_summary += " 已结合历史基线完成变化对比。"
    else:
        executive_summary += " 当前为冷启动或暂无可用历史基线。"

    recommended_actions = []
    if key_insights:
        recommended_actions.append(
            {
                "priority": "ASAP",
                "department": "产品",
                "action": "复核本次竞品核心动态与我方路线图的差异",
                "basis": key_insights[0],
            }
        )
    if alerts:
        recommended_actions.append(
            {
                "priority": "TODAY",
                "department": "战略",
                "action": "优先处理最新变化预警并确认是否需要飞书同步。",
                "basis": alerts[0].get("description", ""),
            }
        )

    chart_data = build_report_charts(analysis_results)
    changes_summary = (
        "已识别并生成 {count} 条变化预警".format(count=len(alerts or []))
        if alerts
        else ("已完成与历史基线对比，当前没有新增预警" if baseline else "暂无历史对比结果")
    )

    report = {
        "report_id": f"RPT-{task_id}",
        "report_type": "single",
        "target": target,
        "generated_at": utc_now_iso(),
        "time_range_covered": "近3个月",
        "executive_summary": executive_summary,
        "dimensions_detail": grouped,
        "changes_summary": changes_summary,
        "chart_data": chart_data,
        "recommended_actions": recommended_actions,
        "key_insights": key_insights,
        "data_quality_note": "结果基于 {count} 条公开来源情报生成".format(
            count=len(analysis_results)
        ),
    }
    report["feishu_card"] = build_report_card(report, alerts or [])
    return report


def build_digest_summary(
    reports: List[Dict[str, Any]],
    alerts: List[Dict[str, Any]],
    frequency: str,
) -> Dict[str, Any]:
    return {
        "summary_type": frequency,
        "report_count": len(reports),
        "alert_count": len(alerts),
        "headline": "本次 {frequency} 摘要共汇总 {report_count} 份报告和 {alert_count} 条预警。".format(
            frequency="每日" if frequency == "daily" else "每周",
            report_count=len(reports),
            alert_count=len(alerts),
        ),
        "reports": reports,
        "alerts": alerts,
    }
