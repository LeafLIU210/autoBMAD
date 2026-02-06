"""
Quality Agents - 重构后的质量检查 Agents
增强后支持TaskGroup管理
"""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from abc import ABC
from pathlib import Path
from typing import Any, TypedDict, NotRequired, Literal, cast

from anyio.abc import TaskGroup

from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.core.sdk_result import SDKResult

logger = logging.getLogger(__name__)


# 类型定义
class SubprocessResult(TypedDict):
    status: Literal["completed", "failed"]
    returncode: int
    stdout: str
    stderr: str
    success: bool
    error: NotRequired[str]
    command: NotRequired[str]


class RuffIssue(TypedDict):
    filename: str
    code: str
    message: str
    severity: Literal["error", "warning"]
    location: dict[str, int]


class RuffResult(TypedDict):
    status: Literal["completed", "failed"]
    errors: int
    warnings: int
    files_checked: int
    issues: list[RuffIssue]
    message: str
    error: NotRequired[str]


class BasedPyrightIssue(TypedDict):
    file: str
    rule: str | None
    message: str
    severity: Literal["error", "warning"]
    range: dict[str, Any]


class BasedPyrightResult(TypedDict):
    status: Literal["completed", "failed"]
    errors: int
    warnings: int
    files_checked: int
    issues: list[BasedPyrightIssue]
    message: str
    error: NotRequired[str]


class PytestTestCase(TypedDict):
    nodeid: str
    failure_type: Literal["failed", "error"]
    message: str
    short_tb: str


class PytestFileResult(TypedDict):
    test_file: str
    status: Literal["passed", "failed", "error", "timeout"]
    failures: list[PytestTestCase]


class PytestResult(TypedDict):
    status: Literal["completed", "failed"]
    files: list[PytestFileResult]
    error: NotRequired[str]


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

    async def _run_subprocess(self, command: str, timeout: int = 300) -> SubprocessResult:
        """
        运行子进程命令（增加超时后强制终止）

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）

        Returns:
            SubprocessResult: 执行结果
        """
        process = None
        try:
            loop = asyncio.get_event_loop()

            # 使用Popen替代run，以便控制进程生命周期
            def run_with_popen():
                nonlocal process
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                )
                stdout, _ = process.communicate(timeout=timeout)
                return subprocess.CompletedProcess(
                    args=command,
                    returncode=process.returncode,
                    stdout=stdout,
                    stderr=""
                )

            completed = await asyncio.wait_for(
                loop.run_in_executor(None, run_with_popen),
                timeout=timeout + 10
            )

            return SubprocessResult(
                status="completed",
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                success=completed.returncode == 0
            )

        except (TimeoutError, subprocess.TimeoutExpired):
            self.logger.error(f"Command timed out after {timeout} seconds: {command}")

            # P0修复: 强制终止进程及其子进程
            if process is not None:
                try:
                    self._kill_process_tree(process.pid)
                except Exception as kill_err:
                    self.logger.warning(f"Failed to kill process: {kill_err}")

            return SubprocessResult(
                status="failed",
                returncode=-1,
                stdout="",
                stderr=f"Timeout after {timeout} seconds",
                success=False,
                error=f"Timeout after {timeout} seconds",
                command=command
            )

        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return SubprocessResult(
                status="failed",
                returncode=-1,
                stdout="",
                stderr=str(e),
                success=False,
                error=str(e),
                command=command
            )

    def _kill_process_tree(self, pid: int) -> None:
        """终止进程及其所有子进程（二阶段强制终止）"""
        import psutil

        GRACE_TIMEOUT = 3   # 优雅退出等待时间
        FORCE_TIMEOUT = 2   # 强杀后等待时间

        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # === 阶段1：优雅终止 ===
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass

            gone, alive = psutil.wait_procs(children, timeout=GRACE_TIMEOUT)

            # === 阶段2：强制杀死未退出的子进程 ===
            for p in alive:
                try:
                    self.logger.warning(f"Force killing child process {p.pid}")
                    p.kill()
                except psutil.NoSuchProcess:
                    pass

            # 等待强杀生效
            if alive:
                psutil.wait_procs(alive, timeout=FORCE_TIMEOUT)

            # === 阶段3：终止父进程 ===
            try:
                parent.terminate()
                parent.wait(timeout=GRACE_TIMEOUT)
            except psutil.TimeoutExpired:
                self.logger.warning(f"Force killing parent process {pid}")
                parent.kill()
                parent.wait(timeout=FORCE_TIMEOUT)

        except psutil.NoSuchProcess:
            pass  # 进程已退出
        except Exception as e:
            self.logger.error(f"Error killing process tree {pid}: {e}")
            # 最后手段：尝试OS级强杀
            self._os_force_kill(pid)

    def _os_force_kill(self, pid: int) -> None:
        """操作系统级强制终止（后备方案）"""
        import os
        import signal
        try:
            if os.name == 'nt':  # Windows
                os.system(f'taskkill /F /T /PID {pid}')
            else:  # Unix
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass

