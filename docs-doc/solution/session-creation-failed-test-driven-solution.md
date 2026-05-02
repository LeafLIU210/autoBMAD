# SessionManager `_work_dir` 缺失问题 - 测试驱动方案

**文档状态**: ✅ 已完成  
**关联根因分析**: [session-creation-failed-work-dir-root-cause.md](../research/session-creation-failed-work-dir-root-cause.md)  
**目标**: 通过测试驱动开发(TDD)方式修复并预防 `SessionManager` 属性缺失问题

---

## 一、方案概述

### 1.1 问题背景

`SessionManager` 在职责分离重构后，`self._work_dir` 被拆分为 `self._cwd` 和 `self._output_dir`，但 `create_session()` 和 `resume_session()` 中仍引用已删除的 `self._work_dir`，导致所有节点启动时崩溃。

### 1.2 TDD 核心理念

> **先写失败的测试 → 修复代码使测试通过 → 重构优化**

本方案遵循红-绿-重构循环，确保修复过程可验证、可回归。

---

## 二、测试矩阵设计

### 2.1 测试覆盖矩阵

| 测试层级 | 测试目标 | 优先级 | 状态 |
|---------|---------|-------|------|
| 单元测试 | `SessionManager` 属性存在性验证 | P0 | 待实现 |
| 单元测试 | `create_session()` 正常实例化 | P0 | 待实现 |
| 单元测试 | `resume_session()` 正常实例化 | P0 | 待实现 |
| 集成测试 | `ClaudeSessionWrapper` 接收正确参数 | P0 | 待实现 |
| 集成测试 | `IndependentAgent` 端到端会话创建 | P1 | 待实现 |
| 回归测试 | 重构后属性引用完整性 | P1 | 待实现 |

### 2.2 测试边界定义

```
┌─────────────────────────────────────────────────────────────┐
│                      端到端集成测试层                         │
│         (验证完整工作流: IndependentAgent → Session)         │
├─────────────────────────────────────────────────────────────┤
│                     组件集成测试层                           │
│    (验证 SessionManager → ClaudeSessionWrapper 交互)        │
├─────────────────────────────────────────────────────────────┤
│                       单元测试层                             │
│       (验证 SessionManager 属性、初始化、边界条件)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、详细测试用例

### 3.1 第一阶段：属性存在性测试（红）

**目标**: 验证 `SessionManager` 初始后所有必需属性存在

**测试文件**: `tests/docuswarm/llm/test_session_manager_attrs.py`

```python
"""SessionManager 属性存在性验证测试

对应根因: SessionManager._work_dir 被删除但引用点未更新
"""
import pytest
from pathlib import Path
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerAttributes:
    """验证 SessionManager 初始化后属性完整性"""
    
    def test_output_dir_attribute_exists(self):
        """Test: _output_dir 属性必须存在"""
        # Arrange
        sm = SessionManager(output_dir="/tmp/test")
        
        # Assert
        assert hasattr(sm, '_output_dir')
        assert isinstance(sm._output_dir, Path)
    
    def test_cwd_attribute_exists(self):
        """Test: _cwd 属性必须存在"""
        # Arrange
        sm = SessionManager(cwd="/tmp/test")
        
        # Assert
        assert hasattr(sm, '_cwd')
        assert isinstance(sm._cwd, Path)
    
    def test_work_dir_property_exists(self):
        """Test: work_dir property 必须存在（向后兼容）"""
        # Arrange
        sm = SessionManager(output_dir="/tmp/test")
        
        # Assert
        assert hasattr(sm, 'work_dir')
        assert isinstance(sm.work_dir, Path)
        assert sm.work_dir == sm._output_dir
    
    def test_work_dir_property_returns_output_dir(self):
        """Test: work_dir property 应返回 _output_dir"""
        # Arrange
        output_dir = Path("/custom/output")
        sm = SessionManager(output_dir=output_dir)
        
        # Assert
        assert sm.work_dir == output_dir
        assert sm.work_dir == sm._output_dir
