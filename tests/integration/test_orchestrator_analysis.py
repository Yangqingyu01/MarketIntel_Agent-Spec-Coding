from __future__ import annotations

from agents.orchestrator import run_analysis


def test_orchestrator_returns_expected_shape() -> None:
    result = run_analysis(["飞书"], dimensions=["product"])
    assert result["task_id"]
    assert result["report"]["report_id"]
    assert isinstance(result["analysis_results"], list)
