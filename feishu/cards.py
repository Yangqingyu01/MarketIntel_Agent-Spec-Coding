"""Feishu card builders for reports and alert digests."""

from __future__ import annotations

from typing import Any, Dict, List


def build_report_card(report: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "{target} 情报摘要".format(target=report.get("target", "竞品"))}
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": report.get("executive_summary", "")},
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "预警数：**{count}**\n变化摘要：{summary}".format(
                        count=len(alerts),
                        summary=report.get("changes_summary", "暂无"),
                    ),
                },
            },
        ],
    }


def build_digest_card(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "{kind}监测摘要".format(kind="每日" if summary.get("summary_type") == "daily" else "每周")}
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": summary.get("headline", "")},
            }
        ],
    }
