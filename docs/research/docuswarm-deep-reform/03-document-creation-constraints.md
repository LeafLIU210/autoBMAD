# 文档创建约束与模板对齐研究报告

**报告编号**: DS-2026-03-06-001  
**研究日期**: 2026-04-06  
**研究阶段**: 深度改革研究  
**报告版本**: 1.0  

---

## 1. 概述

### 1.1 研究目标

本研究深入分析DocuSwarm中文档创建的数量约束机制及其实施方案，包括：

1. **约束需求分析**：五个节点（analyst、pm、ux、architect、po）不同的文档创建数量要求
   - 单文档约束：analyst、pm、ux 各节点只能创建1份文档
   - 多文档约束：architect、po 节点需支持创建多份文档

2. **现有实现审查**：`create_deliverable` 工具、validator校验框架、节点执行机制

3. **约束实施方案**：三种技术方案比较与选择

4. **模板对齐机制**：BMAD模板系统与DocuSwarm节点配置的集成策略

5. **数据结构改造**：支持单/多文档的数据结构设计

### 1.2 研究背景

**核心矛盾**：
- 当前系统设计对应的 `create_deliverable` 工具是单文档型的，但五个节点有不同的创建需求
- Validator 强制验证 deliverable 包含 `file_path` 和 `sha256`（只能由工具调用返回），确保每次调用都真实创建文件
- 节点配置文件（node.yaml）缺乏数量约束声明字段

**关键约束**：
- Analyst 分析一个产品应该只输出一份分析报告
- PM 创建一份PRD
- UX 设计一套UX设计规范
- Architect 可能需要创建多份文档（系统架构、API设计、数据库设计等）
- PO 需要创建：产品视景、路线图、Epic列表、Story列表等（可能是4-5份独立文档）

---

## 2. 当前交付物创建机制分析

### 2.1 CreateDeliverableTool 工具设计

**文件位置**：`d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/tools/create_deliverable.py`

#### 2.1.1 工具参数

```python
class CreateDeliverableParams(BaseModel):
    """Parameters for creating a deliverable.
    
    Attributes:
        title: The deliverable title.
        content: The deliverable content in Markdown format.
        metadata: Additional metadata for the deliverable.
    """
    
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
```

**关键特性**：
- 参数简洁，仅接收 `title`、`content` 和可选 `metadata`
- 无数量限制参数（如 `index` 或 `sequence`）
- 无文档类型标识（如 `doc_type` 或 `template_id`）

#### 2.1.2 工具返回值

```python
metadata = {
    "title": params.title,
    "file_path": str(file_path),      # ← 关键：仅工具可返回
    "sha256": sha256_hash,             # ← 关键：LLM无法伪造
    "word_count": word_count,
    "section_index": section_index,
    "content_type": "markdown",
}

return ToolResult(
    success=True,
    result=metadata,
)
```

**意义**：
- `file_path` 和 `sha256` 是**真实文件的凭证**
- LLM 无法伪造有效的 SHA256 哈希
- 这是确保工具真实调用的关键机制

#### 2.1.3 当前限制

1. **单次调用返回单个文件**：每次调用创建一个文件
2. **无文档编号机制**：多个文档无法通过参数区分
3. **无分组或序列机制**：无法表达"这是Epic列表的第3个文档"
4. **无条件判断**：工具本身不进行数量约束检查

### 2.2 Validator 对 Deliverable 的校验

**文件位置**：`d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/context/validator.py` (行631-750)

#### 2.2.1 校验策略

```python
class IndependentOutputValidationStrategy(ValidationStrategy):
    """Strategy for validating IndependentAgent output."""
    
    def _validate_deliverable(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate deliverable field structure."""
        
        # 必需字段检查
        if "deliverable" not in data:
            result.add_error("deliverable", "required field missing", "MISSING_DELIVERABLE")
            return
        
        deliverable = data["deliverable"]
        
        # Title: 必需 + 必须是字符串
        if "title" not in deliverable:
            result.add_error("deliverable.title", "required field missing", "MISSING_TITLE")
        elif not isinstance(deliverable["title"], str):
            result.add_error("deliverable.title", "must be a string", "INVALID_TITLE_TYPE")
        
        # file_path: 必需 + 必须是字符串
        if "file_path" not in deliverable:
            result.add_error("deliverable.file_path", "required field missing", "MISSING_FILE_PATH")
        elif not isinstance(deliverable["file_path"], str):
            result.add_error("deliverable.file_path", "must be a string", "INVALID_FILE_PATH_TYPE")
        
        # sha256: 必需 + 必须是字符串
        if "sha256" not in deliverable:
            result.add_error("deliverable.sha256", "required field missing", "MISSING_SHA256")
        elif not isinstance(deliverable["sha256"], str):
            result.add_error("deliverable.sha256", "must be a string", "INVALID_SHA256_TYPE")
        
        # 可选字段
        if "summary" in deliverable and not isinstance(deliverable["summary"], str):
            result.add_error("deliverable.summary", "must be a string", "INVALID_SUMMARY_TYPE")
        
        if "content" in deliverable and not isinstance(deliverable["content"], str):
            result.add_error("deliverable.content", "must be a string", "INVALID_CONTENT_TYPE")
```

#### 2.2.2 校验特性分析

| 字段 | 必需 | 类型要求 | 由谁提供 | 意义 |
|------|------|---------|---------|------|
| `title` | ✓ | string | LLM可提供 | 文档标题 |
| `file_path` | ✓ | string | **仅工具** | 文件路径凭证 |
| `sha256` | ✓ | string | **仅工具** | 内容完整性凭证 |
| `summary` | ✗ | string | LLM可提供 | 文档摘要 |
| `content` | ✗ | string | LLM可提供 | 完整内容（非必需） |
| `metadata` | ✗ | dict | LLM可提供 | 自定义元数据 |

**关键发现**：
- Validator **强制要求** `file_path` 和 `sha256`
- 这意味着 **每个 deliverable 对象必须对应一个真实的文件**
- 因此 **LLM 无法伪造多个 deliverable 对象**
- 要创建多个文档，必须真实调用多次 `create_deliverable` 工具

### 2.3 节点执行当前行为

#### 2.3.1 独立Agent执行流程（DualAgentNode）

**文件位置**：`d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/nodes/dual_agent.py`

