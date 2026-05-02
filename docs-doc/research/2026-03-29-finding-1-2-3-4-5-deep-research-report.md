# DocuSwarm Finding 1-5 深度研究报告

**日期**: 2026-03-29  
**研究范围**: `docs/evaluation/2026-03-29-docuswarm-deep-technical-debt-review.md` 中的 Finding 1、2、3、4、5  
**研究目标**: 深度分析问题根源，设计统一解决方案（优先采用：统一重复功能、移除 legacy、移除 deprecated、移除向后兼容）

---

## 执行摘要

本研究对 DocuSwarm 项目的五个关键技术债务进行了深入分析，发现所有问题都指向一个核心架构问题：**职责边界模糊导致的重复实现和兼容层堆积**。所有解决方案都遵循统一原则：**统一重复功能、移除 legacy、移除 deprecated、消除向后兼容**。

| Finding | 严重级别 | 核心问题 | 解决策略 |
|---------|---------|---------|---------|
| F1 | P0 | Session Manager 初始化顺序错误 | 延迟注入 + 移除兼容层 |
| F2 | P0 | Pipeline ID 双轨导致不一致 | 移除自定义 ID 参数 |
| F3 | P1 | 节点执行器双轨实现 | 统一执行入口，删除重复代码 |
| F4 | P1 | 状态双轨模型 | state_json 作为唯一事实源 |
| F5 | P1 | 依赖/命名/文档漂移 | 清理未声明依赖和别名 |

---

## Finding 1: Session Manager 初始化链路故障 [P0]

### 1.1 问题深度分析

#### 1.1.1 代码路径分析

```
HybridOrchestrator.__init__() [line 90-138]
├── session_manager=None 被允许 [line 94]
├── ContextValidator(session_manager=None) [line 132]
│   └── self._session_manager = None
│
start_pipeline() [line 311-393]
├── validate_context_with_llm() [line 314] ← 报错点
│   └── 检查: if self._session_manager is None [line 1526]
│       └── raise RuntimeError("session_manager is required...")
│
└── _get_or_create_session_manager() [line 360] ← 创建在报错后
```

#### 1.1.2 根因分析

**问题 1: 构造函数允许空值，但业务方法要求非空**

```python
# ContextValidator.__init__ - 允许 None
class ContextValidator:
    def __init__(self, session_manager: KimiSessionManager | None = None):
        self._session_manager = session_manager  # 可以是 None

# validate_context_with_llm - 要求非空
async def validate_context_with_llm(self, ...):
    if self._session_manager is None:  # 运行时检查
        raise RuntimeError("session_manager is required...")
```

**问题 2: 初始化顺序错误**

```python
# orchestrator.py line 314: 先调用验证
await self._context_validator.validate_context_with_llm(subject_context)

# orchestrator.py line 360: 后创建 session_manager
session_manager = self._get_or_create_session_manager()
```

**问题 3: 兼容层增加复杂度**

`ContextValidator` 设计时考虑了"可选 LLM 验证"的场景，但实际上:
- 代码路径 `orchestrator.py:314` 强制调用 LLM 验证
- 没有非 LLM 验证的代码路径
- 这导致 `session_manager=None` 的场景实际上不可行

### 1.2 影响评估

| 影响维度 | 严重程度 | 说明 |
|---------|---------|------|
| 默认启动路径 | 🔴 阻塞 | 不传入 session_manager 时必然报错 |
| CLI 可用性 | 🔴 阻塞 | `pipeline_service.py:53-58` 不传入 session_manager |
| 开发者体验 | 🟡 高 | 需要知道隐式前置条件 |
| 测试覆盖 | 🟡 中 | 此路径无法被测试覆盖 |

### 1.3 解决方案（统一策略）

#### 推荐方案: 延迟注入模式（统一和简化）

**核心思想**: 移除构造函数依赖，改为调用时注入，消除无效兼容层

**实施步骤**:

1. **修改 `ContextValidator.__init__`**
```python
# BEFORE
class ContextValidator:
    def __init__(self, session_manager: KimiSessionManager | None = None):
        self._session_manager = session_manager
        # ... backward compatibility code ...

# AFTER - 移除 session_manager 参数
class ContextValidator:
    def __init__(self):
        self._validation_strategy = self._create_default_strategy()
        # 移除所有 backward compatibility 代码
```