```

**预期结果**: 红（测试通过，因为属性定义正确，但下一步会暴露引用问题）

---

### 3.2 第二阶段：方法级单元测试（红→绿）

**目标**: 验证 `create_session()` 和 `resume_session()` 能正确传递参数

**测试文件**: `tests/docuswarm/llm/test_session_manager_create_resume.py`

```python
"""SessionManager create_session / resume_session 单元测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestCreateSession:
    """测试 create_session 方法"""
    
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    def test_create_session_passes_output_dir_as_work_dir(
        self, mock_anthropic, mock_wrapper_class
    ):
        """Test: create_session 必须传递 _output_dir 而非 _work_dir
        
        对应修复点: session_manager.py 第 342 行
        根因: _work_dir 属性不存在导致 AttributeError
        """
        # Arrange
        output_dir = Path("/test/output")
        sm = SessionManager(output_dir=output_dir)
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Act
        sm.create_session(session_id="test_123", options={})
        
        # Assert - 关键验证: 必须传递 _output_dir
        mock_wrapper_class.assert_called_once()
        call_kwargs = mock_wrapper_class.call_args.kwargs
        assert 'work_dir' in call_kwargs
        assert call_kwargs['work_dir'] == output_dir
    
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    def test_create_session_no_attribute_error(
        self, mock_anthropic, mock_wrapper_class
    ):
        """Test: create_session 执行时不应抛出 AttributeError
        
        对应原始错误: 'SessionManager' object has no attribute '_work_dir'
        """
        # Arrange
        sm = SessionManager(output_dir="/test/output")
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Act & Assert - 不应抛出 AttributeError
        try:
            sm.create_session(session_id="test_123", options={})
        except AttributeError as e:
            if "_work_dir" in str(e):
                pytest.fail(f"create_session 不应抛出 _work_dir AttributeError: {e}")
            raise


class TestResumeSession:
    """测试 resume_session 方法"""
    
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    def test_resume_session_passes_output_dir_as_work_dir(
        self, mock_anthropic, mock_wrapper_class
    ):
        """Test: resume_session 必须传递 _output_dir 而非 _work_dir
        
        对应修复点: session_manager.py 第 384 行
        根因: _work_dir 属性不存在导致 AttributeError
        """
        # Arrange
        output_dir = Path("/test/output")
        sm = SessionManager(output_dir=output_dir)
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Act
        sm.resume_session(session_id="test_123")
        
        # Assert - 关键验证: 必须传递 _output_dir
        mock_wrapper_class.assert_called_once()
        call_kwargs = mock_wrapper_class.call_args.kwargs
        assert 'work_dir' in call_kwargs
        assert call_kwargs['work_dir'] == output_dir
    
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    def test_resume_session_no_attribute_error(
        self, mock_anthropic, mock_wrapper_class
    ):
        """Test: resume_session 执行时不应抛出 AttributeError"""
        # Arrange
        sm = SessionManager(output_dir="/test/output")
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Act & Assert - 不应抛出 AttributeError
        try:
            sm.resume_session(session_id="test_123")
        except AttributeError as e:
            if "_work_dir" in str(e):
                pytest.fail(f"resume_session 不应抛出 _work_dir AttributeError: {e}")
            raise
```

**修复前状态**: 红（测试失败，抛出 `AttributeError: 'SessionManager' object has no attribute '_work_dir'`）

**修复后状态**: 绿（测试通过）

---

### 3.3 第三阶段：集成测试

**目标**: 验证 `ClaudeSessionWrapper` 正确接收并使用参数

**测试文件**: `tests/docuswarm/llm/test_session_manager_integration.py`

```python
"""SessionManager 集成测试 - 验证组件间协作"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerIntegration:
    """验证 SessionManager 与下游组件的集成"""
    
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    def test_session_manager_create_session_integration(
        self, mock_wrapper_cls, mock_anthropic
    ):
        """Test: 完整 create_session 调用链验证"""
        # Arrange
        output_dir = Path("/test/output")
        cwd = Path("/test/project")
        sm = SessionManager(output_dir=output_dir, cwd=cwd)
        
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        mock_wrapper = Mock()
        mock_wrapper_cls.return_value = mock_wrapper
        
        # Act
        result = sm.create_session(
            session_id="sess_integration_001",
            options={"temperature": 0.7}
        )
        
        # Assert - 验证 wrapper 构造参数
        mock_wrapper_cls.assert_called_once_with(
            client=mock_client,
            session_id="sess_integration_001",
            work_dir=output_dir,  # 关键: 必须是 output_dir
            options={"temperature": 0.7}
        )
        assert result == mock_wrapper
    
    @patch('autoBMAD.docuswarm.llm.session_manager.Anthropic')
    @patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSessionWrapper')
    def test_session_manager_resume_session_integration(
        self, mock_wrapper_cls, mock_anthropic
    ):
        """Test: 完整 resume_session 调用链验证"""
        # Arrange
        output_dir = Path("/test/output")
        sm = SessionManager(output_dir=output_dir)
        
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        mock_wrapper = Mock()
        mock_wrapper_cls.return_value = mock_wrapper
        
        # Act
        result = sm.resume_session(session_id="sess_resume_001")
        
        # Assert - 验证 wrapper 构造参数
        mock_wrapper_cls.assert_called_once_with(
            client=mock_client,
            session_id="sess_resume_001",
            work_dir=output_dir  # 关键: 必须是 output_dir
        )
        assert result == mock_wrapper