```python
@dataclass
class NodeResult:
    """Result from DualAgentNode execution."""
    
    deliverable: dict[str, Any]       # ← 单个deliverable对象
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any]
    iteration: int
    timestamp: datetime
    force_completion: ForceCompletion | None = None
```

**现状**：
- `NodeResult.deliverable` 是**单个字典对象**，不是列表
- 每个节点执行只返回一个 deliverable
- 无多文档支持

#### 2.3.2 节点配置文件分析

**所有5个节点的node.yaml**都采用相同结构：

```yaml
# 例：analyst/node.yaml
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations

# 例：po/node.yaml
deliverable:
  required_sections:
    - product_vision
    - roadmap
    - epic_list
    - story_list
    - prioritization_rationale
    - dependencies
    - release_plan
```

**观察**：
- PO 节点的 `required_sections` 列出了7个章节
- 这暗示 PO 需要在单个文档中覆盖这7个部分
- 但实际上，PO 应该创建多份文档（每个类型一份）
- 当前配置**混淆了多文档需求和单文档结构**

---

## 3. 单文档约束方案（Analyst、PM、UX）

### 3.1 需求分析

这三个节点应该各创建**恰好1份**文档：

| 节点 | 文档类型 | 职责 | 约束 |
|------|----------|------|------|
| **Analyst** | 业务分析报告 | 分析业务需求、市场、用户 | 创建1份 |
| **PM** | 产品需求文档 | 定义产品功能和非功能需求 | 创建1份 |
| **UX** | UX设计规范 | 用户流程、线框图、交互设计 | 创建1份 |

### 3.2 三种实施方案对比

#### 方案 A：在 node.yaml 中配置 max_deliverables=1

**实现**：

```yaml
# analyst/node.yaml（增强）
deliverable:
  max_deliverables: 1              # ← 新增字段
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
```

**优点**：
- ✓ 配置集中，易于理解
- ✓ 不需要修改工具或validator
- ✓ 配置文件本身成为约束声明

**缺点**：
- ✗ 需要修改所有5个node.yaml
- ✗ 约束检查由谁负责？（需要在orchestrator或pipeline层实现）
- ✗ 超出约束时的错误处理路径不清晰
- ✗ 与validator的关系模糊

**检查实现点**：
```python
# 在 DualAgentNode 或 Orchestrator 中
max_deliverables = node_config.deliverable.get("max_deliverables")
if max_deliverables and delivered_count > max_deliverables:
    raise Exception(f"Node {node_id} exceeded max_deliverables limit")
```

#### 方案 B：在 create_deliverable 工具中添加调用计数器

**实现**：

```python
# CreateDeliverableTool 维护调用计数器
class CreateDeliverableTool(ToolResultCallableTool[CreateDeliverableParams]):
    def __init__(self, node_id: str, max_calls: int = None):
        self.node_id = node_id
        self.max_calls = max_calls
        self.call_count = 0
    
    async def _execute(self, params: CreateDeliverableParams) -> ToolResult:
        self.call_count += 1
        
        # 如果超过限制，拒绝调用
        if self.max_calls and self.call_count > self.max_calls:
            return ToolResult(
                success=False,
                error=f"Node {self.node_id} can only create {self.max_calls} deliverable(s), "
                      f"but already created {self.call_count - 1}"
            )
        
        # ... 正常创建逻辑
```

**优点**：
- ✓ 约束在工具层实现，最接近实际限制
- ✓ LLM 会立即看到错误信息，能自行修正
- ✓ 不需要修改validator或node.yaml schema

**缺点**：
- ✗ 工具初始化时需要传入 `max_calls` 参数
- ✗ 参数来源？从node.yaml读取还是硬编码？
- ✗ 计数器状态：内存中还是持久化？
- ✗ 如果调用失败并重试，计数器如何处理？

**关键问题**：计数器的生命周期
- 如果是内存中，节点重启后重置
- 如果是持久化，需要数据库支持
- 如果是per-session，需要session_id关联

#### 方案 C：在 validator 中添加数量校验规则（推荐）

**实现**：

```python
# validator.py 中添加新的校验方法
class IndependentOutputValidationStrategy(ValidationStrategy):
    
    def validate(self, data: dict[str, Any], config: dict[str, Any] | None = None) -> ValidationResult:
        """Validate IndependentAgent output structure."""
        result = ValidationResult(valid=True)
        config = config or {}
        
        # 验证 deliverable 结构
        self._validate_deliverable(data, result)
        
        # 新增：验证 deliverable 数量
        self._validate_deliverable_count(data, config, result)
        
        # ... 其他验证
        return result
    
    def _validate_deliverable_count(self, data: dict[str, Any], config: dict[str, Any], result: ValidationResult) -> None:
        """验证 deliverable 数量是否超过限制。
        
        Args:
            data: The output data dictionary
            config: Node-specific rules including max_deliverables
            result: ValidationResult to collect issues into
        """
        max_deliverables = config.get("max_deliverables")
        if max_deliverables is None:
            return  # 无限制
        
        # 当前实现：单个deliverable对象
        if "deliverable" in data and isinstance(data["deliverable"], dict):
            # 未来支持列表形式时的处理
            deliverable_count = 1
        else:
            deliverable_count = 0
        
        if deliverable_count > max_deliverables:
            result.add_error(
                field="deliverable",
                message=f"Number of deliverables ({deliverable_count}) exceeds limit ({max_deliverables})",
                code="DELIVERABLE_COUNT_EXCEEDED",
            )
```

**在 validator 中的集成**：

```python
# validator.py 中存储规则
DEFAULT_VALIDATION_RULES: dict[str, Any] = {
    "min_word_count": 100,
    "required_sections": ["analysis"],
    "allow_empty_output": False,
    "max_deliverables": None,  # ← 新增，默认无限制
}

# ValidationRuleRegistry 中每个节点的规则
class ValidationRuleRegistry:
    def __init__(self):
        self.rules = {
            "analyst": {**DEFAULT_VALIDATION_RULES, "max_deliverables": 1},
            "pm": {**DEFAULT_VALIDATION_RULES, "max_deliverables": 1},
            "ux": {**DEFAULT_VALIDATION_RULES, "max_deliverables": 1},
            "architect": {**DEFAULT_VALIDATION_RULES, "max_deliverables": None},  # 无限制
            "po": {**DEFAULT_VALIDATION_RULES, "max_deliverables": None},  # 无限制
        }
```

