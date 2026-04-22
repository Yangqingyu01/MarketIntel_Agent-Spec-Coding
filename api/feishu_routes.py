"""Feishu webhook routes for lightweight MVP integration."""

from typing import Dict

from fastapi import APIRouter

from feishu.webhook import handle_webhook_event


router = APIRouter(prefix="/api/feishu")


@router.post("/webhook")
async def feishu_webhook(body: Dict) -> Dict:
    return handle_webhook_event(body)
