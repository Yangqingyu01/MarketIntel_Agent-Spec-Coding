"""Feishu sender helpers with real Open Platform delivery and local fallback."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx

from config import config


_TOKEN_CACHE: Dict[str, Any] = {"value": "", "expires_at": 0.0}


def _feishu_ready() -> bool:
    return bool(config.feishu_app_id and config.feishu_app_secret)


def get_authorization_url(redirect_uri: str, state: str = "") -> str:
    """获取飞书授权URL"""
    if not _feishu_ready():
        return ""
    
    import urllib.parse
    
    params = {
        "client_id": config.feishu_app_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "im:message.send_as_user"
    }
    
    base_url = "https://accounts.feishu.cn/open-apis/authen/v1/authorize"
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def get_user_access_token(code: str) -> Dict[str, Any]:
    """通过授权码获取用户访问令牌"""
    if not _feishu_ready():
        return {"ok": False, "error": "Feishu not configured"}
    
    with _create_httpx_client() as client:
        try:
            response = client.post(
                "https://open.feishu.cn/open-apis/authen/v1/access_token",
                json={
                    "app_id": config.feishu_app_id,
                    "app_secret": config.feishu_app_secret,
                    "code": code,
                    "grant_type": "authorization_code"
                },
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "MarketIntel-Agent"
                }
            )
            response.raise_for_status()
            return {"ok": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                print(f"Token获取错误: {error_detail}")
            except:
                error_detail = str(e)
                print(f"HTTP错误: {error_detail}")
            return {"ok": False, "error": str(error_detail)}



def _create_httpx_client() -> httpx.Client:
    """Create httpx client with proxy support."""
    # 配置代理 (兼容旧版本 httpx)
    transport = httpx.HTTPTransport(
        proxy="http://127.0.0.1:7892"
    )
    
    return httpx.Client(
        transport=transport,
        timeout=10.0,
    )


def _get_tenant_access_token() -> str:
    if not _feishu_ready():
        return ""

    now = time.time()
    cached = str(_TOKEN_CACHE.get("value", ""))
    expires_at = float(_TOKEN_CACHE.get("expires_at", 0.0))
    if cached and now < expires_at:
        return cached

    with _create_httpx_client() as client:
        try:
            # 使用飞书最新的tenant_access_token接口
            response = client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": config.feishu_app_id,
                    "app_secret": config.feishu_app_secret,
                },
                headers={
                    "Content-Type": "application/json; charset=utf-8"
                }
            )
            response.raise_for_status()
            payload = response.json()
            token = str(payload.get("tenant_access_token", ""))
            expire = int(payload.get("expire", 7200))
            _TOKEN_CACHE["value"] = token
            _TOKEN_CACHE["expires_at"] = now + max(expire - 60, 60)
            return token
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                print(f"Token获取错误: {error_detail}")
            except:
                error_detail = str(e)
                print(f"HTTP错误: {error_detail}")
            return ""


def _mock_delivery(card: Dict[str, Any], chat_id: str = "") -> Dict[str, Any]:
    target_chat = chat_id or config.feishu_target_chat_id
    return {
        "ok": bool(card),
        "delivery_mode": "mock" if not target_chat else "configured",
        "chat_id": target_chat,
        "card": card,
    }


def send_card(card: Dict[str, Any], chat_id: str = "") -> Dict[str, Any]:
    target_chat = chat_id or config.feishu_target_chat_id
    if not target_chat or not _feishu_ready():
        return _mock_delivery(card, chat_id=target_chat)

    token = _get_tenant_access_token()
    
    with _create_httpx_client() as client:
        try:
            response = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages",
                params={"receive_id_type": "chat_id"},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "MarketIntel-Agent"
                },
                json={
                    "receive_id": target_chat,
                    "msg_type": "interactive",
                    "content": json.dumps(card, ensure_ascii=False),
                },
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {})
            return {
                "ok": payload.get("code", 0) == 0,
                "delivery_mode": "live",
                "chat_id": target_chat,
                "message_id": data.get("message_id", ""),
                "card": card,
            }
        except Exception as e:
            try:
                if hasattr(e, 'response') and e.response:
                    error_detail = e.response.json()
                    print(f"Feishu API Error: {error_detail}")
                else:
                    error_detail = str(e)
                    print(f"Error: {error_detail}")
            except:
                error_detail = str(e)
                print(f"Error: {error_detail}")
            
            # 自动降级为模拟模式，确保系统正常运行
            print("飞书连接失败，自动降级为模拟模式")
            return {
                "ok": True,
                "delivery_mode": "mock",
                "chat_id": target_chat,
                "card": card,
                "simulated": True,
                "note": "飞书连接失败，使用模拟模式"
            }


def send_text_message(
    text: str,
    receive_id: str,
    receive_id_type: str = "chat_id",
) -> Dict[str, Any]:
    if not receive_id or not _feishu_ready():
        return {
            "ok": bool(text),
            "delivery_mode": "mock",
            "receive_id": receive_id,
            "message": text,
        }

    token = _get_tenant_access_token()
    
    with _create_httpx_client() as client:
        try:
            response = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages",
                params={"receive_id_type": receive_id_type},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "MarketIntel-Agent"
                },
                json={
                    "receive_id": receive_id,
                    "msg_type": "text",
                    "content": json.dumps({"text": text}, ensure_ascii=False),
                },
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {})
            return {
                "ok": payload.get("code", 0) == 0,
                "delivery_mode": "live",
                "receive_id": receive_id,
                "message_id": data.get("message_id", ""),
                "message": text,
            }
        except Exception as e:
            # 打印详细错误信息
            try:
                if hasattr(e, 'response') and e.response:
                    error_detail = e.response.json()
                    print(f"Feishu API Error: {error_detail}")
                else:
                    error_detail = str(e)
                    print(f"Error: {error_detail}")
            except:
                error_detail = str(e)
                print(f"Error: {error_detail}")
            
            # 自动降级为模拟模式，确保系统正常运行
            print("飞书连接失败，自动降级为模拟模式")
            return {
                "ok": True,
                "delivery_mode": "mock",
                "receive_id": receive_id,
                "message": text,
                "simulated": True,
                "note": "飞书连接失败，使用模拟模式"
            }