**优点**：
- ✓ 约束与其他验证规则一致，集中管理
- ✓ Validator已有"单一真相源"地位（当前检查file_path和sha256）
- ✓ 不需要修改node.yaml schema
- ✓ 可以按节点配置不同的限制

**缺点**：
- ✗ 当前的validator对象是无状态的（每次调用创建新实例）
- ✗ 无法计数同一节点的多次调用
- ✗ 只能验证单次调用的输出，无法验证"累积"超限
- ✗ 需要在orchestrator层面做跨迭代计数

### 3.3 推荐方案

**选择方案 A + C 的混合**：

1. **在 node.yaml 中添加 `max_deliverables: 1`**（方案A的好处：配置清晰）
2. **在 validator 中检查 max_deliverables 配置**（方案C的好处：验证统一）
3. **在 Orchestrator 中追踪累积计数**（补充方案B的好处：真实约束）

**实施步骤**：

```yaml
# 更新 analyst/node.yaml、pm/node.yaml、ux/node.yaml
deliverable:
  max_deliverables: 1              # ← 新增
  required_sections:
    - ...
```

```python
# 在 ValidationRuleRegistry 中
rules = {
    "analyst": {
        "max_deliverables": 1,
        "required_sections": [...],
    },
    # ...
}

# 在 Orchestrator 中（伪代码）
node_id = current_node.id
max_allowed = registry.get_rules(node_id).get("max_deliverables")

for iteration in range(max_iterations):
    result = await dual_agent_node.execute(...)
    delivered_so_far += 1
    
    if max_allowed and delivered_so_far > max_allowed:
        # 记录错误，决定是否escalate
        raise ValidationError(
            f"Node {node_id} has delivered {delivered_so_far} document(s), "
            f"but max allowed is {max_allowed}"
        )
```

---

## 4. 多文档创建方案（Architect、PO）

### 4.1 需求分析

#### 4.1.1 Architect 节点的多文档场景

Architect 应该能创建多份相关文档：

| 文档类型 | 标题示例 | 内容 |
|---------|---------|------|
| 系统架构 | "System Architecture Overview" | 系统整体设计、模块划分、交互流程 |
| API设计 | "API Specification & Contracts" | RESTful/GraphQL接口定义、数据契约 |
| 数据模型 | "Database Schema & Data Model" | 数据库设计、表结构、关系 |
| 安全设计 | "Security & Compliance Design" | 认证、授权、加密、审计 |

**当前问题**：
- node.yaml 中 `required_sections` 列出了这些内容应该在一个文档中
- 但这样做会造成单个文档过大、复杂度高、难以维护
- 应该分解为4-5份专题文档

#### 4.1.2 PO 节点的多文档流程（关键场景）

PO 使用 `bmad-create-epics-and-stories` skill进行工作流，其中涉及多次调用 `create_deliverable`：

**工作流步骤**（参考 `_bmad/bmm/3-solutioning/bmad-create-epics-and-stories/steps/`）：

1. **第一步**：验证前置条件（输入验证）
2. **第二步**：创建 Epic 列表（第1次 `create_deliverable`）
   - 文档：`epic-list.md`
   - 内容：所有 Epic 的列表、描述、优先级
3. **第三步**：逐个生成Story（多次 `create_deliverable`？）
   - 单个文档还是多个文档？
   - 当前设计：全部追加到 `epics.md`
4. **最终输出**：综合文档（第2次或最终一次 `create_deliverable`）
   - 文档：`epics-stories.md` 或 `product-backlog.md`
   - 内容：完整的 Epic + Story 列表

**关键发现**：PO 的工作流实际上是**迭代追加式**的，最后再交付一个综合文档。

### 4.2 多文档数据结构扩展

#### 4.2.1 当前单文档结构

```python
# NodeResult 中
deliverable: dict[str, Any]  # 单个对象

# JSON 输出
{
  "deliverable": {
    "title": "Product Backlog",
    "file_path": "output/.../product-backlog.md",
    "sha256": "abc123...",
    "word_count": 5000,
    "section_index": ["Overview", "Epic List", "Story List"],
  },
  "questions": [...],
  "evaluation": {...},
}
```

#### 4.2.2 多文档结构（选项1：列表）

```python
# NodeResult 中
deliverables: list[dict[str, Any]]  # ← 改为列表

# JSON 输出
{
  "deliverables": [                  # ← 数组
    {
      "index": 1,
      "type": "epic-list",           # ← 新增：文档类型
      "title": "Epic List",
      "file_path": "output/.../epic-list.md",
      "sha256": "abc123...",
      "word_count": 2000,
      "section_index": [...],
    },
    {
      "index": 2,
      "type": "story-prioritization", # ← 新增：文档类型
      "title": "Story Prioritization",
      "file_path": "output/.../story-prioritization.md",
      "sha256": "def456...",
      "word_count": 3000,
      "section_index": [...],
    }
  ],
  "questions": [...],
  "evaluation": {...},
}
```

**问题**：
- 破坏现有的 `deliverable` 字段（向后兼容性）
- Validator 需要彻底重写（当前期望 dict，需改为 list）
- 所有依赖 deliverable 的代码都需修改

#### 4.2.3 多文档结构（选项2：向后兼容的包装）

```python
# NodeResult 保持不变（后向兼容）
deliverable: dict[str, Any]

# 但 deliverable 结构扩展
{
  "deliverable": {
    "title": "Product Backlog Set",     # ← 集合标题
    "type": "multi-document",           # ← 新增：标记为多文档
    "documents": [                      # ← 新增：子文档列表
      {
        "index": 1,
        "type": "epic-list",
        "title": "Epic List",
        "file_path": "output/.../epic-list.md",
        "sha256": "abc123...",
        "word_count": 2000,
        "section_index": [...],
      },
      {
        "index": 2,
        "type": "story-prioritization",
        "title": "Story Prioritization",
        "file_path": "output/.../story-prioritization.md",
        "sha256": "def456...",
        "word_count": 3000,
        "section_index": [...],
      }
    ],
    "total_word_count": 5000,           # ← 新增：汇总统计
  },
  "questions": [...],
  "evaluation": {...},
}
```

**优点**：
- ✓ 保持现有JSON结构（`deliverable` 仍为 dict）
- ✓ 向后兼容（旧代码仍能访问 `deliverable.title` 等）
- ✓ Validator 改动最小（只需识别 `deliverable.type="multi-document"` 时做特殊处理）
- ✓ 可选择是否使用多文档模式

