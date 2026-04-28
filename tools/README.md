# DocuSwarm 工具集

本目录包含用于 DocuSwarm 项目诊断、分析和迁移的专用工具。

---

## 工具列表

### 0. `context_injection_auditor.py` - 上下文注入审计器

静态审计 DocuSwarm 的上下文注入链路，覆盖 `node.yaml -> executor -> DualAgentNode -> agents -> state/file storage -> docs tools`。

#### 用法

```bash
# 直接输出 Markdown 审计报告
python tools/context_injection_auditor.py

# 保存到 docs/research
python tools/context_injection_auditor.py --output docs/research/2026-03-13-context-injection-audit.md

# JSON 格式输出
python tools/context_injection_auditor.py --format json
```

#### 适合排查的问题

- `node.yaml` 配置是否真正进入 prompt
- 上下文是否被重复包装或字符串化
- deliverable 是否存在“双轨真相”
- `update_context` 是否真的持久化
- docs 工具是否具备受控扩展策略

### 0.5 `docs_dependency_auditor.py` - docs-free 工作流依赖审计器

在产品已经决定“工作流完全不读取 `docs/`”的前提下，静态审计 `autoBMAD/docuswarm`、`tests` 和 `tools` 中仍然残留的 docs 读取、写入、注册与上下文字段依赖。

#### 用法

```bash
# 直接输出 Markdown 报告
python tools/docs_dependency_auditor.py

# 保存到 docs/research
python tools/docs_dependency_auditor.py --output docs/research/2026-03-17-docs-free-workflow-dependency-research.md

# JSON 格式输出
python tools/docs_dependency_auditor.py --format json
```

#### 适合排查的问题

- 哪些 runtime 模块仍然开放 `read_docs_file` / `list_docs_files` / `update_docs_file`
- 哪些测试仍然把 docs 工具注册视为既定契约
- `docs_context` 是否仍在执行协议中残留
- 哪些调试工具仍然把 docs 扩展视为未来方向

### 0.6 `docuswarm_decision_researcher.py` - F1-F8 决策研究器

围绕 2026-03-17 审查结论和当前产品决策，对 `autoBMAD/docuswarm` 做一次可重复运行的深度研究，重点覆盖：

- `state_json` vs LangGraph checkpoint 的真相源判断
- `shared_context` 与 Evaluator 输入契约闭环
- docs-free 工具面和 ToolRegistry 收敛
- `ToolResult` / `METADATA:` / `ToolOk` 分叉比较
- 测试可见性快照
- 类型导出面与文档漂移信号

#### 用法

```bash
# 直接输出 Markdown 报告
python tools/docuswarm_decision_researcher.py

# 输出 JSON 供后续脚本处理
python tools/docuswarm_decision_researcher.py --format json

# 保存正式研究报告到 docs/research
python tools/docuswarm_decision_researcher.py --output docs/research/2026-03-17-docuswarm-decision-research-report.md
```

#### 适合排查的问题

- 当前到底该把 `state_json` 还是 checkpoint 当真相源
- `update_context` 为什么“写得进去”但“执行时没用起来”
- Evaluator 为什么仍然评不到稳定的原始上下文
- 为什么工具面明明已选 docs-free，代码和文档却还像双轨系统
- 为什么 `ToolResult`、`METADATA:`、`ToolOk/ToolError` 同时存在

### 1. `docuswarm_debugger.py` - 离线诊断器

诊断 DocuSwarm 启动/流水线执行问题，自动串联数据库、日志和工具注册信息。

#### 用法

```bash
# 基础诊断
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf

# Markdown 格式输出
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf --format markdown

# 保存报告到文件
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf --format markdown --output docs/research/debug-snapshot.md
```

#### 适合排查的问题

- `start` 命令卡在上下文验证
- 节点日志显示失败，但数据库状态却是 `completed`
- `create_deliverable` 工具似乎没有被调用
- 数据库状态、输出目录、日志三者互相矛盾

---

### 2. `architecture_analyzer.py` - 架构分析器

用于深度研究 Kimi 依赖和迁移准备，分析 Kimi 依赖分布，识别关键迁移点。

#### 用法

```bash
# 分析 Kimi 依赖分布
python tools/architecture_analyzer.py --mode deps

# 对比 epic_automation 架构模式
python tools/architecture_analyzer.py --mode compare

# 生成迁移检查清单
python tools/architecture_analyzer.py --mode checklist

# 生成完整报告（包含依赖分析、架构对比、检查清单）
python tools/architecture_analyzer.py --mode report --output docs/research/migration-analysis.md
```

#### 输出示例

