# Quickstart: 市场情报监测智能体核心工作流

## 1. 准备环境

1. 使用 Python 3.11+ 创建并激活虚拟环境。
2. 安装后端依赖：`pip install -r requirements.txt`
3. 准备前端环境：进入 `web/` 后执行 `npm install`
4. 复制 `.env.example` 为 `.env`，填入以下最小配置：
   - `LLM_API_KEY`
   - `LLM_BASE_URL`
   - `LLM_MODEL`
   - `SERPER_API_KEY` 或等价搜索服务密钥
   - `EMBEDDING_MODEL`
   - 飞书相关配置可在 Phase 4 再补齐

## 2. 验证外部依赖

按顺序准备独立验证脚本并确认通过：

1. LLM 连通性验证
2. 搜索 API 验证
3. 向量库写入与查询验证
4. Embedding 接口验证

预期结果：

- LLM 能返回固定测试文本
- 搜索 API 能返回候选结果
- 向量库可以写入并召回测试文本
- Embedding 接口返回非空向量

## 3. 跑通 MVP 主链路

按以下顺序建设并验证：

1. 实现 `config.py`
2. 实现 `tools/web_search.py`
3. 实现 `tools/web_fetcher.py`
4. 实现 `tools/data_extractor.py`
5. 实现 `tools/knowledge_base.py`
6. 编写一个临时 pipeline 脚本，完成：
   - 搜索
   - 抓取
   - 提取
   - 存储
   - 历史检索

验收标准：

- 输入单个竞品后，脚本能输出结构化情报列表
- 失败页面会自动降级到摘要
- 向量库目录中可以看到写入结果

## 4. 迁移到 Agent 工作流

1. 定义统一状态对象
2. 实现 Search Agent
3. 实现 Analysis Agent
4. 实现 Alert Agent
5. 实现 Report Agent
6. 用 Orchestrator 将各节点串联为标准流程

验收标准：

- 日志中可见各 Agent 执行阶段
- 第二次分析同一竞品时，系统能读取历史并尝试生成变化检测结果

## 5. 接入 Web Dashboard

1. 启动 FastAPI API 层
2. 创建 React + Vite 前端
3. 完成以下页面或组件：
   - 对话输入与结果展示
   - 预警面板
   - 竞品配置中心
   - 可选：竞品对比图表

验收标准：

- 用户能在页面输入竞品并看到结构化报告
- 配置页能新增监测竞品
- 有预警时面板中出现对应条目

## 6. 接入飞书

1. 创建企业自建应用
2. 开通机器人和消息相关权限
3. 注册 Webhook 路由
4. 通过公网隧道调试事件订阅
5. 实现“处理中卡片”“报告卡片”“预警卡片”

验收标准：

- 在飞书中 @机器人 可以触发一次分析并收到返回卡片
- 高优先级预警可主动推送

## 7. 演示前检查

- 单竞品分析可跑通
- 多 Agent 日志可展示
- 历史对比可展示
- Web Dashboard 可演示
- 配置中心可演示
- 飞书集成若已完成，可现场展示
