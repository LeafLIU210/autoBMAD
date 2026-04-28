# Epic 30: 集成验证

**Epic ID**: EPIC-30  
**关联方案**: [00-refactoring-roadmap.md](../research/refactor-2026-03-26/00-refactoring-roadmap.md) (Phase 5)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 3-4 Days  
**Priority**: P1 - Phase 5 最终验证  

---

## 1. Epic Overview

### 1.1 Summary

全面验证 EPIC-25 至 EPIC-29 的重构效果。包括端到端管道测试（5 节点完整流水线）、回归测试（全量测试套件）、性能基准测试（节点执行时间、Token 消耗）、以及架构完成度最终验证（95% 目标）。运行所有诊断工具组确认指标达标。

### 1.2 Business Value

- **质量保证**: 确保所有重构不引入回归
- **性能基线**: 建立重构后的性能基准
- **架构验证**: 通过诊断工具客观确认 95% 架构完成度
- **信心交付**: 为后续开发提供可靠的代码基线

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 架构总体完成度 | ≥ 95% |
| 全量测试通过率 | 100% |
| 死代码行数（MemoryManager） | 0 |
| `contracts.py` 行数 | ≤ 70 |
| `NodeExecutionContext` 字段数 | 9 |
| DRY 违反数 | 0 |
| 代码-配置断层数 | 0 |
| SDK 能力实现率 | ≥ 83% |
| 节点执行时间不超过基线 | +10% |

### 1.4 Dependencies

- **Requires**: EPIC-25, EPIC-26, EPIC-27, EPIC-28, EPIC-29（全部完成）
- **Blocks**: 无（本 Epic 为重构收尾）

---

## 2. Architecture Context

### 2.1 验证矩阵

```
诊断工具组:
  ├── context_validator_analyzer.py     → 验证逻辑统一化覆盖率 = 39/39
  ├── node_config_completeness_checker.py → 节点配置真实完整度 ≥ 95%
  ├── agent_sdk_capability_auditor.py   → SDK 能力实现率 ≥ 83%
  └── memory_manager_dependency_scanner.py → MemoryManager 引用 = 0

测试层次:
  ├── 单元测试（unit/）          → 各模块独立验证
  ├── 集成测试（integration/）   → 模块间协作验证
  ├── 端到端测试（e2e/）         → 5 节点完整流水线
  └── 架构测试（architecture/）  → 导出完整性、死代码检测
```

### 2.2 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `tests/e2e/test_full_pipeline.py` | **新建/修改** | 5 节点端到端流水线测试 |
| `tests/architecture/test_refactoring_goals.py` | **新建** | 架构完成度目标验证 |
| `tests/unit/tools/test_file_tools.py` | **新建** | 文件工具权限边界测试 |
| `tests/unit/tools/test_search_tools.py` | **新建** | 搜索工具测试 |

---

## 3. User Stories

### Story 30.1: 端到端管道测试

**Story Points**: 3  
**Priority**: P0  
**Description**: As a quality engineer, I want end-to-end pipeline tests that verify all 5 nodes complete successfully, so that the refactoring doesn't break the core workflow.

**Acceptance Criteria**:

- [ ] 5 节点完整流水线运行，全部完成，输出 5 份交付物
- [ ] ContextValidator 验证失败流程：抛出 `ContextValidationError`，管道停止
- [ ] Schema v2 节点配置加载：`task.name` 正确读取为任务名（非角色名）
- [ ] 文件工具权限边界：po 可读 `docs/`，analyst 不可读 `docs/stories/`
- [ ] BMAD 技能注入验证：system_prompt 含技能描述，token 数 < 400

---

### Story 30.2: 回归测试

**Story Points**: 2  
**Priority**: P0  
**Description**: As a developer, I want the full test suite passing, so that no existing functionality is broken.

**Acceptance Criteria**:

