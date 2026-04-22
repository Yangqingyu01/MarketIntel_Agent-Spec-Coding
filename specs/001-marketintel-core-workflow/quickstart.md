# Quickstart: 市场情报监测智能体核心工作流

## 1. 准备环境

1. 使用 Python `3.11+` 创建并激活虚拟环境
2. 安装后端依赖：`pip install -r requirements.txt`
3. 进入 `web/` 执行 `npm install`
4. 复制 `.env.example` 为 `.env`

可选能力：

- LLM：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`
- 搜索：`SERPER_API_KEY` 或 `TAVILY_API_KEY`
- 飞书：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_TARGET_CHAT_ID`

如果不配置搜索或 LLM，项目仍可通过本地回退数据完成演示。

## 2. 快速验证

推荐先跑轻量测试：

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/smoke/test_basic.py -q
python -m pytest tests/integration/test_pipeline.py -q
python -m pytest tests/contract/test_analyze_api.py -q
```

如需验证预警和摘要：

```powershell
python -m pytest tests/integration/test_alert_dedup.py -q
python -m pytest tests/integration/test_scheduler_summary.py -q
python -m pytest tests/contract/test_report_payloads.py -q
```

## 3. 启动 API

```powershell
python -m uvicorn main:app --reload
```

验证：

- `GET /health`
- `POST /api/analyze`
- `GET /api/alerts`
- `POST /api/feishu/webhook`

## 4. 演示主链路

1. 对 `飞书` 发起一次分析
2. 再对同一目标重复分析，展示变化预警与去重
3. 查看返回的 `report.executive_summary`、`changes_summary`、`chart_data`
4. 切换多竞品分析，观察 comparison report

## 5. 演示前端

当前前端骨架文件：

- `web/src/components/ChatInterface.tsx`
- `web/src/components/AlertPanel.tsx`
- `web/src/pages/ConfigPage.tsx`
- `web/src/services/api.ts`

建议在接入 Vite 页面时展示：

- 分析输入与进度状态
- 预警面板
- 竞品配置中心
- 报告摘要与图表

## 6. 演示调度与飞书

- `scheduler/jobs.py`：daily / weekly summary
- `scheduler/runner.py`：scheduler 描述与任务注册
- `feishu/cards.py`：卡片结构
- `feishu/webhook.py`：webhook 分析入口
- `feishu/sender.py`：安全 mock 发送

## 7. 注意事项

- 所有结果仅应基于公开、合法来源
- 如果命中本地 mock 回退，输出会带数据质量说明
- 本地演示数据仅用于流程验证，不代表真实市场结论
