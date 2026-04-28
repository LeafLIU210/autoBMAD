# ContextValidator 提取重构方案研究报告

**文档编号**: refactor-2026-03-26/01  
**撰写日期**: 2026-03-26  
**状态**: 草稿  
**作者**: Bill（backend-dev）  
**关联任务**: #2 — 研究报告：ContextValidator 提取重构方案

---

## 1. 执行摘要

### 1.1 问题概述

DocuSwarm 当前的验证逻辑以**内联分散**形式存在于多个模块中，形成了高耦合、低可维护性的代码结构：

- `pipeline/orchestrator.py`（39KB / 1102 行）中内嵌 LLM 上下文验证（`_validate_context`，L262–L344）和依赖检查（`_check_dependencies`，L346–L401），使得 `HybridOrchestrator` 类承担了超出其职责范围的验证责任。
- `context/isolation.py` 中的 `ContextManager` 类同时承担"上下文构建"和"私有字段验证"两个职责（`_validate_no_private_fields`，L241–L257；`_check_for_private_fields`，L260–L291）。
- `node_execution/validator.py` 中的 `ContextValidator` 类仅验证 JSON 文件格式和固定字段（`project_description`、`requirements`），尚未覆盖 `NodeExecutionContext` 协议字段。
- `llm/response.py` 中的输出验证（`validate_independent_output` L140–L226、`validate_evaluator_output` L229–L305）为纯函数形式，缺乏统一注册机制。
- `prompts/validator.py` 中的 `TemplateValidator` 孤立存在，与其他验证组件无法协作。

诊断工具（`tools/context_validator_analyzer.py`）扫描 95 个 Python 文件后发现：  
**39 个验证方法、126 处内联验证模式、15 个高优先级提取候选**。

### 1.2 核心目标

将上述分散验证逻辑提取为独立的 **`autoBMAD/docuswarm/context/validator.py`** 组件，实现：

1. **职责单一化**：`HybridOrchestrator` 仅调用验证，不包含验证实现。
2. **策略化验证**：每个节点（analyst/pm/ux/architect/po）可通过 `node.yaml` 自定义验证规则。
3. **统一验证接口**：输入验证、上下文验证、隔离验证、输出验证均通过 `ContextValidator` 统一入口调用。
4. **可测试性提升**：验证逻辑解耦后，单元测试不再需要 Mock LLM 或完整的 Orchestrator 实例。

---

## 2. 现状分析

### 2.1 验证逻辑全量位置清单

基于诊断工具输出（`.tmp/context_validator_analysis.json`），以下为所有验证相关方法的完整位置：

#### 2.1.1 核心验证方法（高优先级提取候选）

| 文件 | 类/函数 | 方法名 | 行号 | 验证类型 | 是否异步 |
|------|---------|--------|------|----------|----------|
| `pipeline/orchestrator.py` | `HybridOrchestrator` | `_validate_context` | L262–L344 | LLM 上下文验证 | ✓ async |
| `pipeline/orchestrator.py` | `HybridOrchestrator` | `_check_dependencies` | L346–L401 | 依赖规则验证 | ✗ sync |
| `context/isolation.py` | `ContextManager` | `_validate_no_private_fields` | L241–L257 | 隔离安全验证 | ✗ sync |
| `context/isolation.py` | — (standalone) | `_check_for_private_fields` | L260–L291 | 私有字段递归检查 | ✗ sync |
| `context/filter.py` | `ContextFilter` | `_validate_critical_fields` | L131–L143 | 过滤后完整性验证 | ✗ sync |
| `node_execution/validator.py` | `ContextValidator` | `validate_context` | L34–L65 | JSON 文件格式验证 | ✓ async |
| `node_execution/validator.py` | `ContextValidator` | `_validate_required_fields` | L79–L96 | 必填字段验证 | ✗ sync |
| `llm/response.py` | — (standalone) | `validate_independent_output` | L140–L226 | Agent 输出结构验证 | ✗ sync |
| `llm/response.py` | — (standalone) | `validate_evaluator_output` | L229–L305 | Evaluator 输出结构验证 | ✗ sync |
| `prompts/validator.py` | `TemplateValidator` | `validate_isolation` | L36–L67 | 模板隔离验证 | ✗ sync |
| `nodes/loader.py` | `NodeConfig` | `_validate` | L56–L75 | 节点配置验证 | ✗ sync |

#### 2.1.2 状态层验证方法（低优先级）

