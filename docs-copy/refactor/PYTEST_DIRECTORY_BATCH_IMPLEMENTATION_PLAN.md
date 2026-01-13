# Pytest目录遍历分批执行实施方案

## 1. 方案概述

### 1.1 核心原则
- **奥卡姆剃刀原则**：利用现有目录结构，不引入额外标记机制，不假设目录命名规范
- **简单性优先**：零配置开箱即用，动态扫描任意测试目录结构
- **超时控制**：每个批次最大超时10分钟（600秒）
- **动态映射**：自动扫描`tests/`下所有子目录，为每个目录创建独立测试任务

### 1.2 策略
```
动态扫描tests/目录：
  ↓
发现所有子目录 + 散装文件
  ↓
为每个目录创建任务映射
  ↓
应用启发式规则配置（超时、并行等）
  ↓
按优先级执行

示例：
tests/
├── unit/          → 任务: unit (60s, 并行) ← 匹配"unit"规则
├── integration/   → 任务: integration (120s, 并行) ← 匹配"integration"规则
├── e2e/           → 任务: e2e (600s, 串行, 非阻断) ← 匹配"e2e"规则
├── custom_tests/  → 任务: custom_tests (120s, 并行) ← 默认配置
└── test_*.py      → 任务: loose_tests (90s, 并行)
```

---

## 2. 技术实现

### 2.1 新增模块

**文件路径**: `autoBMAD/epic_automation/agents/pytest_batch_executor.py`

**核心功能**:
- 自动扫描测试目录结构
- 生成批次执行配置
- 按批次顺序执行pytest
- 超时控制与错误处理

### 2.2 启发式配置规则

**核心机制**: 使用正则表达式模式匹配目录名，自动应用配置（非硬编码目录名）

| 目录名模式 | 超时（秒） | 并行执行 | 阻断失败 | 优先级 | 匹配示例 |
|-----------|-----------|---------|---------|--------|----------|
| `.*smoke.*` | 30 | ❌ | ✅ | 1 | smoke, smoke_tests |
| `.*unit.*` | 60 | ✅ | ✅ | 2 | unit, unit_tests, unittest |
| `.*(integration\|api).*` | 120 | ✅ (限2进程) | ✅ | 3 | integration, api, api_tests |
| `.*(e2e\|end.*end).*` | 600 | ❌ | ❌ | 4 | e2e, end_to_end, e2e_tests |
| `.*(gui\|ui).*` | 300 | ❌ | ❌ | 4 | gui, ui, gui_tests |
| `.*(perf\|performance).*` | 600 | ❌ | ❌ | 5 | perf, performance |
| `散装文件` | 90 | ✅ | ✅ | 2 | test_*.py in tests/ |
| **无匹配（默认）** | 120 | ✅ | ✅ | 3 | 任何未匹配的目录 |

**说明**:
- **模式匹配**: 使用正则表达式，支持灵活命名（如"unit_tests", "unittests"都能匹配）
- **优雅降级**: 未匹配到任何规则的目录使用默认配置
- **并行执行**: 使用pytest-xdist (`-n auto`或`-n 2`)
- **阻断失败**: 失败时是否阻断后续批次执行
- **优先级**: 数字越小优先级越高，按优先级排序执行

---

## 3. 代码实现

### 3.1 批次执行器类

