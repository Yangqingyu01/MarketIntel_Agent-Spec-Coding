# Implementation Plan: 市场情报监测智能体核心工作流

**Branch**: `001-marketintel-core-workflow` | **Date**: 2026-04-22 | **Spec**: [spec.md](C:\Users\杨清榆\PycharmProjects\MarketIntel_Agent\specs\001-marketintel-core-workflow\spec.md)  
**Input**: Feature specification from `/specs/001-marketintel-core-workflow/spec.md`

## Summary

本 feature 的目标是先打通一条可运行的市场情报分析主链路，再逐步扩展为具备多 Agent 编排、
历史基线对比、预警分级、Web 展示和飞书集成的完整系统。实现策略遵循“先跑通、再扩展、
最后打磨”的顺序：先完成 CLI 可演示的搜索→抓取→提取→存储→报告闭环，再收敛为
LangGraph 编排的 Agent 工作流，最后补齐 Web Dashboard、配置中心和飞书触达。

## Technical Context

**Language/Version**: Python 3.11+ for backend and agents; TypeScript + React 18 for frontend  
**Primary Dependencies**: FastAPI, Uvicorn, LangGraph, LangChain/OpenAI-compatible SDK, ChromaDB, SQLAlchemy, Pydantic v2, httpx, BeautifulSoup4, APScheduler, Feishu/Lark SDK, React, Vite, Tailwind CSS, Recharts  
**Storage**: ChromaDB for vectorized intelligence memory, SQLite for structured app state and alerts, JSON files for competitor configuration and local bootstrap data  
**Testing**: pytest for backend and workflow validation, lightweight script-based smoke tests for external integrations, frontend manual acceptance checks during MVP  
**Target Platform**: Local development on Windows/macOS, browser-based dashboard, Feishu bot/webhook integration, deployable to a single Linux server later  
**Project Type**: Full-stack multi-agent web application with scheduled jobs and chat/bot integration  
**Performance Goals**: Single-competitor analysis can complete within 30-90 seconds under normal source availability; progress is visible during execution; repeated analysis can reuse history for faster comparison insight generation  
**Constraints**: Only public and lawful sources; all fact statements must retain source traceability; Chinese-first output; graceful degradation on search/fetch/extraction failures; design must remain demo-friendly for academic presentation  
**Scale/Scope**: MVP scope targets tens of monitored competitors per workspace, daily or weekly monitoring cadence, single-tenant demo deployment, and one primary user-facing dashboard plus Feishu notification path

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Public, lawful, and traceable sources only: PASS. The design explicitly limits collection to public search and fetch flows, records source URLs, and rejects private or unauthorized data.
- Source metadata and credibility preservation: PASS. Search, extraction, storage, report, and alert artifacts all retain source URL, dates, credibility, and content type.
- Fact / inference / unverified separation: PASS. The workflow requires typed content classification during analysis and keeps low-confidence items outside core conclusions.
- Role boundaries and structured handoffs: PASS. Orchestrator, Search, Analysis, Report, and Alert stages have separate contracts and no stage is allowed to bypass the handoff chain.
- Change detection and deduplication behavior: PASS. The plan includes baseline snapshots, change events, alert history, and duplicate suppression logic.
- Concise, decision-oriented Chinese output: PASS. Reports and cards lead with executive summary, concrete actions, and Chinese-first display requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-marketintel-core-workflow/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api-contract.yaml
│   └── agent-io.md
└── tasks.md
```

### Source Code (repository root)

```text
agents/
├── __init__.py
├── orchestrator.py
├── search_agent.py
├── analysis_agent.py
├── report_agent.py
├── alert_agent.py
└── state.py

tools/
├── __init__.py
├── web_search.py
├── web_fetcher.py
├── data_extractor.py
├── knowledge_base.py
├── chart_generator.py
└── report_builder.py

api/
├── __init__.py
├── routes.py
└── feishu_routes.py

feishu/
├── __init__.py
├── bot.py
├── cards.py
├── sender.py
└── webhook.py

scheduler/
├── __init__.py
├── jobs.py
└── runner.py

data/
├── vector_store/
├── intel_history/
└── config/

web/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── package.json

tests/
├── contract/
├── integration/
└── unit/

main.py
config.py
requirements.txt
```

**Structure Decision**: 采用单一仓库的全栈结构。后端 Agent、工具、API、调度与飞书集成共用一套
Python 代码库，前端作为 `web/` 子目录独立构建。这比拆分多仓或前后端完全分离更适合当前
MVP 节奏，也便于按“工具链路 → Agent 工作流 → Web 展示 → 飞书触达”的顺序渐进交付。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