| 文件 | 方法名 | 行号 | 说明 |
|------|--------|------|------|
| `pipeline/state.py` | `validate_state` | L113–L155 | PipelineState 完整性验证 |
| `pipeline/state.py` | `validate_deliverable_format` | L255+ | 交付物格式验证 |
| `node_execution/state.py` | `validate_node_result` | L170–L198 | NodeResult 完整性验证 |
| `node_execution/state.py` | `validate_node_run_state` | L201–L241 | NodeRunState 完整性验证 |
| `node_execution/state.py` | `is_valid_status` | L158–L167 | 状态枚举验证 |
| `storage/checkpoints.py` | 6个验证方法 | 多处 | Checkpoint 数据验证 |

#### 2.1.3 关键内联验证模式（126 处，摘录核心）

- `agents/evaluator.py`：11 处内联 `if not x` 类型的隐式验证
- `agents/evaluator_config/criteria_loader.py`：6 处内联 + 2 个验证方法（`_validate_criteria` L113–L173，`_validate_thresholds` L175–L220）
- `storage/state_manager.py`：12 处内联 `isinstance` 类型检查

### 2.2 验证逻辑分类

```
验证类型分类
├── 输入验证（Input Validation）
│   ├── LLM 上下文语义验证：orchestrator._validate_context（L262）
│   ├── JSON 文件格式验证：node_execution/validator.ContextValidator（L34）
│   └── 节点配置验证：nodes/loader.NodeConfig._validate（L56）
│
├── 上下文验证（Context Validation）
│   ├── NodeExecutionContext 必填字段检查（缺失，待实现）
│   ├── 依赖顺序验证：orchestrator._check_dependencies（L346）
│   └── 模板隔离验证：prompts/validator.TemplateValidator（L36）
│
├── 隔离验证（Isolation Validation）
│   ├── 私有字段泄漏检测：isolation.ContextManager._validate_no_private_fields（L241）
│   ├── 递归私有字段检查：isolation._check_for_private_fields（L260）
│   └── 消息级过滤验证：filter.ContextFilter._validate_critical_fields（L131）
│
└── 输出验证（Output Validation）
    ├── IndependentAgent 输出结构：llm/response.validate_independent_output（L140）
    ├── EvaluatorAgent 输出结构：llm/response.validate_evaluator_output（L229）
    └── 评估标准权重验证：criteria_loader._validate_criteria（L113）
```

### 2.3 当前耦合关系

```
HybridOrchestrator (orchestrator.py)
  ├── 直接持有 LLM 验证逻辑 (_validate_context)
  ├── 直接持有依赖规则逻辑 (_check_dependencies)
  └── 持有 KimiSessionManager（仅为验证目的使用）

ContextManager (context/isolation.py)
  ├── 承担输入构建职责（build_independent_input, build_evaluator_input）
  └── 承担验证职责（_validate_no_private_fields）← 违反单一职责原则

node_execution/validator.py::ContextValidator
  ├── 仅验证旧版 JSON 文件格式（project_description/requirements）
  └── 与 NodeExecutionContext 协议完全解耦（未验证 pipeline_id、node_id 等字段）

llm/response.py
  └── 两个孤立的纯函数验证（无法按节点定制规则）
```

---

## 3. 提取方案设计

### 3.1 新组件架构：`context/validator.py`

新建 `autoBMAD/docuswarm/context/validator.py`，采用**策略模式（Strategy Pattern）+ 组合模式（Composite Pattern）**设计：

```
context/validator.py
└── ContextValidator（统一门面）
    ├── InputValidationStrategy（抽象基类）
    │   ├── LLMContextValidationStrategy（替代 orchestrator._validate_context）
    │   ├── NodeExecutionContextValidationStrategy（新增，验证 NodeExecutionContext 协议）
    │   └── NodeConfigValidationStrategy（重用 NodeConfig._validate 逻辑）
    ├── IsolationValidationStrategy（抽象基类）
    │   ├── PrivateFieldValidationStrategy（迁移自 isolation._validate_no_private_fields）
    │   └── TemplateIsolationValidationStrategy（迁移自 prompts/validator.py）
    ├── OutputValidationStrategy（抽象基类）
    │   ├── IndependentOutputValidationStrategy（迁移自 llm/response.validate_independent_output）
    │   └── EvaluatorOutputValidationStrategy（迁移自 llm/response.validate_evaluator_output）
    └── ValidationRuleRegistry（按 node_id 注册规则）
```

### 3.2 策略化验证模式（Per-Node Validation Rules）

每个节点通过 `node.yaml` 的 `validation` 块自定义验证规则：