```python
# autoBMAD/epic_automation/agents/pytest_batch_executor.py

from __future__ import annotations
import logging
import subprocess
from pathlib import Path
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """批次配置"""
    name: str
    path: str
    timeout: int
    parallel: bool
    workers: int | str
    blocking: bool
    priority: int


class PytestBatchExecutor:
    """Pytest目录遍历批次执行器 - 动态扫描版本"""
    
    # 启发式规则（模式匹配，非硬编码目录名）
    HEURISTIC_RULES = [
        # (目录名正则模式, 配置字典)
        (r".*smoke.*", {"timeout": 30, "parallel": False, "blocking": True, "priority": 1}),
        (r".*unit.*", {"timeout": 60, "parallel": True, "workers": "auto", "blocking": True, "priority": 2}),
        (r".*(integration|api).*", {"timeout": 120, "parallel": True, "workers": 2, "blocking": True, "priority": 3}),
        (r".*(e2e|end.*end).*", {"timeout": 600, "parallel": False, "blocking": False, "priority": 4}),
        (r".*(gui|ui).*", {"timeout": 300, "parallel": False, "blocking": False, "priority": 4}),
        (r".*(perf|performance).*", {"timeout": 600, "parallel": False, "blocking": False, "priority": 5}),
    ]
    
    # 默认配置（未匹配到任何规则的目录）
    DEFAULT_CONFIG = {"timeout": 120, "parallel": True, "workers": "auto", "blocking": True, "priority": 3}
    
    # 散装文件配置
    LOOSE_FILES_CONFIG = {"timeout": 90, "parallel": True, "workers": "auto", "blocking": True, "priority": 2}
    
    def __init__(self, test_dir: Path, source_dir: Path):
        """
        初始化批次执行器
        
        Args:
            test_dir: 测试目录路径
            source_dir: 源代码目录路径
        """
        self.test_dir = test_dir
        self.source_dir = source_dir
        self.logger = logger
    
    def discover_batches(self) -> list[BatchConfig]:
        """
        动态发现并映射测试批次（无预设目录名假设）
        
        Returns:
            List[BatchConfig]: 批次配置列表（已按优先级排序）
        """
        batches = []
        
        if not self.test_dir.exists():
            self.logger.warning(f"Test directory not found: {self.test_dir}")
            return batches
        
        # 1. 动态扫描所有子目录（不预设目录名）
        subdirs = [d for d in self.test_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        self.logger.info(f"Scanning tests directory: found {len(subdirs)} subdirectories")
        
        for subdir in subdirs:
            # 使用启发式规则匹配配置
            config = self._match_config_by_heuristic(subdir.name)
            batches.append(BatchConfig(
                name=subdir.name,
                path=str(subdir),
                timeout=config["timeout"],
                parallel=config["parallel"],
                workers=config.get("workers", "auto"),
                blocking=config["blocking"],
                priority=config["priority"]
            ))
            self.logger.info(
                f"Mapped directory '{subdir.name}' → "
                f"timeout={config['timeout']}s, parallel={config['parallel']}, priority={config['priority']}"
            )
        
        # 2. 检查散装测试文件并创建映射
        loose_files = list(self.test_dir.glob("test_*.py"))
        if loose_files:
            config = self.LOOSE_FILES_CONFIG
            batches.append(BatchConfig(
                name="loose_tests",
                path=str(self.test_dir),
                timeout=config["timeout"],
                parallel=config["parallel"],
                workers=config["workers"],
                blocking=config["blocking"],
                priority=config["priority"]
            ))
            self.logger.info(
                f"Mapped {len(loose_files)} loose test files → 'loose_tests' task "
                f"(timeout={config['timeout']}s)"
            )
        
        # 3. 按优先级排序
        batches.sort(key=lambda b: b.priority)
        
        self.logger.info(f"Total test batches created: {len(batches)}")
        
        return batches
    
    def _match_config_by_heuristic(self, dir_name: str) -> dict[str, Any]:
        """
        使用启发式规则匹配目录配置（而非硬编码目录名）
        
        Args:
            dir_name: 目录名
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        import re
        
        dir_lower = dir_name.lower()
        
        # 遍历启发式规则，按顺序匹配
        for pattern, config in self.HEURISTIC_RULES:
            if re.match(pattern, dir_lower):
                self.logger.debug(f"Directory '{dir_name}' matched pattern '{pattern}'")
                # 合并默认配置与规则配置
                return {**self.DEFAULT_CONFIG, **config}
        
        # 无匹配则使用默认配置（优雅降级）
        self.logger.debug(f"Directory '{dir_name}' using default config (no pattern match)")
        return self.DEFAULT_CONFIG
    
    async def execute_batches(self) -> dict[str, Any]:
        """
        执行所有批次
        
        Returns:
            Dict[str, Any]: 执行结果汇总
        """
        batches = self.discover_batches()
        
        if not batches:
            self.logger.warning("No test batches found")
            return {
                "status": "skipped",
                "message": "No test batches to execute"
            }
        
        self.logger.info(f"Executing {len(batches)} test batches...")
        
        results = []
        failed_batches = []
        
        for batch in batches:
            self.logger.info(f"=== Batch {batch.priority}: {batch.name} ===")
            
            result = await self._execute_batch(batch)
            results.append(result)
            
            if not result["success"]:
                failed_batches.append(batch.name)
                if batch.blocking:
                    self.logger.error(f"Blocking batch '{batch.name}' failed - stopping execution")
                    break
                else:
                    self.logger.warning(f"Non-blocking batch '{batch.name}' failed - continuing")
        
        # 汇总结果
        total_batches = len(results)
        passed_batches = sum(1 for r in results if r["success"])
        
        return {
            "status": "completed" if not failed_batches else "failed",
            "total_batches": total_batches,
            "passed_batches": passed_batches,
            "failed_batches": failed_batches,
            "results": results,
            "message": f"{passed_batches}/{total_batches} batches passed"
        }
    
    async def _execute_batch(self, batch: BatchConfig) -> dict[str, Any]:
        """
        执行单个批次
        
        Args:
            batch: 批次配置
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 构建命令
        cmd = self._build_command(batch)
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        self.logger.info(f"Timeout: {batch.timeout}s")
        
        try:
            # 执行命令
            import asyncio
            loop = asyncio.get_event_loop()
            
            process = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=batch.timeout
                    )
                ),
                timeout=batch.timeout + 10
            )
            
            success = process.returncode == 0
            
            # 解析输出
            import re
            stdout = process.stdout
            
            tests_passed = 0
            tests_failed = 0
            
            if match := re.search(r'(\d+) passed', stdout):
                tests_passed = int(match.group(1))
            if match := re.search(r'(\d+) failed', stdout):
                tests_failed = int(match.group(1))
            
            result = {
                "batch_name": batch.name,
                "success": success,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": process.stderr
            }
            
            if success:
                self.logger.info(f"✓ Batch '{batch.name}' PASSED ({tests_passed} tests)")
            else:
                self.logger.error(f"✗ Batch '{batch.name}' FAILED ({tests_failed} failures)")
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"✗ Batch '{batch.name}' TIMEOUT after {batch.timeout}s")
            return {
                "batch_name": batch.name,
                "success": False,
                "error": f"Timeout after {batch.timeout}s"
            }
        except Exception as e:
            self.logger.error(f"✗ Batch '{batch.name}' ERROR: {e}")
            return {
                "batch_name": batch.name,
                "success": False,
                "error": str(e)
            }
    
    def _build_command(self, batch: BatchConfig) -> list[str]:
        """
        构建pytest命令
        
        Args:
            batch: 批次配置
            
        Returns:
            List[str]: 命令参数列表
        """
        cmd = ["pytest", batch.path]
        
        # 详细输出
        cmd.extend(["-v", "--tb=short"])
        
        # 并行执行
        if batch.parallel:
            if isinstance(batch.workers, int):
                cmd.extend(["-n", str(batch.workers)])
            else:
                cmd.extend(["-n", batch.workers])  # "auto"
        
        # 覆盖率（仅主批次）
        if batch.name in ["unit", "integration", "loose_tests"]:
            cmd.extend([f"--cov={self.source_dir}", "--cov-report=term-missing"])
        
        # 失败快速停止（阻断批次）
        if batch.blocking:
            cmd.append("--maxfail=5")
        
        return cmd
```

