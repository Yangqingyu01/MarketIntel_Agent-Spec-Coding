"""Test Feishu message sending with provided token."""

from feishu.sender import send_text_message

# 测试发送文本消息
result = send_text_message("测试消息", "oc_421d71f989607779be779e4813a7e7b1")
print("发送结果:")
print(result)

# 测试发送卡片消息
from feishu.cards import build_report_card

report = {
    "target": "飞书",
    "executive_summary": "这是一份测试报告摘要",
    "changes_summary": "暂无变化"
}
alerts = []
card = build_report_card(report, alerts)

from feishu.sender import send_card
card_result = send_card(card, "oc_421d71f989607779be779e4813a7e7b1")
print("\n卡片发送结果:")
print(card_result)