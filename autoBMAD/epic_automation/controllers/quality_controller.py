"""
Quality Controller - 质量门控控制器
控制代码质量检查流程（Ruff、BasedPyright、Pytest）
"""
from __future__ import annotations
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from anyio.abc import TaskGroup

from .base_controller import BaseController
from ..agents.quality_agents import (
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)

logger = logging.getLogger(__name__)


class QualityController(BaseController):
    """质量门控控制器"""

    def __init__(
        self,
        task_group: TaskGroup,
        project_root: Optional[Path] = None
    ):
        """
        初始化质量控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            project_root: 项目根目录
        """
        super().__init__(task_group)
        self.project_root = project_root
        self.ruff_agent = RuffAgent()
        self.pyright_agent = BasedPyrightAgent()
        self.pytest_agent = PytestAgent()
        self._log_execution("QualityController initialized")

    async def execute(  # type: ignore[override, reportIncompatibleMethodOverride]
        self,
        source_dir: Optional[str] = None,
        test_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行质量门控

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            Dict[str, Any]: 质量检查结果
        """

        self._log_execution("Starting quality gate process")

        results: Dict[str, Any] = {
            "overall_status": "pending",
            "checks": {}
        }

        try:
            # 计算默认目录
            if not source_dir and not self.project_root:
                # 使用临时目录作为默认值
                temp_dir = Path(tempfile.mkdtemp(prefix="quality_check_"))
                effective_source_dir = str(temp_dir / "src")
                effective_test_dir = str(temp_dir / "tests")
                effective_project_root = str(temp_dir)
                # 创建目录
                Path(effective_source_dir).mkdir(parents=True, exist_ok=True)
                Path(effective_test_dir).mkdir(parents=True, exist_ok=True)
            else:
                effective_source_dir = source_dir or (str(self.project_root / "src") if self.project_root is not None else "")
                effective_test_dir = test_dir or (str(self.project_root / "tests") if self.project_root is not None else None)
                effective_project_root = str(self.project_root) if self.project_root is not None else None

            # Step 1: Ruff 代码风格检查
            self._log_execution("Running Ruff checks")

            # 确保 source_dir 不为空字符串
            if not effective_source_dir:
                results["overall_status"] = "error"
                results["error"] = "No source directory specified"
                return results

            async def call_ruff():
                return await self.ruff_agent.execute(
                    source_dir=effective_source_dir,
                    project_root=effective_project_root
                )
            ruff_result = await self._execute_within_taskgroup(call_ruff)
            results["checks"]["ruff"] = ruff_result

            # Step 2: BasedPyright 类型检查
            self._log_execution("Running BasedPyright checks")

            async def call_pyright():
                return await self.pyright_agent.execute(
                    source_dir=effective_source_dir
                )
            pyright_result = await self._execute_within_taskgroup(call_pyright)
            results["checks"]["pyright"] = pyright_result

            # Step 3: Pytest 测试执行
            self._log_execution("Running Pytest")
            if effective_test_dir is not None:
                async def call_pytest():
                    return await self.pytest_agent.execute(
                        source_dir=effective_source_dir,
                        test_dir=effective_test_dir
                    )
                pytest_result = await self._execute_within_taskgroup(call_pytest)
                results["checks"]["pytest"] = pytest_result
            else:
                # 如果没有测试目录，跳过测试
                results["checks"]["pytest"] = {"status": "skipped", "message": "No test directory provided"}

            # Step 4: 汇总结果
            results["overall_status"] = self._evaluate_overall_status(results["checks"])

            self._log_execution(f"Quality gate completed: {results['overall_status']}")
            # 返回完整的结果字典
            return results

        except Exception as e:
            self._log_execution(f"Quality gate failed: {e}", "error")
            results["overall_status"] = "error"
            results["error"] = str(e)
            return results

    def _evaluate_overall_status(self, checks: Dict[str, Any]) -> str:
        """
        评估整体质量状态

        Args:
            checks: 各检查项结果

        Returns:
            str: 整体状态
        """
        # 评估逻辑
        # 如果所有检查都通过，返回 pass
        # 如果有警告但无错误，返回 pass
        # 如果有错误，返回 fail

        has_error = False
        has_warning = False

        for _check_name, result in checks.items():
            if isinstance(result, dict):
                if result.get("errors", 0) > 0:
                    has_error = True
                elif result.get("warnings", 0) > 0:
                    has_warning = True

        if has_error:
            return "fail"
        elif has_warning:
            return "pass_with_warnings"
        else:
            return "pass"
