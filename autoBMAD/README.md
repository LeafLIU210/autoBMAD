# autoBMAD — 核心 Python 包

本目录是 autoBMAD 项目的核心 Python 包（命名空间 `autoBMAD`），包含两个主要子系统：

- **DocuSwarm** — 多智能体文档编排系统，通过 LangGraph 状态机驱动 5 个专业 Agent 顺序协作
- **Epic Automation** — Epic 级 BMAD 工作流自动化系统，实现 SM-Dev-QA 循环与质量门禁

---

## 目录结构

```
autoBMAD/
├── docuswarm/        # DocuSwarm 多智能体文档编排系统
├── epic_automation/  # Epic 级 BMAD 工作流自动化
├── nodes/            # BMAD 节点配置（5 个角色）
├── agentdocs/        # Claude Agent SDK 官方文档参考
├── output/           # 运行时产出目录
├── __init__.py       # 包初始化（懒加载）
├── py.typed          # PEP 561 类型标记
└── README.md         # 本文件
```

---

## 子文件夹介绍

### docuswarm/

DocuSwarm 多智能体文档编排系统。基于 LangGraph 状态机和 Dual-Agent 模式（Independent Agent + Evaluator Agent），驱动 Analyst、PM、UX Designer、Architect、PO 五个阶段自动产出项目文档。

核心能力：
- 流水线编排与状态管理（SQLite WAL 模式持久化）
- 上下文隔离与工具权限控制
- 迭代评审与质量门禁
- 断点恢复与检查点机制

详细文档：[docuswarm/README.md](docuswarm/README.md)

### epic_automation/

Epic 级 BMAD 工作流自动化系统。实现完整的 5 阶段 BMAD 流程自动化，包含 SM（Scrum Master）、Dev、QA 三角色循环协作，支持质量门禁与自动化验收。

核心能力：
- Epic 驱动的端到端自动化流程
- SM-Dev-QA 角色协作循环
- 质量门禁与自动验收
- 多阶段产出物管理

详细文档：[epic_automation/README.md](epic_automation/README.md)

### nodes/

BMAD 节点配置目录，为 DocuSwarm 流水线中的 5 个角色提供配置：

| 角色目录 | 说明 |
|----------|------|
| `analyst/` | 分析师 — 需求分析与研究 |
| `pm/` | 产品经理 — PRD 与产品规划 |
| `ux/` | UX 设计师 — 用户体验设计 |
| `architect/` | 架构师 — 技术架构设计 |
| `po/` | 产品负责人 — 产品验收与优先级 |

每个角色目录包含三个配置文件：
- `node.yaml` — 节点执行配置（工具、迭代策略、上下文权限）
- `persona.json` — 角色人设定义（技能、行为约束、输出格式）
- `evaluator.yaml` — 评审者配置（评估标准、打分规则）

此外还包含 `loader.py`，负责加载和解析节点配置。

### agentdocs/

Claude Agent SDK 官方文档参考，共 16 个文件，涵盖：
- SDK 概述与快速开始
- Python SDK / TypeScript SDK 详细文档
- 自定义工具、子 Agent、MCP 集成
- 文件检查点、结构化输出、托管部署
- 插件系统与 Slash Commands

供开发时查阅 SDK 用法与最佳实践。

### output/

DocuSwarm 运行时产出目录。流水线执行过程中各阶段 Agent 生成的交付物（Markdown 文档）会输出到此目录。该目录内容由系统自动管理，不纳入版本控制。

---

## 重要文件

| 文件 | 说明 |
|------|------|
| `__init__.py` | 包初始化文件，使用 `__getattr__` 懒加载机制，避免部分模块未实现时引发 ImportError |
| `py.typed` | PEP 561 类型标记文件，声明本包支持类型检查工具（basedpyright 等） |
| `README.md` | 本文件 |

---

## 快速导航

| 子系统 | 入口文档 | 运行命令 |
|--------|----------|----------|
| DocuSwarm | [docuswarm/README.md](docuswarm/README.md) | `python -m autoBMAD.docuswarm start --context <file>` |
| Epic Automation | [epic_automation/README.md](epic_automation/README.md) | `python -m autoBMAD.epic_automation.epic_driver <epic.md>` |
| 节点配置 | [nodes/](nodes/) | — |
| SDK 文档 | [agentdocs/README.md](agentdocs/README.md) | — |
