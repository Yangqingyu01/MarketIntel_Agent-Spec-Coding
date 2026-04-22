"""FastAPI routes for the MarketIntel MVP."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.orchestrator import run_analysis
from config import config
from tools.knowledge_base import load_competitors, save_competitor


router = APIRouter(prefix="/api")


class AnalyzeRequest(BaseModel):
    targets: List[str] = Field(..., min_length=1)
    dimensions: List[str] = Field(default_factory=lambda: list(config.default_dimensions))
    time_range: str = config.default_time_range


@router.post("/analyze")
async def analyze(req: AnalyzeRequest) -> Dict:
    result = run_analysis(
        targets=req.targets,
        dimensions=req.dimensions,
        time_range=req.time_range,
    )
    return {
        "task_id": result["task_id"],
        "report": result["report"],
        "alerts": result["alerts"],
        "intel_count": len(result["analysis_results"]),
    }


@router.get("/alerts")
async def get_alerts() -> Dict:
    return {"alerts": []}


@router.get("/config/competitors")
async def list_competitors() -> Dict:
    return load_competitors()


@router.post("/config/competitors")
async def add_competitor(competitor: Dict) -> Dict:
    save_competitor(competitor)
    return {"ok": True}
