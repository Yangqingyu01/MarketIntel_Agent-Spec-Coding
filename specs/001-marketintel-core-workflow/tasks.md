# Tasks: 市场情报监测智能体核心工作流

**Input**: Design documents from `/specs/001-marketintel-core-workflow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include smoke, integration, and contract validation tasks because the quickstart and plan explicitly require staged validation of the MVP chain and API behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `agents/`, `tools/`, `api/`, `feishu/`, `scheduler/`, `data/`
- Frontend: `web/src/`
- Tests: `tests/unit/`, `tests/integration/`, `tests/contract/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline workspace setup

- [X] T001 Create the backend and data directory structure in `agents/`, `tools/`, `api/`, `feishu/`, `scheduler/`, `data/config/`, `data/vector_store/`, and `data/intel_history/`
- [X] T002 [P] Create the frontend directory scaffold in `web/src/components/`, `web/src/pages/`, and `web/src/services/`
- [X] T003 Create dependency manifests in `requirements.txt` and `web/package.json`
- [X] T004 [P] Create environment and bootstrap config files in `.env.example` and `config.py`
- [X] T005 [P] Create baseline package entry files in `agents/__init__.py`, `tools/__init__.py`, `api/__init__.py`, `feishu/__init__.py`, and `scheduler/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement shared application configuration and client factories in `config.py`
- [ ] T007 [P] Implement source metadata and content-type schemas in `agents/state.py`
- [ ] T008 [P] Implement competitor configuration persistence in `data/config/competitors.json` and `tools/knowledge_base.py`
- [ ] T009 Implement vector memory and baseline repository utilities in `tools/knowledge_base.py`
- [ ] T010 [P] Implement common logging, timeout, and graceful-degradation helpers in `tools/report_builder.py`
- [ ] T011 [P] Create external dependency smoke tests in `tests/integration/test_llm_connectivity.py`, `tests/integration/test_search_connectivity.py`, `tests/integration/test_vector_store.py`, and `tests/integration/test_embedding_connectivity.py`
- [ ] T012 Implement a unified API/app bootstrap in `main.py` and `api/routes.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 发起竞品情报分析 (Priority: P1) 🎯 MVP

**Goal**: 用户可以发起一次单竞品或多竞品分析，并拿到结构化情报结果

**Independent Test**: 调用一次分析入口后，系统能完成目标识别、搜索、抓取、提取、存储与结构化返回，且结果带来源和可信度

### Tests for User Story 1 ⚠️

- [ ] T013 [P] [US1] Add pipeline smoke coverage in `tests/integration/test_pipeline.py`
- [ ] T014 [P] [US1] Add API contract test for `POST /api/analyze` in `tests/contract/test_analyze_api.py`
- [ ] T015 [P] [US1] Add orchestrator integration test for single and multi-target analysis in `tests/integration/test_orchestrator_analysis.py`

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement public search client and result normalization in `tools/web_search.py`
- [ ] T017 [P] [US1] Implement web page fetching with legal-source-safe degradation in `tools/web_fetcher.py`
- [ ] T018 [P] [US1] Implement structured extraction and `fact/inference/unverified` classification in `tools/data_extractor.py`
- [ ] T019 [P] [US1] Implement Search Agent query construction and result packaging in `agents/search_agent.py`
- [ ] T020 [P] [US1] Implement Analysis Agent extraction, credibility scoring, and baseline lookup in `agents/analysis_agent.py`
- [ ] T021 [US1] Implement Orchestrator intent parsing and workflow execution in `agents/orchestrator.py`
- [ ] T022 [US1] Implement report assembly for base analysis responses in `agents/report_agent.py`
- [ ] T023 [US1] Wire the analysis HTTP endpoint and response mapping in `api/routes.py`
- [ ] T024 [US1] Add a CLI or scriptable runner for the end-to-end MVP chain in `tests/integration/test_pipeline.py`
- [ ] T025 [US1] Persist validated intelligence items and baseline snapshots in `tools/knowledge_base.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 接收变化预警 (Priority: P2)

**Goal**: 系统能够基于历史基线识别变化、去重并生成预警事件

**Independent Test**: 对同一竞品运行两次分析后，系统能识别有效变化并只生成一次对应预警

### Tests for User Story 2 ⚠️

- [ ] T026 [P] [US2] Add alert contract validation for alert payload structure in `tests/contract/test_alert_payloads.py`
- [ ] T027 [P] [US2] Add change-detection and dedup integration coverage in `tests/integration/test_alert_dedup.py`

### Implementation for User Story 2

- [ ] T028 [P] [US2] Implement change-event comparison logic in `agents/analysis_agent.py`
- [ ] T029 [P] [US2] Implement alert grading and dedup rules in `agents/alert_agent.py`
- [ ] T030 [US2] Extend memory persistence for alert history and snapshot retrieval in `tools/knowledge_base.py`
- [ ] T031 [US2] Integrate alert generation into the orchestrator workflow in `agents/orchestrator.py`
- [ ] T032 [US2] Expose recent alert retrieval in `api/routes.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - 获取可执行报告与周期摘要 (Priority: P3)

