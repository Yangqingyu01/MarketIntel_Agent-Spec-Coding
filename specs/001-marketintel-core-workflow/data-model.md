# Data Model: 市场情报监测智能体核心工作流

## 1. 任务请求 TaskRequest

- **Purpose**: 表示一次由用户或定时任务发起的完整分析请求。
- **Key Fields**:
  - `task_id`: 唯一任务标识
  - `query`: 原始输入文本
  - `intent_type`: `TYPE_A | TYPE_B | TYPE_C | TYPE_D`
  - `targets`: 竞品名称列表
  - `dimensions`: 维度列表
  - `time_range`: 时间范围描述
  - `output_format`: `web | feishu | summary`
  - `execution_mode`: `sequential | parallel`
  - `status`: `created | running | completed | partial | failed`
  - `created_at`
  - `completed_at`
- **Validation Rules**:
  - `targets` 至少包含 1 个明确目标，除非任务被判定为市场扫描
  - `dimensions` 默认为五大标准维度
  - `output_format` 必须落在支持集合内

## 2. 竞品配置 CompetitorProfile

- **Purpose**: 表示工作空间中被监测的竞品及其配置。
- **Key Fields**:
  - `competitor_id`
  - `name`
  - `aliases`
  - `industry`
  - `search_keywords`
  - `monitoring_frequency`
  - `is_active`
  - `created_at`
  - `updated_at`
- **Relationships**:
  - 一个 `CompetitorProfile` 可以关联多个 `BaselineSnapshot`
  - 一个 `CompetitorProfile` 可以关联多个 `AlertEvent`
- **Validation Rules**:
  - `name` 必填
  - `monitoring_frequency` 限定为 `manual | daily | weekly`
  - `aliases` 和 `search_keywords` 可为空，但应支持数组格式

## 3. 原始搜索结果 RawSearchResult

- **Purpose**: 表示搜索与抓取阶段保留下来的候选公开来源条目。
- **Key Fields**:
  - `result_id`
  - `task_id`
  - `target`
  - `dimension`
  - `title`
  - `url`
  - `source_name`
  - `source_type`
  - `publish_date`
  - `crawl_date`
  - `content`
  - `full_text_available`
  - `initial_relevance`
- **Validation Rules**:
  - `url` 对于进入分析阶段的结果必须存在
  - `initial_relevance` 范围为 `0.0 - 1.0`
  - `content` 允许为空，但空内容不得阻塞其余结果处理

## 4. 结构化情报条目 IntelligenceItem

- **Purpose**: 表示从公开来源中提取并可供分析、报告、存储的标准情报单元。
- **Key Fields**:
  - `intel_id`
  - `task_id`
  - `company`
  - `dimension`
  - `content_type`: `fact | inference | unverified | noise`
  - `extracted_data`
  - `evidence_quote`
  - `entities`
  - `credibility`
  - `source_url`
  - `source_name`
  - `publish_date`
  - `crawl_date`
- **Validation Rules**:
  - `dimension` 只能归属一个标准维度
  - `credibility` 范围为 `0.0 - 1.0`
  - `fact` 和 `inference` 必须有 `evidence_quote`
  - `noise` 类型不进入核心报告和快照写入

## 5. 历史基线快照 BaselineSnapshot

- **Purpose**: 表示某竞品在某一时点的已验证情报基线。
- **Key Fields**:
  - `snapshot_id`
  - `company`
  - `snapshot_date`
  - `baseline_status`: `cold_start | compared`
  - `dimensions`
  - `overall_trend`
  - `overall_confidence`
  - `source_count`
- **Relationships**:
  - 一个快照由多条 `IntelligenceItem` 聚合得到
  - 一个快照可作为后续 `ChangeEvent` 的对比基线
- **Validation Rules**:
  - 首次快照允许 `baseline_status = cold_start`
  - 快照写入前必须去除低可信噪声项

## 6. 变化事件 ChangeEvent

- **Purpose**: 表示与历史基线相比识别出的实质性变化。
- **Key Fields**:
  - `change_id`
  - `company`
  - `dimension`
  - `change_type`
  - `description`
  - `severity_candidate`
  - `credibility`
  - `source_url`
  - `detected_at`
- **Validation Rules**:
  - 必须有证据支撑
  - `credibility >= 0.40` 才允许进入预警判断
  - 纯措辞变化不得生成事件

## 7. 预警事件 AlertEvent

- **Purpose**: 表示对外可消费的分级预警对象。
- **Key Fields**:
  - `alert_id`
  - `company`
  - `change_type`
  - `dimension`
  - `severity`: `high | medium | low`
  - `title`
  - `description`
  - `recommended_actions`
  - `push_timing`: `immediate | daily_digest | weekly_digest`
  - `detected_at`
  - `dedup_key`
- **Validation Rules**:
  - 同公司、同类型、相似描述、近 30 天内事件默认视为重复候选
  - `recommended_actions` 至少在 `high` 级预警中非空

## 8. 情报报告 IntelligenceReport

- **Purpose**: 表示面向 Web 和飞书消费的结果对象。
- **Key Fields**:
  - `report_id`
  - `task_id`
  - `report_type`
  - `target`
  - `generated_at`
  - `time_range_covered`
  - `executive_summary`
  - `dimensions_detail`
  - `changes_summary`
  - `chart_data`
  - `recommended_actions`
  - `data_quality_note`
  - `feishu_card`
- **Validation Rules**:
  - `executive_summary` 必须存在
  - `recommended_actions` 最多 5 条
  - 报告中的核心结论必须可映射回 `IntelligenceItem` 或 `ChangeEvent`

## 9. 状态流转

### 任务状态

`created -> running -> completed`

异常分支：

`created -> running -> partial`

`created -> running -> failed`

### 情报内容类型

`raw result -> fact | inference | unverified | noise`

- `noise` 在分析阶段被丢弃
- `unverified` 进入补充信息区，不进入核心结论

### 预警流转

`change candidate -> dedup check -> alert generated -> pushed or digested`

- 重复候选在 `dedup check` 阶段被标记为跳过
- `high` 级默认立即推送
