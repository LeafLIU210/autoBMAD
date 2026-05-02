# DocuSwarm 类型错误修复 - 测试驱动方案

**方案版本:** 1.0  
**创建日期:** 2026-03-17  
**目标:** 修复 basedpyright 报告的所有类型错误  
**方法论:** 测试驱动开发 (TDD) - 红-绿-重构循环

---

## 1. 执行摘要

### 1.1 待修复问题清单

| 优先级 | 问题 | 文件 | 错误数 | 测试策略 |
|--------|------|------|--------|----------|
| P0 | TypedDict NotRequired 访问 | `agents/evaluator.py` | 5 | 单元测试验证访问安全 |
| P0 | TypedDict NotRequired 访问 | `agents/independent.py` | 7 | 单元测试验证访问安全 |
| P0 | 未定义变量 | `nodes/dual_agent.py` | 2 | 导入测试 + 类型检查 |
| P1 | __all__ 声明不匹配 | `models/__init__.py` | 2 | 导出测试 |
| P1 | __all__ 声明不匹配 | `node_execution/__init__.py` | 40 | 导出测试 |
| P2 | 隐式方法覆盖 | `models/tool_registry.py` | 1 | 装饰器验证 |

### 1.2 TDD 工作流程

```
对于每个问题:
  1. 编写测试 - 验证问题存在 (RED)
  2. 运行测试 - 确认失败 (RED)
  3. 修复代码 - 最小修改 (GREEN)
  4. 运行测试 - 确认通过 (GREEN)
  5. 运行 basedpyright - 确认错误消失 (GREEN)
  6. 重构 - 改进代码质量 (REFACTOR)
  7. 运行所有测试 - 确保无回归 (VERIFY)
```

---

## 2. 测试基础设施

### 2.1 测试文件结构

```
autoBMAD/docuswarm/tests/
├── conftest.py                          # 已有
├── unit/
│   ├── test_type_safety/                # 新增类型安全测试包
│   │   ├── __init__.py
│   │   ├── test_evaluator_types.py      # 测试 evaluator TypedDict
│   │   ├── test_independent_types.py    # 测试 independent TypedDict
│   │   ├── test_dual_agent_types.py     # 测试 dual_agent 导入
│   │   ├── test_models_exports.py       # 测试 models 导出
│   │   ├── test_node_execution_exports.py # 测试 node_execution 导出
│   │   └── test_tool_registry_types.py  # 测试 tool_registry 装饰器
│   └── ...
└── integration/
    └── test_type_safety_integration.py  # 集成测试
```

### 2.2 测试基类和工具

- `TypeSafetyTestCase`: 基础测试类，提供 basedpyright 运行工具
- `TypedDictAccessValidator`: 验证 TypedDict 安全访问的工具
- `ExportValidator`: 验证模块导出的工具

---

## 3. 详细修复计划

### 3.1 P0: TypedDict NotRequired 访问修复

#### 问题描述
代码直接访问 TypedDict 的可选字段，可能导致运行时 KeyError。

#### 测试策略
1. 创建测试用例，传入缺少字段的 TypedDict
2. 验证代码不抛出 KeyError
3. 验证返回合理的默认值

#### 修复步骤

**Step 1: 编写失败测试**
```python
# test_evaluator_types.py
def test_evaluator_handles_missing_task_name():
    """Test that evaluator handles missing task_name gracefully."""
    agent_input = {}  # Empty input
    # Should not raise KeyError
    result = evaluator_agent.execute_with_input(agent_input, "test-pipeline")
    assert result is not None
```

**Step 2: 修复代码**
```python
# evaluator.py
# 修改前:
task_name = agent_input["task_name"]

# 修改后:
task_name = agent_input.get("task_name", "")
```

**Step 3: 验证**
- 测试通过
- basedpyright 无错误

### 3.2 P0: 未定义变量修复

#### 问题描述
`NodeExecutionContext` 未在 `dual_agent.py` 中正确导入。

#### 测试策略
1. 导入测试：验证类型可以正确引用
2. 类型检查测试：验证函数签名有效

#### 修复步骤

**Step 1: 编写失败测试**
```python
# test_dual_agent_types.py
def test_node_execution_context_importable():
    """Test that NodeExecutionContext can be imported."""
    from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
    # This should not raise ImportError
    assert DualAgentNode is not None
```

**Step 2: 修复代码**
添加导入到 TYPE_CHECKING 块。

**Step 3: 验证**
- 测试通过
- basedpyright 无错误

### 3.3 P1: __all__ 声明修复

