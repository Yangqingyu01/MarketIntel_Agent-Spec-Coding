"""LLM-backed intelligence extraction with deterministic fallback heuristics."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from config import config, llm_client


EXTRACT_PROMPT = """你是一名专业情报分析师。请从以下文章中提取关于「{company}」的结构化情报。

文章内容：
{content}

请严格输出 JSON，字段如下：
{{
  "company": "{company}",
  "dimension": "product | pricing | funding | talent | strategy",
  "content_type": "fact | inference | unverified",
  "extracted_data": "一句话核心情报，不超过50字",
  "evidence_quote": "原文中支撑上述结论的原句，不超过100字",
  "entities": {{
    "company": [],
    "person": [],
    "product": [],
    "amount": [],
    "date": []
  }}
}}

如果文章与该公司无关，请输出 {{"skip": true}}。
"""


def _infer_dimension(content: str) -> str:
    content_lower = content.lower()
    if any(token in content_lower for token in ["pricing", "价格", "定价", "套餐"]):
        return "pricing"
    if any(token in content_lower for token in ["融资", "funding", "投资", "估值"]):
        return "funding"
    if any(token in content_lower for token in ["招聘", "高管", "任命", "离职"]):
        return "talent"
    if any(token in content_lower for token in ["合作", "并购", "扩张", "战略"]):
        return "strategy"
    return "product"


def _extract_dates(content: str) -> list[str]:
    return re.findall(r"\d{4}-\d{2}-\d{2}", content)[:3]


def _heuristic_extract(content: str, company: str) -> Optional[Dict[str, Any]]:
    if company not in content:
        return None
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    excerpt = lines[0][:100] if lines else content[:100]
    return {
        "company": company,
        "dimension": _infer_dimension(content),
        "content_type": "fact",
        "extracted_data": excerpt[:50],
        "evidence_quote": excerpt[:100],
        "entities": {
            "company": [company],
            "person": [],
            "product": [],
            "amount": re.findall(r"[¥$]\s?\d+(?:\.\d+)?", content)[:3],
            "date": _extract_dates(content),
        },
    }


def extract_intel(content: str, company: str) -> Optional[Dict[str, Any]]:
    """Extract structured intelligence or return None if irrelevant."""
    if not content.strip():
        return None

    if not config.llm_api_key:
        return _heuristic_extract(content, company)

    prompt = EXTRACT_PROMPT.format(company=company, content=content[:4000])
    try:
        response = llm_client.chat.completions.create(
            model=config.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        if result.get("skip"):
            return None
        return result
    except Exception:
        return _heuristic_extract(content, company)
