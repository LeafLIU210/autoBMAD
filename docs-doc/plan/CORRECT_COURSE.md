## DocuSwarm CLI correct-course（面向 @src 的功能调整方案）

**Version**: 2.2  
**Date**: 2026-02-23  
**Status**: PO Approved  
**Reviewer**: Product Owner  

---

### 1. 背景与目标

**现状：**

- MVP 设计中，`docuswarm start --context <file>` 会：
  - 创建一个新的 `pipeline_id`；
  - 基于固定顺序 `Analyst → PM → UX → Architect → PO` 自动执行完整流水线；
  - 所有节点的执行、检查点、导出等操作都围绕 **整条 pipeline** 进行。

**问题：**

- 自动流水线执行隐含假设：用户总是需要完整的 5 节点输出。实际场景中，用户可能只需执行特定节点（如仅生成 PRD）；
- Pipeline 级操作粒度过粗，无法独立查看、重试或导出单个节点的结果；
- 出错时被迫重跑整条流水线，浪费 LLM 调用成本和时间。

**目标：**

- 移除「自动执行完整流水线」这一设计，改为 **用户显式选择要执行的节点**。
- CLI 从「面向 pipeline」改为「面向单节点」：
  - `docuswarm start <node> ...` 手动执行指定节点；
  - 其他子命令（`status`、`export`、`questions`、`answer`）也改为针对 `<node>` 维度操作。
- 利用 **已有 `nodes/` 目录结构**，不引入冗余的 node-id 后缀。

**用户影响：**

| 用户角色 | 变更前 | 变更后 | 收益 |
|----------|--------|--------|------|
| Solo Developer | 一条命令跑完 5 节点，无法跳过 | 按需执行任意节点 | 节省时间和成本 |
| Tech Lead | 需等全流水线完成后审查 | 逐节点审查，及时介入 | 更早发现问题 |
| Product Manager | 只关心 PRD 但必须等 Analyst | 直接执行 PM 节点（自动链入 Analyst 结果） | 聚焦核心产出 |

---

### 2. 概念重构：从 pipeline → node

#### 2.1 核心概念

- **node（节点名）**
  - 固定 5 个 BMAD 角色名，直接作为 CLI 主操作对象：
    - `analyst` / `pm` / `ux` / `architect` / `po`
  - 与 `nodes/<node>/node.yaml` 一一对应，无需额外 ID 生成。

- **run（节点运行实例）**
  - 对应一次 `docuswarm start <node>` 的执行实例。
  - 每次执行自动生成 `run_id`（8 位短 UUID，如 `a3f7b2c1`）。
  - 一个 `node` 可以有多个 `run_id` 历史记录。
  - 日志、导出文件、问题列表等以 `(node, run_id)` 组合区分。

> **关键变化：不再存在「一条命令自动跑完整个 5 节点 pipeline」的行为。**

#### 2.2 自动上下文链（Context Chaining）

节点间存在隐式依赖顺序：`analyst → pm → ux → architect → po`。

- 当执行 `docuswarm start pm --context <file>` 时，系统 **自动查找** `analyst` 最近一次成功 run 的 deliverable，注入为 pm 的输入上下文。
- 规则：
  - `--context <file>` 对所有节点均为必填，系统以该文件的内容 hash 作为上下文链的关联锚点；
  - 仅注入 **同一 `context_hash`** 关联的前序节点最新成功 deliverable；
  - 若前序节点无成功 run，CLI 发出警告（`⚠ No successful run found for <prev_node>`）但不阻塞执行；
  - 用户可通过 `--no-chain` 跳过自动上下文链，此时节点仅接收 `--context` 文件内容，不注入任何前序 deliverable。

---

### 3. 初始化设计

#### 3.1 `docuswarm init` 命令

- 作用：初始化 DocuSwarm 项目配置。
- 行为：
  1. 检查项目根目录是否已有 `.docuswarm/config.yaml`。
  2. 若不存在，创建：
     - `.docuswarm/config.yaml`（项目级配置：db_path、output_dir、默认 LLM 参数）。
  3. 检查 `nodes/` 目录是否存在且包含 5 个节点子目录：
     - 若完整 → 跳过，输出 "Nodes already configured"。
     - 若缺失 → 仅补全缺失的节点目录与默认 `node.yaml`、`evaluator.yaml`、`persona.json`。
  4. 初始化 SQLite 数据库（`docuswarm.db`），创建 `node_runs` 表。

