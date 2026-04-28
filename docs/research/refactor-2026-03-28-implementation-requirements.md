# DocuSwarm 重构实施方案研究报告

**日期**: 2026-03-28  
**报告编号**: refactor-2026-03-28-implementation  
**作者**: Implementation Research Agent  
**关联文档**: 
- `docs/evaluation/2026-03-28-refactor-2026-03-26-implementation-review.md`
- `docs/research/refactor-2026-03-26/00-refactoring-roadmap.md`

---

## 执行摘要

本报告基于审查报告中的 5 项关键要求，对 `autoBMAD/docuswarm` 代码库进行了深度研究，并提供了详细的实施指南。所有研究结论已通过审计工具 `tools/refactor_implementation_auditor.py` 验证。

| 要求 | 当前状态 | 实施复杂度 | 预估工时 |
|------|----------|------------|----------|
| 1. system_prompt preset/append 结构 | 未实现（使用字符串） | 中 | 4h |
| 2. node.yaml evaluator 内联段 | 未实现（独立文件） | 低 | 2h |
| 3. 主执行链 SessionManager 接入 | 未实现（参数缺失） | 高 | 6h |
| 4. tests/__init__.py 语法错误 | 未修复 | 极低 | 5min |
| 5. NodeDeliverableConfig 扩展字段 | 未实现 | 低 | 2h |

**关键依赖关系**:
```
requirement_3 (主执行链接入)
    ├── depends on: requirement_1 (preset/append 支持)
    ├── depends on: requirement_2 (evaluator 配置来源)
    └── depends on: requirement_5 (deliverable 字段)
```

---

## 1. Claude Agent SDK system_prompt preset/append 高级结构

### 1.1 现状分析

**当前实现** (`session_manager.py:127-228`):

```python
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
    options_dict: dict[str, Any] = {
        "cwd": self._work_dir,
        "model": model,
        "permission_mode": permission_mode,
    }
    # ... MCP 配置 ...
    return ClaudeAgentOptions(**options_dict)  # system_prompt 未在此设置

async def create_session(
    self,
    # ...
    system_prompt: str | None = None,  # 接收字符串参数
) -> ClaudeSessionWrapper:
    options = self._create_options(mode=mode, yolo=yolo)
    if system_prompt is not None:
        options.system_prompt = system_prompt  # 直接赋值字符串
```

**问题诊断**:
1. `create_session` 接收 `system_prompt: str | None`，仅支持字符串格式
2. 调用方 (`independent.py:316-320`) 传递的是字符串格式的 persona + instructions
3. 未使用 Claude Agent SDK 支持的 `{"type": "preset", "preset": "claude_code", "append": ...}` 结构

### 1.2 目标实现

根据报告 05 (T-H) 的设计，四层提示词架构要求：

```python
# Layer 1: claude_code preset (内置工具说明)
# Layer 2+3+4: persona + task context + skills (append)

options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": system_prompt_append  # Layers 2+3+4
    }
)
```

### 1.3 实施步骤

#### Step 1: 修改 `SessionManager.create_session` 签名

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
async def create_session(
    self,
    mode: str = "agent",
    yolo: bool = True,
    max_steps: int | None = None,
    agent_file: Path | None = None,
    approval_handler_fn: Any | None = None,
    system_prompt: str | dict[str, Any] | None = None,  # 支持 dict 格式
) -> ClaudeSessionWrapper:
```

#### Step 2: 修改 `create_session` 内部逻辑

```python
# 创建 options
options = self._create_options(mode=mode, yolo=yolo)

# 处理 system_prompt
if system_prompt is not None:
    if isinstance(system_prompt, dict):
        # 已经是 dict 格式 (preset/append)
        options.system_prompt = system_prompt
    else:
        # 字符串格式 - 包装为 append 结构
        options.system_prompt = {
            "type": "preset",
            "preset": "claude_code",
            "append": system_prompt
        }
