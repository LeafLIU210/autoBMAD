"""
Quality Agents - 重构后的质量检查 Agents
增强后支持TaskGroup管理
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
from abc import ABC
from typing import Any

from anyio.abc import TaskGroup

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BaseQualityAgent(BaseAgent, ABC):
    """质量检查 Agent 基类"""

    def __init__(
        self,
        name: str,
        task_group: TaskGroup | None = None,
    ):
        """
        初始化质量检查 Agent

        Args:
            name: Agent名称
            task_group: TaskGroup实例
        """
        super().__init__(name, task_group)
        self._log_execution(f"{name} initialized")

    async def _run_subprocess(self, command: str, timeout: int = 300) -> dict[str, Any]:
        """
        运行子进程命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 在线程池中运行子进程，避免 cancel scope 传播
            loop = asyncio.get_event_loop()
            process = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                ),
                timeout=timeout + 10  # 额外增加10秒的超时保护
            )

            return {
                "status": "completed",
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "success": process.returncode == 0
            }
        except TimeoutError:
            self.logger.error(f"Command timed out after {timeout} seconds: {command}")
            return {
                "status": "failed",
                "error": f"Timeout after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "command": command
            }


class RuffAgent(BaseQualityAgent):
    """Ruff 代码风格检查 Agent"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("Ruff", task_group)

    async def execute(
        self,
        source_dir: str,
        project_root: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        执行 Ruff 检查

        Args:
            source_dir: 源代码目录
            project_root: 项目根目录

        Returns:
            Dict[str, Any]: 检查结果
        """
        self.logger.info("Running Ruff checks")

        try:
            # 构建 Ruff 命令
            command = f"ruff check {source_dir} --output-format=json"

            result: dict[str, Any] = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                import json
                try:
                    issues_list: list[Any] = json.loads(result["stdout"]) if result["stdout"] else []
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    filenames = {i.get("filename", "") for i in issues_list}
                    files_count = len(filenames)
                    return {
                        "status": "completed",
                        "errors": error_count,
                        "warnings": warning_count,
                        "files_checked": files_count,
                        "issues": issues_list,
                        "message": f"Found {len(issues_list)} issues"
                    }
                except json.JSONDecodeError:
                    # 如果无法解析 JSON，返回基本信息
                    return {
                        "status": "completed",
                        "errors": 0,
                        "warnings": 0,
                        "files_checked": 0,
                        "message": "Check completed (no JSON output)"
                    }
            else:
                return result

        except Exception as e:
            self.logger.error(f"Ruff check failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


class BasedPyrightAgent(BaseQualityAgent):
    """BasedPyright 类型检查 Agent"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("BasedPyright", task_group)

    async def execute(self, source_dir: str, **kwargs: Any) -> dict[str, Any]:
        """
        执行 BasedPyright 检查

        Args:
            source_dir: 源代码目录

        Returns:
            Dict[str, Any]: 检查结果
        """
        self.logger.info("Running BasedPyright checks")

        try:
            # 构建 BasedPyright 命令
            command = f"basedpyright {source_dir} --outputformat=json"

            result: dict[str, Any] = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                import json
                try:
                    output_dict: dict[str, Any] = json.loads(result["stdout"]) if result["stdout"] else {}
                    issues_list: list[Any] = output_dict.get("generalDiagnostics", [])
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    files_set = {i.get("file", "") for i in issues_list}
                    files_count = len(files_set)

                    return {
                        "status": "completed",
                        "errors": error_count,
                        "warnings": warning_count,
                        "files_checked": files_count,
                        "issues": issues_list,
                        "message": f"Found {len(issues_list)} type issues"
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "completed",
                        "errors": 0,
                        "warnings": 0,
                        "files_checked": 0,
                        "message": "Check completed (no JSON output)"
                    }
            else:
                return result

        except Exception as e:
            self.logger.error(f"BasedPyright check failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


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
            from pathlib import Path

            from .pytest_batch_executor import PytestBatchExecutor

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
