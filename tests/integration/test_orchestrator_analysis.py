from __future__ import annotations

from agents.orchestrator import run_analysis


def test_orchestrator_returns_expected_shape_for_single_target() -> None:
    result = run_analysis(["飞书"], dimensions=["product"])
    assert result["task_id"]
    assert result["report"]["report_id"]
    assert isinstance(result["analysis_results"], list)
    assert result["analysis_results"]
    assert result["report"]["target"] == "飞书"


def test_orchestrator_supports_multi_target_analysis() -> None:
    result = run_analysis(["飞书", "钉钉"], dimensions=["product", "strategy"])
    assert result["intent_type"] == "TYPE_B"
    assert result["report"]["report_type"] == "comparison"
    assert len(result["targets"]) == 2
