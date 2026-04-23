"""Test Feishu token handling."""

import json
import httpx

# 直接使用用户提供的令牌
token = 'u-e.t2zJ3Sh2KWS8njB2c.VWg57dv44liVVMGaYQiywCbz'
chat_id = 'oc_421d71f989607779be779e4813a7e7b1'

# 配置代理
transport = httpx.HTTPTransport(
    proxy="http://127.0.0.1:7892"
)

with httpx.Client(transport=transport, timeout=10.0) as client:
    try:
        # 直接测试发送消息
        response = client.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            params={"receive_id_type": "chat_id"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            },
            json={
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": "测试消息"}, ensure_ascii=False),
            },
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