class RuffAgent(BaseQualityAgent):
    """Ruff 代码风格检查 Agent（改造版 - 支持SDK自动修复）"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("Ruff", task_group)

    async def execute(
        self,
        source_dir: str,
        project_root: str | None = None,
        **kwargs: object
    ) -> RuffResult:
        """
        执行 Ruff 检查（增加 --fix 自动修复）

        Args:
            source_dir: 源代码目录
            project_root: 项目根目录

        Returns:
            RuffResult: 检查结果
        """
        self.logger.info("Running Ruff checks with auto-fix")

        try:
            # 构建 Ruff 命令（增加 --fix）
            command = f"ruff check --fix --output-format=json {source_dir}"

            result = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                try:
                    issues_list: list[dict[str, object]] = json.loads(result["stdout"]) if result["stdout"] else []
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    filenames = {i.get("filename", "") for i in issues_list}
                    files_count = len(filenames)

                    return RuffResult(
                        status="completed",
                        errors=error_count,
                        warnings=warning_count,
                        files_checked=files_count,
                        issues=issues_list,
                        message=f"Found {len(issues_list)} issues (after auto-fix)"
                    )
                except json.JSONDecodeError:
                    return RuffResult(
                        status="completed",
                        errors=0,
                        warnings=0,
                        files_checked=0,
                        issues=[],
                        message="Check completed (no JSON output)"
                    )
            else:
                return RuffResult(
                    status="failed",
                    errors=0,
                    warnings=0,
                    files_checked=0,
                    issues=[],
                    message=result.get("stderr", "Ruff check failed")
                )

        except Exception as e:
            self.logger.error(f"Ruff check failed: {e}")
            return RuffResult(
                status="failed",
                errors=0,
                warnings=0,
                files_checked=0,
                issues=[],
                message=f"Ruff check failed: {str(e)}",
                error=f"Ruff check failed: {str(e)}"
            )

    def parse_errors_by_file(
        self,
        issues: list[dict[str, object]]
    ) -> dict[str, list[dict[str, object]]]:
        """
        按文件路径分组错误

        Args:
            issues: ruff JSON 输出的 issues 列表

        Returns:
            {"src/a.py": [error1, error2], ...}
        """
        errors_by_file: dict[str, list[dict[str, object]]] = {}

        for issue in issues:
            issue_dict = cast(dict[str, Any], issue)
            file_path = issue_dict.get("filename", "")
            if not file_path:
                continue

            if file_path not in errors_by_file:
                errors_by_file[file_path] = []

            # 提取关键错误信息
            location = cast(dict[str, Any], issue_dict.get("location", {}))
            errors_by_file[file_path].append({
                "line": location.get("row"),
                "column": location.get("column"),
                "code": issue_dict.get("code"),
                "message": issue_dict.get("message"),
                "severity": issue_dict.get("severity", "error"),
            })

        return errors_by_file

    def build_fix_prompt(
        self,
        tool: str,
        file_path: str,
        errors: list[dict[str, object]],
    ) -> str:
        """
        构造 Ruff 修复 Prompt

        Args:
            tool: 工具名称 ('ruff')
            file_path: 文件路径
            errors: 错误列表

        Returns:
            完整的修复 Prompt
        """
        errors_summary = self._format_errors_summary(file_path, errors)

        return RUFF_FIX_PROMPT.format(
            errors_summary=errors_summary,
        )

    def _format_errors_summary(self, file_path: str, errors: list[dict[str, object]]) -> str:
        """格式化错误摘要（包含文件路径）"""
        lines = [f"## File: {file_path}\n"]
        for i, error in enumerate(errors, 1):
            error_dict = cast(dict[str, Any], error)
            message = str(error_dict.get('message', ''))
            lines.append(f"""
