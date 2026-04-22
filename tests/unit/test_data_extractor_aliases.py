from __future__ import annotations

from tools.data_extractor import extract_intel


def test_extract_intel_accepts_chinese_alias_for_english_target() -> None:
    content = "飞书是什么？能做什么？2026开年飞书产品功能与应用场景全解析！"

    extracted = extract_intel(content, "Feishu")

    assert extracted is not None
    assert extracted["company"] == "Feishu"
    assert extracted["dimension"] == "product"


def test_extract_intel_accepts_english_alias_for_chinese_target() -> None:
    content = "DingTalk launches a new AI meeting workspace on 2026-04-22."

    extracted = extract_intel(content, "钉钉")

    assert extracted is not None
    assert extracted["company"] == "钉钉"
