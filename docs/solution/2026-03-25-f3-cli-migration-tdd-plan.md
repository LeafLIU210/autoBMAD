# F3 CLI 分层入口迁移 - 测试驱动方案

**方案日期**: 2026-03-25  
**方案依据**: [F3 CLI 分层入口深度研究报告](../research/2026-03-25-f3-cli-layered-entry-deep-research-report.md)  
**目标**: 通过 TDD 方式完成 CLI 入口从旧架构向新分层架构的迁移

---

## 1. 方案概述

### 1.1 问题定义

当前 DocuSwarm CLI 存在 **"分层完成 80%，但真实入口未切换"** 的问题：

| 问题 | 严重程度 | 描述 |
|------|----------|------|
| 生产入口未切换 | 🔴 P0 | `pyproject.toml` 仍指向旧入口 |
| 命令缺失 | 🔴 P1 | 新入口缺失 `cancel-all` 命令 |
| 向后兼容性 | 🟡 P1 | `list-pipelines` 改名为 `list` |
| 服务层不完整 | 🟡 P2 | PipelineService 缺失 `start`/`resume` 方法 |

### 1.2 TDD 策略

采用 **Red-Green-Refactor** 循环：

1. **Red**: 编写失败的测试，明确期望行为
2. **Green**: 编写最小代码使测试通过
3. **Refactor**: 优化代码，保持测试通过

### 1.3 阶段规划

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: 入口切换测试                                            │
│ ├── Test: 验证 pyproject.toml 指向新入口                         │
│ ├── Test: 验证 __main__.py 指向新入口                            │
│ └── Test: 验证 `docuswarm` 命令可执行                            │
├─────────────────────────────────────────────────────────────────┤
│ Phase 2: 命令覆盖测试                                            │
│ ├── Test: 新入口包含所有必需命令                                 │
│ ├── Test: cancel-all 命令功能正常                                │
│ └── Test: list-pipelines 向后兼容                                │
├─────────────────────────────────────────────────────────────────┤
│ Phase 3: 服务层测试                                              │
│ ├── Test: PipelineService.start() 存在且可调用                   │
│ ├── Test: PipelineService.resume() 存在且可调用                  │
│ └── Test: 命令通过 Service 调用而非直接 asyncio.run              │
├─────────────────────────────────────────────────────────────────┤
│ Phase 4: 实现与切换                                              │
│ ├── 修改 pyproject.toml                                          │
│ ├── 修改 __main__.py                                             │
│ └── 运行所有测试验证                                             │
├─────────────────────────────────────────────────────────────────┤
│ Phase 5: 功能补全                                                │
│ ├── 实现 cancel-all 命令                                         │
│ ├── 添加 list-pipelines 别名                                     │
│ ├── 完善 PipelineService                                         │
│ └── 运行所有测试验证                                             │
├─────────────────────────────────────────────────────────────────┤
│ Phase 6: 清理与验证                                              │
│ ├── 删除旧入口 main.py                                           │
│ ├── 运行完整回归测试                                             │
│ └── 更新文档                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 测试用例详细设计

### 2.1 Phase 1: 入口切换测试

#### Test 1.1: 验证 pyproject.toml 入口配置
```python
# tests/cli/test_entry_point_migration.py::TestEntryPointConfiguration::test_pyproject_toml_points_to_new_entry
def test_pyproject_toml_points_to_new_entry(self):
    """验证 pyproject.toml 指向新的 CLI 入口."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # 期望: docuswarm = "autoBMAD.docuswarm.cli.main:cli"
    assert 'docuswarm = "autoBMAD.docuswarm.cli.main:cli"' in content
```

#### Test 1.2: 验证 __main__.py 入口配置
```python
# tests/cli/test_entry_point_migration.py::TestEntryPointConfiguration::test_main_py_imports_new_entry
def test_main_py_imports_new_entry(self):
    """验证 __main__.py 导入新的 CLI 入口."""
    main_py_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "__main__.py"
    content = main_py_path.read_text()
    
    # 期望: from autoBMAD.docuswarm.cli.main import cli
    assert "from autoBMAD.docuswarm.cli.main import cli" in content
```

#### Test 1.3: 验证 CLI 可执行
```python
# tests/cli/test_entry_point_migration.py::TestEntryPointConfiguration::test_cli_is_executable
def test_cli_is_executable(self):
    """验证 CLI 可以被导入和执行."""
    from click.testing import CliRunner
    from autoBMAD.docuswarm.cli.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "DocuSwarm" in result.output
```

### 2.2 Phase 2: 命令覆盖测试

