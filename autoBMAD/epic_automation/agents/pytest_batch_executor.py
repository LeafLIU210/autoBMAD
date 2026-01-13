"""
Pytest目录遍历分批执行器 - 动态扫描版本
支持自动发现测试目录并按优先级批次执行
"""

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
        batches: list[BatchConfig] = []

        if not self.test_dir.exists():
            self.logger.warning(f"Test directory not found: {self.test_dir}")
            return batches

        # 1. 动态扫描所有子目录（不预设目录名，排除不需要的目录）
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'htmlcov', '.coverage'}
        subdirs = [
            d for d in self.test_dir.iterdir()
            if d.is_dir()
            and not d.name.startswith('.')
            and d.name not in exclude_dirs
        ]

        self.logger.info(f"Scanning tests directory: found {len(subdirs)} subdirectories")

        for subdir in subdirs:
            # 使用启发式规则匹配配置
            config = self._match_config_by_heuristic(subdir.name)
            batches.append(BatchConfig(
                name=subdir.name,
                path=str(subdir),
                timeout=config["timeout"],  # type: ignore[arg-type]
                parallel=config["parallel"],  # type: ignore[arg-type]
                workers=config.get("workers", "auto"),
                blocking=config["blocking"],  # type: ignore[arg-type]
                priority=config["priority"]  # type: ignore[arg-type]
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
                timeout=config["timeout"],  # type: ignore[arg-type]
                parallel=config["parallel"],  # type: ignore[arg-type]
                workers=config["workers"],
                blocking=config["blocking"],  # type: ignore[arg-type]
                priority=config["priority"]  # type: ignore[arg-type]
            ))
            self.logger.info(
                f"Mapped {len(loose_files)} loose test files → 'loose_tests' task "
                f"(timeout={config['timeout']}s)"
            )

        # 3. 按优先级排序
        batches.sort(key=lambda b: b.priority)  # type: ignore[arg-type]

        self.logger.info("Total test batches created: %d", len(batches))

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

        results: list[dict[str, Any]] = []
        failed_batches: list[str] = []

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
        passed_batches = sum(1 for r in results if r.get("success", False))

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

        import asyncio

        try:
            # 执行命令
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