- [ ] `python -m pytest tests/ -v --tb=short` 全部通过
- [ ] 重点关注改造涉及的文件：`isolation.py`、`orchestrator.py`、`contracts.py`、`loader.py`
- [ ] Mock 目标路径审查：`test_orchestrator.py` 中 `_validate_context` 的 Mock 已更新
- [ ] 测试覆盖率不低于改造前基线

---

### Story 30.3: 性能基准测试

**Story Points**: 2  
**Priority**: P1  
**Description**: As a performance engineer, I want baseline metrics established, so that future changes can be measured against them.

**Acceptance Criteria**:

- [ ] 节点平均执行时间不超过基线 +10%
- [ ] SDK token 消耗增量 < +14000 tokens/节点
- [ ] `ValidationRuleRegistry.get()` 查找性能 < 1μs（O(1)）
- [ ] `PrivateFieldIsolationStrategy` 递归检查性能等价于原实现

---

### Story 30.4: 架构完成度最终验证

**Story Points**: 2  
**Priority**: P0  
**Description**: As the tech lead, I want diagnostic tools to confirm all refactoring goals are met, so that the architecture readiness is objectively verified.

**Acceptance Criteria**:

- [ ] `context_validator_analyzer.py` 报告验证逻辑统一化覆盖率 = 39/39（100%）
- [ ] `grep -r "MemoryManager" autoBMAD/ --include="*.py"` 结果为空
- [ ] `node_config_completeness_checker.py` 报告所有节点 `task.name` 存在
- [ ] `agent_sdk_capability_auditor.py` 报告能力实现率 ≥ 10/12
- [ ] `contracts.py` 行数 ≤ 70
- [ ] `NodeExecutionContext` 字段数 = 9

**验证脚本**:

```bash
# 完整质量门禁
echo "=== Phase 5 架构完成度验证 ==="

echo "[1] Context 模块导入..."
python -c "from autoBMAD.docuswarm.context import ContextValidator, ContextManager; print('OK')"

echo "[2] NodeLoader v2..."
python -c "from autoBMAD.nodes.loader import NodeLoader; c = NodeLoader().load('analyst'); assert c.task.name == 'create-business-analysis-report'; print('OK')"

echo "[3] MemoryManager 零引用..."
python -c "
try:
    from autoBMAD.docuswarm.context import MemoryManager
    print('FAIL: MemoryManager still importable')
    exit(1)
except ImportError:
    print('OK')
"

echo "[4] 诊断工具..."
python tools/node_config_completeness_checker.py

echo "[5] 全量测试..."
python -m pytest tests/ -v --tb=short --cov=autoBMAD/docuswarm --cov-report=term-missing

echo "[6] 类型检查..."
basedpyright autoBMAD/docuswarm/

echo "=== 验证完成 ==="
```

---

## 4. 重构成果汇总（验证 checklist）

| 维度 | 指标 | 当前值 | 目标值 | 验证方式 |
|------|------|--------|--------|----------|
| **死代码** | MemoryManager 代码行数 | 179 | 0 | 文件系统检查 |
| **协议精简** | NodeExecutionContext 字段数 | 16 | 9 | 代码审查 |
| **代码精简** | contracts.py 行数 | 125 | ≤ 70 | `wc -l` |
| **DRY** | 语义等价字段重复数 | 6 | 0 | 人工审查 |
| **配置对齐** | 代码-配置断层数 | 3 | 0 | context_builder.py 审查 |
| **验证统一** | 验证方法统一覆盖率 | 38% | 100% | 诊断工具 |
| **SDK 能力** | 能力实现率 | 58.3% | ≥ 83% | 审计工具 |
| **SDK 字段** | ClaudeAgentOptions 使用率 | 23.5% | ≥ 47% | 代码审查 |
| **BMAD 技能** | 命令利用率 | 0% | 核心命令覆盖 | system_prompt 检查 |
| **task_name 语义** | 正确率 | 0% | 100% | loader 验证 |
| **配置完整度** | 真实完整度 | ~60%(假阳性100%) | ≥ 95% | 升级版诊断工具 |