```

#### Step 3: 验证 SDK 版本兼容性

```python
# 在 _create_options 中添加调试日志
if isinstance(options.system_prompt, dict):
    self._logger.debug(
        "using_preset_system_prompt",
        preset=options.system_prompt.get("preset"),
        has_append=bool(options.system_prompt.get("append")),
    )
```

### 1.4 关键实现细节

**预设内容说明**:
- `claude_code` preset 包含 Claude Code 的工具使用说明、安全指令等
- `append` 内容会被追加到 preset 之后，形成完整的 system prompt
- Token 预算: preset ~2000 tokens + append ~3200 tokens = ~5200 tokens total

**拒绝向后兼容**:
- 不保留字符串直接赋值路径
- 所有调用方必须适配新的 dict 格式或接受自动包装
- 删除 `options.system_prompt = system_prompt` 这种直接字符串赋值

---

## 2. node.yaml evaluator 内联引用段

### 2.1 现状分析

**当前状态**:
- 5 个节点的 `node.yaml` 均无 `evaluator` 字段
- `NodeLoader` 从独立 `evaluator.yaml` 文件加载评估配置

**当前加载逻辑** (`loader.py:218-220`):

```python
node_config = cls._load_yaml(node_dir / "node.yaml")
persona = cls._load_json(node_dir / "persona.json")
evaluator = cls._load_yaml(node_dir / "evaluator.yaml")  # 固定路径加载
```

### 2.2 目标实现

**node.yaml 新增 evaluator 段**:

```yaml
# node.yaml schema v2.1
evaluator:
  criteria_file: evaluator.yaml  # 引用外部文件（可选，默认 evaluator.yaml）
  threshold:
    approval: 0.70
    escalation: 0.50
  max_iterations: 3
  model: sonnet  # 可选，默认继承 agent.model
```

### 2.3 实施步骤

#### Step 1: 更新所有 node.yaml 文件

为 5 个节点添加 evaluator 段：

**analyst/node.yaml**:
```yaml
evaluator:
  criteria_file: evaluator.yaml
  threshold:
    approval: 0.70
    escalation: 0.50
  max_iterations: 3
```

**architect/node.yaml**（阈值不同）:
```yaml
evaluator:
  criteria_file: evaluator.yaml
  threshold:
    approval: 0.75  # 更高要求
    escalation: 0.55
  max_iterations: 3
```

其他节点类似（pm, ux, po）。

#### Step 2: 修改 `NodeLoader._build_node_config`

**文件**: `autoBMAD/nodes/loader.py`

```python
# 从 node.yaml 读取 evaluator 配置（优先）
evaluator_data = config.get("evaluator", {})

# 如果指定了 criteria_file 或没有 evaluator 段，从文件加载
if evaluator_data.get("criteria_file") or not evaluator_data:
    criteria_file = evaluator_data.get("criteria_file", "evaluator.yaml")
    evaluator_file = node_dir / criteria_file
    if evaluator_file.exists():
        file_evaluator = cls._load_yaml(evaluator_file)
        # 合并配置（node.yaml 优先）
        evaluator_data = {**file_evaluator, **evaluator_data}

# 构建 evaluator config
evaluator_config = NodeEvaluatorConfig(
    criteria=evaluator_data.get("criteria", []),
    threshold=evaluator_data.get("threshold", {"approval": 0.7, "escalation": 0.5}),
    max_iterations=evaluator_data.get("max_iterations", 3),
    model=evaluator_data.get("model"),  # 可选
)
```

#### Step 3: 更新 `NodeEvaluatorConfig`

```python
@dataclass
class NodeEvaluatorConfig:
    """Configuration for the evaluator agent."""
    criteria: list[dict[str, Any]] = field(default_factory=list)
    threshold: dict[str, float] = field(default_factory=dict)
    max_iterations: int = 3
    model: str | None = None  # 新增：可选模型配置
    criteria_file: str | None = None  # 新增：引用的外部文件