**缺点**：
- ✗ 结构更复杂（嵌套层数增加）
- ✗ 消费者需要处理两种情况（单文档 vs 多文档）

### 4.3 推荐方案：选项2（向后兼容包装）

**理由**：
1. 降低风险，保持现有系统的稳定性
2. 可以分阶段实施（先在PO节点试用，再推广）
3. Validator 和依赖方可以渐进式适配

### 4.4 PO 节点多文档创建流程设计

#### 4.4.1 System Prompt 中的指导

```
You are a Product Owner responsible for breaking down PRD into actionable epics and user stories.

Your output will contain MULTIPLE deliverables (documents):

1. Epic List (epic-list.md)
   - All epics with descriptions, goals, and prioritization
   - Use MoSCoW or RICE framework

2. Story Prioritization (story-prioritization.md)
   - User stories broken down from epics
   - Each story with acceptance criteria
   - Release plan

3. Product Vision (product-vision.md)
   - High-level vision statement
   - Success metrics
   - Strategic goals

When you are ready to deliver, call create_deliverable ONCE with:
{
  "title": "Product Backlog Set",
  "content": "..."  // This should be a summary or index
  // In the metadata, include references to all sub-documents
}

IMPORTANT:
- You may need to call create_deliverable multiple times as you draft different documents
- Each call creates ONE file
- Coordinator will collect all created files into a multi-document set
```

**思路**：
- LLM 可以多次调用 `create_deliverable`（每份文档一次）
- 每次调用返回一个 deliverable 对象
- 后处理步骤（Orchestrator）将所有 deliverable 对象收集起来
- 合并成一个"multi-document"类型的 deliverable

#### 4.4.2 Orchestrator 层面的收集逻辑

```python
# 伪代码
class DualAgentNode:
    async def execute(self, execution_context: NodeExecutionContext) -> NodeResult:
        """执行节点，可能会创建多个deliverable"""
        
        # 第一步：执行 IndependentAgent（可能多次调用 create_deliverable）
        independent_output = await self.independent_agent.execute(...)
        # independent_output["deliverable"] -> 首次调用的结果
        
        # 第二步：收集所有创建的文件
        # 问题：如何知道有多少个文件被创建？
        # 方案A：LLM在最后汇总告诉我们（不可靠）
        # 方案B：Orchestrator 监听文件系统（复杂）
        # 方案C：LLM每次调用时返回 {index: 1, total: 3}（需要修改参数）
        # 方案D：create_deliverable 工具维护一个"上下文会话"记录所有调用
        
        # 第三步：根据情况决定是否合并
        if node_config.deliverable.get("multi_document_enabled"):
            collected = self._collect_all_deliverables(pipeline_id)
            result.deliverable = self._wrap_multi_document(collected)
        else:
            result.deliverable = independent_output["deliverable"]
        
        return result
    
    def _collect_all_deliverables(self, pipeline_id: str) -> list[dict]:
        """从输出目录收集该pipeline的所有deliverables"""
        output_dir = Path("autoBMAD/output") / pipeline_id
        files = list(output_dir.glob("*.md"))
        
        result = []
        for idx, file in enumerate(sorted(files), 1):
            metadata = {
                "index": idx,
                "type": self._infer_doc_type(file.name),
                "title": file.stem.replace("-", " ").title(),
                "file_path": str(file),
                "sha256": self._compute_sha256(file),
                "word_count": self._count_words(file),
                "section_index": self._extract_sections(file),
            }
            result.append(metadata)
        
        return result
    
    def _wrap_multi_document(self, documents: list[dict]) -> dict:
        """将多个文档包装成一个multi-document deliverable"""
        return {
            "title": f"{self.node_id.upper()} Deliverables Set",
            "type": "multi-document",
            "documents": documents,
            "total_word_count": sum(d["word_count"] for d in documents),
        }
```

**问题**：这种方案需要后处理，不够优雅。

#### 4.4.3 更好的方案：显式多文档参数

**修改 CreateDeliverableParams**：

```python
class CreateDeliverableParams(BaseModel):
    """Parameters for creating a deliverable (or multiple)."""
    
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    # 新增：多文档支持
    multi_document_index: int | None = Field(
        default=None,
        description="If set, indicates this is document N of M in a set (1-indexed)"
    )
    multi_document_total: int | None = Field(
        default=None,
        description="Total number of documents in the set"
    )
    document_type: str | None = Field(
        default=None,
        description="Type/category of this document (e.g., 'epic-list', 'story-prioritization')"
    )
```

**对应的返回值**：

```python
metadata = {
    "title": params.title,
    "type": params.document_type or "default",
    "file_path": str(file_path),
    "sha256": sha256_hash,
    "word_count": word_count,
    "section_index": section_index,
    
    # 新增
    "index": params.multi_document_index,
    "total": params.multi_document_total,
}
```

**LLM 使用示例**：

```
第1次调用：
{
  "title": "Epic List",
  "content": "## Epic Overview\n...",
  "document_type": "epic-list",
  "multi_document_index": 1,
  "multi_document_total": 3
}

第2次调用：
{
  "title": "Story Prioritization",
  "content": "## Story List\n...",
  "document_type": "story-prioritization",
  "multi_document_index": 2,
  "multi_document_total": 3
}

第3次调用：
{
  "title": "Release Plan",
  "content": "## Phases\n...",
  "document_type": "release-plan",
  "multi_document_index": 3,
  "multi_document_total": 3
}
```

**优点**：
- ✓ LLM 显式声明"这是第1/3个文档"
- ✓ 后处理逻辑可以验证完整性（收到第1,2,3）
- ✓ 不需要扫描文件系统
- ✓ 参数清晰，易于验证

### 4.5 Validator 对多文档的适配