#### Test 2.1: 验证所有必需命令存在
```python
# tests/cli/test_entry_point_migration.py::TestCommandCoverage::test_all_required_commands_exist
def test_all_required_commands_exist(self):
    """验证新入口包含所有必需的命令."""
    from autoBMAD.docuswarm.cli.main import cli
    
    required_commands = [
        "start",
        "status", 
        "resume",
        "cancel",
        "cancel-all",
        "clean",
        "list",
        "list-pipelines",  # 向后兼容
        "export",
        "questions",
        "answer",
    ]
    
    for cmd in required_commands:
        assert cmd in cli.commands, f"Command '{cmd}' not found in CLI"
```

#### Test 2.2: 验证 cancel-all 命令
```python
# tests/cli/test_entry_point_migration.py::TestCommandCoverage::test_cancel_all_command_works
def test_cancel_all_command_works(self):
    """验证 cancel-all 命令功能正常."""
    from click.testing import CliRunner
    from autoBMAD.docuswarm.cli.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ["cancel-all", "--help"])
    
    assert result.exit_code == 0
    assert "cancel" in result.output.lower()
```

#### Test 2.3: 验证 list-pipelines 向后兼容
```python
# tests/cli/test_entry_point_migration.py::TestCommandCoverage::test_list_pipelines_backward_compatible
def test_list_pipelines_backward_compatible(self):
    """验证 list-pipelines 命令作为 list 的别名存在."""
    from autoBMAD.docuswarm.cli.main import cli
    
    assert "list-pipelines" in cli.commands
    
    # 验证两个命令指向同一实现
    list_cmd = cli.commands.get("list")
    list_pipelines_cmd = cli.commands.get("list-pipelines")
    
    if list_pipelines_cmd:
        assert list_cmd.callback == list_pipelines_cmd.callback
```

### 2.3 Phase 3: 服务层测试

#### Test 3.1: 验证 PipelineService.start 存在
```python
# tests/cli/test_entry_point_migration.py::TestServiceLayer::test_pipeline_service_has_start_method
def test_pipeline_service_has_start_method(self):
    """验证 PipelineService 有 start 方法."""
    from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
    
    assert hasattr(PipelineService, 'start')
    assert callable(getattr(PipelineService, 'start'))
```

#### Test 3.2: 验证 PipelineService.resume 存在
```python
# tests/cli/test_entry_point_migration.py::TestServiceLayer::test_pipeline_service_has_resume_method
def test_pipeline_service_has_resume_method(self):
    """验证 PipelineService 有 resume 方法."""
    from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
    
    assert hasattr(PipelineService, 'resume')
    assert callable(getattr(PipelineService, 'resume'))
```

#### Test 3.3: 验证命令不直接调用 asyncio.run
```python
# tests/cli/test_entry_point_migration.py::TestServiceLayer::test_commands_use_service_not_asyncio_run
def test_commands_use_service_not_asyncio_run(self):
    """验证命令通过 Service 调用而非直接 asyncio.run."""
    from autoBMAD.docuswarm.cli.commands import start, resume, answer
    import inspect
    
    for cmd_module in [start, resume, answer]:
        source = inspect.getsource(cmd_module)
        # 允许在命令文件中使用 asyncio.run，但应该调用 service 方法
        assert "PipelineService" in source or "service" in source
```

---

## 3. 实施计划

### Phase 1: 编写入口切换测试 (RED)

**目标**: 创建测试文件，验证当前状态为失败

```bash
# 创建测试文件
touch tests/cli/test_entry_point_migration.py

# 运行测试 - 期望失败
pytest tests/cli/test_entry_point_migration.py -v
```

**预期结果**: 所有测试失败，因为入口配置尚未切换

### Phase 2: 执行入口切换 (GREEN)

**目标**: 修改配置使 Phase 1 的测试通过

```bash
# 1. 修改 pyproject.toml
sed -i 's/autoBMAD.docuswarm.main:cli/autoBMAD.docuswarm.cli.main:cli/g' pyproject.toml

# 2. 修改 __main__.py  
sed -i 's/from autoBMAD.docuswarm.main import cli/from autoBMAD.docuswarm.cli.main import cli/g' autoBMAD/docuswarm/__main__.py

# 3. 运行测试验证
pytest tests/cli/test_entry_point_migration.py::TestEntryPointConfiguration -v
```

### Phase 3: 编写命令覆盖测试 (RED)

**目标**: 创建测试验证命令覆盖

```bash
# 运行命令覆盖测试 - 期望失败
pytest tests/cli/test_entry_point_migration.py::TestCommandCoverage -v
```

**预期结果**: `cancel-all` 和 `list-pipelines` 测试失败

### Phase 4: 实现缺失命令 (GREEN)

**目标**: 实现缺失的命令使测试通过