```

### 2.4 关键决策

**保留 evaluator.yaml 吗？**
- 方案 A: 完全内联（删除 evaluator.yaml）- 不推荐，criteria 列表可能很长
- **方案 B**: node.yaml 引用 + evaluator.yaml 存储 criteria（推荐）
- 方案 C: 完全独立（当前状态）

本报告采用方案 B：node.yaml 存储运行参数（threshold, max_iterations），evaluator.yaml 存储评审标准（criteria）。

---

## 3. 主执行链 SessionManager 接入 node_id 和 tool_permissions

### 3.1 现状分析

**问题代码** (`independent.py:676-682`):

```python
# Create new session manager with work_dir for this pipeline execution
pipeline_session_manager = SessionManager(
    work_dir=output_dir,
    agent_file=self._agent_file,
    config=self.session_manager.config if self.session_manager else None,
    # 缺少: node_id=self.node_id
    # 缺少: allowed_dirs=...
)
```

**影响**: 
- `SessionManager._create_options()` 中 `self._node_id` 为 None
- MCP 服务器和工具权限配置被跳过（`if self._node_id and self._allowed_dirs:` 条件不满足）
- 节点无法使用文件读取/搜索工具

### 3.2 目标实现

**修改 `execute_with_input` 方法**，在创建 SessionManager 时传入：
1. `node_id`: 用于标识节点，生成 MCP 服务器名称
2. `tool_permissions`: 从 node_config 获取的文件/搜索权限

### 3.3 实施步骤

#### Step 1: 获取节点配置

```python
async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
) -> IndependentOutput:
    # ... 现有代码 ...
    
    # 加载节点配置获取 tool_permissions
    from autoBMAD.nodes.loader import NodeLoader
    
    node_config = NodeLoader.load(self.node_id)
    tool_permissions = node_config.tool_permissions
    
    # 转换权限为 allowed_dirs 格式
    allowed_read_dirs = tool_permissions.file_permissions.allowed_read_dirs
    search_dirs = tool_permissions.search_permissions.search_dirs
    
    # 合并为绝对路径（相对于 project_root）
    import os
    abs_allowed_dirs = [
        str(self.project_root / d) for d in allowed_read_dirs
    ]
```

#### Step 2: 创建带权限的 SessionManager

```python
# Create new session manager with full configuration
pipeline_session_manager = SessionManager(
    work_dir=output_dir,
    agent_file=self._agent_file,
    config=self.session_manager.config if self.session_manager else None,
    node_id=self.node_id,  # 新增
    allowed_dirs=abs_allowed_dirs,  # 新增
)
```

#### Step 3: 验证工具可用性

```python
# 在 _call_llm_with_prompts 中添加调试日志
async def _call_llm_with_prompts(self, ...):
    sm = self.session_manager
    assert sm is not None
    
    # 验证 node_id 和 allowed_dirs 已设置
    if not sm.node_id:
        self.logger.warning("session_manager_missing_node_id")
    if not sm.allowed_dirs:
        self.logger.warning("session_manager_missing_allowed_dirs")
    
    # ... 创建 session ...
```

### 3.4 复杂依赖处理

**文件权限 vs 搜索权限分离**:

当前 `SessionManager` 使用同一 `allowed_dirs` 配置 file 和 search 权限，但 node.yaml 中这两个权限可能不同：

```yaml
tools:
  file_permissions:
    allowed_read_dirs:
      - "docs/"
      - "docs/research/"
  search_permissions:
    search_dirs:
      - "docs/"  # 搜索范围可能更小
```

**解决方案**:

修改 `SessionManager.__init__` 支持分离的权限配置：

```python
def __init__(
    self,
    work_dir: Path,
    # ...
    node_id: str | None = None,
    file_dirs: list[str] | None = None,  # 新增：文件权限目录
    search_dirs: list[str] | None = None,  # 新增：搜索权限目录
) -> None:
    # ...
    self._file_dirs = file_dirs or []
    self._search_dirs = search_dirs or []

