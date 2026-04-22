"""HTML fetching with basic cleanup and graceful degradation."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional

from config import config


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch(url: str, timeout: Optional[int] = None) -> Dict:
    """Fetch a page and extract readable text content."""
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
            }

        return {"url": url, "content": content, "success": True, "error": ""}
    except httpx.TimeoutException:
        return {"url": url, "content": "", "success": False, "error": "请求超时"}
    except Exception as exc:
        return {"url": url, "content": "", "success": False, "error": str(exc)}
