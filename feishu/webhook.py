"""Feishu webhook handling helpers for real event subscription callbacks."""

from __future__ import annotations

import json
import re
from typing import Any, Dict

from agents.orchestrator import run_analysis
from config import config
from feishu.sender import send_card, send_text_message


def _token_valid(body: Dict[str, Any]) -> bool:
    expected = config.feishu_verification_token.strip()
    if not expected:
        return True
    return str(body.get("token", "")).strip() == expected


def _extract_text_message(raw_content: Any) -> str:
    if isinstance(raw_content, dict):
        return str(raw_content.get("text", "")).strip()
    if isinstance(raw_content, str):
        try:
            payload = json.loads(raw_content)
        except Exception:
            return raw_content.strip()
        return str(payload.get("text", "")).strip()
    return ""


def _parse_command(text: str) -> Dict[str, str]:
    normalized = text.strip()
    if not normalized:
        return {"command": "", "target": ""}

    match = re.match(r"^(?:\u5206\u6790|analyze)\s+(.+)$", normalized, re.IGNORECASE)
    if match:
        return {"command": "analyze", "target": match.group(1).strip()}

    if normalized.lower() in {"help", "\u5e2e\u52a9"}:
        return {"command": "help", "target": ""}

    return {"command": "", "target": normalized}


def _help_message() -> str:
    return (
        "\u53ef\u4ee5\u76f4\u63a5\u53d1\u9001\uff1a\n"
        "\u5206\u6790 \u98de\u4e66\n"
        "Analyze Feishu\n"
        "\u6211\u4f1a\u8fd4\u56de\u8be5\u7ade\u54c1\u7684\u5e02\u573a\u60c5\u62a5\u6458\u8981\u4e0e\u9884\u8b66\u7ed3\u679c\u3002"
    )


def _handle_url_verification(body: Dict[str, Any]) -> Dict[str, Any]:
    if not _token_valid(body):
        return {"challenge": "", "msg": "invalid verification token"}
    return {"challenge": body.get("challenge", "")}


def _safe_help_reply(chat_id: str) -> Dict[str, Any]:
    try:
        delivery = send_text_message(_help_message(), chat_id)
    except Exception as exc:
        return {"ok": False, "handled": False, "reason": "reply_failed", "detail": str(exc)}
    return {"ok": True, "handled": True, "reply": delivery}


def _handle_message_event(body: Dict[str, Any]) -> Dict[str, Any]:
    event = body.get("event", {}) or {}
    sender = event.get("sender", {}) or {}
    if sender.get("sender_type") == "app":
        return {"ok": True, "handled": False, "reason": "bot_message_ignored"}

    message = event.get("message", {}) or {}
    chat_id = str(message.get("chat_id", "")).strip()
    if not chat_id:
        return {"ok": False, "handled": False, "reason": "missing_chat_id"}

    if str(message.get("message_type", "")).strip() != "text":
        return _safe_help_reply(chat_id)

    text = _extract_text_message(message.get("content", ""))
    command = _parse_command(text)

    if command["command"] == "help":
        return _safe_help_reply(chat_id)

    if command["command"] == "analyze" and command["target"]:
        try:
            ack = send_text_message(
                "\u5df2\u6536\u5230\u5206\u6790\u8bf7\u6c42\uff0c\u6b63\u5728\u6574\u7406\u516c\u5f00\u6765\u6e90\u60c5\u62a5\uff0c\u8bf7\u7a0d\u5019\u3002",
                chat_id,
            )
        except Exception as exc:
            return {"ok": False, "handled": False, "reason": "reply_failed", "detail": str(exc)}

        result = run_analysis(
            [command["target"]],
            dimensions=list(config.default_dimensions),
            output_format="feishu",
        )
        report = result.get("report", {})
        card = report.get("feishu_card")
        try:
            delivery = (
                send_card(card, chat_id=chat_id)
                if card
                else send_text_message(
                    report.get("executive_summary", "\u5206\u6790\u5df2\u5b8c\u6210\u3002"),
                    chat_id,
                )
            )
        except Exception as exc:
            fallback_text = report.get("executive_summary", "\u5206\u6790\u5df2\u5b8c\u6210\u3002")
            return {
                "ok": False,
                "handled": False,
                "reason": "delivery_failed",
                "detail": str(exc),
                "fallback_text": fallback_text,
            }
        return {
            "ok": True,
            "handled": True,
            "command": "analyze",
            "target": command["target"],
            "ack": ack,
            "reply": delivery,
        }

    return _safe_help_reply(chat_id)


def handle_webhook_event(body: Dict[str, Any]) -> Dict[str, Any]:
    if body.get("encrypt"):
        return {
            "ok": False,
            "handled": False,
            "reason": "encrypted_events_not_supported",
            "detail": "Disable Feishu event encryption or implement FEISHU_ENCRYPT_KEY decryption first.",
        }

    if body.get("type") == "url_verification":
        return _handle_url_verification(body)

    event_type = str((body.get("header") or {}).get("event_type", "")).strip()
    if event_type == "im.message.receive_v1":
        if not _token_valid(body):
            return {"ok": False, "handled": False, "reason": "invalid_verification_token"}
        return _handle_message_event(body)

    return {"ok": True, "handled": False, "received": bool(body)}
