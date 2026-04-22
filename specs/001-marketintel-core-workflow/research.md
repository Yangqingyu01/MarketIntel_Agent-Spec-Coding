# Research: 市场情报监测智能体核心工作流

## Decision 1: 后端采用 Python 3.11+ 作为统一实现语言

- **Decision**: 将后端、Agent 工作流、调度器、飞书集成统一建立在 Python 3.11+ 上。
- **Rationale**: 你提供的计划文档已经围绕 FastAPI、LangGraph、ChromaDB、OpenAI SDK 和
  APScheduler 给出了完整实现路径，这些依赖在 Python 3.11+ 上兼容性与维护体验更稳。
  此外，Spec Kit 本身也要求 3.11+，与项目环境目标保持一致更省心。
- **Alternatives considered**:
  - Python 3.8: 本机当前可用，但对新版本依赖支持偏弱，会增加后续兼容负担。
  - Node.js-only backend: 不适合直接承接你提供的 Agent 设计和工具链规划。

## Decision 2: 先做 CLI/脚本级闭环，再升级到 LangGraph 编排

- **Decision**: Phase 1 先用普通函数打通搜索、抓取、提取、存储、检索闭环；Phase 2 再迁移为
  LangGraph 状态流。
- **Rationale**: 这与计划文档“先跑通一条链路，再完善所有 Agent”的原则一致，可以最早暴露
  搜索 API、抓取、提取、存储等外部依赖问题，避免一开始就在图编排层调试。
- **Alternatives considered**:
  - 一开始直接上 LangGraph: 架构更完整，但会把环境问题和编排问题缠在一起，定位成本高。

## Decision 3: 记忆层采用 ChromaDB + SQLite + JSON 配置 的分层组合

- **Decision**: 向量记忆使用 ChromaDB，结构化状态使用 SQLite，竞品配置与本地引导数据使用
  JSON 文件。
- **Rationale**: 这正好对应“历史语义检索、预警记录/任务状态、易编辑配置”三类需求。
  该组合便于本地开发、答辩演示、快速备份，也适合 MVP 阶段低运维复杂度。
- **Alternatives considered**:
  - 只用 SQLite: 结构化方便，但不适合相似语义检索和快照召回。
  - 只用向量库: 不适合管理预警去重、竞品配置和结构化状态。
  - PostgreSQL + pgvector: 更完整，但对当前演示项目属于过度建设。

## Decision 4: 搜索与网页抓取采用“搜索 API + 定向抓取 + 降级摘要”模式

- **Decision**: 先走搜索 API 获取候选结果，再对高价值页面执行抓取；抓取失败时保留搜索摘要并
  明确标记降级。
- **Rationale**: 这满足宪章对合法公开来源、可追溯性和 graceful degradation 的要求，也与
  你提供的 Search Agent SOP 完全一致。
- **Alternatives considered**:
  - 纯搜索摘要: 实现简单，但证据质量和详情不足，不利于可信度评分。
  - 全量抓取所有结果: 成本高、稳定性差，也容易触发无意义抓取。

## Decision 5: 可信度评分在分析阶段统一计算，而不是分散在搜索和报告阶段

- **Decision**: 来源评级、交叉验证、时效修正和最终可信度统一由 Analysis Agent 负责。
- **Rationale**: 搜索阶段只做召回和初筛，报告阶段只做表达，分析阶段最适合承担“事实/推断/
  待验证”分类和评分逻辑，角色边界最清晰。
- **Alternatives considered**:
  - 搜索阶段先粗打分: 会把采集与分析耦合，降低可解释性。
  - 报告阶段打分: 太晚，不能指导变化检测和预警分级。

## Decision 6: Web 端与飞书端共享结构化报告源，但维持不同输出契约

- **Decision**: 分析与报告生成统一的中间报告对象，再分别映射为 Web 响应和飞书卡片。
- **Rationale**: 这样既能复用同一份情报结果，又能保留不同终端对信息密度、格式和交互能力的
  不同要求，符合报告 Agent 的职责边界。
- **Alternatives considered**:
  - 直接为每个终端单独生成分析结果: 容易造成内容漂移和维护重复。

## Decision 7: MVP 优先级遵循“核心链路 → Agent 编排 → Web 演示 → 飞书加分项”

- **Decision**: 开发顺序严格按你给的 Plan 文档推进：Phase 0 环境、Phase 1 核心链路、
  Phase 2 Agent、Phase 3 Web、Phase 4 飞书、Phase 5 打磨。
- **Rationale**: 这条路径最适合答辩导向项目，能够最早形成可演示结果，并把高风险项前置。
- **Alternatives considered**:
  - 先做前端或飞书: 演示观感好，但核心价值链未打通前收益很低。

## Decision 8: AGENTS.md 只保留计划引用，而不复制实现细节

- **Decision**: 在 `AGENTS.md` 中维护当前计划文件引用，让后续 Agent 通过计划获取实现上下文。
- **Rationale**: 这是 Spec Kit 默认协作方式，避免同一实现计划在多个文件中复制和漂移。
- **Alternatives considered**:
  - 在 AGENTS.md 中复制整份计划: 信息冗余，后续更新容易不一致。