```yaml
# nodes/analyst/node.yaml 示例扩展
validation:
  input:
    required_context_fields:
      - project_description
      - requirements
    optional_fields:
      - goals
      - constraints
  context:
    min_description_length: 50
    require_deliverable_requirements: true
  output:
    require_file_path: true
    require_sha256: true
    require_summary: true
    min_word_count: 100
  llm_validation:
    enabled: true
    mode: "fast"  # fast | thorough
```

### 3.3 与 NodeExecutionContext 的接口契约

新组件与 `NodeExecutionContext`（`node_execution/contracts.py`）的接口契约：

**验证点一：必填身份字段**
- `pipeline_id`: 非空字符串
- `node_id`: 属于 `{"analyst", "pm", "ux", "architect", "po"}`
- `node_name`: 非空字符串
- `node_order`: 1–5 的整数

**验证点二：任务契约字段**
- `task_name`: 非空字符串
- `task_description`: 非空字符串，且长度 ≥ 节点配置的 `min_description_length`
- `role_supplement`: 字符串（允许为空）

**验证点三：交付物契约字段**
- `deliverable_type`: 非空字符串
- `deliverable_requirements`: 符合 `DeliverableRequirements` 类型

**验证点四：上下文数据字段**
- `original_context`: 非 None 的 dict
- `chained_deliverables`: list（允许为空）
- `shared_context`: dict（允许为空）

**验证点五：隔离安全字段**
- 对 `original_context` 和 `chained_deliverables` 进行私有字段扫描
- 确保 `PRIVATE_FIELDS = ["private_reasoning", "tool_call_history", "iteration_feedback", "internal_notes"]` 不出现在 Evaluator 可见路径

### 3.4 验证规则配置化方案

验证规则通过两级配置加载：

**第一级：节点 YAML 配置**（`nodes/{node_id}/node.yaml`）
- 定义该节点特有的验证规则
- 由 `nodes/loader.py::NodeLoader` 加载后传入 `ValidationRuleRegistry`

**第二级：Persona JSON 配置**（`nodes/{node_id}/persona.json`）
- 定义角色特有的输出质量要求（如 min_word_count）
- 在输出验证阶段引用

**配置加载流程**：
```
NodeLoader.load_node(node_id)
    → 读取 node.yaml（已有）
    → 读取 persona.json（已有）
    → 提取 node_yaml.get("validation", {}) 作为 validation_config
    → 传入 ContextValidator.register_node_rules(node_id, validation_config)
```

---

## 4. 接口定义（类型注解与伪代码）

### 4.1 ValidationResult 模型

```python
# autoBMAD/docuswarm/context/validator.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    """单条验证问题"""
    field: str          # 问题字段路径，如 "deliverable.file_path"
    message: str        # 问题描述
    severity: str       # "error" | "warning" | "info"
    code: str           # 问题代码，如 "MISSING_REQUIRED_FIELD"


@dataclass
class ValidationResult:
    """验证结果汇总"""
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def add_error(self, field: str, message: str, code: str = "VALIDATION_ERROR") -> None:
        self.issues.append(ValidationIssue(field=field, message=message,
                                            severity="error", code=code))
        self.valid = False

    def add_warning(self, field: str, message: str, code: str = "VALIDATION_WARNING") -> None:
        self.warnings.append(ValidationIssue(field=field, message=message,
                                              severity="warning", code=code))
```

### 4.2 ValidationStrategy 抽象基类

```python
from abc import ABC, abstractmethod


class ValidationStrategy(ABC):
    """验证策略抽象基类"""

    @abstractmethod
    def validate(
        self,
        data: Any,
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """执行验证，返回 ValidationResult

        Args:
            data: 待验证的数据
            config: 节点级验证配置（来自 node.yaml）

        Returns:
            ValidationResult 实例
        """
        ...

    @property
    def strategy_name(self) -> str:
        """策略名称，用于日志和调试"""
        return self.__class__.__name__
```

### 4.3 各验证策略类

