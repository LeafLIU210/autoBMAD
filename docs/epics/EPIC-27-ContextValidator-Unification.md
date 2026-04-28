# Epic 27: ContextValidator 统一化重构

**Epic ID**: EPIC-27  
**关联方案**: [01-context-validator-extraction.md](../research/refactor-2026-03-26/01-context-validator-extraction.md)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 3-4 Days  
**Priority**: P1 - Phase 2 核心架构重构  
**取代**: EPIC-13-CONTEXT-VALIDATOR  

---

## 1. Epic Overview

### 1.1 Summary

将散布于 10+ 文件的 39 个验证方法收归统一的 `context/validator.py` 策略门面。采用策略模式（Strategy Pattern）+ 组合模式（Composite Pattern），实现 `NodeExecutionContextStrategy`、`PrivateFieldIsolationStrategy`、`LLMContextValidationStrategy`、`IndependentOutputValidationStrategy`、`EvaluatorOutputValidationStrategy` 五个策略类。**直接替换旧实现**，不保留 `@deprecated` 别名或委托调用包装器。

### 1.2 Business Value

- **职责单一化**: `HybridOrchestrator` 不再持有验证实现（83 行验证代码移出）
- **可测试性**: 验证逻辑解耦后，单元测试不再需要 Mock LLM 或完整 Orchestrator
- **节点级定制**: 通过 `ValidationRuleRegistry` 支持按 `node_id` 注册不同验证规则
- **统一入口**: 所有验证通过 `ContextValidator` 单一门面调用

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| `from ... import ContextValidator` 可用 | Yes |
| `HybridOrchestrator` 验证代码行数 | ≤ 5（仅委托调用） |
| `orchestrator.py` 中 `_validate_context` 方法 | 不存在（已删除） |
| `node_execution/validator.py::ContextValidator`（旧类） | 不存在（已删除） |
| ContextValidator 专项单元测试 | ≥ 12 条 |
| 所有现有验证相关测试通过 | 100% |

### 1.4 Dependencies

- **Requires**: EPIC-26（NodeConfig v2 的 `task` 字段用于 `NodeExecutionContextStrategy` 验证）
- **Blocks**: EPIC-30（集成验证依赖 ContextValidator）

---

## 2. Architecture Context

### 2.1 Component Overview

```
context/validator.py（新建）
└── ContextValidator（统一门面）
    ├── NodeExecutionContextStrategy        ← 新实现
    ├── PrivateFieldIsolationStrategy       ← 迁移自 isolation.py L241-L291
    ├── LLMContextValidationStrategy        ← 迁移自 orchestrator.py L262-L344
    ├── IndependentOutputValidationStrategy ← 迁移自 llm/response.py L140-L226
    ├── EvaluatorOutputValidationStrategy   ← 迁移自 llm/response.py L229-L305
    └── ValidationRuleRegistry              ← 按 node_id 注册规则（来自 node.yaml）
```

### 2.2 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `autoBMAD/docuswarm/context/validator.py` | **新建** | ContextValidator 统一门面 + 5 个策略类 |
| `autoBMAD/docuswarm/context/__init__.py` | **修改** | 导出 ContextValidator, ValidationResult |
| `autoBMAD/docuswarm/context/isolation.py` | **修改** | 删除 `_validate_no_private_fields` 和 `_check_for_private_fields`，改为调用策略类 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | **修改** | 删除 `_validate_context` 实现，注入 ContextValidator |
| `autoBMAD/docuswarm/llm/response.py` | **修改** | 删除 `validate_independent_output` 和 `validate_evaluator_output`，调用方直接使用策略类 |
| `autoBMAD/docuswarm/node_execution/validator.py` | **删除** | 旧 `ContextValidator` 类完全删除 |
| `tests/unit/context/test_validator.py` | **新建** | 12+ 条专项测试 |

---

## 3. User Stories

### Story 27.1: 创建 ContextValidator 框架和数据模型

**Story Points**: 2  
**Priority**: P0  
**Description**: As a developer, I want the ContextValidator skeleton with ValidationResult, ValidationIssue, and ValidationStrategy ABC, so that all strategy classes have a common foundation.

**Acceptance Criteria**:

- [ ] `context/validator.py` 包含 `ValidationIssue`（field, message, severity, code）、`ValidationResult`（valid, issues, warnings, metadata）、`ValidationStrategy`（ABC with `validate` method）、`ValidationRuleRegistry`、`ContextValidator` 主类
- [ ] `from autoBMAD.docuswarm.context.validator import ContextValidator` 无报错
- [ ] `ContextValidator` 暴露 `validate_execution_context`、`validate_isolation`、`validate_independent_output`、`validate_evaluator_output`、`validate_context_with_llm` 方法
- [ ] `context/__init__.py` 导出 `ContextValidator` 和 `ValidationResult`

---

### Story 27.2: 私有字段验证策略迁移

**Story Points**: 2  
**Priority**: P0  
**Description**: As the isolation system, I want private field validation moved to PrivateFieldIsolationStrategy, so that ContextManager no longer violates single responsibility.

**Acceptance Criteria**:

