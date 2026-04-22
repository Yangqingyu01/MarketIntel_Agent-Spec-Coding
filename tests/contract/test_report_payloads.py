from __future__ import annotations

from agents.report_agent import build_report


def test_report_payload_contains_summary_chart_and_card() -> None:
    report = build_report(
        "TASK-1",
        "飞书",
        [
            {
                "dimension": "product",
                "extracted_data": "飞书上线 AI 会议纪要",
                "crawl_date": "2026-04-22",
            },
            {
                "dimension": "strategy",
                "extracted_data": "飞书强化海外合作",
                "crawl_date": "2026-04-22",
            },
        ],
        baseline={"snapshot_id": "SNP-1", "items": []},
        alerts=[
            {
                "description": "飞书在 product 维度出现新的公开信号：飞书上线 AI 会议纪要",
            }
        ],
    )
    assert report["report_type"] == "single"
    assert report["chart_data"]
    assert report["recommended_actions"]
    assert report["feishu_card"]["header"]["title"]["content"] == "飞书 情报摘要"

