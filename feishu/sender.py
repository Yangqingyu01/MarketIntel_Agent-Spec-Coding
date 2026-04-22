"""Feishu sender helpers with a safe local fallback."""

from __future__ import annotations

from typing import Any, Dict

from config import config


def send_card(card: Dict[str, Any], chat_id: str = "") -> Dict[str, Any]:
    target_chat = chat_id or config.feishu_target_chat_id
    return {
        "ok": bool(card),
        "delivery_mode": "mock" if not target_chat else "configured",
        "chat_id": target_chat,
        "card": card,
    }
