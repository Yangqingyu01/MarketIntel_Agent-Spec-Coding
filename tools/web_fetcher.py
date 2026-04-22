"""HTML fetching with basic cleanup and graceful degradation."""

from __future__ import annotations

from typing import Dict, Optional
from urllib.parse import unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from config import config
from tools.report_builder import degradation_note


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch(url: str, timeout: Optional[int] = None) -> Dict:
    """Fetch a page and extract readable text content."""
    if url.startswith("https://example.com/"):
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split("/") if part]
        company = unquote(path_parts[0]) if path_parts else "竞品"
        content = (
            "示例公开页面\n"
            "该页面仅用于本地 smoke / integration 测试。\n"
            "{company} 发布了新的产品、定价、招聘和战略扩张信息。\n"
            "2026-04-22"
        ).format(company=company)
        return {
            "url": url,
            "content": content,
            "success": True,
            "error": "",
            "fallback_used": True,
            "compliance_note": "本地模拟页面，仅用于演示公开来源处理流程。",
        }

    try:
        response = httpx.get(
            url,
            headers=HEADERS,
            timeout=timeout or config.fetch_timeout_seconds,
            follow_redirects=True,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["nav", "footer", "script", "style", "aside", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)
        if len(content) > 8000:
            content = content[:8000] + "\n[内容已截断]"

        if not content:
            return {
                "url": url,
                "content": "",
                "success": False,
                "error": "页面内容为空",
                "degradation_note": degradation_note("页面抓取成功但无可读正文", "低"),
            }

        return {
            "url": url,
            "content": content,
            "success": True,
            "error": "",
            "fallback_used": False,
            "compliance_note": "仅处理公开页面内容，请在分析阶段结合来源可信度判断。",
        }
    except httpx.TimeoutException:
        return {
            "url": url,
            "content": "",
            "success": False,
            "error": "请求超时",
            "degradation_note": degradation_note("页面抓取超时，后续将回退到搜索摘要", "中"),
        }
    except Exception as exc:
        return {
            "url": url,
            "content": "",
            "success": False,
            "error": str(exc),
            "degradation_note": degradation_note("页面抓取失败，后续将回退到搜索摘要", "中"),
        }