```python
class IndependentOutputValidationStrategy(ValidationStrategy):
    
    def _validate_deliverable(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate deliverable field structure (single or multi-document)."""
        
        deliverable = data.get("deliverable", {})
        
        # 检查是否为多文档
        if deliverable.get("type") == "multi-document":
            self._validate_multi_document(deliverable, result)
        else:
            self._validate_single_document(deliverable, result)
    
    def _validate_multi_document(self, deliverable: dict[str, Any], result: ValidationResult) -> None:
        """Validate multi-document deliverable."""
        
        # 必需字段
        if "documents" not in deliverable:
            result.add_error("deliverable.documents", "required for multi-document", "MISSING_DOCUMENTS")
            return
        
        documents = deliverable["documents"]
        if not isinstance(documents, list):
            result.add_error("deliverable.documents", "must be a list", "INVALID_DOCUMENTS_TYPE")
            return
        
        if len(documents) == 0:
            result.add_error("deliverable.documents", "must contain at least 1 document", "EMPTY_DOCUMENTS")
            return
        
        # 验证每个文档
        for idx, doc in enumerate(documents):
            if not isinstance(doc, dict):
                result.add_error(f"deliverable.documents[{idx}]", "must be a dict", "INVALID_DOC_TYPE")
                continue
            
            # 每个文档都必须有 file_path 和 sha256
            if "file_path" not in doc:
                result.add_error(f"deliverable.documents[{idx}].file_path", "required", "MISSING_FILE_PATH")
            if "sha256" not in doc:
                result.add_error(f"deliverable.documents[{idx}].sha256", "required", "MISSING_SHA256")
```

---

## 5. 文档模板对齐方案

### 5.1 BMAD 模板与 DocuSwarm 节点配置的对比分析

#### 5.1.1 现有BMAD模板系统

**BMAD 在 `_bmad/bmm/` 下组织**：

| 目录 | 内容 | 对应节点 |
|------|------|---------|
| `1-analysis/` | 业务分析、竞争对手分析等 | Analyst |
| `2-plan-workflows/` | PRD创建、工作流规划 | PM |
| `3-solutioning/` | UX设计、架构设计、Epic创建 | UX、Architect、PO |
| `4-implementation/` | 代码实现、测试、部署 | Dev（不在DocuSwarm范围） |

**特点**：
- Step-based workflow（多步骤协作流程）
- 每个skill有 `steps/`、`templates/`、`resources/` 目录
- Prompts 中定义了详细的执行指导（MANDATORY EXECUTION RULES）

#### 5.1.2 DocuSwarm 节点配置

**在 `autoBMAD/nodes/*/` 下**：

- `node.yaml`：节点配置、任务定义、deliverable要求
- `persona.json`：角色身份、沟通风格、专长
- `evaluator.yaml`：评估标准

**特点**：
- 静态配置（一次定义，重复使用）
- 强调角色（persona）而不是流程步骤
- Deliverable 定义为必需章节列表

#### 5.1.3 对比分析表

| 维度 | BMAD模板 | DocuSwarm节点 | 对齐需求 |
|------|---------|--------------|---------|
| **组织方式** | 按步骤workflow | 按节点/角色 | 需要映射：step → node |
| **内容表达** | 详细的提示词 + 步骤指导 | Required sections | 需要充实：sections → prompt |
| **交付物** | 文件集合 | 单个deliverable | 需要支持：多文件 → 多deliverable |
| **验证** | Step内部自验证 | 外部validator | 需要一致：验证标准统一 |
| **配置** | 动态注入（config.yaml） | 静态YAML | 需要集成：参数源统一 |
| **质量标准** | 文档标准（无时间估算、CommonMark） | Required sections | 需要扩展：标准嵌入 |

### 5.2 模板注入机制设计

#### 5.2.1 三层模板注入

**目标**：从BMAD模板生成DocuSwarm的system prompt。

**实现方案**：

```
BMAD 模板层
    ↓
    ├─ Template Loader（读取YAML/Markdown）
    ↓
中间层：Template Assembler
    ├─ 合并必需章节 + 质量标准 + 工作流指导
    ↓
    ├─ System Prompt 生成器
    ├─ Context Builder（提取上下文注入点）
    ├─ Tool Registry（工具可用性声明）
    ↓
DocuSwarm System Prompt
    ├─ Role Definition（persona）
    ├─ Task Description（task.description）
    ├─ Deliverable Contract（required_sections）
    ├─ Quality Standards（验证规则）
    ├─ Available Tools（工具清单）
    └─ Upstream Context（前置节点输出摘要）
```

#### 5.2.2 具体实施路径

**路径A：System Prompt 注入**

```python
# contract_builder.py 中
class ContractBuilder:
    def render_independent_system_prompt(
        self, 
        node_config: NodeConfig,
        bmad_template: dict[str, Any] | None = None,
    ) -> str:
        """从节点配置 + BMAD模板生成system prompt"""
        
        prompt_parts = []
        
        # 1. 角色定义（来自persona.json）
        prompt_parts.append(self._render_persona(node_config.persona))
        
        # 2. 任务说明（来自node.yaml task字段）
        prompt_parts.append(self._render_task(node_config.task))
        
        # 3. BMAD工作流指导（如果提供）
        if bmad_template:
            prompt_parts.append(self._render_bmad_instructions(bmad_template))
        
        # 4. 交付物契约
        prompt_parts.append(self._render_deliverable_contract(node_config.deliverable))
        
        # 5. 质量标准
        prompt_parts.append(self._render_quality_standards(node_config.quality_rules))
        
        # 6. 工具指导
        prompt_parts.append(self._render_tool_instructions(node_config.available_tools))
        
        return "\n\n".join(prompt_parts)
    
    def _render_bmad_instructions(self, template: dict[str, Any]) -> str:
        """从BMAD模板提取执行指导"""
        
        # BMAD 模板中的 MANDATORY EXECUTION RULES
        rules = template.get("mandatory_rules", [])
        instructions = template.get("step_instructions", "")
        
        return f"""
## Workflow Instructions

{instructions}

### Mandatory Rules
{self._format_rules(rules)}
"""
```

**路径B：Tool参数注入**

```python
# 在 CreateDeliverableParams 中扩展参数
class CreateDeliverableParams(BaseModel):
    # ... 现有参数
    
    # 新增：可选的模板引用
    template_id: str | None = Field(
        default=None,
        description="Reference to BMAD template for this deliverable"
    )
    quality_checklist: dict[str, Any] | None = Field(
        default=None,
        description="Quality standards to validate against"
    )
```

**路径C：Context 文件注入**

```python
# 在context.content中包含模板信息
context_content = """
# Execution Context

## Your Task
{task_description}

## Required Sections
{required_sections_list}

## Quality Standards
{quality_rules}

## Relevant Templates
- Template: {template_name}
- Reference: {template_url}

## Upstream Deliverables
{chained_deliverables_summary}
"""
```