### Error {i}
- **Line**: {error_dict.get('line')}
- **Column**: {error_dict.get('column')}
- **Code**: `{error_dict.get('code')}`
- **Message**: {message}
- **Severity**: {error_dict.get('severity')}""".strip())

        return "\n\n".join(lines)

    async def format(self, source_dir: str) -> dict[str, Any]:
        """
        执行 ruff format（新增）

        Args:
            source_dir: 源代码目录

        Returns:
            {
                "status": "completed" | "failed",
                "formatted": bool,
                "message": str
            }
        """
        self.logger.info("Running ruff format")

        try:
            command = f"ruff format {source_dir}"
            result = await self._run_subprocess(command)

            formatted = result["returncode"] == 0

            return {
                "status": "completed" if formatted else "failed",
                "formatted": formatted,
                "message": "Code formatted successfully" if formatted else "Format failed",
            }

        except Exception as e:
            self.logger.error(f"Ruff format failed: {e}")
            return {
                "status": "failed",
                "formatted": False,
                "error": str(e)
            }


class BasedPyrightAgent(BaseQualityAgent):
    """BasedPyright 类型检查 Agent（改造版 - 支持SDK自动修复）"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("BasedPyright", task_group)

    async def execute(self, source_dir: str, **kwargs: object) -> BasedPyrightResult:
        """
        执行 BasedPyright 检查

        Args:
            source_dir: 源代码目录

        Returns:
            BasedPyrightResult: 检查结果
        """
        self.logger.info("Running BasedPyright checks")

        try:
            # 构建 BasedPyright 命令
            command = f"basedpyright --outputjson {source_dir}"

            result = await self._run_subprocess(command)

            if result["status"] == "completed":
                # 解析 JSON 输出
                try:
                    output_dict: dict[str, object] = json.loads(result["stdout"]) if result["stdout"] else {}
                    issues_list: list[dict[str, object]] = cast(list[dict[str, object]], output_dict.get("generalDiagnostics", []))
                    error_count = len([i for i in issues_list if i.get("severity") == "error"])
                    warning_count = len([i for i in issues_list if i.get("severity") == "warning"])
                    files_set = {i.get("file", "") for i in issues_list}
                    files_count = len(files_set)

                    return BasedPyrightResult(
                        status="completed",
                        errors=error_count,
                        warnings=warning_count,
                        files_checked=files_count,
                        issues=issues_list,
                        message=f"Found {len(issues_list)} type issues"
                    )
                except json.JSONDecodeError:
                    return BasedPyrightResult(
                        status="completed",
                        errors=0,
                        warnings=0,
                        files_checked=0,
                        issues=[],
                        message="Check completed (no JSON output)"
                    )
            else:
                return BasedPyrightResult(
                    status="failed",
                    errors=0,
                    warnings=0,
                    files_checked=0,
                    issues=[],
                    message=result.get("stderr", "BasedPyright check failed")
                )

        except Exception as e:
            self.logger.error(f"BasedPyright check failed: {e}")
            return BasedPyrightResult(
                status="failed",
                errors=0,
                warnings=0,
                files_checked=0,
                issues=[],
                message=f"BasedPyright check failed: {str(e)}",
                error=f"BasedPyright check failed: {str(e)}"
            )

    def parse_errors_by_file(
        self,
        issues: list[dict[str, object]]
    ) -> dict[str, list[dict[str, object]]]:
        """
        按文件路径分组错误

        Args:
            issues: basedpyright JSON 输出的 generalDiagnostics

        Returns:
            {"src/x.py": [error1], ...}
        """
        errors_by_file: dict[str, list[dict[str, object]]] = {}

        for issue in issues:
            issue_dict = cast(dict[str, Any], issue)
            file_path = issue_dict.get("file", "")
            if not file_path:
                continue

            if file_path not in errors_by_file:
                errors_by_file[file_path] = []

            # 提取关键错误信息
            range_info: dict[str, object] = cast(dict[str, object], issue_dict.get("range", {}))
            start_info: dict[str, Any] = cast(dict[str, Any], range_info.get("start", {}))

            errors_by_file[file_path].append({
                "line": start_info.get("line"),
                "column": start_info.get("character"),
                "rule": issue_dict.get("rule"),
                "message": issue_dict.get("message"),
                "severity": issue_dict.get("severity", "error"),
            })

        return errors_by_file

    def build_fix_prompt(
        self,
        tool: str,
        file_path: str,
        errors: list[dict[str, object]],
    ) -> str:
        """构造 BasedPyright 修复 Prompt"""
        errors_summary = self._format_errors_summary(file_path, errors)

        return BASEDPYRIGHT_FIX_PROMPT.format(
            errors_summary=errors_summary,
        )

    def _format_errors_summary(self, file_path: str, errors: list[dict[str, object]]) -> str:
        """格式化错误摘要（包含文件路径）"""
        lines = [f"## File: {file_path}\n"]
        for i, error in enumerate(errors, 1):
            error_dict = cast(dict[str, Any], error)
            message = str(error_dict.get('message', ''))
            lines.append(f"""
### Type Error {i}
- **Line**: {error_dict.get('line')}
- **Column**: {error_dict.get('column')}
- **Rule**: `{error_dict.get('rule')}`
- **Message**: {message}
- **Severity**: {error_dict.get('severity')}""".strip())

        return "\n\n".join(lines)