**Goal**: 系统可以生成管理层报告、图表数据、周期摘要，并支持 Web 与飞书输出

**Independent Test**: 在已有分析结果的前提下，系统能独立生成可读报告、周期摘要和终端适配输出

### Tests for User Story 3 ⚠️

- [ ] T033 [P] [US3] Add report contract validation for report and card payloads in `tests/contract/test_report_payloads.py`
- [ ] T034 [P] [US3] Add scheduled-summary integration coverage in `tests/integration/test_scheduler_summary.py`

### Implementation for User Story 3

- [ ] T035 [P] [US3] Implement executive summary, actions, and chart data generation in `agents/report_agent.py`
- [ ] T036 [P] [US3] Implement chart data builders for timeline and comparison output in `tools/chart_generator.py`
- [ ] T037 [P] [US3] Implement Web dashboard analysis flow service in `web/src/services/api.ts`
- [ ] T038 [P] [US3] Implement dashboard chat and result display UI in `web/src/components/ChatInterface.tsx`
- [ ] T039 [P] [US3] Implement alert panel UI in `web/src/components/AlertPanel.tsx`
- [ ] T040 [P] [US3] Implement competitor configuration UI in `web/src/pages/ConfigPage.tsx`
- [ ] T041 [US3] Implement scheduler job orchestration for daily and weekly scans in `scheduler/jobs.py` and `scheduler/runner.py`
- [ ] T042 [US3] Implement Feishu webhook handling and reply flow in `feishu/webhook.py` and `api/feishu_routes.py`
- [ ] T043 [US3] Implement Feishu cards and push sender in `feishu/cards.py` and `feishu/sender.py`
- [ ] T044 [US3] Connect report, alert, dashboard, and Feishu output paths in `agents/orchestrator.py` and `main.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] Document environment setup and demo flow in `README.md`
- [ ] T046 Harden public-source compliance, fallback messaging, and data quality notes across `agents/` and `tools/`
- [ ] T047 [P] Add end-to-end stability coverage in `tests/integration/test_e2e.py`
- [ ] T048 [P] Validate quickstart steps against the current implementation in `specs/001-marketintel-core-workflow/quickstart.md`
- [ ] T049 Finalize demo-ready frontend styling and progress-state visibility in `web/src/components/` and `web/src/pages/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 baseline persistence and analysis outputs
- **User Story 3 (Phase 5)**: Depends on User Story 1 analysis/report core and benefits from User Story 2 alert outputs
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - establishes the MVP chain
- **User Story 2 (P2)**: Depends on User Story 1 because alerting requires baseline snapshots and analyzed change candidates
- **User Story 3 (P3)**: Depends on User Story 1 for report inputs; can integrate User Story 2 outputs for alert surfaces and Feishu notifications

### Within Each User Story

- Tests should be written before or alongside implementation and must validate the story independently
- Core tool or model work comes before orchestration and endpoint wiring
- API or UI integration comes after the underlying workflow contracts exist
- Story completion should end with an independently runnable validation path

### Parallel Opportunities

- Setup tasks T002, T004, and T005 can run in parallel
- Foundational tasks T007, T008, T010, and T011 can run in parallel once T006 is started
- In User Story 1, T016-T020 are parallelizable across separate files before T021-T025
- In User Story 2, T028 and T029 can run in parallel before integration tasks T030-T032
- In User Story 3, frontend tasks T037-T040 and Feishu tasks T042-T043 can run in parallel after report shaping begins

---

## Parallel Example: User Story 1

```bash
# Tool-layer work in parallel:
Task: "Implement public search client and result normalization in tools/web_search.py"
Task: "Implement web page fetching with legal-source-safe degradation in tools/web_fetcher.py"
Task: "Implement structured extraction and fact/inference/unverified classification in tools/data_extractor.py"

# Agent-layer work in parallel after tool contracts exist:
Task: "Implement Search Agent query construction and result packaging in agents/search_agent.py"
Task: "Implement Analysis Agent extraction, credibility scoring, and baseline lookup in agents/analysis_agent.py"
Task: "Implement report assembly for base analysis responses in agents/report_agent.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the pipeline, orchestrator, and analyze API tests
5. Demo the single-competitor and multi-competitor analysis flow

### Incremental Delivery

1. Build the base analysis chain and persistence layer
2. Add alerting and change detection as the second increment
3. Add dashboard, scheduling, and Feishu delivery as the third increment
4. Finish with cross-cutting hardening, demo polish, and e2e validation

### Parallel Team Strategy

With multiple developers:

1. One developer handles toolchain and configuration foundation
2. One developer handles core agents and orchestration
3. One developer handles frontend and endpoint integration after API contracts stabilize
4. One developer can handle alerting plus Feishu integration once baseline data flow exists

---

## Notes

- Total tasks: 49
- Suggested MVP scope: Through Phase 3 / User Story 1
- All tasks follow the required checklist format with IDs, optional parallel markers, story labels where required, and concrete file paths