```python
class NodeExecutionContextStrategy(ValidationStrategy):
    """验证 NodeExecutionContext 协议完整性

    迁移来源：新增（当前缺失）
    替代：原 node_execution/validator.py::ContextValidator（仅验证旧版字段）
    """

    REQUIRED_FIELDS: list[str] = [
        "pipeline_id", "node_id", "node_name", "node_order",
        "task_name", "task_description", "role_supplement",
        "deliverable_type", "deliverable_requirements",
        "original_context", "chained_deliverables", "shared_context",
    ]
    VALID_NODE_IDS: set[str] = {"analyst", "pm", "ux", "architect", "po"}

    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        result = ValidationResult(valid=True)
        cfg = config or {}

        # 验证必填字段存在
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in data:
                result.add_error(
                    field=field_name,
                    message=f"NodeExecutionContext 缺失必填字段: {field_name}",
                    code="MISSING_REQUIRED_FIELD",
                )

        # 验证 node_id 枚举值
        if "node_id" in data and data["node_id"] not in self.VALID_NODE_IDS:
            result.add_error(
                field="node_id",
                message=f"无效的 node_id: {data['node_id']}，合法值: {self.VALID_NODE_IDS}",
                code="INVALID_NODE_ID",
            )

        # 验证 node_order 范围
        if "node_order" in data:
            if not isinstance(data["node_order"], int) or not (1 <= data["node_order"] <= 5):
                result.add_error(
                    field="node_order",
                    message="node_order 必须是 1-5 的整数",
                    code="INVALID_NODE_ORDER",
                )

        # 验证 task_description 最小长度（可从 config 覆盖）
        min_len = cfg.get("min_description_length", 10)
        if "task_description" in data:
            if len(data.get("task_description", "")) < min_len:
                result.add_warning(
                    field="task_description",
                    message=f"task_description 过短（< {min_len} 字符），可能导致 Agent 输出质量下降",
                    code="SHORT_DESCRIPTION",
                )

        return result


class PrivateFieldIsolationStrategy(ValidationStrategy):
    """验证上下文中不含私有字段

    迁移来源：context/isolation.py L241–L291
    （ContextManager._validate_no_private_fields + _check_for_private_fields）
    """

    PRIVATE_FIELDS: list[str] = [
        "private_reasoning",
        "tool_call_history",
        "iteration_feedback",
        "internal_notes",
    ]

    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        result = ValidationResult(valid=True)
        self._check_recursive(data, "context", result)
        return result

    def _check_recursive(
        self,
        obj: Any,
        path: str,
        result: ValidationResult,
    ) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in self.PRIVATE_FIELDS:
                    result.add_error(
                        field=f"{path}.{key}",
                        message=f"私有字段 '{key}' 不得出现在 Evaluator 可见上下文中",
                        code="PRIVATE_FIELD_LEAK",
                    )
                else:
                    self._check_recursive(value, f"{path}.{key}", result)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_recursive(item, f"{path}[{i}]", result)


class LLMContextValidationStrategy(ValidationStrategy):
    """使用 LLM 进行语义上下文验证（异步策略）

    迁移来源：pipeline/orchestrator.py L262–L344
    (HybridOrchestrator._validate_context)

    注意：此策略需异步执行，通过 ContextValidator.validate_async 调用
    """

    PROMPT_TEMPLATE: str = """You are a technical context validator. Analyze the context and output ONLY a JSON object.

**Context to validate:**
{subject_context}

**Validation rules:**
1. Check if there's a clear objective (what to create)
2. Check if scope is defined (requirements stated)
3. Check if there's sufficient detail to start

**Output format (respond with ONLY this JSON):**
{{"valid": true, "reason": "Brief validation reason", "missing_info": []}}
"""

    def __init__(self, session_manager: Any) -> None:
        self._session_manager = session_manager

    def validate(self, data: Any, config: dict[str, Any] | None = None) -> ValidationResult:
        raise NotImplementedError("LLMContextValidationStrategy 必须通过 validate_async 调用")

    async def validate_async(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """异步 LLM 验证

        Args:
            data: subject_context 字典
            config: 节点级验证配置，支持 llm_validation.enabled 字段

        Returns:
            ValidationResult
        """
        cfg = config or {}
        if not cfg.get("llm_validation", {}).get("enabled", True):
            return ValidationResult(valid=True, metadata={"skipped": "llm_validation disabled"})

        import json
        result = ValidationResult(valid=True)
        try:
            context_str = json.dumps(data, indent=2, ensure_ascii=False)
            prompt = self.PROMPT_TEMPLATE.format(subject_context=context_str)
            messages = await self._session_manager.single_prompt(
                prompt=prompt, mode="agent", yolo=True
            )
            # 解析响应...（与原实现一致）
            # [略：JSON 提取逻辑迁移自 orchestrator.py L295–L334]
        except Exception as e:
            result.metadata["llm_error"] = str(e)
            # Fail open - 允许 Pipeline 继续执行
        return result


class IndependentOutputValidationStrategy(ValidationStrategy):
    """验证 IndependentAgent 输出结构

    迁移来源：llm/response.py L140–L226 (validate_independent_output)
    """

    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        result = ValidationResult(valid=True)
        cfg = config or {}

        # 验证 deliverable 存在
        if "deliverable" not in data:
            result.add_error("deliverable", "必填字段缺失", "MISSING_REQUIRED_FIELD")
            return result

        deliverable = data["deliverable"]

        # P0-3: file_path REQUIRED
        for required in ("title", "file_path", "sha256"):
            if required not in deliverable:
                result.add_error(
                    f"deliverable.{required}",
                    f"必填字段缺失: {required}",
                    "MISSING_REQUIRED_FIELD",
                )

        # 节点级最小字数验证
        min_words = cfg.get("min_word_count", 0)
        word_count = deliverable.get("word_count", 0)
        if min_words > 0 and word_count < min_words:
            result.add_warning(
                "deliverable.word_count",
                f"字数 {word_count} 低于节点要求 {min_words}",
                "LOW_WORD_COUNT",
            )

        # 验证 questions 字段
        if "questions" not in data:
            result.add_error("questions", "必填字段缺失", "MISSING_REQUIRED_FIELD")

        return result


class EvaluatorOutputValidationStrategy(ValidationStrategy):
    """验证 EvaluatorAgent 输出结构

    迁移来源：llm/response.py L229–L305 (validate_evaluator_output)
    """

    VALID_VERDICTS: set[str] = {"APPROVED", "NEEDS_REVISION", "BLOCKED"}

    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        result = ValidationResult(valid=True)

        for required in ("criterion_scores", "alignment_score", "verdict",
                          "issues_found", "suggestions"):
            if required not in data:
                result.add_error(required, f"必填字段缺失: {required}", "MISSING_REQUIRED_FIELD")

        if "verdict" in data and data["verdict"] not in self.VALID_VERDICTS:
            result.add_error(
                "verdict",
                f"无效 verdict 值: {data['verdict']}，合法值: {self.VALID_VERDICTS}",
                "INVALID_VERDICT",
            )

        if "alignment_score" in data:
            score = data["alignment_score"]
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                result.add_error(
                    "alignment_score",
                    f"alignment_score 必须是 0.0–1.0 的数值，实际: {score}",
                    "INVALID_SCORE_RANGE",
                )

        return result
```

