"""
Quality Agents - 重构后的质量检查 Agents
增强后支持TaskGroup管理
"""
from __future__ import annotations
import json
import logging
from anyio.abc import TaskGroup
import anyio
from abc import ABC
from typing import Any, Dict, Optional
import asyncio
import subprocess

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BaseQualityAgent(BaseAgent, ABC):
    """质量检查 Agent 基类"""

    def __init__(
        self,
        name: str,
        task_group: Optional[TaskGroup] = None,
    ):
        """
        初始化质量检查 Agent

        Args:
            name: Agent名称
            task_group: TaskGroup实例
        """
        super().__init__(name, task_group)
        self._log_execution(f"{name} initialized")

    async def _run_subprocess(self, command: str, timeout: int = 300) -> Dict[str, Any]:
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
        except asyncio.TimeoutError:
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

    def __init__(self, task_group: Optional[TaskGroup] = None):
        super().__init__("Ruff", task_group)

    async def execute(
        self,
        source_dir: str,
        project_root: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

            result: Dict[str, Any] = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                import json
                try:
                    issues_list: list[Any] = json.loads(result["stdout"]) if result["stdout"] else []
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    filenames = set(i.get("filename", "") for i in issues_list)
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

    def __init__(self, task_group: Optional[TaskGroup] = None):
        super().__init__("BasedPyright", task_group)

    async def execute(self, source_dir: str, **kwargs: Any) -> Dict[str, Any]:
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

            result: Dict[str, Any] = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                import json
                try:
                    output_dict: dict[str, Any] = json.loads(result["stdout"]) if result["stdout"] else {}
                    issues_list: list[Any] = output_dict.get("generalDiagnostics", [])
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    files_set = set(i.get("file", "") for i in issues_list)
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
    """Pytest 测试执行 Agent"""

    def __init__(self, task_group: Optional[TaskGroup] = None):
        super().__init__("Pytest", task_group)

    async def execute(
        self,
        source_dir: str,
        test_dir: str
    ) -> Dict[str, Any]:
        """
        执行 Pytest 测试

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            Dict[str, Any]: 测试结果
        """
        self.logger.info("Running Pytest")

        try:
            # 构建 Pytest 命令
            command = f"pytest {test_dir} -v --tb=short --cov={source_dir} --cov-report=json"

            result = await self._run_subprocess(command, timeout=600)

            if result["status"] == "completed":
                # 解析测试结果
                import re

                # 尝试从 JSON 输出中获取覆盖率信息
                try:
                    # 查找 JSON 覆盖率输出
                    coverage_match = re.search(r'\{.*\}', result["stdout"], re.DOTALL)
                    if coverage_match:
                        coverage_data = json.loads(coverage_match.group())
                        coverage_percent = coverage_data.get("totals", {}).get("percent_covered", 0)
                    else:
                        coverage_percent = 0
                except json.JSONDecodeError:
                    coverage_percent = 0

                # 解析测试统计
                output_lines = result["stdout"].split('\n')
                tests_passed = 0
                tests_failed = 0
                tests_errors = 0

                for line in output_lines:
                    if "passed" in line:
                        match = re.search(r'(\d+) passed', line)
                        if match:
                            tests_passed = int(match.group(1))
                    elif "failed" in line:
                        match = re.search(r'(\d+) failed', line)
                        if match:
                            tests_failed = int(match.group(1))
                    elif "error" in line:
                        match = re.search(r'(\d+) error', line)
                        if match:
                            tests_errors = int(match.group(1))

                return {
                    "status": "completed",
                    "tests_passed": tests_passed,
                    "tests_failed": tests_failed,
                    "tests_errors": tests_errors,
                    "coverage": coverage_percent,
                    "total_tests": tests_passed + tests_failed + tests_errors,
                    "message": f"{tests_passed} tests passed, {tests_failed} failed, {tests_errors} errors"
                }
            else:
                return result

        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