class PytestAgent(BaseQualityAgent):
    """Pytest 测试执行 Agent - 支持目录遍历批次执行和SDK修复"""

    def __init__(self, task_group: TaskGroup | None = None):
        super().__init__("Pytest", task_group)

    async def execute(
        self,
        source_dir: str,
        test_dir: str
    ) -> PytestResult:
        """
        执行 Pytest 测试（目录遍历批次执行）

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            PytestResult: 测试结果
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

            # 转换结果格式为PytestResult
            files = []
            if "results" in result:
                for batch_result in result.get("results", []):
                    # 解析stdout中的测试信息
                    stdout = batch_result.get("stdout", "")
                    tests_passed = batch_result.get("tests_passed", 0)
                    tests_failed = batch_result.get("tests_failed", 0)

                    # 构建文件结果
                    file_result = {
                        "test_file": batch_result.get("batch_name", ""),
                        "status": "passed" if batch_result.get("success", False) else "failed",
                        "failures": []
                    }

                    # 如果有失败的测试，添加失败信息
                    if tests_failed > 0:
                        # 简单的失败信息提取（实际实现中可能需要更复杂的解析）
                        file_result["failures"].append({
                            "nodeid": f"{batch_result.get('batch_name', '')}::*",
                            "failure_type": "failed",
                            "message": f"Batch failed: {tests_failed} tests failed, {tests_passed} tests passed",
                            "short_tb": stdout
                        })

                    files.append(file_result)

            return PytestResult(
                status=result.get("status", "failed"),
                files=files
            )

        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return PytestResult(
                status="failed",
                files=[],
                error=str(e)
            )

    async def run_tests_sequential(
        self,
        test_files: list[str],
        timeout_per_file: int,
        round_index: int,
        round_type: str,
    ) -> dict[str, object]:
        """
        按文件顺序执行 pytest -v --tb=short（增加资源错误检测）

        Args:
            test_files: 测试文件列表
            timeout_per_file: 每个文件的超时时间（秒）
            round_index: 轮次索引
            round_type: "initial" | "retry"

        Returns:
            {
                "files": [
                    {
                        "test_file": "...",
                        "status": "passed" | "failed" | "error" | "timeout",
                        "failures": [...],  # 仅当 status != passed
                    }
                ]
            }
        """
        self.logger.info(f"Running sequential tests: {len(test_files)} files (round {round_index}, type: {round_type})")

        results = []
        consecutive_resource_errors = 0

        for test_file in test_files:
            # 执行单个文件的 pytest
            file_result = await self._run_pytest_single_file(
                test_file=test_file,
                timeout=timeout_per_file,
            )
            results.append(file_result)

            # 检测资源错误
            if self._is_resource_error(file_result):
                consecutive_resource_errors += 1
                self.logger.warning(f"Resource error detected for {test_file} (count: {consecutive_resource_errors})")
                if consecutive_resource_errors >= 3:
                    self.logger.error(
                        "System resources exhausted, aborting remaining tests"
                    )
                    break
            else:
                consecutive_resource_errors = 0

        return {"files": results}

    def _is_resource_error(self, result: dict[str, Any]) -> bool:
        """检测是否为系统资源耗尽错误"""
        RESOURCE_ERROR_CODES = {8, 1450, 1455}  # WinError资源相关错误
        failures = result.get("failures", [])
        if not failures:
            return False
        error_msg = str(failures[0].get("message", ""))
        return any(f"WinError {code}" in error_msg for code in RESOURCE_ERROR_CODES)

    async def _run_pytest_single_file(
        self,
        test_file: str,
        timeout: int,
    ) -> PytestFileResult:
        """
        执行单个测试文件的 pytest

        增强版：添加stderr后备机制

        命令：pytest <test_file> -v --tb=short --json-report --json-report-file=<tmp>

        Args:
            test_file: 测试文件路径
            timeout: 超时时间（秒）

        Returns:
            {
                "test_file": str,
                "status": str,
                "failures": list[dict],  # 从 json-report 提取
            }
        """
        self.logger.debug(f"Running pytest on {test_file}")

        # 1. 构造命令
        import tempfile
        from pathlib import Path

        tmp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        tmp_json_path = tmp_json.name
        tmp_json.close()

        try:
            # 使用 -o addopts= 覆盖 pyproject.toml 的默认配置，避免冲突
            cmd = f'pytest {test_file} -v --tb=short --json-report --json-report-file={tmp_json_path} -o addopts='

            # 2. 执行（复用 BaseQualityAgent._run_subprocess）
            result = await self._run_subprocess(cmd, timeout=timeout)

            # 3. 解析 json-report
            failures = self._parse_json_report(tmp_json_path, test_file)

            # ✅ 新增：后备机制 - 当failures为空但执行失败时，使用stderr
            if not failures and result["returncode"] != 0:
                stderr = result.get("stderr", "")
                stdout = result.get("stdout", "")

                # 优先使用stderr，如果为空则使用stdout
                error_output = stderr if stderr else stdout

                if error_output:
                    # 提取关键错误信息（前500字符）
                    error_summary = error_output[:500]
                    failures = [{
                        "nodeid": test_file,
                        "failure_type": "error",
                        "message": f"Pytest execution failed (no JSON report):\n{error_summary}",
                        "short_tb": "Check pytest output - no structured report available"
                    }]
                    self.logger.warning(
                        f"No failures parsed from JSON but returncode={result['returncode']}, "
                        f"using stderr/stdout as fallback"
                    )

            # 4. 判断状态
            if result.get("status") == "failed" and "Timeout" in result.get("error", ""):
                status = "timeout"
            elif result["returncode"] == 0:
                status = "passed"
            elif failures:
                status = "failed" if any(f["failure_type"] == "failed" for f in failures) else "error"
            else:
                # 🆕 最终后备：即使无输出也构造错误条目
                status = "error"
                if not failures:
                    failures = [{
                        "nodeid": test_file,
                        "failure_type": "error",
                        "message": f"Test execution failed with returncode {result['returncode']}",
                        "short_tb": "Run pytest manually for details"
                    }]
                    self.logger.info(f"Constructed minimal failure entry for {test_file}")

            return {
                "test_file": test_file,
                "status": status,
                "failures": failures,
            }

        finally:
            # 清理临时文件
            try:
                Path(tmp_json_path).unlink(missing_ok=True)
            except Exception:
                pass

    def _parse_json_report(
        self,
        json_path: str,
        test_file: str,
    ) -> list[PytestTestCase]:
        """
        从 pytest-json-report 中提取失败信息

        增强版：支持捕获collection error和测试用例失败

        Args:
            json_path: JSON 报告文件路径
            test_file: 测试文件路径

        Returns:
            [
                {
                    "nodeid": "...",
                    "failure_type": "failed" | "error",
                    "message": "...",
                    "short_tb": "...",
                }
            ]
        """
        if not Path(json_path).exists():
            self.logger.warning(f"JSON report not found: {json_path}")
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Failed to parse JSON report: {e}")
            return []

        failures = []

        # ✅ 新增：检查collection错误
        collectors = data.get("collectors", [])
        if collectors:
            for collector in collectors:
                if collector.get("outcome") == "failed":
                    longrepr = collector.get("longrepr", "")
                    # 提取关键错误信息
                    error_lines = str(longrepr).split("\n")
                    error_summary = "\n".join(error_lines[:10])  # 前10行

                    failures.append({
                        "nodeid": collector.get("nodeid", test_file),
                        "failure_type": "error",  # collection错误标记为error
                        "message": f"Collection failed: {error_summary}",
                        "short_tb": f"Test file collection error at {test_file}"
                    })
                    self.logger.warning(f"Captured collection error for {test_file}")

        # ✅ 原有逻辑：提取测试用例失败
        tests = data.get("tests", [])
        for test in tests:
            outcome = test.get("outcome")
            if outcome in ["failed", "error"]:
                # 仅保留当前测试文件的用例
                if not test["nodeid"].startswith(test_file):
                    continue

                call = test.get("call", {})
                failures.append({
                    "nodeid": test["nodeid"],
                    "failure_type": outcome,  # 保留原始类型(failed/error)
                    "message": call.get("longrepr", "Unknown error"),
                    "short_tb": self._extract_short_traceback(test),
                })

        # ✅ 新增：诊断日志
        if not failures and not tests and not collectors:
            self.logger.warning(
                f"JSON report for {test_file} is empty (no tests, no collectors). "
                f"This may indicate a pytest execution failure."
            )

        return failures

    def _extract_short_traceback(self, test: dict[str, object]) -> str:
        """从 test 对象中提取精简的堆栈信息"""
        # 提取关键行号和错误位置
        try:
            call: dict[str, object] = cast(dict[str, object], test.get("call", {}))
            longrepr = call.get("longrepr", "")

            # 尝试提取最后几行作为短堆栈
            if isinstance(longrepr, str):
                lines = longrepr.split("\n")
                # 取最后3行
                return "\n".join(lines[-3:]) if len(lines) > 3 else longrepr

            return str(longrepr)
        except Exception:
            return "Traceback information unavailable"

    async def run_sdk_fix_for_file(
        self,
        test_file: str,
        source_dir: str,
        summary_json_path: str,
        round_index: int,
    ) -> dict[str, bool | str]:
        """
        对单个测试文件发起 SDK 修复调用

        流程：
        1. 从汇总 JSON 中读取该文件的失败信息
        2. 读取测试文件内容
        3. 构造 Prompt（使用 Prompt 模板）
        4. 通过 SafeClaudeSDK 发起调用
        5. 收到 ResultMessage → 触发取消 → 等待确认
        6. 返回简单的成功/失败标志

        Args:
            test_file: 测试文件路径
            source_dir: 源代码目录
            summary_json_path: 汇总 JSON 路径
            round_index: 当前轮次

        Returns:
            {
                "success": bool,
                "error": str | None,
            }
        """
        self.logger.info(f"Starting SDK fix for {test_file} (round {round_index})")

        try:
            # 1. 读取失败信息
            failures: list[PytestTestCase] = self._load_failures_from_json(summary_json_path, test_file)

            if not failures:
                self.logger.warning(f"No failure information found for {test_file}")
                return {"success": False, "error": "No failure information available"}

            # 2. 读取测试文件内容
            with open(test_file, "r", encoding="utf-8") as f:
                test_content = f.read()

            # 3. 构造 Prompt
            prompt = self._build_fix_prompt(
                test_file=test_file,
                source_dir=source_dir,
                test_content=test_content,
                failures=failures,
            )

            # 4. 调用 SDK（返回 SDKResult）
            from ..core.sdk_result import SDKResult
            sdk_result: SDKResult = await self._execute_sdk_call_with_cancel(prompt)

            # 5. 使用 SDKResult 语义
            if sdk_result.is_success():
                self.logger.info(
                    f"SDK fix succeeded for {test_file} "
                    f"(duration: {sdk_result.duration_seconds:.2f}s)"
                )
                return {
                    "success": True,
                    "error": None
                }
            else:
                error_summary = sdk_result.get_error_summary()
                self.logger.error(
                    f"SDK fix failed for {test_file}: {error_summary}"
                )
                return {
                    "success": False,
                    "error": error_summary
                }

        except Exception as e:
            self.logger.error(f"SDK fix failed for {test_file}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def _execute_sdk_call_with_cancel(self, prompt: str) -> SDKResult:
        """
        执行 SDK 调用并处理取消流程（重构为统一路径）

        修复点:
        1. 使用 execute_sdk_call 统一入口
        2. 自动处理 ClaudeAgentOptions 构造
        3. 返回类型明确为 SDKResult
        """
        from .sdk_helper import execute_sdk_call

        # 统一调用，自动处理 options 类型转换
        result = await execute_sdk_call(
            prompt=prompt,
            agent_name="PytestAgent",
            timeout=300.0,
            permission_mode="bypassPermissions"
        )

        return result

    def _load_failures_from_json(
        self,
        summary_json_path: str,
        test_file: str,
    ) -> list[PytestTestCase]:
        """从汇总 JSON 中加载指定测试文件的失败信息"""
        import json

        if not Path(summary_json_path).exists():
            self.logger.warning(f"Summary JSON not found: {summary_json_path}")
            return []

        try:
            with open(summary_json_path, "r", encoding="utf-8") as f:
                data: dict[str, object] = json.load(f)

            # 从最后一轮中查找该文件的失败信息
            rounds: list[object] = cast(list[object], data.get("rounds", []))
            if rounds:
                last_round: dict[str, object] = cast(dict[str, object], rounds[-1])
                failed_files: list[object] = cast(list[object], last_round.get("failed_files", []))
                for item in failed_files:
                    item_dict: dict[str, object] = cast(dict[str, object], item)
                    if item_dict["test_file"] == test_file:
                        failures_raw = item_dict.get("failures", [])
                        # 验证并转换类型
                        if not isinstance(failures_raw, list):
                            self.logger.warning(
                                f"Invalid failures format for {test_file}: expected list, got {type(failures_raw)}"
                            )
                            return []

                        # 转换为 PytestTestCase 类型
                        failures: list[PytestTestCase] = []
                        for failure in failures_raw:
                            if not isinstance(failure, dict):
                                continue

                            # 验证必需字段
                            if not all(k in failure for k in ["nodeid", "failure_type", "message", "short_tb"]):
                                self.logger.warning(f"Incomplete failure data: {failure}")
                                continue

                            failures.append({
                                "nodeid": str(failure["nodeid"]),
                                "failure_type": str(failure["failure_type"]),
                                "message": str(failure["message"]),
                                "short_tb": str(failure["short_tb"])
                            })

                        return failures

            return []

        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Failed to load failures from JSON: {e}")
            return []

    def _build_fix_prompt(
        self,
        test_file: str,
        source_dir: str,
        test_content: str,
        failures: list[PytestTestCase],
    ) -> str:
        """
        构造 SDK 修复提示词

        使用 Prompt 模板
        """
        # 构造失败摘要部分
        failures_lines: list[str] = []
        for i, failure in enumerate(failures, 1):
            nodeid = failure['nodeid']
            failure_type = failure['failure_type']
            message = failure['message']
            short_tb = failure['short_tb']
            failures_lines.append(f"""