### 4.4 ContextValidator 主类（统一门面）

```python
class ValidationRuleRegistry:
    """按 node_id 管理验证规则配置"""

    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}

    def register(self, node_id: str, config: dict[str, Any]) -> None:
        """注册节点级验证配置（来自 node.yaml）"""
        self._rules[node_id] = config

    def get(self, node_id: str) -> dict[str, Any]:
        """获取节点验证配置，不存在时返回空字典"""
        return self._rules.get(node_id, {})


class ContextValidator:
    """统一上下文验证门面

    使用策略模式，支持按验证阶段和节点类型分别调用。

    使用示例：
        validator = ContextValidator(session_manager=session_manager)
        validator.load_node_rules(node_id="analyst", config=node_yaml.get("validation"))

        # 验证 NodeExecutionContext
        result = validator.validate_execution_context(execution_context)
        if not result.valid:
            raise ContextValidationError(result.issues)

        # 验证 IndependentAgent 输出
        out_result = validator.validate_independent_output(output_data, node_id="analyst")
    """

    def __init__(
        self,
        session_manager: Any | None = None,
    ) -> None:
        self._registry = ValidationRuleRegistry()
        self._ctx_strategy = NodeExecutionContextStrategy()
        self._isolation_strategy = PrivateFieldIsolationStrategy()
        self._independent_strategy = IndependentOutputValidationStrategy()
        self._evaluator_strategy = EvaluatorOutputValidationStrategy()
        self._llm_strategy: LLMContextValidationStrategy | None = (
            LLMContextValidationStrategy(session_manager) if session_manager else None
        )
        self._logger = get_logger(__name__)

    def load_node_rules(self, node_id: str, config: dict[str, Any]) -> None:
        """从 node.yaml 加载节点验证规则"""
        self._registry.register(node_id, config)

    def validate_execution_context(
        self,
        context: dict[str, Any],
        node_id: str | None = None,
    ) -> ValidationResult:
        """验证 NodeExecutionContext 协议合规性

        Args:
            context: NodeExecutionContext 字典
            node_id: 节点 ID，用于获取节点级规则

        Returns:
            ValidationResult
        """
        config = self._registry.get(node_id or context.get("node_id", ""))
        return self._ctx_strategy.validate(context, config)

    def validate_isolation(self, data: dict[str, Any]) -> ValidationResult:
        """验证数据不含私有字段（用于 Evaluator 输入路径）"""
        return self._isolation_strategy.validate(data)

    def validate_independent_output(
        self,
        output: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """验证 IndependentAgent 输出结构

        Args:
            output: Agent 原始输出字典
            node_id: 节点 ID，用于节点级规则（如 min_word_count）
        """
        config = self._registry.get(node_id)
        return self._independent_strategy.validate(output, config)

    def validate_evaluator_output(
        self,
        output: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """验证 EvaluatorAgent 输出结构"""
        config = self._registry.get(node_id)
        return self._evaluator_strategy.validate(output, config)

    async def validate_context_with_llm(
        self,
        subject_context: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """使用 LLM 进行语义验证（异步）

        Args:
            subject_context: 待验证的上下文字典
            node_id: 节点 ID，用于控制 llm_validation.enabled

        Raises:
            RuntimeError: 如果未配置 session_manager
        """
        if self._llm_strategy is None:
            raise RuntimeError("LLM 验证需要 session_manager，但当前实例未配置")
        config = self._registry.get(node_id)
        return await self._llm_strategy.validate_async(subject_context, config)
```

