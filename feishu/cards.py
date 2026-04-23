"""Feishu card builders for reports and alert digests."""

from __future__ import annotations

from typing import Any, Dict, List


def build_report_card(report: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    target = str(report.get("target", "竞品") or "竞品")
    executive_summary = str(report.get("executive_summary", "") or "").strip()
    changes_summary = str(report.get("changes_summary", "") or "").strip()

    if not executive_summary:
        executive_summary = f"{target} 的分析已完成，请在工作台查看结构化结果。"
    if not changes_summary:
        changes_summary = "当前没有补充变化摘要，建议打开工作台查看详情。"

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"{target} 情报摘要"}
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": executive_summary},
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "预警数：**{count}**\n变化摘要：{summary}".format(
                        count=len(alerts),
                        summary=changes_summary,
                    ),
                },
            },
        ],
    }


def build_digest_card(summary: Dict[str, Any]) -> Dict[str, Any]:
    summary_type = str(summary.get("summary_type", "daily"))
    headline = str(summary.get("headline", "") or "").strip()
    if not headline:
        headline = "当前暂无可展示的自动摘要内容。"

    period_label = "每日" if summary_type == "daily" else "每周"
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"{period_label}监测摘要"}
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": headline},
            }
        ],
    }