### 3.2 修改PytestAgent

```python
# autoBMAD/epic_automation/agents/quality_agents.py

class PytestAgent(BaseQualityAgent):
    """Pytest 测试执行 Agent - 支持目录遍历批次执行"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("Pytest", task_group)

    async def execute(
        self,
        source_dir: str,
        test_dir: str
    ) -> dict[str, Any]:
        """
        执行 Pytest 测试（目录遍历批次执行）

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            Dict[str, Any]: 测试结果
        """
        self.logger.info("Running Pytest with directory-based batching")

        try:
            from .pytest_batch_executor import PytestBatchExecutor
            from pathlib import Path
            
            # 创建批次执行器
            executor = PytestBatchExecutor(
                test_dir=Path(test_dir),
                source_dir=Path(source_dir)
            )
            
            # 执行所有批次
            result = await executor.execute_batches()
            
            return result

        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
```

---

## 4. 质量门控集成

### 4.1 修改epic_driver.py

**文件路径**: `autoBMAD/epic_automation/epic_driver.py`

**修改点**: Phase 2质量门控调用

```python
async def _run_quality_gates(self):
    """执行质量门控"""
    self.logger.info("=== Phase 2: Quality Gates ===")
    
    try:
        # 1. Ruff检查
        ruff_agent = RuffAgent(task_group=self.task_group)
        ruff_result = await ruff_agent.execute(
            source_dir=str(self.project_root / "src")
        )
        
        if ruff_result["status"] != "completed":
            raise QualityGateError(f"Ruff check failed: {ruff_result.get('error')}")
        
        self.logger.info("✓ Ruff quality gate PASSED")
        
        # 2. BasedPyright检查
        pyright_agent = BasedPyrightAgent(task_group=self.task_group)
        pyright_result = await pyright_agent.execute(
            source_dir=str(self.project_root / "src")
        )
        
        if pyright_result["status"] != "completed":
            raise QualityGateError(f"BasedPyright check failed: {pyright_result.get('error')}")
        
        self.logger.info("✓ BasedPyright quality gate PASSED")
        
        # 3. Pytest批次执行（新实现）
        pytest_agent = PytestAgent(task_group=self.task_group)
        pytest_result = await pytest_agent.execute(
            source_dir=str(self.project_root / "src"),
            test_dir=str(self.project_root / "tests")
        )
        
        if pytest_result["status"] == "failed":
            raise QualityGateError(
                f"Pytest batches failed: {pytest_result.get('message')}"
            )
        
        self.logger.info(
            f"✓ Pytest quality gate PASSED: {pytest_result['message']}"
        )
        
        return True
        
    except QualityGateError as e:
        self.logger.error(f"Quality gate failed: {e}")
        # 非阻断：继续执行
        return False
```

