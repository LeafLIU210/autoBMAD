# autoBMAD — 多智能体 BMAD 自动化系统

![Python](https://img.shields.io/badge/Python-%3E%3D3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

---

## 项目简介

**autoBMAD** 是一个面向 BMAD（Breakthrough Method of Agile AI-driven Development）方法论的多智能体自动化系统，致力于将 AI 驱动的敏捷开发流程标准化、可复用、可恢复。项目包含两个核心子系统：

- **DocuSwarm**：多智能体文档编排系统，通过双 Agent 模式（Independent Agent + Evaluator Agent）顺序编排 5 个 BMAD 阶段（Analyst → PM → UX → Architect → PO），自动化产出完整项目文档。
- **Epic Automation**：Epic 级 BMAD 工作流自动化，基于 SM-Dev-QA 循环 + 质量门控 + 测试自动化，实现从故事拆分到代码交付的端到端开发闭环。

整体架构基于 **LangGraph** 状态机 + **Claude Agent SDK** + **SQLite WAL** 持久化，具备上下文隔离、检查点恢复与可观测性能力。

---

## 核心特性

- **双 Agent 协作**：Independent Agent 负责生产交付物，Evaluator Agent 在隔离上下文中独立评审，避免单点偏差。
- **顺序流水线**：DocuSwarm 内置 Analyst → PM → UX → Architect → PO 五阶段固定流水线，自动衔接上下游交付物。
- **三层上下文隔离**：运行时访问控制、提示词模板隔离、消息过滤三重防御，违规即抛出 `ContextIsolationError`。
- **检查点恢复**：基于 LangGraph Checkpointing + SQLite WAL，流水线可在中断后从最近检查点恢复，乐观锁防止并发损坏。
- **Epic 五层架构**：Driver / Controller / Phase / Agent / Tool 分层清晰，便于扩展与替换。
- **SM-Dev-QA 循环**：Story Manager → Developer → QA 自动闭环，配合质量门控保证交付质量。
- **质量门控**：内置 Ruff（lint）+ BasedPyright（类型检查）双重门控，未通过即阻塞流水线。
- **Pytest 测试自动化**：开发产物自动触发 pytest 测试套件，失败可回流至 QA 节点重新修正。
- **结构化日志**：基于 structlog 的 per-pipeline 日志分流，支持敏感信息脱敏。
- **可插拔 LLM**：支持 Anthropic Claude 原生协议，并兼容 DeepSeek 等 Anthropic 兼容模式提供商。

---

## 快速开始

```bash
git clone https://github.com/LeafLIU210/autoBMAD.git
cd autoBMAD
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key" > .env
```

详细安装与配置说明见 [SETUP.md](SETUP.md)。

---

## 项目结构 — 各文件夹介绍

| 目录 | 说明 |
| --- | --- |
| `autoBMAD/docuswarm/` | DocuSwarm 多智能体文档编排系统（核心子系统） |
| `autoBMAD/epic_automation/` | Epic 级 BMAD 工作流自动化（核心子系统） |
| `autoBMAD/nodes/` | BMAD 节点配置（analyst / pm / ux / architect / po） |
| `autoBMAD/agentdocs/` | Claude Agent SDK 官方文档参考资料 |
| `claude_docs/` | 项目开发指南与规范文档（中文） |
| `tests/` | pytest 测试套件，按优先级组织（P0–P4） |
| `docs-doc/` | DocuSwarm 文档产出示例（PRD、架构、评估报告等） |
| `docs-test/` | 测试用例文档（bubble-sort、calc-one-plus-one 等示例） |
| `scripts/` | 实用脚本（post-commit hook 等） |
| `tools/` | 独立工具脚本 |
| `src/` | 遗留最小核心代码（models、config 等，主代码已迁移至 `autoBMAD/`） |

---

## 重要文件说明

### 开发文档

| 文件 | 说明 |
| --- | --- |
| [CLAUDE.md](CLAUDE.md) | AI 开发工作流指南，描述 Claude 在本仓库的协作约定 |
| [AGENTS.md](AGENTS.md) | AI Agent 参考手册，面向自动化代理零知识接入 |
| [SETUP.md](SETUP.md) | 完整安装与环境配置指南 |
| [claude_docs/](claude_docs/) | 核心原则、AI 工作流、测试指南等开发规范文档 |

### 配置文件

| 文件 | 说明 |
| --- | --- |
| [pyproject.toml](pyproject.toml) | 构建系统、依赖、Ruff、BasedPyright、Pytest 等工具配置 |
| [.env.example](.env.example) | 环境变量模板（复制为 `.env` 后填写） |
| [requirements.txt](requirements.txt) | 生产环境依赖清单 |
| [requirements-dev.txt](requirements-dev.txt) | 开发与测试依赖清单 |

### 运行文件

| 文件 | 说明 |
| --- | --- |
| [.gitignore](.gitignore) | Git 忽略规则 |
| [LICENSE](LICENSE) | MIT 开源许可证 |
| `progress.db` | Epic Automation 状态数据库（SQLite，运行时生成） |
| `docuswarm.db` | DocuSwarm 流水线状态数据库（SQLite WAL，运行时生成） |

---

## 两个核心子系统概要

### DocuSwarm — 多智能体文档编排

DocuSwarm 通过双 Agent 模式自动化生成完整项目文档。Independent Agent 在每个 BMAD 阶段产出交付物（如 Brief、PRD、UX Spec、架构文档、PO Backlog），Evaluator Agent 在隔离上下文中独立评审并给出 verdict，未通过则触发迭代修正。状态由 LangGraph + SQLite 持久化，支持中断恢复。

详细文档：[autoBMAD/docuswarm/README.md](autoBMAD/docuswarm/README.md)

```bash
python -m autoBMAD.docuswarm start --context docs-test/calc-one-plus-one/calc-context.md
```

### Epic Automation — Epic 级 BMAD 工作流

Epic Automation 接收 Epic 文档作为输入，按五层架构（Driver / Controller / Phase / Agent / Tool）执行 SM-Dev-QA 循环：Story Manager 拆分故事，Developer 实现代码，QA 运行测试与质量门控。每阶段完成后由 Ruff + BasedPyright 把关，未达标自动回流至开发节点。

详细文档：[autoBMAD/epic_automation/README.md](autoBMAD/epic_automation/README.md)

```bash
python -m autoBMAD.epic_automation.epic_driver docs-doc/epics/my-epic.md --verbose
```

---

## 技术栈概览

| 技术 | 版本 | 用途 |
| --- | --- | --- |
| LangGraph | 0.2.x | 多 Agent 状态机与流水线编排 |
| claude-agent-sdk | 0.1.x | Claude Agent SDK，工具调用与会话管理 |
| Anthropic Claude | Sonnet | 主要 LLM（200K 上下文） |
| SQLite WAL | — | 状态持久化与检查点 |
| Pydantic | >=2.0 | 数据校验与配置模型 |
| Click | 8.x | CLI 框架 |
| structlog | >=24.0 | 结构化日志 |
| Ruff | 0.5.x | 代码 lint 与格式化 |
| BasedPyright | 1.x | 静态类型检查 |
| pytest | 8.x | 测试框架（含 asyncio / cov / timeout） |

---

## 贡献指南

### 开发流程

1. Fork 本仓库并 clone 到本地
2. 基于 `main` 创建 Feature Branch（命名建议：`feat/xxx`、`fix/xxx`）
3. 提交前运行 `pre-commit run --all-files`
4. 提交 Pull Request 并描述变更

### 代码规范

- 遵循 [Ruff](https://docs.astral.sh/ruff/) 规则（line-length=100，target=py312）
- 公开函数必须包含返回类型注解，通过 BasedPyright 检查
- 使用绝对导入，禁止相对导入
- 中文文本直接书写，禁用 Unicode 转义

### 测试

```bash
pytest -v --tb=short
pytest --cov=autoBMAD.docuswarm --cov-report=term-missing
```

详细开发指南见 [CLAUDE.md](CLAUDE.md) 与 [claude_docs/](claude_docs/)。

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