```bash
# 1. 创建 cancel-all 命令
# 2. 添加 list-pipelines 作为 list 的别名
# 3. 运行测试验证
pytest tests/cli/test_entry_point_migration.py::TestCommandCoverage -v
```

### Phase 5: 编写服务层测试 (RED)

**目标**: 创建测试验证服务层完整

```bash
# 运行服务层测试 - 期望失败
pytest tests/cli/test_entry_point_migration.py::TestServiceLayer -v
```

**预期结果**: PipelineService 方法缺失测试失败

### Phase 6: 完善服务层 (GREEN)

**目标**: 在 PipelineService 中添加缺失的方法

```bash
# 1. 在 PipelineService 中添加 start 和 resume 方法
# 2. 运行测试验证
pytest tests/cli/test_entry_point_migration.py::TestServiceLayer -v
```

### Phase 7: 清理旧入口 (REFACTOR)

**目标**: 删除旧入口并验证整体功能

```bash
# 1. 备份旧入口
cp autoBMAD/docuswarm/main.py autoBMAD/docuswarm/main.py.bak

# 2. 删除旧入口
rm autoBMAD/docuswarm/main.py

# 3. 运行完整测试
pytest tests/cli/ -v
pytest tests/ -v --tb=short
```

---

## 4. 测试文件模板

### 4.1 完整测试文件

```python
"""CLI 入口迁移测试 - TDD 方案验证

本测试文件依据 F3 CLI 分层入口迁移方案编写，
用于验证 CLI 从旧入口向新分层架构的迁移。
"""

from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


class TestEntryPointConfiguration:
    """Phase 1: 验证入口配置指向新架构."""
    
    def test_pyproject_toml_points_to_new_entry(self):
        """RED: pyproject.toml 应该指向新的 CLI 入口."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        assert 'docuswarm = "autoBMAD.docuswarm.cli.main:cli"' in content, \
            "pyproject.toml 应该指向新入口 autoBMAD.docuswarm.cli.main:cli"
    
    def test_main_py_imports_new_entry(self):
        """RED: __main__.py 应该导入新的 CLI 入口."""
        main_py_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "__main__.py"
        content = main_py_path.read_text()
        
        assert "from autoBMAD.docuswarm.cli.main import cli" in content, \
            "__main__.py 应该导入 autoBMAD.docuswarm.cli.main"
    
    def test_cli_is_executable(self):
        """GREEN: CLI 应该可以被导入和执行."""
        from autoBMAD.docuswarm.cli.main import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0, f"CLI 应该正常执行，但返回 {result.exit_code}"
        assert "DocuSwarm" in result.output, "CLI help 应该包含 DocuSwarm"


class TestCommandCoverage:
    """Phase 2: 验证命令覆盖完整."""
    
    def test_all_required_commands_exist(self):
        """RED: 新入口应该包含所有必需的命令."""
        from autoBMAD.docuswarm.cli.main import cli
        
        required_commands = [
            "start", "status", "resume", "cancel",
            "cancel-all", "clean", "list", "list-pipelines",
            "export", "questions", "answer",
        ]
        
        for cmd in required_commands:
            assert cmd in cli.commands, f"命令 '{cmd}' 应该存在于 CLI 中"
    
    def test_cancel_all_command_works(self):
        """RED: cancel-all 命令应该正常工作."""
        from autoBMAD.docuswarm.cli.main import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ["cancel-all", "--help"])
        
        assert result.exit_code == 0, "cancel-all --help 应该正常执行"
    
    def test_list_pipelines_backward_compatible(self):
        """RED: list-pipelines 应该作为 list 的别名存在."""
        from autoBMAD.docuswarm.cli.main import cli
        
        assert "list-pipelines" in cli.commands, \
            "list-pipelines 应该存在以支持向后兼容"


class TestServiceLayer:
    """Phase 3: 验证服务层完整."""
    
    def test_pipeline_service_has_start_method(self):
        """RED: PipelineService 应该有 start 方法."""
        from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
        
        assert hasattr(PipelineService, 'start'), \
            "PipelineService 应该有 start 方法"
        assert callable(getattr(PipelineService, 'start', None)), \
            "PipelineService.start 应该是可调用的"
    
    def test_pipeline_service_has_resume_method(self):
        """RED: PipelineService 应该有 resume 方法."""
        from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
        
        assert hasattr(PipelineService, 'resume'), \
            "PipelineService 应该有 resume 方法"
        assert callable(getattr(PipelineService, 'resume', None)), \
            "PipelineService.resume 应该是可调用的"
    
    def test_pipeline_service_has_restart_from_node_method(self):
        """RED: PipelineService 应该有 restart_from_node 方法."""
        from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
        
        assert hasattr(PipelineService, 'restart_from_node'), \
            "PipelineService 应该有 restart_from_node 方法"


class TestBackwardCompatibility:
    """Phase 4: 验证向后兼容性."""
    
    def test_old_imports_still_work(self):
        """GREEN: 旧的导入路径应该仍然有效."""
        # 验证可以通过旧路径导入（如果旧文件存在）
        try:
            from autoBMAD.docuswarm.main import cli as old_cli
            # 如果旧文件存在，CLI 应该可调用
            runner = CliRunner()
            result = runner.invoke(old_cli, ["--help"])
            assert result.exit_code == 0
        except ImportError:
            # 旧文件已删除，这是预期的
            pytest.skip("旧入口已删除，这是预期的")
    
    def test_command_line_interface_unchanged(self):
        """GREEN: 命令行接口应该保持不变."""
        from autoBMAD.docuswarm.cli.main import cli
        
        runner = CliRunner()
        
        # 测试主要命令的 help 输出
        for cmd in ["start", "status", "resume", "cancel", "list"]:
            result = runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0, f"命令 {cmd} --help 应该正常工作"
```

