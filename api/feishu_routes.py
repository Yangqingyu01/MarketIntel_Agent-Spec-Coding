"""Feishu webhook routes placeholder for later integration."""

from typing import Dict

from fastapi import APIRouter


router = APIRouter(prefix="/api/feishu")


@router.post("/webhook")
async def feishu_webhook(body: Dict) -> Dict:
    return {"ok": True, "received": bool(body)}