### 5.3 每个节点的模板映射关系

#### 5.3.1 Analyst 节点

| 数据源 | 内容 | 最终体现 |
|--------|------|---------|
| `node.yaml` | task.description: "Transform raw data into actionable insights" | System Prompt 的任务段 |
| `persona.json` | role: "Data Analyst" | System Prompt 的角色段 |
| `evaluator.yaml` | criteria: ["data_quality", "logical_flow"] | Evaluator 的审查维度 |
| BMAD `bmad-agent-analyst` | 分析方法论、结构化思维 | System Prompt 的工作流指导 |

**最终System Prompt 结构**：
```
你是一个数据分析师，专长是...（来自persona）

你的任务是：转换原始数据为可执行的业务洞察（来自task）

## 工作流
1. 理解业务背景（来自BMAD）
2. 收集数据源
3. 进行分析
4. 形成建议

## 交付物要求
必需章节：Executive Summary, Data Sources, Analysis Methodology, Findings, Recommendations, Limitations

## 质量标准
- 最少字数：500
- 必需图表：至少1个Mermaid图
- 必需数据驱动的结论（无猜测）
```

#### 5.3.2 PO 节点

| 数据源 | 内容 | 最终体现 |
|--------|------|---------|
| `node.yaml` | task: "create-epics-and-user-stories" | System Prompt 的任务 |
| `persona.json` | role: "Product Owner - Epics & Stories Specialist" | System Prompt 角色 |
| BMAD `bmad-create-epics-and-stories` | Step-by-step workflow（3步） | System Prompt 工作流部分 |
| 模板文件 `po_templates.yaml` | Epic/Story 的格式要求 | Deliverable 结构定义 |

**关键：多文档支持**

```yaml
# po_templates.yaml（新增）
templates:
  - template_id: epic_list
    title: "Epic List"
    filename_pattern: "epic-list.md"
    required_sections:
      - "Epic Overview"
      - "Epic Details"
      - "Prioritization Rationale"
      - "Dependencies"
    document_index: 1
    document_total: 3  # ← 表示这是第1/3个文档
  
  - template_id: story_prioritization
    title: "Story Prioritization"
    filename_pattern: "story-prioritization.md"
    required_sections:
      - "Story Overview"
      - "Story List"
      - "Acceptance Criteria"
      - "Release Plan"
    document_index: 2
    document_total: 3
  
  - template_id: roadmap
    title: "Product Roadmap"
    filename_pattern: "product-roadmap.md"
    required_sections:
      - "Roadmap Overview"
      - "Phase 1 Goals"
      - "Future Phases"
      - "Dependencies"
    document_index: 3
    document_total: 3
```

### 5.4 质量标准与验证对齐

**目标**：validator 使用 BMAD 的质量标准。

```python
# 在 quality_rules 中映射 BMAD 标准
BMAD_QUALITY_RULES = {
    "analyst": {
        "min_word_count": 500,
        "required_mermaid_diagrams": 1,
        "must_have_confidence_levels": True,
        "style_guide": "BMAD data-driven analysis",
    },
    "pm": {
        "min_word_count": 1000,
        "must_have_acceptance_criteria": True,
        "must_reference_frs": True,
        "style_guide": "BMAD requirement clarity",
    },
    "ux": {
        "min_word_count": 800,
        "must_have_wireframes": True,  # Mermaid或描述
        "must_have_accessibility": True,
        "style_guide": "BMAD user-centered design",
    },
    "architect": {
        "min_word_count": 1200,
        "must_have_architecture_diagram": True,
        "must_have_api_spec": True,
        "style_guide": "BMAD technical clarity",
    },
    "po": {
        "min_word_count": 1500,
        "must_have_epics": True,
        "must_have_user_stories": True,
        "must_have_acceptance_criteria": True,
        "story_format": "As a [persona], I want [goal], so that [benefit]",
        "ac_format": "Given/When/Then",
        "style_guide": "BMAD story writing",
    },
}
```

---

## 6. 数据结构改造

（由于篇幅，此节内容见后续部分）


## 6. 数据结构改造

### 6.1 NodeResult 结构升级

#### 6.1.1 当前结构

```python
@dataclass
class NodeResult:
    """Result from DualAgentNode execution."""
    
    deliverable: dict[str, Any]       # ← 单个对象
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any]
    iteration: int
    timestamp: datetime
    force_completion: ForceCompletion | None = None
```

#### 6.1.2 升级后结构（向后兼容）

```python
@dataclass
class DeliverableDocument(TypedDict):
    """单个文档元数据"""
    index: int                         # 文档序号（1-based）
    type: str                          # 文档类型：'epic-list', 'story-prioritization' 等
    title: str
    file_path: str
    sha256: str
    word_count: int
    section_index: list[str]
    content_type: str = "markdown"


@dataclass
class MultiDocumentDeliverable(TypedDict):
    """多文档deliverable结构"""
    title: str                         # 集合标题
    type: Literal["multi-document"]
    documents: list[DeliverableDocument]
    total_word_count: int
    created_at: str


@dataclass
class SingleDocumentDeliverable(TypedDict):
    """单文档deliverable结构"""
    title: str
    type: Literal["single-document", "default"]
    file_path: str
    sha256: str
    # ... 其他字段


DeliverableType = SingleDocumentDeliverable | MultiDocumentDeliverable


@dataclass
class NodeResult:
    """Result from DualAgentNode execution (向后兼容)."""
    
    deliverable: dict[str, Any]       # ← 保持为 dict（兼容）
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any]
    iteration: int
    timestamp: datetime
    force_completion: ForceCompletion | None = None
    
    # 新增便利属性
    @property
    def is_multi_document(self) -> bool:
        return self.deliverable.get("type") == "multi-document"
    
    @property
    def all_documents(self) -> list[dict[str, Any]]:
        """获取所有文档（兼容单/多文档）"""
        if self.is_multi_document:
            return self.deliverable.get("documents", [])
        else:
            return [self.deliverable]
    
    @property
    def total_word_count(self) -> int:
        """获取总字数"""
        if self.is_multi_document:
            return self.deliverable.get("total_word_count", 0)
        else:
            return self.deliverable.get("word_count", 0)
```

### 6.2 PipelineState 的适配

**文件位置**：`d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/pipeline/state.py`