#### 问题描述
`__all__` 列表中的项目通过 `__getattr__` 延迟加载，类型检查器无法识别。

#### 测试策略
1. 导出测试：验证 `__all__` 中所有名称都可以导入
2. 类型检查：验证导出项有正确的类型注解

#### 修复策略
**选项 A:** 显式重新导出（推荐用于 models）
**选项 B:** 添加类型忽略注释（推荐用于 node_execution）

---

## 4. 测试用例规范

### 4.1 测试命名规范

```
test_<module>_<specific_issue>_<condition>

例如:
- test_evaluator_typeddict_access_missing_task_name
- test_independent_typeddict_access_empty_input
- test_dual_agent_import_node_execution_context
```

### 4.2 测试分类

- `unit/type_safety/`: 单元测试，验证特定类型问题
- `integration/`: 集成测试，验证模块间类型兼容性
- `regression/`: 回归测试，防止问题再次出现

### 4.3 断言规范

```python
# TypedDict 访问测试
assert agent_input.get("key") == expected_value  # 安全访问

# 导入测试
from module import Name  # 不应抛出 ImportError

# 类型检查测试
assert callable(func)  # 验证可调用
assert isinstance(obj, ExpectedType)  # 验证类型
```

---

## 5. 执行计划

### Phase 1: 准备工作 (30 分钟)

- [ ] 创建测试目录结构
- [ ] 创建测试基类
- [ ] 设置 basedpyright 验证脚本

### Phase 2: P0 问题修复 (2 小时)

#### 2.1 evaluator.py (30 分钟)
- [ ] 编写 TypedDict 访问测试
- [ ] 运行测试 - 确认失败
- [ ] 修复代码
- [ ] 运行测试 - 确认通过
- [ ] 运行 basedpyright - 确认无错误

#### 2.2 independent.py (30 分钟)
- [ ] 编写 TypedDict 访问测试
- [ ] 运行测试 - 确认失败
- [ ] 修复代码
- [ ] 运行测试 - 确认通过
- [ ] 运行 basedpyright - 确认无错误

#### 2.3 dual_agent.py (30 分钟)
- [ ] 编写导入测试
- [ ] 运行测试 - 确认失败
- [ ] 修复代码
- [ ] 运行测试 - 确认通过
- [ ] 运行 basedpyright - 确认无错误

### Phase 3: P1 问题修复 (1 小时)

#### 3.1 models/__init__.py (20 分钟)
- [ ] 编写导出测试
- [ ] 修复代码
- [ ] 验证

#### 3.2 node_execution/__init__.py (20 分钟)
- [ ] 编写导出测试
- [ ] 修复代码
- [ ] 验证

#### 3.3 tool_registry.py (20 分钟)
- [ ] 编写装饰器测试
- [ ] 修复代码
- [ ] 验证

### Phase 4: 验证与回归测试 (30 分钟)

- [ ] 运行所有单元测试
- [ ] 运行所有集成测试
- [ ] 运行 basedpyright 完整扫描
- [ ] 验证 0 错误 0 警告

---

## 6. 回滚策略

### 6.1 如果修复导致功能问题

```bash
# 回滚特定文件
git checkout autoBMAD/docuswarm/agents/evaluator.py

# 重新运行测试
pytest autoBMAD/docuswarm/tests/unit/test_type_safety/ -v
```

### 6.2 如果测试无法通过

1. 检查修复是否正确应用
2. 检查测试是否合理
3. 考虑替代修复方案
4. 咨询原始代码作者

---

## 7. 成功标准

### 7.1 定量标准

- [ ] basedpyright 报告 0 错误
- [ ] basedpyright 报告 ≤ 10 警告（可选修复）
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率 ≥ 80%

### 7.2 定性标准

- [ ] 代码保持原有功能
- [ ] 修复最小化，只修改必要部分
- [ ] 新增测试可作为回归测试
- [ ] 文档已更新

---

## 8. 附录

### 8.1 相关文件

- 分析报告: `docs/research/basedpyright_analysis_report.md`
- 快速修复: `docs/research/quick_fix_guide.md`
- 修复工具: `tools/apply_type_fixes.py`

### 8.2 命令参考

```bash
# 运行特定测试
pytest autoBMAD/docuswarm/tests/unit/test_type_safety/test_evaluator_types.py -v

# 运行 basedpyright
python -m basedpyright autoBMAD/docuswarm

# 应用自动修复
python tools/apply_type_fixes.py --apply

# 检查修复状态
python tools/apply_type_fixes.py --check
```

---

**准备开始执行此方案！**
