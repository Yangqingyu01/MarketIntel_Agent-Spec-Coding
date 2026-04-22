"""Feishu webhook routes placeholder for later integration."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/feishu")


@router.post("/webhook")
async def feishu_webhook(body: dict) -> dict:
    return {"ok": True, "received": bool(body)}
