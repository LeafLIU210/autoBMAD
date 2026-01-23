# 质量门禁独立执行 - 测试驱动开发方案

## 1. 需求概述

### 1.1 目标
在 `epic_driver.py` 中添加CLI子命令支持，允许独立执行质量门禁阶段，无需依赖完整的Epic流程。

### 1.2 核心架构依赖

| 组件 | 路径 | 职责 |
|------|------|------|
| `QualityGateOrchestrator` | `epic_driver.py:93-855` | 质量门禁编排器 |
| `QualityCheckController` | `controllers/quality_check_controller.py` | Ruff/BasedPyright检查控制 |
| `PytestController` | `controllers/pytest_controller.py` | Pytest测试控制 |
| `RuffAgent` | `agents/quality_agents.py` | Ruff代码检查 |
| `BasedPyrightAgent` | `agents/quality_agents.py` | 类型检查 |
| `PytestAgent` | `agents/quality_agents.py` | 测试执行 |

---

## 2. CLI子命令设计

### 2.1 命令结构

```bash
# 原有命令（保持兼容）
python -m autoBMAD.epic_automation.epic_driver <epic_path> [options]

# 新增子命令
python -m autoBMAD.epic_automation.epic_driver run-quality [options]
```

### 2.2 参数定义

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--source-dir` | str | `src` | 源代码目录 |
| `--test-dir` | str | `tests` | 测试代码目录 |
| `--epic-id` | str | `standalone-quality` | 标识符（用于错误汇总JSON） |
| `--skip-quality` | flag | False | 跳过ruff+basedpyright |
| `--skip-tests` | flag | False | 跳过pytest |
| `--max-cycles` | int | 3 | 最大修复循环次数 |
| `--verbose` | flag | False | 详细日志输出 |
| `--log-file` | flag | False | 创建日志文件 |

### 2.3 调用示例

```bash
# 完整质量门禁（ruff + basedpyright + pytest）
python -m autoBMAD.epic_automation.epic_driver run-quality

# 仅代码质量检查（跳过测试）
python -m autoBMAD.epic_automation.epic_driver run-quality --skip-tests

# 仅测试执行（跳过静态检查）
python -m autoBMAD.epic_automation.epic_driver run-quality --skip-quality

# 自定义目录
python -m autoBMAD.epic_automation.epic_driver run-quality \
  --source-dir autoBMAD/epic_automation \
  --test-dir tests/epic_automation

# 详细日志模式
python -m autoBMAD.epic_automation.epic_driver run-quality --verbose --log-file
```

---

## 3. 测试用例设计

### 3.1 测试文件结构

```
tests/
├── epic_automation/
│   ├── __init__.py
│   ├── test_cli_run_quality.py       # CLI子命令测试
│   ├── test_quality_gate_standalone.py  # 独立执行测试
│   └── fixtures/
│       ├── __init__.py
│       ├── mock_source/              # 模拟源代码
│       │   ├── clean_module.py       # 无错误文件
│       │   └── error_module.py       # 有错误文件
│       └── mock_tests/               # 模拟测试文件
│           ├── test_pass.py          # 通过测试
│           └── test_fail.py          # 失败测试
```

### 3.2 测试用例清单

#### 3.2.1 CLI参数解析测试 (`test_cli_run_quality.py`)

```python
"""CLI子命令参数解析测试"""

import pytest
from unittest.mock import patch, AsyncMock

class TestRunQualityCommand:
    """run-quality 子命令测试"""

    def test_parse_run_quality_default_args(self):
        """测试默认参数解析"""
        # Given: run-quality 子命令无额外参数
        # When: 解析参数
        # Then: source_dir='src', test_dir='tests', skip_quality=False, skip_tests=False

    def test_parse_run_quality_custom_dirs(self):
        """测试自定义目录参数"""
        # Given: --source-dir custom_src --test-dir custom_tests
        # When: 解析参数
        # Then: source_dir='custom_src', test_dir='custom_tests'

    def test_parse_run_quality_skip_quality(self):
        """测试跳过质量检查参数"""
        # Given: --skip-quality
        # When: 解析参数
        # Then: skip_quality=True

    def test_parse_run_quality_skip_tests(self):
        """测试跳过测试参数"""
        # Given: --skip-tests
        # When: 解析参数
        # Then: skip_tests=True

    def test_parse_run_quality_max_cycles(self):
        """测试最大循环次数参数"""
        # Given: --max-cycles 5
        # When: 解析参数
        # Then: max_cycles=5

    def test_parse_run_quality_invalid_max_cycles(self):
        """测试无效循环次数参数"""
        # Given: --max-cycles 0
        # When: 解析参数
        # Then: 抛出参数错误

    def test_parse_run_quality_epic_id(self):
        """测试Epic ID参数"""
        # Given: --epic-id my-custom-id
        # When: 解析参数
        # Then: epic_id='my-custom-id'

    def test_backward_compatibility_positional_epic(self):
        """测试向后兼容：位置参数epic_path"""
        # Given: docs/epics/my-epic.md (无子命令)
        # When: 解析参数
        # Then: 保持原有行为，epic_path='docs/epics/my-epic.md'