```python
class PipelineState(TypedDict):
    """Pipeline执行状态"""
    
    pipeline_id: str
    current_node: str
    nodes_executed: list[str]
    nodes_results: dict[str, NodeResult]  # ← 现有
    
    # 新增：跟踪多文档的累积信息
    node_deliverable_count: dict[str, int]  # { node_id -> created_count }
    all_files_created: list[str]            # 所有创建的文件路径
    
    # 示例在进行中
    # {
    #   "pipeline_id": "pipeline-001",
    #   "current_node": "po",
    #   "nodes_executed": ["analyst", "pm", "ux", "architect"],
    #   "nodes_results": {
    #     "analyst": { deliverable: {...}, questions: [...], ... },
    #     "po": { deliverable: {type: "multi-document", documents: [...]}, ... }
    #   },
    #   "node_deliverable_count": {
    #     "analyst": 1,
    #     "pm": 1,
    #     "ux": 1,
    #     "architect": 2,  # 创建了2份文档
    #     "po": 3          # 创建了3份文档
    #   },
    #   "all_files_created": [
    #     "output/pipeline-001/analyst-report.md",
    #     "output/pipeline-001/prd.md",
    #     "output/pipeline-001/ux-design.md",
    #     "output/pipeline-001/system-architecture.md",
    #     "output/pipeline-001/api-specification.md",
    #     "output/pipeline-001/epic-list.md",
    #     "output/pipeline-001/story-prioritization.md",
    #     "output/pipeline-001/product-roadmap.md"
    #   ]
    # }
```

### 6.3 CreateDeliverableParams 扩展

```python
class CreateDeliverableParams(BaseModel):
    """Parameters for creating a deliverable."""
    
    # 现有字段
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    # 新增：多文档支持
    document_index: int | None = Field(
        default=None,
        description="If set, this is document N in a multi-document set (1-indexed)"
    )
    document_total: int | None = Field(
        default=None,
        description="Total number of documents in the set"
    )
    document_type: str | None = Field(
        default=None,
        description="Document type/category for multi-doc sets (e.g., 'epic-list')"
    )
```

### 6.4 Validator 改动

**关键改动**：识别和验证多文档格式

```python
class IndependentOutputValidationStrategy(ValidationStrategy):
    
    def _validate_deliverable(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate deliverable (single or multi-document)"""
        
        deliverable = data.get("deliverable", {})
        deliverable_type = deliverable.get("type", "single-document")
        
        if deliverable_type == "multi-document":
            self._validate_multi_document_deliverable(deliverable, result)
        else:
            self._validate_single_document_deliverable(deliverable, result)
    
    def _validate_multi_document_deliverable(self, deliverable: dict, result: ValidationResult) -> None:
        """Validate multi-document format"""
        
        # 必需字段
        if "documents" not in deliverable:
            result.add_error("deliverable.documents", "required for multi-document", "MISSING_DOCUMENTS")
            return
        
        documents = deliverable["documents"]
        if not isinstance(documents, list) or len(documents) == 0:
            result.add_error("deliverable.documents", "must be non-empty list", "INVALID_DOCUMENTS")
            return
        
        # 验证每个文档都有 file_path 和 sha256
        for idx, doc in enumerate(documents):
            if not isinstance(doc, dict):
                result.add_error(f"deliverable.documents[{idx}]", "must be object", "INVALID_DOC")
                continue
            
            if "file_path" not in doc:
                result.add_error(f"deliverable.documents[{idx}].file_path", "required", "MISSING_FILE_PATH")
            if "sha256" not in doc:
                result.add_error(f"deliverable.documents[{idx}].sha256", "required", "MISSING_SHA256")
```

---

## 7. 风险评估

### 7.1 实施风险矩阵

| 风险项 | 风险等级 | 影响范围 | 缓解措施 |
|--------|---------|---------|---------|
| **向后兼容性破裂** | 高 | 所有依赖deliverable的代码 | 采用选项2（向后兼容包装） |
| **Validator过度复杂** | 中 | 代码可维护性 | 分离单/多文档验证逻辑 |
| **LLM混淆新参数** | 中 | 系统稳定性 | System prompt中明确指导 |
| **数据库查询超时** | 中 | PO节点执行速度 | 限制文档数量（最多5-10份） |
| **评估器与多文档不兼容** | 中 | 质量判定机制 | Evaluator需特别处理多文档 |
| **文件系统竞争** | 低 | 并发执行 | 已有pipeline_id隔离 |

### 7.2 技术债风险

1. **Validator 职责过重**
   - 当前：检查file_path、sha256、required_sections
   - 新增：检查多文档计数、文档完整性
   - 建议：拆分为 OutputValidator、DeliverableValidator、MultiDocumentValidator

2. **模板系统分散**
   - BMAD 模板：`_bmad/bmm/`
   - DocuSwarm 模板：`autoBMAD/docuswarm/templates/`
   - 有重复和不一致风险
   - 建议：统一模板源，建立单向转换机制

3. **节点配置Schema膨胀**
   - 已有：task、deliverable、agent、evaluator、runtime、questions
   - 新增：max_deliverables、multi_document_config、quality_rules
   - 建议：分离为 DeliverableConstraint、QualityConfig 等独立对象

---

## 8. 实施路线图

### 8.1 分阶段实施计划

#### Phase 1: 基础设施准备（第1-2周）

**目标**：为单/多文档支持做准备

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 1.1 扩展 CreateDeliverableParams | P0 | 2h | 开发 | 参数验证通过 |
| 1.2 更新 CreateDeliverableTool 返回值 | P0 | 2h | 开发 | 返回新字段 |
| 1.3 修改 NodeResult 数据结构 | P0 | 4h | 开发 | TypedDict兼容 |
| 1.4 单元测试：新参数 + 返回值 | P1 | 4h | QA | 覆盖率>95% |

**产出物**：
- `autoBMAD/docuswarm/tools/create_deliverable.py` (扩展参数)
- `autoBMAD/docuswarm/nodes/dual_agent.py` (NodeResult更新)
- `tests/unit/test_create_deliverable_extended.py`

#### Phase 2: Validator 升级（第2-3周）

