"""Web search client with Serper/Tavily fallback and normalized output."""

from __future__ import annotations

from datetime import date
from typing import Dict, List
from urllib.parse import urlparse

import httpx

from config import config


def extract_domain(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def _normalize_serper(items: List[Dict], query: str, limit: int) -> List[Dict]:
    results: List[Dict] = []
    today = date.today().isoformat()
    for item in items[:limit]:
        link = item.get("link", "")
        results.append(
            {
                "title": item.get("title", ""),
                "url": link,
                "snippet": item.get("snippet", ""),
                "source_name": extract_domain(link),
                "source_type": "search_result",
                "date": item.get("date", ""),
                "crawl_date": today,
                "query": query,
            }
        )
    return results


def _search_serper(query: str, num: int) -> List[Dict]:
    if not config.serper_api_key:
        return []
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": config.serper_api_key},
        json={"q": query, "num": num},
        timeout=config.fetch_timeout_seconds,
    )
    response.raise_for_status()
    organic = response.json().get("organic", [])
    return _normalize_serper(organic, query, num)


def _search_tavily(query: str, num: int) -> List[Dict]:
    if not config.tavily_api_key:
        return []
    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": config.tavily_api_key,
            "query": query,
            "max_results": num,
            "search_depth": "basic",
        },
        timeout=config.fetch_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json().get("results", [])
    today = date.today().isoformat()
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "source_name": extract_domain(item.get("url", "")),
            "source_type": "search_result",
            "date": item.get("published_date", ""),
            "crawl_date": today,
            "query": query,
        }
        for item in data[:num]
    ]


def _mock_results(query: str, num: int) -> List[Dict]:
    """Return deterministic local-only results when external search is unavailable."""
    today = date.today().isoformat()
    company = query.split()[0] if query.strip() else "竞品"
    snippets = [
        {
            "title": u"%s 发布智能协作更新" % company,
            "url": "https://example.com/%s/product-update" % company,
            "snippet": u"%s 今日发布新的智能协作能力，覆盖产品动态与会议场景。" % company,
        },
        {
            "title": u"%s 调整产品定价策略" % company,
            "url": "https://example.com/%s/pricing-update" % company,
            "snippet": u"%s 宣布套餐价格调整，并强化企业版能力。" % company,
        },
        {
            "title": u"%s 招聘与战略扩张信号" % company,
            "url": "https://example.com/%s/strategy-update" % company,
            "snippet": u"%s 正在扩招相关岗位，并提及新的市场合作方向。" % company,
        },
    ]
    results: List[Dict] = []
    for item in snippets[:num]:
        results.append(
            {
                "title": item["title"],
                "url": item["url"],
                "snippet": item["snippet"],
                "source_name": extract_domain(item["url"]),
                "source_type": "official",
                "date": today,
                "crawl_date": today,
                "query": query,
            }
        )
    return results


def search(query: str, num: int = 5) -> List[Dict]:
    """Execute a single query and return normalized results."""
    try:
        results = _search_serper(query, num)
        if results:
            return results
    except Exception:
        pass

    try:
        results = _search_tavily(query, num)
        if results:
            return results
    except Exception:
        pass

    return _mock_results(query, num)