2. **修改 `validate_context_with_llm`**
```python
# BEFORE
async def validate_context_with_llm(self, subject_context, ...):
    if self._session_manager is None:
        raise RuntimeError("...")
    # ...

# AFTER - 调用时注入
async def validate_context_with_llm(
    self, 
    subject_context: dict, 
    session_manager: KimiSessionManager,  # 必需参数
    ...
) -> ValidationResult:
    # 移除 None 检查，类型系统保证非空
    config = {"session_manager": session_manager}
    return await self._llm_validation_strategy.validate(subject_context, config)
```

3. **修改 `HybridOrchestrator.start_pipeline`**
```python
# BEFORE - 第 314 行直接调用验证
await self._context_validator.validate_context_with_llm(subject_context)

# AFTER - 先获取 session_manager，再验证
session_manager = self._get_or_create_session_manager()
await self._context_validator.validate_context_with_llm(
    subject_context, 
    session_manager=session_manager
)
```

4. **删除兼容代码**
- 删除 `ContextValidator` 中所有 `backward compatibility` 注释和代码块
- 删除 `_session_manager` 实例变量（不再需要）
- 删除 `_llm_validation_strategy` 的延迟初始化逻辑

### 1.4 验收标准

- [ ] `HybridOrchestrator(db_path=":memory:")` 可直接调用 `start_pipeline()` 不报错
- [ ] 移除 `ContextValidator` 所有 backward compatibility 代码
- [ ] 单元测试覆盖：不传 session_manager 也能正常启动

---

## Finding 2: 自定义 Pipeline ID 功能损坏 [P0]

### 2.1 问题深度分析

#### 2.1.1 代码路径分析

```python
# orchestrator.py line 318-331
# Step 2: Create pipeline in database
subject = subject_context.get("subject", "Untitled")
db_pipeline_id = self._state_manager.create_pipeline(  # ← 生成自动 ID
    subject=subject,
    subject_context=subject_context,
)

# Use provided pipeline_id or generated one
final_pipeline_id = pipeline_id or db_pipeline_id  # ← 可能使用自定义 ID

# Step 3: Update status to running
_ = self._state_manager.update_pipeline_status(
    final_pipeline_id,  # ← 使用可能不存在的 ID
    status=RUNNING,
    current_node=PIPELINE_NODES[0],
)
```

#### 2.1.2 根因分析

**问题 1: 数据库写入与更新使用不同 ID**

| 步骤 | 使用的 ID | 数据库是否存在 |
|------|----------|---------------|
| create_pipeline | 自动生成 (db_pipeline_id) | ✅ 是 |
| update_pipeline_status | final_pipeline_id (可能是自定义) | ❌ 可能否 |

**问题 2: StateManager 不支持显式 ID**

```python
# storage/state_manager.py line 129-165
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()  # ← 总是自动生成
    # ... 写入数据库
    return pipeline_id
```

**问题 3: 自定义 ID 从未真正工作**

- 代码中存在 `pipeline_id` 参数但从未正确实现
- 这是"看起来支持但实际上不支持"的虚假功能
- 维护此参数增加了认知负担

### 2.2 影响评估

| 影响维度 | 严重程度 | 说明 |
|---------|---------|------|
| 外部集成 | 🔴 高 | 外部系统无法使用稳定 ID 引用 |
| 恢复/取消 | 🔴 高 | 依赖 ID 一致性的功能损坏 |
| 日志追踪 | 🟡 中 | ID 不一致导致追踪困难 |
| 代码清晰度 | 🟡 中 | 虚假参数误导开发者 |

### 2.3 解决方案（移除优先）

#### 推荐方案: 完全移除自定义 ID 参数

**核心思想**: 删除从未工作的功能，简化架构

**实施步骤**:

1. **修改 `HybridOrchestrator.start_pipeline` 签名**
```python
# BEFORE
async def start_pipeline(
    self, 
    subject_context: dict, 
    pipeline_id: str | None = None,  # ← 删除此参数
) -> str:

# AFTER
async def start_pipeline(
    self, 
    subject_context: dict,
) -> str:
```

2. **简化 ID 处理逻辑**
```python
# BEFORE
db_pipeline_id = self._state_manager.create_pipeline(...)
final_pipeline_id = pipeline_id or db_pipeline_id  # ← 删除此行
_ = self._state_manager.update_pipeline_status(
    final_pipeline_id,  # ← 改为 db_pipeline_id
    ...
)

# AFTER
pipeline_id = self._state_manager.create_pipeline(...)
_ = self._state_manager.update_pipeline_status(
    pipeline_id,  # 直接使用
    ...
)
```