#### 3.2 节点配置（复用已有 `nodes/` 结构）

已有目录结构无需变更：

```
nodes/
├── analyst/
│   ├── node.yaml       # 节点配置
│   ├── evaluator.yaml   # 评估标准
│   └── persona.json     # BMAD persona
├── pm/
├── ux/
├── architect/
└── po/
```

`node.yaml` 已包含必要字段：`node_id`、`name`、`description`、`sequence`、`deliverable_type`、`dependencies`。

---

### 4. CLI 行为重设计：面向 `<node>` 的交互

#### 4.1 总体原则

- **保留原有命令名**：`start`、`status`、`export`、`questions`、`answer`。
- **新增辅助命令**：`init`、`nodes`、`runs`。
- **改变命令语义**：所有命令从 `pipeline` 维度转为 `node` + 单次执行维度（可选 `--run`）。

#### 4.2 `docuswarm init`：项目初始化

```bash
docuswarm init
```

- 详见 §3.1。

#### 4.3 `docuswarm nodes`：列出可用节点

```bash
docuswarm nodes
```

- 扫描 `nodes/` 目录，列出所有已配置节点及其最新 run 状态。
- 输出示例：

```
Node        Sequence  Latest Run   Status      Score
─────────────────────────────────────────────────────
analyst     1         a3f7b2c1     completed   0.85
pm          2         (none)       -           -
ux          3         (none)       -           -
architect   4         (none)       -           -
po          5         (none)       -           -
```

#### 4.4 `docuswarm start <node>`：执行指定节点

```bash
docuswarm start <node> --context <file> [--no-chain]
```

- 必填参数：
  - `<node>`：节点名（`analyst` / `pm` / `ux` / `architect` / `po`）。
  - `--context <file>`：项目上下文文件（所有节点均必填，用于计算 `context_hash` 以关联上下文链）。
- 可选参数：
  - `--no-chain`：禁用自动上下文链，不注入前序节点 deliverable。
- 主要步骤：
  1. 校验 `<node>` 是否存在于 `nodes/` 目录。
  2. 生成 `run_id`（8 位短 UUID）。
  3. 执行自动上下文链：查找前序节点最新成功 run，注入 deliverable（除非 `--no-chain`）。
  4. 基于 `node.yaml` + `persona.json` + `evaluator.yaml`，执行 dual-agent 流程：
     - Independent Agent 生成 deliverable + questions；
     - Evaluator Agent 进行评估与迭代（最多 3 次）。
  5. 将执行结果存入 `node_runs` 表，按 `(node, run_id)` 记录。

> **不再自动触发其他节点。** 用户按需手动调用：
>
> ```bash
> docuswarm start analyst --context project.yaml
> docuswarm start pm --context project.yaml
> docuswarm start ux --context project.yaml
> docuswarm start architect --context project.yaml
> docuswarm start po --context project.yaml
> ```

#### 4.5 `docuswarm runs <node>`：查看节点运行历史

```bash
docuswarm runs <node> [--limit N]
```

- 列出该节点的所有历史 run，按时间倒序。
- 输出示例：

```
Runs for: analyst
Run ID     Status      Score  Iterations  Created
──────────────────────────────────────────────────
a3f7b2c1   completed   0.85   1           2026-02-20 10:30
9e2d4f6a   failed      0.42   3           2026-02-19 15:20
```

#### 4.6 `docuswarm status <node>`：查看节点运行状态

```bash
docuswarm status <node> [--run <run-id>]
```

- 不带 `--run`：默认展示最近一次 run 的状态（迭代次数、verdict、评估分数等）。
- 带 `--run`：展示具体某次 run 的详细状态。
- 状态值：`pending` / `running` / `completed` / `failed` / `blocked`。

#### 4.7 `docuswarm export <node>`：导出单节点交付物

```bash
docuswarm export <node> [--run <run-id>] [--output <dir>]
```

- 导出该节点某次 run 的 deliverable。
- 未指定 `--run` 时，默认导出最近一次成功 run 的结果。
- 默认输出目录：`output/<node>/<run-id>/`
- 输出结构：

```text
output/
└── <node>/
    └── <run-id>/
        ├── deliverable.md
        ├── evaluation.json
        └── questions.json
```