---

## 5. 依赖安装

### 5.1 更新requirements.txt

```txt
# 添加pytest-xdist用于并行执行
pytest-xdist>=3.0.0
```

### 5.2 安装命令

```bash
pip install pytest-xdist
```

---

## 6. 使用说明

### 6.1 目录结构示例

**示例1: 标准命名**
```
tests/
├── unit/                 # 匹配".*unit.*" → 60秒超时，并行
│   ├── test_parser.py
│   └── test_state.py
├── integration/          # 匹配".*integration.*" → 120秒超时，并行限2进程
│   ├── test_workflow.py
│   └── test_agents.py
└── e2e/                  # 匹配".*e2e.*" → 600秒超时，串行，非阻断
    └── test_full_epic.py
```

**示例2: 自定义命名（也能正常工作）**
```
tests/
├── unit_tests/           # 匹配".*unit.*" → 60秒超时，并行
├── api_tests/            # 匹配".*api.*" → 120秒超时，并行限2进程
├── gui_automation/       # 匹配".*gui.*" → 300秒超时，串行
└── custom_module/        # 无匹配 → 默认配置（120秒超时，并行）
```

**示例3: 完全自定义（使用默认配置）**
```
tests/
├── phase1/               # 无匹配 → 默认配置（120秒超时，并行）
├── phase2/               # 无匹配 → 默认配置（120秒超时，并行）
└── acceptance/           # 无匹配 → 默认配置（120秒超时，并行）
```

### 6.2 执行工作流

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 执行epic
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md
```

### 6.3 预期输出

```
2026-01-13 20:00:00 - epic_driver - INFO - === Phase 2: Quality Gates ===
2026-01-13 20:00:00 - quality_agents - INFO - ✓ Ruff quality gate PASSED
2026-01-13 20:00:05 - quality_agents - INFO - ✓ BasedPyright quality gate PASSED

2026-01-13 20:00:05 - pytest_batch_executor - INFO - Scanning tests directory: found 3 subdirectories
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Mapped directory 'unit' → timeout=60s, parallel=True, priority=2
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Mapped directory 'integration' → timeout=120s, parallel=True, priority=3
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Mapped directory 'e2e' → timeout=600s, parallel=False, priority=4
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Total test batches created: 3
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Executing 3 test batches...