3. **更新所有调用点**
- 检查 `cli/services/pipeline_service.py`
- 检查所有测试用例
- 更新文档

4. **考虑未来扩展**
```python
# 如果未来确实需要自定义 ID，应在 StateManager 层支持
def create_pipeline(
    self, 
    subject: str, 
    subject_context: dict | None = None,
    pipeline_id: str | None = None,  # 在这里支持
) -> str:
    if pipeline_id is None:
        pipeline_id = self._generate_pipeline_id()
    # ... 使用传入的 ID
```

### 2.4 验收标准

- [ ] `start_pipeline()` 不再接受 `pipeline_id` 参数
- [ ] 所有调用点已更新
- [ ] 数据库中的 ID 与返回的 ID 始终一致
- [ ] 回归测试验证 ID 一致性

---

## Finding 3: 双轨节点执行器 [P1]

### 3.1 问题深度分析

#### 3.1.1 重复函数对比

| 函数 | node_execution/executor.py | nodes/dual_agent.py | 差异 |
|------|---------------------------|---------------------|------|
| `create_node_executor` | line 33 | line 926 | 输入类型不同 (NodeRunState vs PipelineState) |
| `_execute_node` | line 75 | line 961 | 执行逻辑几乎相同 |
| `_get_config` | line 314 | line 1061 | **配置来源完全不同** |

#### 3.1.2 配置来源分叉（严重问题）

```python
# node_execution/executor.py _get_config()
def _get_config() -> Config:
    """Loads configuration from .env file and YAML"""
    from autoBMAD.docuswarm.config import load_config
    return load_config()  # ← 统一配置加载

# nodes/dual_agent.py _get_config()
def _get_config():
    """reads from environment or uses defaults"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "test-api-key")
    db_path = Path(os.environ.get("DB_PATH", "docuswarm.db"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "output"))
    return Config(...)  # ← 直接读环境变量
```

#### 3.1.3 实际执行路径

```
pipeline/graph.py
└── create_pipeline_graph()
    └── 使用 create_integrated_node_executor (来自 node_execution/executor.py)
        └── 这是当前主路径

nodes/dual_agent.py:create_node_executor
└── 保留但可能未被使用
    └── 存在是为了 backward compatibility?
```

#### 3.1.4 根因分析

**问题 1: 职责边界不清**
- 节点执行逻辑应该只在 `node_execution` 模块
- `nodes/dual_agent.py` 应该只包含节点业务逻辑
- 历史原因导致执行器代码留在了两个地方

**问题 2: 配置系统不统一**
- 一套使用 `load_config()`（Config 类）
- 一套直接读环境变量
- 这会导致配置优先级不一致

**问题 3: Legacy 桥接代码**
```python
# nodes/dual_agent.py line 204-249
# 存在 legacy 参数到 NodeExecutionContext 的桥接逻辑
```

### 3.2 影响评估

| 影响维度 | 严重程度 | 说明 |
|---------|---------|------|
| 维护成本 | 🔴 高 | 改一个地方需要同步改另一个 |
| 配置一致性 | 🔴 高 | 两套配置来源可能产生不同结果 |
| 代码可读性 | 🟡 中 | 开发者不知道走哪条路径 |
| 测试覆盖 | 🟡 中 | 需要测试两套几乎相同的逻辑 |

### 3.3 解决方案（统一执行入口）

#### 推荐方案: 删除 nodes/dual_agent.py 中的执行器代码

**核心思想**: 唯一执行入口在 `node_execution/executor.py`，`nodes/dual_agent.py` 专注于节点业务逻辑

**实施步骤**:

1. **确认主路径**
```python
# 检查 pipeline/graph.py 确认使用哪个执行器
grep -n "create_node_executor\|create_integrated_node_executor" pipeline/graph.py
```

2. **从 dual_agent.py 删除以下函数**
```python
# 删除这些函数（约 150 行代码）
- create_node_executor()        # line 926-958
- _execute_node()               # line 961-1058
- _get_config()                 # line 1061-1079
```

3. **更新 dual_agent.py 的 `__all__`**
```python
# BEFORE
__all__ = [
    "NodeResult",
    "create_dual_agent_node",
    "create_node_executor",  # ← 删除
]

# AFTER
__all__ = [
    "NodeResult",
    "create_dual_agent_node",
]
```

4. **删除 legacy 桥接代码**
```python
# nodes/dual_agent.py line 204-249
# 删除 legacy 参数到 NodeExecutionContext 的桥接逻辑
```