### Case {i}
- **nodeid**: `{nodeid}`
- **type**: `{failure_type}`
- **message**: `{message}`
- **short traceback**: `{short_tb}`""".strip())

        failures_summary = "\n\n".join(failures_lines)

        # 填充模板
        prompt = PROMPT_TEMPLATE.format(
            test_file=test_file,
            source_dir=source_dir,
            test_content=test_content,
            failures_summary=failures_summary,
        )

        return prompt


# Prompt 模板
PROMPT_TEMPLATE = """
<system>
You are a senior Python testing and code fixing expert.

**Skill Activation**: Use skill "/claude-plan" for complex analysis and execution.

Objective:
- Detect test hangs or stalls, and fix them if present.
- Based on the given test file path and failure/error information, deeply inspect and analyze the root causes of failures.
- After thorough analysis and deep thinking, provide a complete and detailed fix solution.
- Execute the fix immediately to ensure all tests pass.
- Maintain correct business logic and avoid unrelated refactoring.

Constraints:
- Only modify necessary code (test files and related source code).
- Keep test names, semantics, and acceptance intent unchanged.
- Output format: first provide a summary of changes, then provide the complete new version of each file.

输出格式示例：
## Summary of Changes
- 修复点 1
- 修复点 2

## Patched Files
### File: tests/unit/test_x.py
```python
# 完整修复后的测试文件内容
```

