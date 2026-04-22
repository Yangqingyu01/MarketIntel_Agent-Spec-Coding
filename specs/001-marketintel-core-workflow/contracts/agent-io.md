# Agent I/O Contract

## Orchestrator -> Search Agent

```json
{
  "target": "飞书",
  "aliases": ["Lark", "字节跳动飞书"],
  "dimensions": ["product", "pricing", "funding", "talent", "strategy"],
  "time_range": "近3个月",
  "search_keywords": ["企业协作", "AI办公", "智能文档"]
}
```

## Search Agent -> Analysis Agent

```json
{
  "task_id": "TASK-xxx",
  "target": "飞书",
  "search_completed_at": "2026-04-21T09:30:00Z",
  "dimensions_coverage": {
    "product": 5,
    "pricing": 3,
    "funding": 4,
    "talent": 2,
    "strategy": 5
  },
  "results": [],
  "empty_dimensions": []
}
```

## Analysis Agent -> Report Agent / Alert Agent

```json
{
  "task_id": "TASK-xxx",
  "company": "飞书",
  "analysis_completed_at": "2026-04-21T09:45:00Z",
  "baseline_status": "compared",
  "overall_trend": "aggressive_expansion",
  "overall_confidence": 0.82,
  "dimensions": {},
  "changes_detected": [],
  "key_insights": [],
  "low_credibility_items": []
}
```

## Alert Agent -> Orchestrator

```json
{
  "task_id": "TASK-xxx",
  "alerts": [],
  "immediate_push_required": false,
  "highest_severity": "low"
}
```

## Report Agent -> Orchestrator

```json
{
  "report_id": "RPT-TASK-xxx",
  "report_type": "single",
  "target": "飞书",
  "generated_at": "2026-04-21T10:00:00Z",
  "executive_summary": "本次分析覆盖飞书近3个月动态...",
  "dimensions_detail": {},
  "chart_data": [],
  "recommended_actions": [],
  "feishu_card": {}
}
```

## Contract Rules

- 所有 handoff 都必须包含 `task_id` 或等价任务上下文。
- Search 阶段不得输出洞察或预警结论。
- Analysis 阶段必须输出 `content_type`、`credibility` 和可追溯证据。
- Report 阶段不得修改分析事实，只负责格式转换与摘要组织。
- Alert 阶段必须基于变化事件和去重结果生成，不得绕过 Analysis 直接构造预警。