5. **统一配置获取**
```python
# 确保 node_execution/executor.py 的 _get_config 是唯一配置入口
# 所有节点执行都通过这里获取配置
```

### 3.4 验收标准

- [ ] `nodes/dual_agent.py` 不再包含 `create_node_executor` 等执行器函数
- [ ] `nodes/dual_agent.py` 不再包含 `_get_config` 函数
- [ ] 删除所有 legacy 桥接代码
- [ ] 所有节点执行都通过 `node_execution/executor.py`
- [ ] 代码行数减少约 150 行

---

## Finding 4: 状态双轨模型 [P1]

### 4.1 问题深度分析

#### 4.1.1 数据库表结构

```sql
CREATE TABLE pipelines (
    pipeline_id TEXT PRIMARY KEY,
    subject TEXT,
    status TEXT,        -- 顶层列（与 state_json 重复）
    current_node TEXT,  -- 顶层列（与 state_json 重复）
    state_json TEXT,    -- JSON 包含完整状态
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 4.1.2 状态创建双轨

```python
# pipeline/state.py line 80-110
def create_initial_state(pipeline_id, subject_context) -> PipelineState:
    """TypedDict，包含 session_ids 等完整字段"""
    return PipelineState(
        pipeline_id=pipeline_id,
        subject_context=subject_context,
        session_ids={"pipeline": pipeline_session_id},  # 特有字段
        ...
    )

# storage/state_manager.py line 98-127
def _create_initial_state(self, pipeline_id, subject_context) -> dict:
    """本地复制，普通 dict，注释说明是"local copy""""
    return {
        "pipeline_id": pipeline_id,
        "subject_context": subject_context,
        # 缺少 session_ids 等字段
        ...
    }
```

#### 4.1.3 读写路径不一致

```
写入路径:
update_pipeline_status()
├── 更新顶层列 (status, current_node) [line 286-295]
└── 调用 _update_state_json_partial() 同步 state_json [line 301]

读取路径:
get_pipeline()
├── 读取 state_json [line 436-456]
└── 以 state_json 为准进行 flatten

list_pipelines()
├── 直接从顶层列读取 [line 483-509]
└── 不使用 state_json
```

#### 4.1.4 一致性检查的存在说明问题

```python
# storage/state_manager.py line 167-209
def _verify_state_consistency(self, pipeline_id):
    """运行时一致性检查 - P0 新增
    
    验证顶层字段与 state_json 的一致性
    发现不一致时记录警告
    """
    # 如果架构正确，不应该需要这个检查
```

### 4.2 影响评估

| 影响维度 | 严重程度 | 说明 |
|---------|---------|------|
| 数据一致性 | 🔴 高 | 读写来源不同可能导致看到不同状态 |
| 查询一致性 | 🔴 高 | list_pipelines vs get_pipeline 结果可能不同 |
| 代码复杂度 | 🟡 中 | 需要维护同步逻辑和一致性检查 |
| 维护成本 | 🟡 中 | 修改状态需要改多处 |

### 4.3 解决方案（单一事实源）

#### 推荐方案: state_json 作为唯一事实源

**核心思想**: state_json 包含完整状态，顶层列仅保留最小索引字段

**实施步骤**:

1. **删除重复的 `_create_initial_state`**
```python
# storage/state_manager.py
# 删除 _create_initial_state 方法（line 98-127）
# 统一使用 pipeline/state.py 的 create_initial_state

from autoBMAD.docuswarm.pipeline.state import create_initial_state
```

2. **修改 `create_pipeline` 使用统一函数**
```python
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()
    # 使用统一的 create_initial_state
    from autoBMAD.docuswarm.pipeline.state import create_initial_state
    initial_state = create_initial_state(pipeline_id, subject_context or {})
    state_json = json.dumps(initial_state)
    
    with self._db.acquire() as conn:
        conn.execute(
            "INSERT INTO pipelines (pipeline_id, subject, state_json) "
            "VALUES (?, ?, ?)",
            (pipeline_id, subject, state_json),
        )
    return pipeline_id
```

3. **简化 update_pipeline_status**
```python
def update_pipeline_status(self, pipeline_id, status, current_node=None):
    """只更新 state_json，不更新顶层列"""
    # 读取当前 state_json
    # 更新状态
    # 写回 state_json
    # 更新 updated_at
    
    # 移除顶层列的更新
    # 移除了 _update_state_json_partial 调用