```

---

### 3.4 第四阶段：回归测试（预防机制）

**目标**: 防止未来重构再次引入类似问题

**测试文件**: `tests/docuswarm/llm/test_session_manager_regression.py`

```python
"""SessionManager 回归测试 - 防止重构引入的破坏性变更"""
import pytest
import ast
import inspect
from pathlib import Path
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerRegression:
    """回归测试: 防止已删除属性的引用残留"""
    
    def test_no_private_work_dir_attribute_reference(self):
        """Test: 源代码中不应存在对 _work_dir 的直接引用
        
        这是一个静态代码分析测试，确保 _work_dir 不再被引用。
        如果将来有人不小心重新引入 _work_dir 引用，此测试会失败。
        """
        # Arrange - 读取源代码
        import autoBMAD.docuswarm.llm.session_manager as sm_module
        source_file = Path(sm_module.__file__)
        source_code = source_file.read_text(encoding='utf-8')
        
        # Act - 解析 AST
        tree = ast.parse(source_code)
        
        # Assert - 查找所有 Attribute 节点，确保没有 _work_dir
        work_dir_references = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == '_work_dir':
                    # 获取行号用于报告
                    work_dir_references.append(getattr(node, 'lineno', '?'))
        
        assert len(work_dir_references) == 0, (
            f"发现 {len(work_dir_references)} 处对 _work_dir 的引用，"
            f"位于第 {work_dir_references} 行。"
            f"应使用 _output_dir 或 work_dir property 替代。"
        )
    
    def test_output_dir_and_cwd_separation(self):
        """Test: _output_dir 和 _cwd 职责分离验证"""
        # Arrange
        output_dir = Path("/custom/output")
        cwd = Path("/custom/project")
        
        # Act
        sm = SessionManager(output_dir=output_dir, cwd=cwd)
        
        # Assert - 两个属性应独立
        assert sm._output_dir == output_dir
        assert sm._cwd == cwd
        assert sm._output_dir != sm._cwd
    
    def test_work_dir_property_backward_compatibility(self):
        """Test: work_dir property 向后兼容性"""
        # Arrange - 模拟旧代码通过 work_dir 访问
        output_dir = Path("/test/output")
        sm = SessionManager(output_dir=output_dir)
        
        # Act & Assert - work_dir 应返回 output_dir
        assert sm.work_dir == output_dir
        
        # 验证可以通过 work_dir 进行路径操作
        test_path = sm.work_dir / "subdir" / "file.txt"
        assert str(test_path) == "/test/output/subdir/file.txt"
```

---

## 四、修复代码实现

### 4.1 修复步骤

根据测试驱动原则，在测试失败后实施以下修复：

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

#### 步骤 1: 修复 `create_session()` (第 342 行)

```python
# 修复前（导致 AttributeError）
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._work_dir,   # ← 错误: _work_dir 不存在
    options=options,
)

# 修复后 ✅
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._output_dir,  # ← 正确: 使用 _output_dir
    options=options,
)
```

#### 步骤 2: 修复 `resume_session()` (第 384 行)

```python
# 修复前（导致 AttributeError）
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._work_dir,   # ← 错误: _work_dir 不存在
)

