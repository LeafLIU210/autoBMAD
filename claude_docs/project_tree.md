# DocuSwarm 项目结构说明

**版本**: 2.2
**最后更新**: 2026-05-02
**项目**: DocuSwarm Multi-Agent Orchestration System

---

## 目录结构

```
DocuSwarm/                     # 项目根目录
├── autoBMAD/                  # autoBMAD 工作流系统
│   ├── docuswarm/             # DocuSwarm 核心系统
│   │   ├── agents/            # Agent 实现
│   │   │   ├── base.py        # BaseAgent 基类
│   │   │   ├── independent.py # Independent Agent
│   │   │   ├── evaluator.py   # Evaluator Agent
│   │   │   └── evaluator_config/  # Evaluator 配置
│   │   ├── context/           # 上下文管理
│   │   │   ├── isolation.py   # ContextManager
│   │   │   ├── filter.py      # ContextFilter
│   │   │   ├── audit.py       # IsolationAuditLogger
│   │   │   └── memory.py      # ContextMemory
│   │   ├── llm/               # LLM 集成
│   │   │   ├── session_manager.py  # SessionManager
│   │   │   ├── response.py    # ResponseParser
│   │   │   ├── approval.py    # ApprovalSystem
│   │   │   ├── mode_mapper.py # ModeMapper
│   │   │   ├── tool_filter.py # ToolFilter
│   │   │   └── config.py      # LLM 配置
│   │   ├── nodes/             # 节点系统
│   │   │   ├── dual_agent.py  # DualAgentNode
│   │   │   ├── iteration.py   # IterationController
│   │   │   └── loader.py      # NodeConfigLoader
│   │   ├── node_execution/    # 节点执行系统
│   │   │   ├── executor.py    # NodeExecutor
│   │   │   ├── pipeline_adapter.py  # PipelineAdapter
│   │   │   ├── context_builder.py   # ContextBuilder
│   │   │   ├── state.py       # ExecutionState
│   │   │   ├── metrics.py     # ExecutionMetrics
│   │   │   ├── node_escalation.py   # EscalationHandler
│   │   │   ├── run_tracker.py # RunTracker
│   │   │   ├── chaining.py    # NodeChaining
│   │   │   └── contracts.py   # ExecutionContracts
│   │   ├── pipeline/          # 流水线编排
│   │   │   ├── orchestrator.py   # HybridOrchestrator
│   │   │   ├── state.py       # PipelineState
│   │   │   ├── graph.py       # LangGraph 图定义
│   │   │   ├── quality.py     # VerdictDeterminer
│   │   │   ├── questions.py   # QuestionHandler
│   │   │   ├── transitions.py # StateTransitions
│   │   │   ├── metrics.py     # PipelineMetrics
│   │   │   ├── force_completion.py  # ForceCompletion
│   │   │   ├── escalation.py  # EscalationHandler
│   │   │   └── lease.py       # LeaseManager
│   │   ├── prompts/           # 提示词模板
│   │   │   ├── templates/     # YAML/Markdown 模板文件
│   │   │   ├── template_loader.py
│   │   │   ├── template_engine.py
│   │   │   ├── contract_builder.py
│   │   │   ├── skill_injector.py
│   │   │   ├── validator.py
│   │   │   ├── independent_agent.py
│   │   │   └── evaluator_agent.py
│   │   ├── storage/           # 存储层
│   │   │   ├── state_manager.py
│   │   │   ├── checkpoints.py
│   │   │   ├── database.py
│   │   │   ├── files.py
│   │   │   └── state_access.py
│   │   ├── tools/             # 工具函数
│   │   │   ├── create_deliverable.py / create_deliverable_sdk.py
│   │   │   ├── create_document_set.py
│   │   │   ├── update_context.py / update_context_sdk.py
│   │   │   ├── file_tools.py / file_tools_sdk.py
│   │   │   ├── search_tools.py / search_tools_sdk.py
│   │   │   ├── tool_registry.py
│   │   │   ├── tool_result.py
│   │   │   ├── callable_tool_wrapper.py
│   │   │   ├── sdk_adapter.py
│   │   │   └── protocols.py
│   │   ├── utils/             # 工具类
│   │   │   ├── logging.py
│   │   │   └── session_ids.py
│   │   ├── config.py          # 配置管理
│   │   ├── exceptions.py      # 异常定义
│   │   ├── public_api.py      # 稳定公共 API
│   │   ├── __main__.py        # 模块入口
│   │   ├── __init__.py        # 包初始化
│   │   ├── README.md          # DocuSwarm 文档
│   │   └── CONFIGURATION.md   # 配置说明
│   │
│   ├── epic_automation/       # Epic 自动化系统
│   │   ├── agents/            # Agent 实现
│   │   │   ├── base_agent.py
│   │   │   ├── dev_agent.py
│   │   │   ├── qa_agent.py
│   │   │   ├── sm_agent.py
│   │   │   └── state_agent.py
│   │   ├── controllers/       # 控制器模块
│   │   │   ├── devqa_controller.py
│   │   │   ├── pytest_controller.py
│   │   │   └── quality_check_controller.py
│   │   ├── core/              # 核心功能
│   │   │   ├── cancellation_manager.py
│   │   │   ├── sdk_executor.py
│   │   │   └── sdk_result.py
│   │   ├── architecture/      # 架构文档
│   │   ├── logs/              # 日志输出
│   │   ├── reports/           # 报告生成
│   │   ├── epic_driver.py     # 主编排器
│   │   ├── state_manager.py   # 状态管理
│   │   ├── sdk_wrapper.py     # SDK 封装
│   │   ├── README.md          # 详细文档
│   │   └── SETUP.md           # 安装指南
│   │
│   ├── nodes/                 # 节点配置
│   │   ├── analyst/           # Analyst 节点配置
│   │   ├── pm/                # PM 节点配置
│   │   ├── ux/                # UX 节点配置
│   │   ├── architect/         # Architect 节点配置
│   │   └── po/                # PO 节点配置
│   │
│   └── Skill/                 # Claude Code Skill
│       ├── autoBMAD-epic-automation.skill
│       ├── SKILL.md
│       └── SKILL_INSTALLATION_GUIDE.md
│
├── claude_docs/               # 详细说明文档
│   ├── core_principles.md     # 四大开发原则
│   ├── ai_workflow.md         # AI 助手工作流程
│   ├── development_rules.md   # 编码规范
│   ├── testing_guide.md       # 测试规范
│   ├── quality_assurance.md   # 质量保证流程
│   ├── technical_specs.md     # 技术规范
│   ├── workflow_tools.md      # autoBMAD 工作流
│   ├── bmad_methodology.md    # BMAD 方法论
│   ├── quick_reference.md     # 常用命令速查
│   ├── project_tree.md        # 项目结构
│   ├── venv.md                # 虚拟环境管理
│   └── git-commit-trigger-update.md  # Git 提交触发更新
│
├── docs-test/                 # 测试用示例文档
│   ├── bubble-sort/           # Bubble Sort 示例
│   ├── calc-one-plus-one/     # 计算器示例
│   └── evaluation/            # 评估报告
│
├── docs-doc/                  # 项目文档
│   ├── solution/              # TDD 重构方案
│   ├── research/              # 研究文档
│   └── architecture/          # 架构文档
│
├── scripts/                   # 脚本工具
├── tests/                     # 测试目录
├── output/                    # 输出目录
├── logs/                      # 日志目录
├── .bmad-core/               # BMAD 核心配置
│
├── README.md                  # 项目主文档
├── CLAUDE.md                  # Claude Code 指导文档
├── SETUP.md                   # 安装指南
├── pyproject.toml             # 项目配置
├── requirements.txt           # 生产依赖
├── .env                       # 环境变量（不提交）
└── .gitignore                 # Git 忽略规则
```