#### 4.8 `docuswarm questions <node>`：查看节点问题

```bash
docuswarm questions <node> [--run <run-id>]
```

- 展示该节点某次 run 产生的 blocking / clarifying / optional 问题。
- `question-id` 格式：`<node>_<run-id-short>_<index>`（如 `analyst_a3f7_0`）。
- 输出保持分类显示（Blocking 醒目标记）。

#### 4.9 `docuswarm answer <question-id>`：回答问题

```bash
docuswarm answer <question-id> "<answer>"
```

- 从 `question-id` 解析出 `node` 与 `run_id`。
- 将答案写入该 run 的上下文中（`answers` 字段），供后续重新执行或其他节点使用。
- 回答本身不触发重新执行。

---

### 5. 状态与存储层调整

#### 5.1 数据模型

从「pipeline-centric」调整为「node-run-centric」：

**新增 `node_runs` 表（替代 `pipelines` + `node_results` 组合）：**

```sql
CREATE TABLE node_runs (
    run_id TEXT PRIMARY KEY,           -- 8 位短 UUID
    node_id TEXT NOT NULL,             -- analyst / pm / ux / architect / po
    context_hash TEXT NOT NULL,        -- context 文件内容 hash，用于上下文链关联
    context_file TEXT,                 -- 原始 context 文件路径
    status TEXT NOT NULL DEFAULT 'pending',
    iteration INTEGER NOT NULL DEFAULT 0,
    deliverable TEXT,                  -- JSON
    questions TEXT,                    -- JSON array
    evaluation TEXT,                   -- JSON
    answers TEXT,                      -- JSON (用户回答)
    chained_context TEXT,              -- JSON (自动注入的前序节点 deliverable)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'blocked')),
    CHECK (node_id IN ('analyst', 'pm', 'ux', 'architect', 'po'))
);

CREATE INDEX idx_node_runs_node ON node_runs(node_id, created_at DESC);
CREATE INDEX idx_node_runs_context ON node_runs(context_hash, node_id);
CREATE INDEX idx_node_runs_status ON node_runs(status);
```

**保留 `subject_context` 表** 用于缓存解析后的上下文数据（键从 `pipeline_id` 改为 `context_hash`），非必需时可延迟实现。

> **状态与判定的区别：**
> - `status`（run 级别）：`pending` / `running` / `completed` / `failed` / `blocked` — 描述 run 的生命周期。
> - `verdict`（迭代级别）：`APPROVED` / `NEEDS_REVISION` / `BLOCKED` — Evaluator Agent 的单次评审结论，内部驱动迭代循环，不直接暴露为 run status。

#### 5.2 上下文链查询逻辑

```python
def get_chained_deliverables(node_id: str, context_hash: str) -> dict:
    """获取当前节点的前序节点最新成功 deliverable。"""
    SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    current_idx = SEQUENCE.index(node_id)
    previous_nodes = SEQUENCE[:current_idx]

    chained = {}
    for prev_node in previous_nodes:
        latest_run = db.execute(
            "SELECT deliverable FROM node_runs "
            "WHERE node_id = ? AND context_hash = ? AND status = 'completed' "
            "ORDER BY created_at DESC LIMIT 1",
            (prev_node, context_hash)
        ).fetchone()
        if latest_run and latest_run["deliverable"]:
            chained[f"{prev_node}_deliverable"] = json.loads(latest_run["deliverable"])
    return chained
```

#### 5.3 日志与质量指标

- 日志上下文：所有日志事件绑定 `(node, run_id)` 以便追踪单次节点执行。
- 质量指标按节点维度聚合：
  - 每节点平均 alignment score；
  - 每节点平均迭代次数；
  - 每节点成功率。

---

### 6. 实施优先级

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | 新增 `node_runs` 表 + 迁移存储层 | 替代 pipeline-centric 数据模型 |
| P0 | 重构 `start` 命令为 `start <node>` | 核心交互变更 |
| P0 | 实现自动上下文链 | `context_hash` 关联 + 前序 deliverable 注入 |
| P1 | 新增 `init` / `nodes` / `runs` 命令 | 辅助命令 |
| P1 | 重构 `status` / `export` / `questions` / `answer` | 面向 `<node>` 维度 |
| P2 | 输出目录结构调整为 `output/<node>/<run-id>/` | 文件存储对齐 |
| P2 | 清理/废弃旧 `pipeline_id` 相关代码 | 移除已无用的 pipeline-centric 逻辑 |