### File: src/module.py (如需修改源码)
```python
# 完整修复后的源码文件内容
```

<END_OF_PATCH>
</system>

<user>
## Test File Information
- **Test file path**: {test_file}
- **Project source dir**: {source_dir}

## Test File Content (Current)
```python
{test_content}
```

## Failures Summary
{failures_summary}

## Expected Result
修复导致上述失败的根因，使所有用例通过。若需要修改业务源码，请说明修改位置和原因。
</user>
"""


# Ruff 修复 Prompt 模板
RUFF_FIX_PROMPT = """
<system>
You are a senior Python code quality expert specializing in Ruff code style fixes.

**Skill Activation**: Use skill "/claude-plan" for complex analysis and execution.

Objective:
- Read the file at the given path and fix all Ruff errors listed below.
- Execute the fix immediately to ensure the code passes Ruff checks.
- Keep business logic unchanged, only fix code style issues.

Constraints:
- Only modify necessary code to resolve issues reported by Ruff.
- Do not perform unrelated refactoring or optimization.
- Maintain code readability and consistency.
- Follow PEP 8 specifications.
</system>

<user>
{errors_summary}

## Expected Result
读取上述文件，修复所有 Ruff 错误，使代码通过检查。
</user>
"""

# BasedPyright 修复 Prompt 模板
BASEDPYRIGHT_FIX_PROMPT = """
<system>
You are a senior Python type annotation expert specializing in BasedPyright type checking fixes.

Objective:
- Read the file at the given path and fix all type errors listed below.
- Execute the fix immediately to ensure the code passes BasedPyright type checks.

Constraints:
- Only modify necessary code to resolve type checking issues.
- Keep business logic unchanged.
</system>

<user>
{errors_summary}

## Expected Result
读取上述文件，修复所有类型检查错误，添加必要的类型注解。
</user>
"""