2026-01-13 20:00:05 - pytest_batch_executor - INFO - === Batch 1: unit ===
2026-01-13 20:00:05 - pytest_batch_executor - INFO - Running: pytest tests/unit/ -v --tb=short -n auto
2026-01-13 20:00:25 - pytest_batch_executor - INFO - ✓ Batch 'unit' PASSED (45 tests)

2026-01-13 20:00:25 - pytest_batch_executor - INFO - === Batch 2: integration ===
2026-01-13 20:00:25 - pytest_batch_executor - INFO - Running: pytest tests/integration/ -v --tb=short -n 2
2026-01-13 20:01:15 - pytest_batch_executor - INFO - ✓ Batch 'integration' PASSED (20 tests)

2026-01-13 20:01:15 - pytest_batch_executor - INFO - === Batch 3: e2e ===
2026-01-13 20:01:15 - pytest_batch_executor - INFO - Running: pytest tests/e2e/ -v --tb=short
2026-01-13 20:06:00 - pytest_batch_executor - INFO - ✓ Batch 'e2e' PASSED (8 tests)

2026-01-13 20:06:00 - quality_agents - INFO - ✓ Pytest quality gate PASSED: 3/3 batches passed
```

---

## 7. 故障处理

### 7.1 批次超时

**场景**: 某批次超过10分钟超时

**处理**:
1. 检查该批次是否可拆分为更小的子目录
2. 评估是否需要将耗时测试移至独立目录（如`e2e/`或`performance/`）
3. 考虑优化测试代码（减少不必要的等待）

### 7.2 批次失败

**阻断批次失败**（如`unit`）:
- 工作流停止，不执行后续批次
- 修复失败测试后重新运行

**非阻断批次失败**（如`e2e`）:
- 工作流继续执行
- 失败信息记录到日志
- 后续可单独重跑该批次

### 7.3 无目录结构项目

**场景**: `tests/`目录下全是散装文件

**自动处理**:
- 所有文件作为一个批次执行
- 超时：90秒
- 并行执行：是
- 阻断失败：是

---

## 8. 优势总结

### 8.1 简单性
- ✅ 零配置开箱即用
- ✅ 动态扫描任意目录结构，无需预设
- ✅ 无需学习pytest标记语法
- ✅ 无需创建配置文件

### 8.2 灵活性
- ✅ 适配任意目录命名（不限于"unit", "integration"等）
- ✅ 启发式规则自动匹配常见模式
- ✅ 未匹配目录使用默认配置（优雅降级）
- ✅ 自动处理散装测试文件

### 8.3 可控性
- ✅ 每个批次独立超时（最大10分钟）
- ✅ 独立失败隔离
- ✅ 清晰的日志输出（显示目录映射过程）

### 8.4 性能
- ✅ 并行执行（pytest-xdist）
- ✅ 批次间串行避免资源竞争
- ✅ 非阻断批次后台执行

### 8.5 可维护性
- ✅ 启发式规则集中管理
- ✅ 项目无需额外配置文件
- ✅ 跨项目通用性强
- ✅ 新增目录自动识别

---

## 9. 实施检查清单

- [ ] 创建`pytest_batch_executor.py`模块
- [ ] 修改`quality_agents.py`中的`PytestAgent`
- [ ] 更新`epic_driver.py`质量门控调用
- [ ] 安装`pytest-xdist`依赖
- [ ] 测试验证：标准目录结构项目
- [ ] 测试验证：散装文件项目
- [ ] 测试验证：混合结构项目
- [ ] 更新项目文档

---

- 自动调整超时为平均值的1.5倍

---

## 11. 相关文档

- [AGENTS.md](../AGENTS.md) - AI Agent开发指南
- [claude_docs/testing_guide.md](../claude_docs/testing_guide.md) - 测试策略
- [claude_docs/quality_assurance.md](../claude_docs/quality_assurance.md) - 质量保证

---

**文档版本**: 1.0  
**创建日期**: 2026-01-13  
**维护者**: autoBMAD Team