```

4. **统一读取路径**
```python
def get_pipeline(self, pipeline_id):
    """从 state_json 读取完整状态"""
    with self._db.acquire() as conn:
        row = conn.execute(
            "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
            (pipeline_id,)
        ).fetchone()
        if row:
            return json.loads(row["state_json"])
    return None

def list_pipelines(self, status=None, limit=100):
    """也从 state_json 读取状态"""
    with self._db.acquire() as conn:
        rows = conn.execute(
            "SELECT state_json FROM pipelines ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        pipelines = []
        for row in rows:
            state = json.loads(row["state_json"])
            if status is None or state.get("status") == status:
                pipelines.append(state)
        return pipelines
```

5. **考虑数据库索引**
```sql
-- 如果需要按 status 查询，可以添加表达式索引
CREATE INDEX idx_pipeline_status ON pipelines(json_extract(state_json, '$.status'));
```

6. **删除一致性检查**
```python
# 删除 _verify_state_consistency 方法（不再需要）
```

### 4.4 验收标准

- [ ] 删除 `StateManager._create_initial_state`
- [ ] 统一使用 `pipeline/state.py:create_initial_state`
- [ ] `update_pipeline_status` 只更新 state_json
- [ ] `get_pipeline` 和 `list_pipelines` 都从 state_json 读取
- [ ] 删除 `_verify_state_consistency` 方法
- [ ] 状态读写结果始终一致

---

## Finding 5: 依赖、命名与文档漂移 [P1]

### 5.1 问题深度分析

#### 5.1.1 未声明依赖

| 依赖 | 使用位置 | pyproject.toml 声明 | 状态 |
|------|---------|--------------------|------|
| `kaos.path` | orchestrator.py:15 | ❌ 未声明 | 必须使用 |
| `kimi_agent_sdk` | approval.py:29 | ❌ 未声明 | 残留引用 |
| `kimi_agent_sdk._aggregator` | session_manager.py | ❌ 未声明 | 残留引用 |

#### 5.1.2 命名不一致

```python
# llm/session_manager.py line 687-693
KimiSessionManager = SessionManager  # 向后兼容别名

# 代码中混用
# orchestrator.py
session_manager: KimiSessionManager  # 使用别名

# node_execution/executor.py  
session_manager: SessionManager  # 使用真实名称
```

#### 5.1.3 Deprecated/Legacy 代码扫描

```
扫描结果:
- "deprecated": 多处
- "legacy": nodes/dual_agent.py line 204-249
- "backward compatibility": ContextValidator 等处
- "TODO.*remove": 多处
```

#### 5.1.4 文档不一致

```
docs/PRD.md: "完全移除 kimi-agent-sdk、零向后兼容"
实际代码: 仍导入 kimi_agent_sdk

README.md: 包含 Kimi 相关命名
```

### 5.2 影响评估

| 影响维度 | 严重程度 | 说明 |
|---------|---------|------|
| 部署风险 | 🔴 高 | 未声明依赖在目标环境可能不可用 |
| 开发者认知 | 🟡 中 | 命名不一致导致困惑 |
| 文档可信度 | 🟡 中 | 文档与代码不符 |
| 技术债务 | 🟡 中 | 残留代码增加维护成本 |

### 5.3 解决方案（清理和统一）

#### 推荐方案: 全面清理依赖和命名

**实施步骤**:

1. **移除 `kaos.path` 依赖**
```python
# orchestrator.py line 15
# BEFORE
from kaos.path import KaosPath

# AFTER - 使用标准库
from pathlib import Path

# 替换所有 KaosPath 使用为 Path
```

2. **移除 `kimi_agent_sdk` 残留**
```python
# approval.py line 29
# 移除 kimi_agent_sdk.ApprovalRequest 引用
# 使用 claude-agent-sdk 的对应类型

# session_manager.py
# 移除所有 kimi_agent_sdk 和 kimi_agent_sdk._aggregator 导入
```

3. **统一命名**
```python
# llm/session_manager.py
# 删除 KimiSessionManager = SessionManager 别名

# 更新所有使用 KimiSessionManager 的地方为 SessionManager
# orchestrator.py
# node_execution/executor.py
# nodes/dual_agent.py
```

4. **删除 deprecated/legacy 代码**
```python
# 删除所有标记为 deprecated 的函数
# 删除所有 backward compatibility 代码块
# 删除所有 TODO remove 的代码
```

5. **更新依赖声明**
```toml
# pyproject.toml
# 确保所有运行时依赖都已声明
# 移除未使用的依赖
```

6. **同步文档**
```
README.md: 移除 Kimi 命名，使用 SessionManager
docs/PRD.md: 确保与实际代码一致
```

### 5.4 验收标准

- [ ] 无 `kaos.path` 导入
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `KimiSessionManager` 使用
- [ ] pyproject.toml 声明所有运行时依赖
- [ ] 删除所有 deprecated/legacy 代码
- [ ] 文档与实际代码一致

---

## 综合实施计划

### 阶段 0: 紧急修复（P0）

**目标**: 修复启动链路故障

1. **Finding 1 + Finding 2 同时修复**
   - 修改 `ContextValidator` 移除 session_manager 构造函数参数
   - 修改 `start_pipeline` 先获取 session_manager 再验证
   - 移除 `pipeline_id` 参数
   - **预计代码变更**: 3 个文件，约 50 行修改
   - **预计时间**: 1 天

### 阶段 1: 主干收敛（P1）

**目标**: 统一执行入口和状态模型

2. **Finding 3: 统一节点执行器**
   - 删除 `nodes/dual_agent.py` 中的执行器代码
   - 删除 legacy 桥接
   - **预计代码变更**: 1 个文件，约 -150 行
   - **预计时间**: 半天

3. **Finding 4: 统一状态模型**
   - 删除 `_create_initial_state` 重复实现
   - 统一使用 state_json 作为事实源
   - 删除 `_verify_state_consistency`
   - **预计代码变更**: 2 个文件，约 100 行修改
   - **预计时间**: 1 天

### 阶段 2: 清理漂移（P1）

**目标**: 清理依赖和命名

4. **Finding 5: 清理依赖**
   - 移除 `kaos.path` 和 `kimi_agent_sdk`
   - 统一命名为 `SessionManager`
   - 删除 deprecated/legacy 代码
   - 更新文档
   - **预计代码变更**: 5+ 个文件
   - **预计时间**: 1 天

### 依赖关系

```
Finding 1 (Session Manager)
    ↓
Finding 2 (Pipeline ID) - 可在同一 PR 中修复
    ↓
Finding 3 (执行器) - 依赖于 F1 完成
    ↓
Finding 4 (状态模型) - 可并行
    ↓
Finding 5 (依赖清理) - 最后进行，清理所有残留
```

---

## 风险和缓解措施

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 修改引入新 Bug | 中 | 高 | 每个 Finding 都有验收标准，充分测试 |
| 外部依赖未声明依赖 | 高 | 高 | 在干净环境测试部署 |
| 删除代码导致功能缺失 | 低 | 高 | 确保删除的是真正未使用的代码 |
| 命名变更破坏 API | 中 | 中 | 检查所有导入点，一次性完成变更 |

---

## 附录

### A. 调试工具清单

本次研究创建了以下调试工具，位于 `tools/debt_research/`:

| 工具 | 用途 |
|------|------|
| `finding_1_session_manager_debug.py` | 分析 Session Manager 初始化链路 |
| `finding_2_pipeline_id_debug.py` | 分析 Pipeline ID 双轨问题 |
| `finding_3_dual_executor_debug.py` | 分析双轨执行器 |
| `finding_4_state_model_debug.py` | 分析状态双轨模型 |
| `finding_5_dependency_drift_debug.py` | 分析依赖和命名漂移 |
| `run_all_findings.py` | 批量运行所有调试工具 |

### B. 关键代码位置速查

| 组件 | 文件路径 | 关键行号 |
|------|---------|---------|
| Orchestrator | `pipeline/orchestrator.py` | 132, 314, 324 |
| ContextValidator | `context/validator.py` | 1526 |
| StateManager | `storage/state_manager.py` | 98-127, 167-209, 239-309 |
| Node Executor (主) | `node_execution/executor.py` | 33, 75, 314 |
| Node Executor (重复) | `nodes/dual_agent.py` | 926, 961, 1061 |
| Pipeline State | `pipeline/state.py` | 80-110 |

### C. 术语表

- **单一事实源 (Single Source of Truth)**: 数据只在一个地方权威存储
- **双轨模型 (Dual-track Model)**: 同一数据在两个地方存储，需要同步
- **Backward Compatibility**: 向后兼容，通常指保留旧接口
- **Legacy Code**: 遗留代码，通常需要被替换
- **Split-brain**: 分布式系统中数据不一致的状态