```markdown
# DocuSwarm Kimi 依赖分析报告

## 统计概览
- 分析文件数: 42
- Kimi 依赖总数: 23
- 使用 SessionManager 的文件: 7

## 关键迁移点
| 文件 | Kimi 导入数 | 关键类型 | SessionManager |
|------|------------|----------|----------------|
| llm/session_manager.py | 8 | Session, Message | 是 |
| agents/independent.py | 3 | ApprovalRequest | 是 |
...
```

---

### 3. `migration_tracker.py` - 迁移追踪器

追踪迁移进度和代码变更，检测 Kimi 代码残留，验证新架构组件存在性。

#### 用法

```bash
# 检查整体迁移状态
python tools/migration_tracker.py --check

# 检查特定 Phase 的详细状态
python tools/migration_tracker.py --phase 0

# 生成完整迁移报告
python tools/migration_tracker.py --report

# JSON 格式输出（供脚本使用）
python tools/migration_tracker.py --check --json

# 保存报告到文件
python tools/migration_tracker.py --report --output docs/research/migration-status.md
```

#### Phase 定义

| Phase | 名称 | 说明 |
|-------|------|------|
| 0 | 运行时抽象层建设 | 新增 SDKResult、CancellationManager、SDKExecutor 等核心组件 |
| 1 | 轻量调用路径迁移 | 迁移 Context Validator 和 EvaluatorAgent |
| 2 | IndependentAgent 迁移 | 迁移工具调用和审批策略 |
| 3 | 编排恢复链路迁移 | 迁移 resume/restart/cancel 和状态机语义 |
| 4 | Kimi 代码移除 | 移除所有 Kimi 专属代码和配置 |

---

## 快速参考

### 开始迁移前

```bash
# 1. 分析当前依赖
python tools/architecture_analyzer.py --mode deps

# 2. 对比目标架构
python tools/architecture_analyzer.py --mode compare

# 3. 生成检查清单
python tools/architecture_analyzer.py --mode checklist --output CHECKLIST.md
```

### 迁移过程中

```bash
# 每完成一个 Phase，检查状态
python tools/migration_tracker.py --phase 0
python tools/migration_tracker.py --phase 1
...

# 检查 Kimi 代码残留
python tools/migration_tracker.py --check
```

### 遇到问题

```bash
# 诊断流水线问题
python tools/docuswarm_debugger.py --pipeline-id <id> --format markdown

# 查看详细架构分析
python tools/architecture_analyzer.py --mode report
```

---

## 环境要求

所有工具均使用标准库编写，无需额外依赖。Python 版本要求：>= 3.10

---

## 输出目录建议

建议将工具输出保存到 `docs/research/` 目录：

```bash
docs/research/
├── debug-snapshot.md           # 诊断报告
├── migration-analysis.md       # 架构分析报告
├── migration-status.md         # 迁移进度报告
└── CHECKLIST.md                # 迁移检查清单
```

---

### 4. `node_execution_context_researcher.py` - NodeExecutionContext 深度研究工具

针对方案B (统一 NodeExecutionContext) 的深度研究工具，分析上下文链路的断裂问题。

#### 用法

```bash
# 生成 Markdown 研究报告
python tools/node_execution_context_researcher.py

# 保存到 docs/research
python tools/node_execution_context_researcher.py --output docs/research/2026-03-13-p0-single-context-protocol-deep-research-report.md

# JSON 格式输出
python tools/node_execution_context_researcher.py --format json
```

#### 适合排查的问题

- executor 从 state 里"猜 task"，而非使用节点契约
- DualAgentNode 二次包装上下文 `{subject, task}`
- IndependentAgent 反向解析被包装的上下文
- node.yaml 的契约信息未进入 prompt
- 五个节点只有 persona 不同，缺乏任务契约差异

#### 示例输出

```bash
$ python tools/node_execution_context_researcher.py --output docs/research/report.md
报告已保存到: D:\GITHUB\DocuSwarm\docs\research\report.md
```

### 5. `node_execution_context_example.py` - 方案B 示例演示

交互式示例，展示新旧流程的对比。

#### 用法

```bash
python tools/node_execution_context_example.py
```

#### 输出内容

1. 旧流程示例（存在问题）
2. 新流程示例（方案B）
3. 新旧方案对比表
4. 五个节点的契约差异展示

---

## 故障排除

### 工具找不到项目根目录

确保从项目根目录运行工具：

```bash
cd D:\GITHUB\DocuSwarm
python tools/architecture_analyzer.py --mode deps
```

### 中文显示乱码

Windows PowerShell 用户如遇中文乱码，先执行：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 贡献

如需添加新工具或改进现有工具，请遵循以下规范：

1. 使用标准库，避免外部依赖
2. 添加详细的 docstring 和使用说明
3. 支持 `--output` 参数输出到文件
4. 更新本 README 文档