---

## 5. 执行检查清单

### Phase 1: 入口切换检查清单
- [ ] 创建 `tests/cli/test_entry_point_migration.py`
- [ ] 运行测试，确认全部失败 (RED)
- [ ] 修改 `pyproject.toml` 指向新入口
- [ ] 修改 `__main__.py` 导入新入口
- [ ] 运行测试，确认全部通过 (GREEN)

### Phase 2: 命令覆盖检查清单
- [ ] 运行命令覆盖测试，确认失败 (RED)
- [ ] 实现 `cancel-all` 命令
- [ ] 添加 `list-pipelines` 别名
- [ ] 运行测试，确认通过 (GREEN)

### Phase 3: 服务层检查清单
- [ ] 运行服务层测试，确认失败 (RED)
- [ ] 在 `PipelineService` 中添加 `start` 方法
- [ ] 在 `PipelineService` 中添加 `resume` 方法
- [ ] 在 `PipelineService` 中添加 `restart_from_node` 方法
- [ ] 运行测试，确认通过 (GREEN)

### Phase 4: 清理检查清单
- [ ] 备份 `main.py`
- [ ] 删除旧 `main.py`
- [ ] 运行完整回归测试
- [ ] 验证 `docuswarm --help` 正常工作
- [ ] 验证 `python -m autoBMAD.docuswarm --help` 正常工作

---

## 6. 风险缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 入口切换后 CLI 不可用 | 低 | 高 | 1. 保留旧入口备份<br>2. 小步修改<br>3. 每次修改后测试 |
| 命令行为不一致 | 中 | 中 | 1. 详细对比新旧命令<br>2. 编写行为一致性测试<br>3. 逐步迁移验证 |
| 服务层方法缺失功能 | 低 | 中 | 1. 对照旧实现编写测试<br>2. 逐步迁移业务逻辑 |
| 其他模块依赖旧 main.py | 中 | 高 | 1. 全局搜索导入语句<br>2. 更新所有依赖<br>3. 保留兼容层 |

---

## 7. 成功标准

所有以下测试必须通过：

1. ✅ `TestEntryPointConfiguration` - 入口配置正确
2. ✅ `TestCommandCoverage` - 命令覆盖完整
3. ✅ `TestServiceLayer` - 服务层完整
4. ✅ `TestBackwardCompatibility` - 向后兼容
5. ✅ 完整回归测试套件

---

## 8. 附录

### 8.1 命令对比参考

| 旧命令 | 新命令 | 状态 |
|--------|--------|------|
| start | start | 已迁移 ✅ |
| status | status | 已迁移 ✅ |
| resume | resume | 已迁移 ✅ |
| cancel | cancel | 已迁移 ✅ |
| cancel-all | ~~缺失~~ | 待实现 📝 |
| clean | clean | 已迁移 ✅ |
| list-pipelines | list | 需别名 📝 |
| export | export | 已迁移 ✅ |
| questions | questions | 已迁移 ✅ |
| answer | answer | 已迁移 ✅ |

### 8.2 PipelineService 方法清单

| 方法 | 状态 | 用途 |
|------|------|------|
| `__init__` | ✅ | 初始化服务 |
| `start` | 📝 | 启动 pipeline |
| `status` | ✅ | 获取 pipeline 状态 |
| `resume` | 📝 | 恢复 pipeline |
| `restart_from_node` | 📝 | 从指定节点重启 |
| `cancel` | ✅ | 取消 pipeline |
| `list_pipelines` | ✅ | 列出所有 pipelines |