---

## 5. 迁移实施步骤

### Step 1：创建新组件框架

**操作**：创建 `autoBMAD/docuswarm/context/validator.py`

**输入**：
- 本文档第 4 节的接口定义

**输出**：
- 新文件，包含 `ValidationResult`、`ValidationIssue`、`ValidationStrategy`（ABC）、`ValidationRuleRegistry`、`ContextValidator` 主类的骨架代码

**验证标准**：
- `python -c "from autoBMAD.docuswarm.context.validator import ContextValidator"` 无报错
- `python -m pytest tests/unit/context/test_validator.py` 通过基础构建测试

---

### Step 2：迁移私有字段验证逻辑

**操作**：  
将 `context/isolation.py` 中的 `_validate_no_private_fields`（L241）和 `_check_for_private_fields`（L260）迁移为 `PrivateFieldIsolationStrategy`

**具体修改**：
1. 在 `context/validator.py` 中实现 `PrivateFieldIsolationStrategy.validate()`（复用 `_check_for_private_fields` 递归逻辑）
2. 修改 `ContextManager._validate_no_private_fields`（`isolation.py` L241）：改为调用 `PrivateFieldIsolationStrategy().validate(data, "deliverable")`
3. 保留 `isolation.py` 中 `_check_for_private_fields` 函数，标注为 `@deprecated`

**输入**：`context/isolation.py` L241–L291  
**输出**：`PrivateFieldIsolationStrategy` 完整实现 + `isolation.py` 更新  
**验证标准**：
- `ContextIsolationError` 仍由同一路径抛出（向后兼容）
- 已有测试 `tests/unit/context/test_isolation.py` 全部通过

---

### Step 3：迁移 NodeExecutionContext 验证逻辑

**操作**：  
扩展 `node_execution/validator.py::ContextValidator` 的旧实现，但在新 `context/validator.py` 中实现完整的 `NodeExecutionContextStrategy`

**具体修改**：
1. 实现 `NodeExecutionContextStrategy.validate()` —— 验证所有 `NodeExecutionContextRequired` 字段（`contracts.py` L39–L74）
2. 在 `node_execution/validator.py` 中，将 `ContextValidator` 标记为 `@deprecated`，并提供 `from autoBMAD.docuswarm.context.validator import ContextValidator` 的别名重导出

**输入**：`node_execution/contracts.py` L39–L74（`NodeExecutionContextRequired` 字段定义）  
**输出**：`NodeExecutionContextStrategy` 完整实现  
**验证标准**：
- 对合法 `NodeExecutionContext` 字典返回 `ValidationResult(valid=True)`
- 对缺失 `pipeline_id` 字段时返回含 `MISSING_REQUIRED_FIELD` error 的结果

---

### Step 4：迁移输出验证逻辑

**操作**：  
将 `llm/response.py` 中的 `validate_independent_output`（L140）和 `validate_evaluator_output`（L229）迁移为策略类

**具体修改**：
1. 实现 `IndependentOutputValidationStrategy.validate()`（保持与现有逻辑等价）
2. 实现 `EvaluatorOutputValidationStrategy.validate()`
3. 修改 `llm/response.py`：原函数保持不变，内部改为委托调用策略类
4. 在策略类中增加节点级规则支持（`min_word_count` 等）

