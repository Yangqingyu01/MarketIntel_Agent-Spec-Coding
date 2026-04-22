# MarketIntel Agent

面向公开来源市场情报监测的多 Agent 演示项目，支持竞品分析、变化预警、报告摘要、Web 面板和飞书输出。

## 当前能力

- 单竞品和多竞品分析
- 历史快照对比与变化预警去重
- 管理层摘要、图表数据和周期汇总
- FastAPI API、前端组件骨架、飞书卡片和 webhook
- 本地演示回退模式：外部搜索或抓取不可用时仍可完成演示链路

## 环境准备

1. 推荐 Python `3.11+`，当前代码也临时兼容 Python `3.8`
2. 安装后端依赖：`pip install -r requirements.txt`
3. 安装前端依赖：`cd web` 后执行 `npm install`
4. 复制 [`.env.example`](C:\Users\杨清榆\PycharmProjects\MarketIntel_Agent\.env.example) 为 `.env`

最小可选配置：

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `SERPER_API_KEY` 或 `TAVILY_API_KEY`
- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_TARGET_CHAT_ID`

## 本地启动

后端：

```powershell
python -m uvicorn main:app --reload
```

单文件快速测试建议关闭 pytest 插件自动加载：

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/smoke/test_basic.py -q
```

## 推荐演示流程

1. 调 `POST /api/analyze` 运行一次单竞品分析
2. 再次分析同一竞品，展示变化检测和 `/api/alerts`
3. 展示报告中的 `executive_summary`、`changes_summary`、`chart_data`
4. 演示 `scheduler/jobs.py` 的 daily/weekly summary
5. 演示飞书 webhook 和卡片结构

## 已验证的关键测试

- `tests/smoke/test_basic.py`
- `tests/integration/test_pipeline.py`
- `tests/integration/test_alert_dedup.py`
- `tests/integration/test_scheduler_summary.py`
- `tests/contract/test_analyze_api.py`
- `tests/contract/test_alert_payloads.py`
- `tests/contract/test_report_payloads.py`

## 可靠性说明

- 只面向公开、合法来源
- 每条结论都应结合 `source_url`、`credibility` 和 `content_type` 使用
- 当搜索或抓取回退到本地 mock 数据时，结果会带降级说明，不应视为真实线上结论

## Spec Kit 工作流

本项目已接入 GitHub `spec-kit`，可继续在 Codex 中按以下顺序工作：

1. `$speckit-constitution`
2. `$speckit-specify`
3. `$speckit-plan`
4. `$speckit-tasks`
5. `$speckit-implement`