---

## 核心目录说明

### autoBMAD/docuswarm/
DocuSwarm 多 Agent 文档编排系统核心代码，包含：
- **agents/**: Independent Agent 和 Evaluator Agent 实现
- **context/**: 三层上下文隔离机制
- **llm/**: claude-agent-sdk 集成 (Anthropic Claude API)
- **pipeline/**: LangGraph 流水线编排
- **storage/**: SQLite 状态持久化
- **tools/**: Agent 可调用的工具函数

### autoBMAD/epic_automation/
Epic 自动化工作流系统，包含：
- **agents/**: SM、Dev、QA 等 Agent 实现
- **controllers/**: 工作流控制器
- **core/**: 核心功能（SDK 封装、取消管理等）
- Epic Driver: 完整的 5 阶段 BMAD 自动化

### claude_docs/
面向 Claude Code AI 助手的详细指导文档：
- 开发原则和工作流程
- 编码规范和测试指南
- 质量保证和技术规范

### docs-doc/
项目文档目录：
- **architecture/**: 系统架构设计文档
- **solution/**: TDD 重构方案
- **research/**: 深度研究报告

### docs-test/
测试用示例文档：
- **calc-one-plus-one/**: 计算器示例
- **bubble-sort/**: 排序示例

---

## 配置文件

### pyproject.toml
项目核心配置文件，包含：
- 项目元数据
- 依赖列表
- Pytest、Ruff、BasedPyright 配置

### .env
环境变量文件（不提交到 Git）：
```env
ANTHROPIC_API_KEY=your_api_key_here
# ANTHROPIC_BASE_URL=https://custom-api-url/
```

### requirements.txt / requirements-dev.txt
- **requirements.txt**: 生产依赖（LangGraph、LangChain、claude-agent-sdk 等）
- **requirements-dev.txt**: 开发依赖（pytest、ruff、basedpyright 等）

---

**参考文档**:
- [技术规范](./technical_specs.md)
- [开发规则](./development_rules.md)

---

**版本历史**:
- v2.2 (2026-05-02): 根据 autoBMAD/docuswarm 实际代码对齐更新目录结构
- v2.0 (2026-03-02): 更新为 DocuSwarm 实际项目结构
- v1.0 (2026-01-04): 初始版本