```

#### 3.2.2 独立执行测试 (`test_quality_gate_standalone.py`)

```python
"""质量门禁独立执行测试"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path

class TestQualityGateStandalone:
    """独立质量门禁执行测试"""

    @pytest.fixture
    def mock_source_dir(self, tmp_path):
        """创建模拟源代码目录"""
        src = tmp_path / "src"
        src.mkdir()
        (src / "module.py").write_text("x = 1\n")
        return str(src)

    @pytest.fixture
    def mock_test_dir(self, tmp_path):
        """创建模拟测试目录"""
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_module.py").write_text(
            "def test_pass():\n    assert True\n"
        )
        return str(tests)

    @pytest.mark.asyncio
    async def test_standalone_execution_success(self, mock_source_dir, mock_test_dir):
        """测试独立执行成功场景"""
        # Given: 干净的源代码和通过的测试
        # When: 执行 run_quality_gates_standalone()
        # Then: 返回 success=True

    @pytest.mark.asyncio
    async def test_standalone_skip_quality(self, mock_source_dir, mock_test_dir):
        """测试跳过质量检查"""
        # Given: skip_quality=True
        # When: 执行
        # Then: ruff_result.skipped=True, basedpyright_result.skipped=True

    @pytest.mark.asyncio
    async def test_standalone_skip_tests(self, mock_source_dir, mock_test_dir):
        """测试跳过测试执行"""
        # Given: skip_tests=True
        # When: 执行
        # Then: pytest_result.skipped=True

    @pytest.mark.asyncio
    async def test_standalone_ruff_errors_with_fix(self, tmp_path):
        """测试Ruff错误检测与SDK修复"""
        # Given: 有ruff错误的代码
        # When: 执行
        # Then: 触发SDK修复流程

    @pytest.mark.asyncio
    async def test_standalone_basedpyright_errors_with_fix(self, tmp_path):
        """测试BasedPyright错误检测与SDK修复"""
        # Given: 有类型错误的代码
        # When: 执行
        # Then: 触发SDK修复流程

    @pytest.mark.asyncio
    async def test_standalone_pytest_failures_with_fix(self, tmp_path):
        """测试Pytest失败检测与SDK修复"""
        # Given: 失败的测试
        # When: 执行
        # Then: 触发SDK修复流程

    @pytest.mark.asyncio
    async def test_standalone_max_cycles_exceeded(self, tmp_path):
        """测试超过最大循环次数"""
        # Given: 无法修复的错误，max_cycles=1
        # When: 执行
        # Then: 返回 success=True, warning='max_cycles_exceeded'

    @pytest.mark.asyncio
    async def test_standalone_error_summary_json_generated(self, tmp_path):
        """测试错误汇总JSON生成"""
        # Given: 存在残留错误
        # When: 执行完成
        # Then: 生成 errors/quality_errors_*.json

    @pytest.mark.asyncio
    async def test_standalone_no_test_files(self, mock_source_dir, tmp_path):
        """测试无测试文件场景"""
        # Given: 空测试目录
        # When: 执行
        # Then: pytest_result.skipped=True, message='No test files'

    @pytest.mark.asyncio
    async def test_standalone_nonexistent_source_dir(self, tmp_path):
        """测试不存在的源目录"""
        # Given: 不存在的source_dir
        # When: 执行
        # Then: 返回错误信息
```

#### 3.2.3 集成测试 (`test_quality_gate_integration.py`)

```python
"""质量门禁集成测试"""

import pytest
import subprocess
import sys

class TestQualityGateIntegration:
    """端到端集成测试"""

    def test_cli_run_quality_help(self):
        """测试帮助信息输出"""
        result = subprocess.run(
            [sys.executable, "-m", "autoBMAD.epic_automation.epic_driver", 
             "run-quality", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "--source-dir" in result.stdout
        assert "--skip-quality" in result.stdout

    def test_cli_run_quality_nonexistent_dir(self):
        """测试不存在的目录"""
        result = subprocess.run(
            [sys.executable, "-m", "autoBMAD.epic_automation.epic_driver",
             "run-quality", "--source-dir", "/nonexistent/path"],
            capture_output=True,
            text=True
        )
        # 应该返回错误或警告
        assert result.returncode != 0 or "not found" in result.stderr.lower()

    @pytest.mark.slow
    def test_cli_run_quality_real_execution(self, tmp_path):
        """真实执行测试（慢速）"""
        # 创建测试文件
        src = tmp_path / "src"
        src.mkdir()
        (src / "app.py").write_text("def hello(): return 'world'\n")
        
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_app.py").write_text(
            "from src.app import hello\n"
            "def test_hello():\n"
            "    assert hello() == 'world'\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "autoBMAD.epic_automation.epic_driver",
             "run-quality",
             "--source-dir", str(src),
             "--test-dir", str(tests),
             "--skip-quality"],  # 跳过静态检查加速
            capture_output=True,
            text=True,
            cwd=str(tmp_path)
        )
        
        # 验证执行完成
        assert "Quality gates" in result.stdout or result.returncode == 0
```

---

## 4. 实现步骤

### 4.1 Phase 1: CLI参数扩展

**文件**: `epic_driver.py`

**修改点**:

```python
# 1. 修改 parse_arguments() 函数，添加子命令支持

def parse_arguments():
    """Parse command line arguments with subcommand support."""
    parser = argparse.ArgumentParser(
        description="BMAD Epic Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # --- 子命令 1: run-epic (原有功能，默认行为) ---
    epic_parser = subparsers.add_parser(
        'run-epic',
        help='Run full epic workflow (SM-Dev-QA + Quality Gates)'
    )
    epic_parser.add_argument('epic_path', type=str, help='Path to epic markdown file')
    # ... 其他原有参数 ...
    
    # --- 子命令 2: run-quality (新增) ---
    quality_parser = subparsers.add_parser(
        'run-quality',
        help='Run quality gates only (Ruff, BasedPyright, Pytest)'
    )
    quality_parser.add_argument(
        '--source-dir', type=str, default='src',
        help='Source code directory (default: src)'
    )
    quality_parser.add_argument(
        '--test-dir', type=str, default='tests',
        help='Test directory (default: tests)'
    )
    quality_parser.add_argument(
        '--epic-id', type=str, default='standalone-quality',
        help='Identifier for error summary JSON'
    )
    quality_parser.add_argument(
        '--skip-quality', action='store_true',
        help='Skip ruff and basedpyright checks'
    )
    quality_parser.add_argument(
        '--skip-tests', action='store_true',
        help='Skip pytest execution'
    )
    quality_parser.add_argument(
        '--max-cycles', type=int, default=3,
        help='Maximum fix cycles (default: 3)'
    )
    quality_parser.add_argument(
        '--verbose', action='store_true',
        help='Enable verbose logging'
    )
    quality_parser.add_argument(
        '--log-file', action='store_true',
        help='Create timestamped log file'
    )
    
    # --- 向后兼容：无子命令时的位置参数 ---
    # 处理 python epic_driver.py epic.md 的旧调用方式
    
    return parser.parse_args()
```

### 4.2 Phase 2: 独立执行入口

**文件**: `epic_driver.py`

**新增函数**:

```python
async def run_quality_gates_standalone(
    source_dir: str = "src",
    test_dir: str = "tests",
    epic_id: str = "standalone-quality",
    skip_quality: bool = False,
    skip_tests: bool = False,
    max_cycles: int = 3,
    verbose: bool = False,
    create_log_file: bool = False,
) -> dict[str, Any]:
    """
    独立执行质量门禁流水线
    
    Args:
        source_dir: 源代码目录
        test_dir: 测试目录
        epic_id: 标识符
        skip_quality: 跳过静态检查
        skip_tests: 跳过测试
        max_cycles: 最大修复循环
        verbose: 详细日志
        create_log_file: 创建日志文件
    
    Returns:
        质量门禁执行结果字典
    """
    # 1. 初始化日志
    log_manager = LogManager(create_log_file=create_log_file)
    init_logging(log_manager)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 2. 验证目录
        source_path = Path(source_dir).resolve()
        test_path = Path(test_dir).resolve()
        
        if not source_path.exists():
            return {
                "success": False,
                "error": f"Source directory not found: {source_dir}"
            }
        
        # 3. 创建编排器
        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_path),
            test_dir=str(test_path),
            skip_quality=skip_quality,
            skip_tests=skip_tests,
        )
        
        # 4. 执行质量门禁
        results = await orchestrator.execute_quality_gates(epic_id)
        
        return results
        
    finally:
        cleanup_logging()
```

### 4.3 Phase 3: main() 函数路由

**文件**: `epic_driver.py`

**修改 main()**:

```python
async def main():
    """Main entry point with subcommand routing."""
    args = parse_arguments()
    
    # 路由到对应处理器
    if args.command == 'run-quality':
        # 独立质量门禁
        results = await run_quality_gates_standalone(
            source_dir=args.source_dir,
            test_dir=args.test_dir,
            epic_id=args.epic_id,
            skip_quality=args.skip_quality,
            skip_tests=args.skip_tests,
            max_cycles=args.max_cycles,
            verbose=args.verbose,
            create_log_file=args.log_file,
        )
        
        # 输出结果摘要
        if results.get("success"):
            logger.info("✓ Quality gates completed successfully")
            sys.exit(0)
        else:
            logger.error(f"✗ Quality gates failed: {results.get('errors', [])}")
            sys.exit(1)
    
    elif args.command == 'run-epic' or hasattr(args, 'epic_path'):
        # 原有完整流程
        # ... 保持原有逻辑 ...
        pass
    
    else:
        # 无子命令，显示帮助
        parse_arguments(['--help'])
```

---

## 5. 验收标准

### 5.1 功能验收

| 编号 | 验收项 | 预期结果 |
|------|--------|----------|
| AC-01 | `run-quality --help` | 显示所有参数说明 |
| AC-02 | `run-quality` 默认执行 | 完整质量门禁流程 |
| AC-03 | `run-quality --skip-quality` | 仅执行pytest |
| AC-04 | `run-quality --skip-tests` | 仅执行ruff+basedpyright |
| AC-05 | `run-quality --skip-quality --skip-tests` | 跳过所有检查，直接成功 |
| AC-06 | 原有命令 `epic_driver.py epic.md` | 保持向后兼容 |
| AC-07 | 错误汇总JSON生成 | 存在错误时生成文件 |
| AC-08 | 退出码 | 成功=0，失败=1 |

### 5.2 测试覆盖率

| 测试类型 | 覆盖目标 |
|----------|----------|
| 单元测试 | ≥80% |
| 集成测试 | CLI所有子命令 |
| 端到端测试 | 真实执行场景 |

### 5.3 性能指标

| 指标 | 基准 |
|------|------|
| CLI启动时间 | <2s |
| 参数解析 | <100ms |
| 空目录执行 | <5s |

---

## 6. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 向后兼容破坏 | 高 | 保留位置参数epic_path的支持 |
| SDK调用失败 | 中 | 错误汇总JSON记录详细信息 |
| 目录不存在 | 低 | 启动时验证并提前报错 |

---

## 7. 时间估算

| 阶段 | 工作项 | 估时 |
|------|--------|------|
| Phase 1 | CLI参数扩展 | 2h |
| Phase 2 | 独立执行入口 | 1h |
| Phase 3 | main()路由 | 1h |
| Phase 4 | 单元测试编写 | 3h |
| Phase 5 | 集成测试编写 | 2h |
| Phase 6 | 文档更新 | 1h |
| **总计** | | **10h** |

---

## 8. 参考文档

- [epic_driver.py](../epic_driver.py) - 主驱动模块
- [quality_check_controller.py](../controllers/quality_check_controller.py) - 质量检查控制器
- [pytest_controller.py](../controllers/pytest_controller.py) - Pytest控制器
- [quality_agents.py](../agents/quality_agents.py) - 质量检查Agents
