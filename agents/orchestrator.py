"""Main orchestration flow for MarketIntel MVP analysis."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.alert_agent import generate_alerts
from agents.analysis_agent import analyze_results, build_change_events
from agents.report_agent import build_report
from agents.search_agent import run_search
from config import config
from feishu.sender import send_card
from tools.knowledge_base import save_intel, save_snapshot
from tools.report_builder import get_logger


logger = get_logger("marketintel.orchestrator")


def _infer_intent_type(targets: List[str], dimensions: List[str]) -> str:
    if len(targets) > 1:
        return "TYPE_B"
    if len(dimensions) == 1:
        return "TYPE_C"
    return "TYPE_A"


def _build_comparison_report(
    task_id: str,
    targets: List[str],
    reports: List[Dict[str, Any]],
    analysis_count: int,
) -> Dict[str, Any]:
    return {
        "report_id": f"RPT-{task_id}",
        "report_type": "comparison",
        "target": ", ".join(targets),
        "generated_at": reports[0]["generated_at"] if reports else "",
        "executive_summary": "已完成 {count} 个竞品的对比分析。".format(
            count=len(targets)
        ),
        "dimensions_detail": {
            report["target"]: report["dimensions_detail"] for report in reports
        },
        "changes_summary": "跨竞品对比已生成，请重点关注差异化动态。",
        "chart_data": [],
        "recommended_actions": [],
        "key_insights": [report["executive_summary"] for report in reports],
        "data_quality_note": "总计提取 {count} 条结构化情报。".format(
            count=analysis_count
        ),
    }


def run_analysis(
    targets: List[str],
    dimensions: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    output_format: str = "web",
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the MVP analysis chain."""
    dimensions = dimensions or list(config.default_dimensions)
    time_range = time_range or config.default_time_range
    task_id = f"TASK-{int(datetime.utcnow().timestamp())}"
    intent_type = _infer_intent_type(targets, dimensions)

    all_search_results: List[Dict[str, Any]] = []
    all_analysis_results: List[Dict[str, Any]] = []
    all_change_events: List[Dict[str, Any]] = []
    all_alerts: List[Dict[str, Any]] = []
    reports: List[Dict[str, Any]] = []

    for target in targets:
        logger.info("[Search Agent] searching %s", target)
        search_results = run_search(target, dimensions, time_range)
        all_search_results.extend(search_results)

        logger.info("[Analysis Agent] analyzing %s", target)
        analysis_results, baseline = analyze_results(
            target,
            search_results,
            organization_id=organization_id,
        )
        change_events = build_change_events(target, analysis_results, baseline)
        for intel in analysis_results:
            save_intel(intel, intel.get("evidence_quote", ""))
        all_analysis_results.extend(analysis_results)
        all_change_events.extend(change_events)

        logger.info("[Alert Agent] evaluating %s", target)
        alerts = generate_alerts(
            target,
            analysis_results,
            baseline,
            change_events=change_events,
            organization_id=organization_id,
        )
        all_alerts.extend(alerts)

        save_snapshot(target, analysis_results, organization_id=organization_id)

        logger.info("[Report Agent] building report for %s", target)
        report = build_report(
            task_id,
            target,
            analysis_results,
            baseline,
            alerts=alerts,
        )
        if output_format == "feishu":
            report["feishu_delivery"] = send_card(report.get("feishu_card", {}))
        reports.append(report)

    final_report = (
        reports[0]
        if len(reports) == 1
        else _build_comparison_report(task_id, targets, reports, len(all_analysis_results))
    )

    return {
        "query": "分析 {targets}".format(targets=", ".join(targets)),
        "task_id": task_id,
        "intent_type": intent_type,
        "targets": targets,
        "dimensions": dimensions,
        "time_range": time_range,
        "output_format": output_format,
        "search_results": all_search_results,
        "analysis_results": all_analysis_results,
        "change_events": all_change_events,
        "alerts": all_alerts,
        "report": final_report,
        "dashboard": {
            "report": final_report,
            "alerts": all_alerts,
            "cards": [
                report.get("feishu_card")
                for report in reports
                if report.get("feishu_card")
            ],
        },
        "error": "",
    }