**输入**：`llm/response.py` L140–L305  
**输出**：两个策略类 + `llm/response.py` 委托调用  
**验证标准**：
- `validate_independent_output` / `validate_evaluator_output` 的外部接口不变（向后兼容）
- 原有测试全部通过

---

### Step 5：迁移 LLM 上下文验证逻辑

**操作**：  
将 `pipeline/orchestrator.py::HybridOrchestrator._validate_context`（L262–L344）迁移为 `LLMContextValidationStrategy`

**具体修改**：
1. 实现 `LLMContextValidationStrategy.validate_async()`（复制 orchestrator L262–L344 逻辑）
2. 修改 `HybridOrchestrator.__init__` 注入 `ContextValidator` 实例
3. 修改 `HybridOrchestrator.start_pipeline`（L427–L436）：将 `await self._validate_context(subject_context)` 改为 `await self._context_validator.validate_context_with_llm(subject_context)`
4. 删除 `HybridOrchestrator._validate_context` 方法（或保留空方法调用新实现）

**输入**：`pipeline/orchestrator.py` L46–L69（CONTEXT_VALIDATION_PROMPT）+ L262–L344  
**输出**：`LLMContextValidationStrategy` + `orchestrator.py` 简化  
**验证标准**：
- `HybridOrchestrator` 在 start_pipeline 流程中仍能触发 LLM 验证
- `ContextValidationError` 异常在验证失败时仍能被正确抛出

---

### Step 6：实现 ValidationRuleRegistry 配置加载

**操作**：  
在 `NodeLoader.load_node` 调用链中加入规则注册

**具体修改**：
1. 修改 `nodes/loader.py::NodeLoader.load_node` 方法：在返回 `NodeConfig` 前，将 `node_yaml.get("validation", {})` 注入 `ContextValidator` 的 `load_node_rules`
2. 修改 `nodes/dual_agent.py`（使用 `NodeLoader` 的地方）：传入 `ContextValidator` 实例
3. 为 5 个节点的 `node.yaml` 添加 `validation` 配置块（可选，有默认值）

**输入**：`nodes/loader.py` L78–L238 中的 `NodeLoader.load_node` 实现  
**输出**：配置化验证规则注册流程  
**验证标准**：
- 不同节点调用 `validate_independent_output` 时，使用各自的节点级规则
- 若 `node.yaml` 无 `validation` 块，使用全局默认值

---

### Step 7：更新 `context/__init__.py` 导出

**操作**：  
将新 `ContextValidator` 加入 `context/__init__.py` 的 `__all__`

**具体修改**：
```python
# autoBMAD/docuswarm/context/__init__.py 增加
from autoBMAD.docuswarm.context.validator import ContextValidator, ValidationResult
__all__ = [..., "ContextValidator", "ValidationResult"]
```

**验证标准**：
- `from autoBMAD.docuswarm.context import ContextValidator` 可用

---

## 6. 风险评估

### 6.1 兼容性风险

| 风险项 | 风险级别 | 影响范围 | 缓解策略 |
|--------|----------|----------|----------|
| `ContextIsolationError` 抛出路径变化 | 中 | `isolation.py` 调用方 | Step 2 中保持异常抛出位置不变（wrapper） |
| `validate_independent_output` 返回值类型变化 | 高 | `nodes/dual_agent.py`、`llm/response.py` 调用方 | Step 4 保持函数签名和返回 `None`（仅抛出异常）的原有行为 |
| `ContextValidator`（旧类）被重名覆盖 | 中 | `node_execution/validator.py` 导入方 | Step 3 保留旧类作为别名，发出 `DeprecationWarning` |
| `CONTEXT_VALIDATION_PROMPT` 常量位置变化 | 低 | 无外部依赖 | Step 5 中从 `orchestrator.py` 迁移为策略类内部常量 |

### 6.2 性能影响

**预期影响**：可忽略

- 策略模式引入的额外方法调用层级 < 1μs
- `ValidationRuleRegistry.get()` 为 O(1) 字典查找
- `PrivateFieldIsolationStrategy` 的递归检查：与原 `_check_for_private_fields` 性能等价
- LLM 验证（`LLMContextValidationStrategy`）为异步调用，网络 I/O 主导，策略封装无影响

**注意事项**：  
`NodeLoader` 在 `load_node` 时加入 `load_node_rules` 调用，仅在节点首次加载时执行，已有缓存机制（`_cache: dict[str, NodeConfig]`）可避免重复加载。

### 6.3 测试覆盖

**现有测试影响分析**：