# 在 _create_options 中
tool_permissions = NodeToolPermissions(
    file_permissions=NodeFilePermissions(allowed_read_dirs=self._file_dirs),
    search_permissions=NodeSearchPermissions(search_dirs=self._search_dirs),
)
```

---

## 4. 修复 tests/__init__.py 语法错误

### 4.1 问题描述

**文件内容** (`tests/__init__.py:1`):
```
: DocuSwarm test suite.
```

**错误**: 这是无效的 Python 语法，会导致 `pytest` 无法加载测试。

### 4.2 修复方案

**修改为**:
```python
# DocuSwarm test suite.
"""DocuSwarm test suite."""
```

### 4.3 验证

```bash
python -c "import tests; print('OK')"
python -m pytest tests/ --collect-only 2>&1 | head -20
```

---

## 5. NodeDeliverableConfig 扩展字段

### 5.1 现状分析

**当前定义** (`loader.py:59-64`):

```python
@dataclass
class NodeDeliverableConfig:
    """Configuration for the node's deliverable."""
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)
    # 缺少: template_title, output_filename, format_hints
```

**当前解析** (`loader.py:379-384`):

```python
deliverable_config = NodeDeliverableConfig(
    type=config["deliverable_type"],
    required_sections=deliverable_data.get("required_sections", [])
    # 未解析 template_title, output_filename, format_hints
)
```

### 5.2 目标实现

**扩展 `NodeDeliverableConfig`**:

```python
@dataclass
class NodeDeliverableConfig:
    """Configuration for the node's deliverable."""
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)
    template_title: str | None = None  # 新增
    output_filename: str | None = None  # 新增
    format_hints: dict[str, Any] = field(default_factory=dict)  # 新增
```

### 5.3 实施步骤

#### Step 1: 更新数据类定义

**文件**: `autoBMAD/nodes/loader.py`

```python
@dataclass
class NodeDeliverableConfig:
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)
    template_title: str | None = None
    output_filename: str | None = None
    format_hints: dict[str, Any] = field(default_factory=dict)
```

#### Step 2: 更新解析逻辑

```python
# Build deliverable config
deliverable_config = NodeDeliverableConfig(
    type=config["deliverable_type"],
    required_sections=deliverable_data.get("required_sections", []),
    template_title=deliverable_data.get("template_title"),
    output_filename=deliverable_data.get("output_filename"),
    format_hints=deliverable_data.get("format_hints", {}),
)
```

#### Step 3: 更新 node.yaml 文件

为所有节点补充 deliverable 扩展字段：

**analyst/node.yaml**:
```yaml
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
  template_title: "Business Analysis Report"  # 新增
  output_filename: "analyst-report.md"  # 新增
  format_hints:  # 新增
    max_words: 3000
    target_audience: "Product and Engineering teams"
    tone: "analytical, evidence-based"
```

其他节点类似。

### 5.4 消费者更新

**contract_builder.py** 已支持读取这些字段（通过 `reqs.get("template_title")`），但需要确保它们进入 `deliverable_requirements`。

检查 `ContextManager.build_independent_input` 是否正确传递：

```python
# 在 isolation.py 中
deliverable_requirements = {
    "required_sections": node_config.deliverable.required_sections,
    "template_title": node_config.deliverable.template_title,  # 新增
    "output_filename": node_config.deliverable.output_filename,  # 新增
    "format_hints": node_config.deliverable.format_hints,  # 新增
}
```

---

## 6. 实施顺序建议

基于依赖关系，推荐按以下顺序实施：

```
Phase 1: 基础修复（无依赖）
├── Step 4: 修复 tests/__init__.py 语法错误（5分钟）
└── Step 5: NodeDeliverableConfig 扩展字段（2小时）
    └── 并行: 更新所有 node.yaml 的 deliverable 段

Phase 2: 配置层改造
├── Step 2: node.yaml evaluator 内联段（2小时）
└── Step 1: system_prompt preset/append 结构（4小时）