# 修复后 ✅
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._output_dir,  # ← 正确: 使用 _output_dir
)
```

### 4.2 验证修复

运行测试套件确认修复成功：

```bash
# 运行 SessionManager 相关测试
python -m pytest tests/docuswarm/llm/test_session_manager*.py -v

# 预期输出
# tests/docuswarm/llm/test_session_manager_attrs.py::TestSessionManagerAttributes::test_output_dir_attribute_exists PASSED
# tests/docuswarm/llm/test_session_manager_attrs.py::TestSessionManagerAttributes::test_cwd_attribute_exists PASSED
# tests/docuswarm/llm/test_session_manager_attrs.py::TestSessionManagerAttributes::test_work_dir_property_exists PASSED
# tests/docuswarm/llm/test_session_manager_create_resume.py::TestCreateSession::test_create_session_passes_output_dir_as_work_dir PASSED
# tests/docuswarm/llm/test_session_manager_create_resume.py::TestCreateSession::test_create_session_no_attribute_error PASSED
# tests/docuswarm/llm/test_session_manager_create_resume.py::TestResumeSession::test_resume_session_passes_output_dir_as_work_dir PASSED
# tests/docuswarm/llm/test_session_manager_create_resume.py::TestResumeSession::test_resume_session_no_attribute_error PASSED
# tests/docuswarm/llm/test_session_manager_integration.py::TestSessionManagerIntegration::test_session_manager_create_session_integration PASSED
# tests/docuswarm/llm/test_session_manager_integration.py::TestSessionManagerIntegration::test_session_manager_resume_session_integration PASSED
# tests/docuswarm/llm/test_session_manager_regression.py::TestSessionManagerRegression::test_no_private_work_dir_attribute_reference PASSED
# tests/docuswarm/llm/test_session_manager_regression.py::TestSessionManagerRegression::test_output_dir_and_cwd_separation PASSED
# tests/docuswarm/llm/test_session_manager_regression.py::TestSessionManagerRegression::test_work_dir_property_backward_compatibility PASSED
```

---

## 五、CI/CD 集成

### 5.1 自动化测试配置

在 `.github/workflows/test.yml` 中添加：

```yaml
- name: Run SessionManager Regression Tests
  run: |
    python -m pytest tests/docuswarm/llm/test_session_manager_regression.py -v
```

### 5.2 预提交钩子

在 `.pre-commit-config.yaml` 中添加自定义钩子：

```yaml
- repo: local
  hooks:
    - id: check-work-dir-reference
      name: Check for _work_dir references
      entry: bash -c 'grep -r "self._work_dir" autoBMAD/ && exit 1 || exit 0'
      language: system
      files: \.py$
```

---

## 六、执行计划

### 6.1 任务清单

- [x] **Phase 1: 根因分析** - 已完成（见根因分析文档）
- [x] **Phase 2: 编写失败测试** - 创建所有测试文件，验证测试失败
- [x] **Phase 3: 实施修复** - 修复 `__init__` 中路径类型转换问题
- [x] **Phase 4: 验证通过** - 运行所有测试，确认全部通过
- [x] **Phase 5: 回归防护** - AST 静态分析测试已添加
- [ ] **Phase 6: 端到端验证** - 运行完整工作流验证（可选）

### 6.2 测试执行命令

```bash
# 1. 运行 SessionManager 所有测试
python -m pytest tests/docuswarm/llm/test_session_manager*.py -v --tb=short

# 2. 运行所有 LLM 模块测试
python -m pytest tests/docuswarm/llm/ -v --tb=short

# 3. 运行端到端验证
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md

