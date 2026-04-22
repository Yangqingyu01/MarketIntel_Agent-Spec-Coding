"""Feishu webhook handling helpers."""

from __future__ import annotations

from typing import Any, Dict

from agents.orchestrator import run_analysis


def handle_webhook_event(body: Dict[str, Any]) -> Dict[str, Any]:
    command = body.get("command", "")
    target = body.get("target", "")
    if command == "analyze" and target:
        result = run_analysis([target], dimensions=body.get("dimensions") or ["product", "strategy"])
        return {
            "ok": True,
            "handled": True,
            "report": result.get("report", {}),
            "alerts": result.get("alerts", []),
        }
    return {"ok": True, "handled": False, "received": bool(body)}