Phase 3: 执行层整合（依赖 Phase 1 和 2）
└── Step 3: 主执行链 SessionManager 接入（6小时）
    ├── 依赖: node_id/tool_permissions 配置就绪（Phase 1, 2）
    └── 依赖: preset/append 结构就绪（Phase 2）

Phase 4: 验证
└── 运行 audit 工具验证所有检查通过
```

---

## 7. 审计工具

已创建 `tools/refactor_implementation_auditor.py` 用于验证实施进度。

**用法**:
```bash
python tools/refactor_implementation_auditor.py
```

**预期输出**（全部完成后）:
```
================================================================================
统计
================================================================================
  通过: 8
  失败: 0
  警告: 0
  未找到: 0

[OK] 所有关键检查通过！
```

---

## 附录 A: 关键代码片段

### A.1 完整的 SessionManager 修改

```python
# session_manager.py

class SessionManager:
    def __init__(
        self,
        work_dir: Path,
        agent_file: Path | None = None,
        config: Any | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        node_id: str | None = None,
        file_dirs: list[str] | None = None,  # 替代 allowed_dirs
        search_dirs: list[str] | None = None,  # 新增分离的搜索权限
    ) -> None:
        # ...
        self._node_id = node_id
        self._file_dirs = file_dirs or []
        self._search_dirs = search_dirs or []

    async def create_session(
        self,
        mode: str = "agent",
        yolo: bool = True,
        max_steps: int | None = None,
        agent_file: Path | None = None,
        approval_handler_fn: Any | None = None,
        system_prompt: str | dict[str, Any] | None = None,
    ) -> ClaudeSessionWrapper:
        # ...
        if system_prompt is not None:
            if isinstance(system_prompt, dict):
                options.system_prompt = system_prompt
            else:
                options.system_prompt = {
                    "type": "preset",
                    "preset": "claude_code",
                    "append": system_prompt
                }
```

### A.2 完整的 IndependentAgent.execute_with_input 修改

```python
# independent.py

async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
) -> IndependentOutput:
    # ... 提取 agent_input 字段 ...
    
    # 加载节点配置
    from autoBMAD.nodes.loader import NodeLoader
    node_config = NodeLoader.load(self.node_id)
    
    # 计算输出目录
    output_dir = self.project_root / "output" / pipeline_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 准备权限目录（绝对路径）
    file_dirs = [
        str(self.project_root / d)
        for d in node_config.tool_permissions.file_permissions.allowed_read_dirs
    ]
    search_dirs = [
        str(self.project_root / d)
        for d in node_config.tool_permissions.search_permissions.search_dirs
    ]
    
    # 创建带完整配置的 SessionManager
    pipeline_session_manager = SessionManager(
        work_dir=output_dir,
        agent_file=self._agent_file,
        config=self.session_manager.config if self.session_manager else None,
        node_id=self.node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
    )
    
    # ... 执行流程 ...
```

---

## 附录 B: 完整的 node.yaml 示例

```yaml
# Schema Version: 2.1
schema_version: "2.1"

node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist
sequence: 1
deliverable_type: analyst-report

task:
  name: create-business-analysis-report
  description: Transform raw data into actionable business insights
  role_supplement: Focus on evidence-based conclusions

deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
  template_title: "Business Analysis Report"
  output_filename: "analyst-report.md"
  format_hints:
    max_words: 3000
    target_audience: "Product and Engineering teams"
    tone: "analytical, evidence-based"

agent:
  type: independent
  model: sonnet
  temperature: 0.7

runtime:
  timeout: 300
  retry_max_attempts: 3
  retry_backoff: 1.5

evaluator:
  criteria_file: evaluator.yaml
  threshold:
    approval: 0.70
    escalation: 0.50
  max_iterations: 3

tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs:
      - "docs/"
      - "docs/research/"
  search_permissions:
    search_dirs:
      - "docs/"

questions:
  - id: q1
    text: "What is the business context?"
    required: true

dependencies: []
```

---

*报告完成*