---

### 7. 设计约束与原则

- **奥卡姆剃刀**：不引入不必要的抽象（如 node-id 后缀），直接用角色名作节点标识。
- **复用优先**：利用已有 `nodes/` 目录结构和 `node.yaml` 配置，不重新生成。
- **渐进式迁移**：存储层可保留旧表作过渡，但 CLI 仅暴露新的 node-centric 模式。
- **隐式智能**：上下文链自动注入，减少用户手动操作，但提供 `--no-chain` 逃逸阀。

本 correct-course 文档用于约束和指导 `@src` 下后续实现重构：
- 在不引入额外复杂度的前提下，简化用户心智模型；
- 明确 DocuSwarm 从「自动 pipeline 执行」转向「手动节点驱动」的设计方向。

---

### 8. 验收标准

| 编号 | 验收项 | 达成条件 |
|------|--------|----------|
| AC-1 | CLI 命令签名正确 | `docuswarm start <node> --context <file>` 可执行且不触发其他节点 |
| AC-2 | 上下文链生效 | PM 节点自动获取同 `context_hash` 的 Analyst 成功 deliverable |
| AC-3 | `--no-chain` 生效 | 使用该 flag 时不注入任何前序 deliverable |
| AC-4 | 数据模型迁移 | `node_runs` 表替代 `pipelines` + `node_results`，旧表不再被 CLI 访问 |
| AC-5 | Run 历史独立 | 同一节点多次执行产生独立 `run_id`，互不覆盖 |
| AC-6 | 导出结构正确 | `output/<node>/<run-id>/` 目录结构包含 deliverable、evaluation、questions |
| AC-7 | 无 pipeline 残留 | CLI 帮助文本、错误信息、日志中不再出现 `pipeline` 术语 |
| AC-8 | Agent 实际执行 | 每个节点的 DualAgentNode 被实际调用，deliverable 包含 LLM 生成的内容（非空占位符） |
| AC-9 | 文件输出有效 | 节点执行完成后，deliverable 文件写入 `output/{pipeline_id}/` 目录 |

---

### 9. 实现差距发现与修复计划

> **引用**: 详见 `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

#### 9.1 发现的关键问题

经深度代码分析发现，当前实现存在**两套并行的节点执行系统**未建立连接：

| 系统 | 位置 | 状态 | 问题 |
|------|------|------|------|
| **系统A: LangGraph Pipeline** | `pipeline/graph.py` | 正在使用 | `_create_default_node_executor()` 创建空占位符，不调用 Agent 逻辑 |
| **系统B: Node Execution** | `node_execution/executor.py` | 完整但未使用 | 包含完整的 DualAgentNode 集成，但从未被 Pipeline 调用 |

**直接后果**（假性成功）：
- Pipeline 状态正常流转至 `completed`，但所有 deliverable 均为空对象 `{}`
- IndependentAgent / EvaluatorAgent 从未被调用
- CreateDeliverableTool 从未被实例化
- 无文件生成到输出目录

#### 9.2 推荐修复方案：方案C（SDK Agent File + 动态 work_dir）

利用 kimi-agent-sdk 的 `agent_file` + `work_dir` 机制实现自然文件输出：

1. **启用 agent_file**: IndependentAgent 创建 Session 时传入 `agent_file` 配置，激活 CallableTool2 工具
2. **设置 work_dir**: 将输出目录设为 `output/{pipeline_id}/`，SDK 在此目录执行工具写入
3. **修改提示词**: 移除 "Respond only with JSON" 指令，明确要求 "MUST use create_deliverable tool"
4. **集成测试**: 端到端验证 proposal.md -> output/{pipeline_id}/*.md 文件生成

#### 9.3 修复优先级

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | 实施方案C：启用 agent_file + work_dir | 消除假性成功，实现实际 Agent 调用和文件输出 |
| P0 | 修改 IndependentAgent 提示词 | 从 JSON 输出改为工具调用输出 |
| P1 | 编写端到端集成测试 | 验证 deliverable 文件实际生成且内容非空 |
| P2 | 清理双系统并存 | 统一 graph.py 和 node_execution 为单一执行路径 |