- [ ] `PrivateFieldIsolationStrategy` 完整实现递归私有字段检查（等价于原 `_check_for_private_fields`）
- [ ] `isolation.py` 中 `_validate_no_private_fields` 方法**删除**（非委托，直接删除）
- [ ] `isolation.py` 中 `_check_for_private_fields` 函数**删除**
- [ ] `ContextManager` 在需要验证时调用 `ContextValidator.validate_isolation()`
- [ ] `ContextIsolationError` 仍由 `ContextManager` 在验证失败时抛出（抛出位置不变）
- [ ] `tests/unit/context/test_isolation.py` 全部通过

---

### Story 27.3: NodeExecutionContext 验证策略实现

**Story Points**: 2  
**Priority**: P0  
**Description**: As the pipeline, I want NodeExecutionContext validated against its protocol, so that incomplete contexts are caught before agent execution.

**Acceptance Criteria**:

- [ ] `NodeExecutionContextStrategy` 验证所有必填身份字段（`pipeline_id`, `node_id`, `node_name`, `node_order`）
- [ ] 验证 `node_id` 属于 `{"analyst", "pm", "ux", "architect", "po"}`
- [ ] 验证 `node_order` 为 1-5 的整数
- [ ] `node_execution/validator.py` 中的旧 `ContextValidator` 类**删除**（不保留别名）
- [ ] 所有引用旧 `ContextValidator` 的导入路径更新为新路径

---

### Story 27.4: 输出验证策略迁移

**Story Points**: 2  
**Priority**: P0  
**Description**: As the dual-agent system, I want output validation extracted to strategy classes, so that validation rules can be customized per node.

**Acceptance Criteria**:

- [ ] `IndependentOutputValidationStrategy` 完整实现（等价于原 `validate_independent_output`）
- [ ] `EvaluatorOutputValidationStrategy` 完整实现（等价于原 `validate_evaluator_output`）
- [ ] `llm/response.py` 中 `validate_independent_output` 和 `validate_evaluator_output` 函数**删除**
- [ ] 所有调用方直接使用 `ContextValidator.validate_independent_output()` 和 `ContextValidator.validate_evaluator_output()`
- [ ] 支持节点级规则（如 `min_word_count`，通过 `ValidationRuleRegistry` 获取）

---

### Story 27.5: LLM 上下文验证策略迁移

**Story Points**: 3  
**Priority**: P0  
**Description**: As the orchestrator, I want LLM context validation extracted from HybridOrchestrator, so that the orchestrator only coordinates, never validates.

**Acceptance Criteria**:

- [ ] `LLMContextValidationStrategy` 完整实现异步验证（迁移自 `orchestrator.py` L262-L344）
- [ ] `CONTEXT_VALIDATION_PROMPT` 常量迁移为策略类内部常量
- [ ] `HybridOrchestrator._validate_context` 方法**删除**
- [ ] `HybridOrchestrator.__init__` 注入 `ContextValidator` 实例
- [ ] `start_pipeline` 中调用 `self._context_validator.validate_context_with_llm()`
- [ ] `ContextValidationError` 在验证失败时仍被正确抛出
- [ ] `tests/unit/pipeline/test_orchestrator.py` 中 Mock 目标路径更新为 `ContextValidator.validate_context_with_llm`

---

### Story 27.6: ValidationRuleRegistry 配置加载

**Story Points**: 1  
**Priority**: P1  
**Description**: As the node loader, I want validation rules from node.yaml automatically registered, so that each node gets its own validation configuration.

**Acceptance Criteria**:

- [ ] `NodeLoader.load_node` 在加载节点配置后，将 `node_yaml.get("validation", {})` 注入 `ContextValidator.load_node_rules()`
- [ ] 不同节点调用 `validate_independent_output` 时，使用各自的节点级规则
- [ ] 若 `node.yaml` 无 `validation` 块，使用全局默认值

---

### Story 27.7: ContextValidator 专项测试

**Story Points**: 2  
**Priority**: P0

**Acceptance Criteria**:

- [ ] `test_validation_result_creation` - 结果对象创建和属性
- [ ] `test_node_execution_context_strategy_valid` - 合法上下文通过
- [ ] `test_node_execution_context_strategy_missing_fields` - 缺失字段检测
- [ ] `test_node_execution_context_strategy_invalid_node_id` - 非法 node_id 检测
- [ ] `test_private_field_isolation_strategy_clean` - 无泄漏通过
- [ ] `test_private_field_isolation_strategy_detects_leak` - 检测私有字段泄漏
- [ ] `test_independent_output_strategy_valid` - 合法输出通过
- [ ] `test_independent_output_strategy_missing_file_path` - 缺失字段检测
- [ ] `test_evaluator_output_strategy_valid_verdict` - 合法判决通过
- [ ] `test_evaluator_output_strategy_invalid_verdict` - 非法判决检测
- [ ] `test_validation_rule_registry_register_and_get` - 注册和获取规则
- [ ] `test_context_validator_load_node_rules` - 节点规则加载

---

## 4. 质量门禁

```bash
python -c "from autoBMAD.docuswarm.context import ContextValidator; print('validator OK')"
python -m pytest tests/unit/context/ tests/unit/pipeline/ -v
basedpyright autoBMAD/docuswarm/context/validator.py
```
