"""Application entry for the MarketIntel API."""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.feishu_routes import router as feishu_router
from api.routes import router as api_router
from scheduler.runner import describe_scheduler
from tools.knowledge_base import initialize_storage


app = FastAPI(title="MarketIntel API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(feishu_router)


@app.on_event("startup")
async def startup() -> None:
    initialize_storage()


@app.get("/health")
async def health() -> Dict:
    return {
        "status": "ok",
        "service": "MarketIntel API",
        "version": "0.1.0",
        "scheduler": describe_scheduler(),
    }