| 测试文件 | 影响评估 | 处理方式 |
|----------|----------|----------|
| `tests/unit/context/test_isolation.py` | 低风险 | `_validate_no_private_fields` 行为不变，无需修改 |
| `tests/unit/node_execution/test_validator.py` | 低风险 | 旧 `ContextValidator` 保留别名，测试继续通过 |
| `tests/unit/pipeline/test_orchestrator.py` | 中风险 | `_validate_context` 迁移后，Mock 目标改为 `ContextValidator.validate_context_with_llm` |
| `tests/unit/llm/test_response.py` | 低风险 | `validate_independent_output` 函数签名不变 |

**新增测试需求**：

```
tests/unit/context/test_validator.py
├── test_validation_result_creation
├── test_node_execution_context_strategy_valid
├── test_node_execution_context_strategy_missing_fields
├── test_node_execution_context_strategy_invalid_node_id
├── test_private_field_isolation_strategy_clean
├── test_private_field_isolation_strategy_detects_leak
├── test_independent_output_strategy_valid
├── test_independent_output_strategy_missing_file_path
├── test_evaluator_output_strategy_valid_verdict
├── test_evaluator_output_strategy_invalid_verdict
├── test_validation_rule_registry_register_and_get
└── test_context_validator_load_node_rules
```

---

## 7. 附录

### 7.1 诊断工具原始输出摘要

工具命令：
```bash
python tools/context_validator_analyzer.py --format json --output .tmp/context_validator_analysis.json
```

关键统计（来自 `.tmp/context_validator_analysis.json`）：

```json
{
  "summary": {
    "total_files_analyzed": 95,
    "total_validation_methods": 39,
    "total_call_sites": 104,
    "total_inline_patterns": 126,
    "total_coupling_relations": 59,
    "high_priority_extractions": 15,
    "files_with_most_validation": [
      {"file": "autoBMAD/docuswarm/storage/checkpoints.py", "count": 6},
      {"file": "autoBMAD/docuswarm/node_execution/state.py", "count": 3},
      {"file": "autoBMAD/docuswarm/pipeline/graph.py", "count": 3},
      {"file": "autoBMAD/docuswarm/pipeline/orchestrator.py", "count": 3},
      {"file": "autoBMAD/docuswarm/context/isolation.py", "count": 2},
      {"file": "autoBMAD/docuswarm/llm/response.py", "count": 2},
      {"file": "autoBMAD/docuswarm/node_execution/validator.py", "count": 2}
    ]
  }
}
```

### 7.2 受影响文件清单

#### 直接修改文件（需代码变更）

| 文件 | 变更类型 | 变更步骤 |
|------|----------|----------|
| `autoBMAD/docuswarm/context/validator.py` | **新建** | Step 1–7 |
| `autoBMAD/docuswarm/context/__init__.py` | 新增导出 | Step 7 |
| `autoBMAD/docuswarm/context/isolation.py` | 委托调用（L241–L257） | Step 2 |
| `autoBMAD/docuswarm/node_execution/validator.py` | 添加 deprecated 别名 | Step 3 |
| `autoBMAD/docuswarm/llm/response.py` | 委托调用（L140–L305） | Step 4 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | 移除 `_validate_context` 实现 | Step 5 |
| `autoBMAD/docuswarm/nodes/loader.py` | 注入规则注册（`load_node`） | Step 6 |

#### 间接影响文件（可能需要更新 Mock 路径）

| 文件 | 影响原因 |
|------|----------|
| `tests/unit/pipeline/test_orchestrator.py` | Mock 目标路径变化 |
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 需要传入 `ContextValidator` 实例 |
| `autoBMAD/docuswarm/pipeline/graph.py` | 若 `create_pipeline_graph` 构造 DualAgentNode，需传入验证器 |

#### 节点配置文件（可选，建议补充）

| 文件 | 变更类型 |
|------|----------|
| `nodes/analyst/node.yaml` | 新增 `validation` 块 |
| `nodes/pm/node.yaml` | 新增 `validation` 块 |
| `nodes/ux/node.yaml` | 新增 `validation` 块 |
| `nodes/architect/node.yaml` | 新增 `validation` 块 |
| `nodes/po/node.yaml` | 新增 `validation` 块 |

### 7.3 参考评估文档

本报告参考了以下 DocuSwarm 内部评估文档：
- `docs/evaluation/2026-03-26-docuswarm-unified-context-system-analysis.md`：统一上下文体系深度解析（410 行）
- `docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md`：深度架构分析

---

*文档结束 — 共 7 章节 + 3 个附录*