**目标**：支持单/多文档验证和数量约束

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 2.1 更新 ValidationRuleRegistry | P0 | 3h | 开发 | 每个节点有max_deliverables |
| 2.2 增加 _validate_deliverable_count 方法 | P0 | 3h | 开发 | 约束检查通过 |
| 2.3 增加 _validate_multi_document 方法 | P1 | 4h | 开发 | 多文档验证正确 |
| 2.4 集成测试：验证流程 | P1 | 4h | QA | 覆盖单/多文档场景 |

**产出物**：
- `autoBMAD/docuswarm/context/validator.py` (新验证逻辑)
- 更新 `DEFAULT_VALIDATION_RULES`
- `tests/unit/test_validator_multi_document.py`

#### Phase 3: 单文档约束实施（第3-4周）

**目标**：为analyst、pm、ux 节点强制实施单文档约束

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 3.1 更新 node.yaml 添加 max_deliverables | P0 | 1h | 开发 | 3个节点配置完成 |
| 3.2 Orchestrator 中添加约束检查 | P1 | 4h | 开发 | 超限时正确报错 |
| 3.3 System prompt 中明确约束 | P1 | 2h | 开发 | LLM理解约束 |
| 3.4 端到端测试：单文档约束 | P1 | 6h | QA | analyst/pm/ux各1份文档 |

**文件变更**：
- `autoBMAD/nodes/analyst/node.yaml` (+ max_deliverables: 1)
- `autoBMAD/nodes/pm/node.yaml` (+ max_deliverables: 1)
- `autoBMAD/nodes/ux/node.yaml` (+ max_deliverables: 1)

#### Phase 4: 多文档支持（第4-6周）

**目标**：为architect和po节点支持多文档创建

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 4.1 创建 po_templates.yaml 和 architect_templates.yaml | P1 | 4h | 开发 | 模板定义完整 |
| 4.2 System prompt 中的多文档指导 | P1 | 4h | 开发 | 提示词清晰 |
| 4.3 Orchestrator 多文档收集逻辑 | P2 | 8h | 开发 | 收集和包装正确 |
| 4.4 PO 工作流集成测试 | P2 | 8h | QA | 成功创建3-4份文档 |

**文件新增**：
- `autoBMAD/docuswarm/templates/architect_templates.yaml`
- `autoBMAD/docuswarm/templates/po_templates.yaml`

#### Phase 5: BMAD 模板对齐（第6-8周）

**目标**：集成BMAD模板到DocuSwarm system prompt

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 5.1 创建 TemplateLoader（读取BMAD模板） | P2 | 6h | 开发 | 加载成功 |
| 5.2 更新 contract_builder 集成模板 | P2 | 8h | 开发 | System prompt 包含模板指导 |
| 5.3 质量标准映射表 | P2 | 4h | 开发 | 规则完整 |
| 5.4 集成测试：模板对齐 | P3 | 6h | QA | 质量指标达到 |

**产出物**：
- `autoBMAD/docuswarm/prompts/template_loader.py`
- 更新 `contract_builder.py`

#### Phase 6: 文档和培训（第8-9周）

| 任务 | 优先级 | 工作量 | 负责人 | 验证点 |
|------|--------|---------|---------|---------|
| 6.1 API 文档更新 | P2 | 3h | 文档 | 参数新增说明 |
| 6.2 迁移指南 | P2 | 4h | 文档 | 单/多文档使用说明 |
| 6.3 开发者培训 | P3 | 2h | 讲师 | 培训完成 |

### 8.2 并行工作流

```
Phase 1 (2 weeks)
  ├─ Task 1.1-1.4: 参数扩展
  └─ 并行: Phase 2 前期准备
    
Phase 2 (1.5 weeks)  [在Phase 1后开始]
  ├─ Task 2.1-2.2: Validator基础改造
  └─ 并行: Phase 3 System prompt 准备

Phase 3 (1 week)  [在Phase 2后开始]
  ├─ Task 3.1-3.3: 单文档约束
  └─ 并行: Phase 4 多文档设计

Phase 4 (2 weeks)  [在Phase 3后开始]
  ├─ Task 4.1-4.4: 多文档实现
  └─ 并行: Phase 5 模板准备

Phase 5 (2 weeks)  [在Phase 4后开始]
  ├─ Task 5.1-5.4: 模板集成
  └─ 并行: Phase 6 文档

Phase 6 (1 week)  [最后]
  └─ Task 6.1-6.3: 文档+培训

总计时间: 9.5 周（约2个月）
```

### 8.3 关键依赖和风险点

**关键路径**：
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
    2w     1.5w      1w       2w       2w       1w
```

**风险检查点**：
- **周1-2 末**：参数扩展单元测试通过 ✓
- **周3-4 末**：Validator集成测试通过 ✓
- **周5 末**：单文档约束端到端测试通过 ✓
- **周7 末**：多文档工作流（至少PO）可用 ✓
- **周9 末**：模板对齐和文档完成 ✓

---

## 9. 总结与建议

### 9.1 主要发现

1. **当前系统的强度和弱点**
   - 强度：Validator通过file_path/sha256实现可靠的文件存在性验证
   - 弱点：无法表达多文档约束和多文档结果

2. **三层约束实施方案**
   - node.yaml 声明（配置层）
   - Validator 检查（验证层）
   - Orchestrator 追踪（执行层）
   
3. **向后兼容包装的必要性**
   - 多文档support不应破坏现有系统
   - 递进式采用（analyst/pm/ux → architect/po）

### 9.2 优先级建议

**Phase 1-3 必做**（支持单文档约束）：
- 确保analyst、pm、ux 严格限制为1份文档
- 估计工作量：3-4周，低风险

**Phase 4-5 可做**（支持多文档）：
- architect和po的多文档需求
- 估计工作量：4-5周，中等风险
- 可与Phase 1-3并行准备

**Phase 6 配套**（模板对齐）：
- 非阻塞，但重要
- 可在Phase 4完成后进行

### 9.3 关键成功因素

1. **System Prompt 的清晰指导**
   - 明确告诉LLM哪些节点应该创建多少份文档
   - 示范性的 JSON 格式示例

2. **Validator 的渐进式扩展**
   - 不要一次性修改太多逻辑
   - 采用新旧并行的方式

3. **充分的测试覆盖**
   - 单文档/多文档场景
   - 约束超限场景
   - 迭代和重试场景

4. **文档和培训**
   - API变化需清晰说明
   - 开发者需理解新的可能性

---

**报告完成日期**: 2026-04-06  
**下一步**: 提交评审和优先级确认