# 4. 覆盖率检查
python -m pytest tests/docuswarm/llm/test_session_manager*.py --cov=autoBMAD.docuswarm.llm.session_manager --cov-report=html
```

---

## 七、风险评估

| 风险项 | 概率 | 影响 | 缓解措施 |
|-------|------|------|---------|
| 修复遗漏其他引用点 | 低 | 高 | 使用 Grep 全局搜索 `self._work_dir` |
| 测试覆盖率不足 | 低 | 中 | 分三层测试（单元/集成/回归） |
| 向后兼容性问题 | 极低 | 高 | 验证 `work_dir` property 行为 |

---

## 八、相关文档

| 文档 | 路径 |
|-----|------|
| 根因分析报告 | `docs/research/session-creation-failed-work-dir-root-cause.md` |
| 修复 PR | （待创建） |
| 测试报告 | （修复后生成） |

---

## 九、附录：快速参考

### 9.1 错误签名

```
[error] session_creation_failed    error='SessionManager' object has no attribute '_work_dir'
```

### 9.2 修复代码片段

```python
# 两处修改位置
# autoBMAD/docuswarm/llm/session_manager.py:342
# autoBMAD/docuswarm/llm/session_manager.py:384

# 修改内容: self._work_dir → self._output_dir
```

### 9.3 测试运行速查

```bash
# 仅运行相关测试
python -m pytest tests/docuswarm/llm/test_session_manager*.py -v
```

---

## 十、测试执行报告

### 10.1 执行摘要

**执行时间**: 2026-04-06  
**执行环境**: Windows / Python 3.12.10 / pytest 8.4.2  
**测试范围**: SessionManager 全量测试套件

### 10.2 测试结果

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.4.2, pluggy-1.6.0
collected 13 items

tests\docuswarm\llm\test_session_manager_attrs.py ....                   [ 30%]
tests\docuswarm\llm\test_session_manager_create_resume.py ....           [ 61%]
tests\docuswarm\llm\test_session_manager_integration.py ..               [ 76%]
tests\docuswarm\llm\test_session_manager_regression.py ...               [100%]

============================= 13 passed in 1.29s =============================
```

### 10.3 代码修复记录

#### 修复 1: `SessionManager.__init__` 路径类型转换

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

**问题**: `__init__` 方法接收字符串路径但未转换为 `Path` 对象

**修复前**:
```python
if work_dir is not None:
    self._cwd = cwd or work_dir
    self._output_dir = output_dir or work_dir
else:
    self._cwd = cwd or Path.cwd()
    self._output_dir = output_dir or self._cwd
```

**修复后**:
```python
# Convert string paths to Path objects
if work_dir is not None:
    work_dir = Path(work_dir) if not isinstance(work_dir, Path) else work_dir
if cwd is not None:
    cwd = Path(cwd) if not isinstance(cwd, Path) else cwd
if output_dir is not None:
    output_dir = Path(output_dir) if not isinstance(output_dir, Path) else output_dir

if work_dir is not None:
    self._cwd = cwd or work_dir
    self._output_dir = output_dir or work_dir
else:
    self._cwd = cwd or Path.cwd()
    self._output_dir = output_dir or self._cwd
```

### 10.4 验证结论

| 验证项 | 状态 | 说明 |
|-------|------|------|
| `_output_dir` 属性存在性 | ✅ 通过 | 类型正确为 `Path` |
| `_cwd` 属性存在性 | ✅ 通过 | 类型正确为 `Path` |
| `work_dir` property 向后兼容 | ✅ 通过 | 返回 `_output_dir` |
| `create_session()` 无 AttributeError | ✅ 通过 | 不再抛出 `_work_dir` 错误 |
| `resume_session()` 无 AttributeError | ✅ 通过 | 不再抛出 `_work_dir` 错误 |
| `_output_dir` 正确传递给 Wrapper | ✅ 通过 | 参数传递验证通过 |
| AST 静态分析无违规 | ✅ 通过 | SessionManager 中无 `_work_dir` 引用 |
| 职责分离验证 | ✅ 通过 | `_cwd` 和 `_output_dir` 独立工作 |

### 10.5 测试文件清单

| 文件 | 测试数 | 说明 |
|------|-------|------|
| `test_session_manager_attrs.py` | 4 | 属性存在性和类型验证 |
| `test_session_manager_create_resume.py` | 4 | create/resume 方法测试 |
| `test_session_manager_integration.py` | 2 | 组件集成测试 |
| `test_session_manager_regression.py` | 3 | 回归防护测试 |

---

*本文档遵循测试驱动开发(TDD)原则，确保修复的可验证性和可回归性。*
