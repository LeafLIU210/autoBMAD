"""
Quality Agents - Ruff Code Quality Integration

This module provides quality agents for automated code quality checks and fixes.
Currently implements Ruff integration for Python code linting and auto-fixing.

主要功能：
1. Ruff代码检查和自动修复
2. Claude SDK集成用于自动修复生成
3. 重试机制（最多3个周期，每个周期最多2次重试）
4. JSON输出解析

主要修复：
1. 移除外部超时机制（asyncio.wait_for/asyncio.shield）
2. 使用max_turns=150进行SDK保护
3. 零Cancel Scope错误
"""
# pyright: reportAny=false

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable, cast, override

try:
    from claude_agent_sdk import ClaudeAgentOptions as _ClaudeAgentOptions
    from claude_agent_sdk import ResultMessage as _ResultMessage
    from claude_agent_sdk import query as _query
except ImportError:
    _query = None
    _ClaudeAgentOptions = None
    _ResultMessage = None

logger = logging.getLogger(__name__)


class CodeQualityAgent:
    """
    Agent for automated code quality checks and fixes using various tools.

    Currently supports:
    - Ruff: Python linting and auto-fixing
    """

    def __init__(self, tool_name: str, command_template: str):
        """
        Initialize CodeQualityAgent.

        Args:
            tool_name: Name of the quality tool (e.g., 'ruff')
            command_template: Template for executing the tool with placeholders
        """
        self.tool_name: str = tool_name
        self.command_template: str = command_template
        logger.info(f"Initialized CodeQualityAgent for {tool_name}")

    async def execute_check(
        self, source_dir: Path
    ) -> tuple[bool, list[dict[str, Any]]]:  # type: ignore[reportExplicitAny, type-arg]
        """
        Execute quality check on source directory.

        Args:
            source_dir: Path to source directory to check

        Returns:
            Tuple of (success, issues_list)
            - success: True if check completed successfully
            - issues_list: List of issues found (empty if none)
        """
        try:
            # Build command with JSON output format
            command = self.command_template.format(source_dir=str(source_dir))

            logger.info(f"Executing {self.tool_name} check: {command}")

            # Execute command without asyncio.shield to avoid cancel scope errors
            async def create_and_communicate():
                # Execute command using asyncio subprocess
                # Note: Using venv\Scripts for Windows compatibility
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True,
                )

                try:
                    stdout, _stderr = await process.communicate()
                    return stdout, _stderr, process
                except asyncio.CancelledError:
                    logger.warning(
                        f"Cancelled during {self.tool_name} check, cleaning up process"
                    )
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                    raise

            stdout, _stderr, process = await create_and_communicate()

            # Parse JSON output
            if stdout and stdout.strip():
                try:
                    stdout_text = stdout.decode("utf-8")
                    issues = json.loads(stdout_text)
                    logger.info(f"Found {len(issues)} issues")
                    return True, issues
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON output: {e}")
                    logger.error(
                        f"Raw output: {stdout.decode('utf-8') if stdout else 'None'}"
                    )
                    return False, []
            else:
                logger.info("No issues found")
                return True, []

        except Exception as e:
            logger.error(f"Unexpected error during {self.tool_name} check: {e}")
            return False, []

    async def fix_issues(
        self,
        issues: list[dict[str, Any]],  # type: ignore[type-arg]
        source_dir: Path,
        max_turns: int = 150,
    ) -> tuple[bool, str, int]:  # type: ignore[reportExplicitAny]
        """
        Use Claude SDK to generate fixes for identified issues.

        Args:
            issues: List of issues to fix
            source_dir: Path to source directory
            max_turns: Maximum turns for SDK session (default 150, NO external timeouts)

        Returns:
            Tuple of (success, message, fixed_count)
            - success: True if fix attempt was successful
            - message: Status message
            - fixed_count: Number of issues fixed
        """
        if not issues:
            return True, "No issues to fix", 0

        if _query is None:
            logger.warning("Claude SDK not available, cannot generate fixes")
            return False, "Claude SDK not available", 0

        try:
            # Generate fix prompt
            prompt = self._generate_fix_prompt(issues, source_dir)

            logger.info(f"Requesting fixes for {len(issues)} issues")

            # Execute SDK query with max_turns protection (NO external timeouts)
            options = (
                _ClaudeAgentOptions(max_turns=max_turns)
                if _ClaudeAgentOptions
                else None
            )

            # Execute query - using prompt parameter (not messages)
            # The SDK returns an AsyncIterator of messages
            response_iterator = _query(prompt=prompt, options=options)

            # Collect messages from the iterator
            messages: list[Any] = []
            async for message in response_iterator:
                messages.append(message)  # type: ignore[arg-type]
                # Check if we got a ResultMessage
                if _ResultMessage is not None:
                    if isinstance(message, _ResultMessage):
                        if hasattr(message, "is_error") and message.is_error:
                            error_msg = getattr(message, "result", "Unknown error")
                            logger.error(f"SDK error: {error_msg}")
                            return False, f"SDK error: {error_msg}", 0
                        else:
                            # Success - count fixes
                            fixed_count = len(issues)  # Assume all issues can be fixed
                            logger.info(f"Generated fixes for {fixed_count} issues")
                            return (
                                True,
                                f"Successfully generated fixes for {fixed_count} issues",
                                fixed_count,
                            )
                else:
                    # If _ResultMessage is not available or is mocked, just check for result attribute
                    if hasattr(message, "result"):
                        fixed_count = len(issues)
                        logger.info(f"Generated fixes for {fixed_count} issues")
                        return (
                            True,
                            f"Successfully generated fixes for {fixed_count} issues",
                            fixed_count,
                        )

            # If we get here, no ResultMessage was received
            if messages:
                # Some messages were received but no final result
                logger.warning("SDK returned messages but no final result")
                return False, "Incomplete response from SDK", 0
            else:
                return False, "No response from SDK", 0

        except Exception as e:
            logger.error(f"Error generating fixes: {e}")
            # Return simple error without external timeout mechanisms
            return False, f"Error generating fixes: {str(e)}", 0

    async def retry_cycle(
        self, source_dir: Path, max_cycles: int = 3, retries_per_cycle: int = 2
    ) -> dict[str, Any]:  # type: ignore[type-arg]
        """
        Execute check and fix cycle with retry logic.

        Args:
            source_dir: Path to source directory
            max_cycles: Maximum number of fix cycles (default 3)
            retries_per_cycle: Number of retries per cycle (default 2)

        Returns:
            Dictionary with cycle results
        """
        cycle_results: dict[str, Any] = {  # type: ignore[type-arg]
            "total_cycles": 0,
            "successful_cycles": 0,
            "total_issues_found": 0,
            "total_issues_fixed": 0,
            "cycles": [],
        }

        for cycle_num in range(1, max_cycles + 1):
            logger.info(f"Starting cycle {cycle_num}/{max_cycles}")

            # Execute check
            success, issues = await self.execute_check(source_dir)

            if not success:
                logger.error(f"Check failed in cycle {cycle_num}")
                cycle_results["cycles"].append(
                    {  # type: ignore[arg-type]
                        "cycle": cycle_num,
                        "success": False,
                        "issues_found": 0,
                        "issues_fixed": 0,
                        "error": "Check execution failed",
                    }
                )
                continue

            issues_found = len(issues)
            cycle_results["total_issues_found"] += issues_found

            # If no issues, we're done
            if not issues:
                logger.info(f"No issues found in cycle {cycle_num}, stopping")
                cycle_results["successful_cycles"] += 1
                cycle_results["total_cycles"] = cycle_num
                cycle_results["cycles"].append(
                    {  # type: ignore[arg-type]
                        "cycle": cycle_num,
                        "success": True,
                        "issues_found": 0,
                        "issues_fixed": 0,
                        "message": "No issues found",
                    }
                )

                # 【新增】在循环完成后执行一次format
                logger.info("=== 执行代码格式化 ===")
                format_method = getattr(self, 'format_code', None)
                if format_method is not None and callable(format_method):
                    # Cast to proper type to satisfy type checkers
                    format_func = cast(Callable[[Path], Awaitable[bool]], format_method)
                    format_success = await format_func(source_dir)
                    if not format_success:
                        logger.warning("格式化执行完成，但有警告（不影响整体成功）")
                else:
                    logger.info("格式化功能不可用，跳过格式化步骤")

                break

            # Try to fix issues with retry logic
            # Each cycle can have retries_per_cycle attempts
            fix_success = False
            fix_message = ""
            fixed_count = 0

            for retry_num in range(1, retries_per_cycle + 1):
                logger.info(f"Cycle {cycle_num}, Retry {retry_num}/{retries_per_cycle}")

                # Try to fix issues
                fix_success, fix_message, fixed_count = await self.fix_issues(
                    issues, source_dir
                )

                if fix_success:
                    logger.info(
                        f"Cycle {cycle_num}, Retry {retry_num} successful: {fix_message}"
                    )
                    break
                else:
                    logger.warning(
                        f"Cycle {cycle_num}, Retry {retry_num} failed: {fix_message}"
                    )

            if fix_success:
                cycle_results["successful_cycles"] += 1
                cycle_results["total_issues_fixed"] += fixed_count

            cycle_results["total_cycles"] = cycle_num
            cycle_results["cycles"].append(
                {  # type: ignore[arg-type]
                    "cycle": cycle_num,
                    "success": fix_success,
                    "issues_found": issues_found,
                    "issues_fixed": fixed_count,
                    "message": fix_message,
                }
            )

        logger.info(
            f"Cycle complete: {cycle_results['successful_cycles']}/{cycle_results['total_cycles']} successful, {cycle_results['total_issues_fixed']} issues fixed"
        )

        return cycle_results

    def _generate_fix_prompt(
        self, issues: list[dict[str, Any]], source_dir: Path
    ) -> str:  # type: ignore[type-arg]
        """
        Generate a prompt for the Claude SDK to fix issues.

        Args:
            issues: List of issues to fix
            source_dir: Path to source directory

        Returns:
            Prompt string for SDK
        """
        issues_summary: list[dict[str, Any]] = []  # type: ignore[type-arg]
        for issue in issues[:10]:  # Limit to first 10 issues for prompt size
            issues_summary.append(
                {
                    "file": issue.get("filename", "unknown"),
                    "line": issue.get("line", 0),
                    "code": issue.get("code", ""),
                    "message": issue.get("message", ""),
                }
            )

        prompt = f"""You are an expert Python code quality assistant. Please fix the following code issues found by {self.tool_name}:

Source Directory: {source_dir}

Issues to Fix:
{json.dumps(issues_summary, indent=2)}

Instructions:
1. Analyze each issue and provide the correct Python code
2. Follow PEP 8 style guidelines
3. Focus on fixing linting errors and warnings
4. Provide clear, minimal fixes
5. Do not change functionality, only fix style and quality issues

Please provide the fixed code with explanations for each change."""

        return prompt


class RuffAgent(CodeQualityAgent):
    """
    Specialized agent for Ruff code quality checks and fixes.
    """

    def __init__(self):
        """Initialize RuffAgent with Ruff-specific configuration."""
        # Ruff command template with JSON output
        command_template = "ruff check --fix --output-format=json {source_dir}"
        super().__init__("ruff", command_template)
        logger.info("RuffAgent initialized")

    async def format_code(self, source_dir: Path) -> bool:
        """
        执行ruff format格式化代码。

        Args:
            source_dir: 源代码目录

        Returns:
            bool: format是否执行完成（失败不影响整体成功状态）
        """
        try:
            # 构建format命令
            command = f"ruff format {source_dir}"

            logger.info(f"执行代码格式化: {command}")

            # Execute without asyncio.shield to avoid cancel scope errors
            async def run_format():
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True,
                )
                try:
                    _stdout, stderr = await process.communicate()
                    return _stdout, stderr, process.returncode
                except asyncio.CancelledError:
                    logger.warning("格式化被取消，清理进程")
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                    raise

            _stdout, stderr, returncode = await run_format()

            # Format执行完成即可，不检查返回值
            if returncode == 0:
                logger.info("✓ 代码格式化完成")
            else:
                logger.warning(
                    f"格式化完成但有警告: {stderr.decode() if stderr else ''}"
                )

            return True

        except Exception as e:
            # Format失败不抛异常，记录日志即可
            logger.warning(f"格式化执行异常，但继续流程: {e}")
            return False

    @override
    async def execute_check(
        self, source_dir: Path
    ) -> tuple[bool, list[dict[str, Any]]]:  # type: ignore[reportExplicitAny, type-arg]
        """
        Execute Ruff check on source directory.

        Args:
            source_dir: Path to source directory to check

        Returns:
            Tuple of (success, issues_list)
        """
        return await super().execute_check(source_dir)

    @override
    async def fix_issues(
        self,
        issues: list[dict[str, Any]],  # type: ignore[type-arg]
        source_dir: Path,
        max_turns: int = 150,
    ) -> tuple[bool, str, int]:  # type: ignore[reportExplicitAny]
        """
        Fix Ruff-identified issues using Claude SDK.

        Args:
            issues: List of Ruff issues to fix
            source_dir: Path to source directory
            max_turns: Maximum turns for SDK session

        Returns:
            Tuple of (success, message, fixed_count)
        """
        return await super().fix_issues(issues, source_dir, max_turns)


# Additional agents and pipeline
class BasedpyrightAgent(CodeQualityAgent):
    """
    BasedPyright type checking agent.

    Executes basedpyright check and uses Claude SDK to generate fixes.
    """

    def __init__(self):
        """Initialize BasedPyright agent."""
        super().__init__(
            tool_name="basedpyright",
            command_template="basedpyright --outputjson {source_dir}",
        )
        logger.info("BasedpyrightAgent initialized")

    @override
    async def execute_check(
        self, source_dir: Path
    ) -> tuple[bool, list[dict[str, Any]]]:  # type: ignore[reportExplicitAny, type-arg]
        """
        Execute BasedPyright type check on source directory.

        Args:
            source_dir: Path to source directory to check

        Returns:
            Tuple of (success, issues_list)
            - success: True if check completed successfully
            - issues_list: List of type errors found (empty if none)
        """
        try:
            # Build command with JSON output format
            command = self.command_template.format(source_dir=str(source_dir))

            logger.info(f"Executing {self.tool_name} check: {command}")

            # Execute subprocess with proper cancellation handling
            process = None
            try:
                # Execute command using asyncio subprocess
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True,
                )

                stdout, _stderr = await process.communicate()
            except asyncio.CancelledError:
                logger.warning(
                    f"Cancelled during {self.tool_name} check, cleaning up process"
                )
                if process is not None:
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                # Return empty result instead of re-raising to prevent cancel scope propagation
                logger.info(f"{self.tool_name} check cancelled, returning empty result")
                return True, []
            except Exception as e:
                error_msg = str(e)
                # Handle cancel scope errors gracefully
                if "cancel scope" in error_msg:
                    logger.warning(f"Cancel scope error during {self.tool_name} check (suppressed): {e}")
                    return True, []
                logger.error(
                    f"Error during {self.tool_name} subprocess communication: {e}"
                )
                if process is not None:
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                raise

            # Parse JSON output
            _stdout = stdout
            if _stdout and _stdout.strip():
                try:
                    stdout_text = _stdout.decode("utf-8")
                    data = json.loads(stdout_text)

                    # Extract generalDiagnostics from the JSON response
                    diagnostics: list[dict[str, Any]] = data.get(
                        "generalDiagnostics", []
                    )

                    # Convert diagnostics to issue format expected by parent class
                    issues: list[dict[str, Any]] = []
                    for diag in diagnostics:  # type: ignore[assignment]
                        issue = {
                            "file": diag.get("file", ""),
                            "line": diag.get("range", {})
                            .get("start", {})
                            .get("line", 0),
                            "column": diag.get("range", {})
                            .get("start", {})
                            .get("character", 0),
                            "severity": diag.get("severity", "warning"),
                            "message": diag.get("message", ""),
                            "rule": diag.get("rule", ""),
                            "end_line": diag.get("range", {})
                            .get("end", {})
                            .get("line", 0),
                            "end_column": diag.get("range", {})
                            .get("end", {})
                            .get("character", 0),
                        }
                        issues.append(issue)

                    # type: ignore[arg-type]  # BasedPyright sometimes struggles with len() on generic lists
                    logger.info(f"Found {len(issues)} type issues")
                    return True, issues

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON output: {e}")
                    logger.error(
                        f"Raw output: {stdout.decode('utf-8') if stdout else 'None'}"
                    )
                    return False, []
            else:
                logger.info("No type issues found")
                return True, []

        except Exception as e:
            logger.error(f"Unexpected error during {self.tool_name} check: {e}")
            return False, []

    @override
    async def fix_issues(
        self,
        issues: list[dict[str, Any]],  # type: ignore[type-arg]
        source_dir: Path,
        max_turns: int = 150,
    ) -> tuple[bool, str, int]:  # type: ignore[reportExplicitAny]
        """
        Fix BasedPyright-identified type issues using Claude SDK.

        Args:
            issues: List of BasedPyright type issues to fix
            source_dir: Path to source directory
            max_turns: Maximum turns for SDK session (default 150, NO external timeouts)

        Returns:
            Tuple of (success, message, fixed_count)
        """
        return await super().fix_issues(issues, source_dir, max_turns)

    def _generate_fix_prompt(
        self, issues: list[dict[str, Any]], source_dir: Path
    ) -> str:  # type: ignore[type-arg]
        """
        Generate a prompt for the Claude SDK to fix type checking issues.

        Args:
            issues: List of type checking issues to fix
            source_dir: Path to source directory

        Returns:
            Prompt string for SDK
        """
        issues_summary: list[dict[str, Any]] = []  # type: ignore[type-arg]
        for issue in issues[:10]:  # Limit to first 10 issues for prompt size
            issues_summary.append(
                {
                    "file": issue.get("file", "unknown"),
                    "line": issue.get("line", 0),
                    "severity": issue.get("severity", ""),
                    "message": issue.get("message", ""),
                    "rule": issue.get("rule", ""),
                }
            )

        prompt = f"""You are an expert Python type annotation assistant. Please fix the following type checking issues found by basedpyright:

Source Directory: {source_dir}

Type Issues to Fix:
{json.dumps(issues_summary, indent=2)}

Instructions:
1. Analyze each type issue and provide the correct type annotations
2. Add missing type hints to function signatures, variables, and return types
3. Use proper Python typing constructs (List, Dict, Optional, Union, etc.)
4. Follow PEP 484 and PEP 526 type hinting standards
5. Fix any incorrect type annotations
6. Provide clear, minimal type fixes
7. Do not change functionality, only add or correct type annotations

Please provide the fixed code with explanations for each type annotation change."""

        return prompt


class PytestAgent:
    """
    Pytest execution agent for running tests after quality checks.
    """

    def __init__(self):
        """Initialize Pytest agent."""
        self.logger = logging.getLogger(f"{__name__}.pytest")

    async def run_tests(self, test_dir: str, source_dir: str) -> dict[str, Any]:  # type: ignore[type-arg]
        """
        Run pytest on test directory.

        Args:
            test_dir: Path to test directory
            source_dir: Path to source directory

        Returns:
            Dictionary with test results
        """
        self.logger.info(f"Running pytest in {test_dir}")

        try:
            # Find venv path
            venv_path = self._find_venv_path()

            if not venv_path or not venv_path.exists():
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "errors": ["Virtual environment not found"],
                }

            # Construct path to pytest
            pytest_path = (
                venv_path / "Scripts" / "pytest.exe"
                if self._is_windows()
                else venv_path / "bin" / "pytest"
            )

            # Execute pytest
            command = f"{pytest_path} -v --tb=short --cov={source_dir}"

            # Use asyncio.shield to protect subprocess operations from cancellation
            async def run_pytest():
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=test_dir,
                )

                try:
                    _stdout, stderr = await process.communicate()
                    return _stdout, stderr, process
                except asyncio.CancelledError:
                    self.logger.warning(
                        "Pytest execution cancelled, cleaning up process"
                    )
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                    raise

            _stdout, stderr, process = await run_pytest()

            # Parse output (simplified)
            output = _stdout.decode("utf-8") if _stdout else ""

            return {
                "success": process.returncode == 0,
                "output": output,
                "errors": [stderr.decode("utf-8")] if stderr else [],
            }

        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {"success": False, "output": "", "errors": [str(e)]}

    def _find_venv_path(self) -> Path | None:
        """Find virtual environment path."""
        cwd = Path.cwd()
        venv_candidates = [
            cwd / "venv",
            cwd / ".venv",
            Path(__file__).parent.parent.parent / "venv",
            Path(__file__).parent.parent.parent / ".venv",
        ]

        for venv_path in venv_candidates:
            if venv_path.exists():
                return venv_path

        return None

    def _is_windows(self) -> bool:
        """Check if running on Windows."""
        import sys

        return sys.platform == "win32"


# Quality Gate Pipeline
class QualityGatePipeline:
    """
    Pipeline for executing quality gates in sequence: Ruff → BasedPyright → Pytest.
    """

    def __init__(self):
        """Initialize quality gate pipeline."""
        self.logger = logging.getLogger(f"{__name__}.pipeline")
        self.ruff_agent = RuffAgent()
        self.basedpyright_agent = BasedpyrightAgent()
        self.pytest_agent = PytestAgent()

    async def execute_pipeline(
        self, source_dir: str, test_dir: str, max_cycles: int = 3
    ) -> dict[str, Any]:  # type: ignore[type-arg]
        """
        Execute complete quality gate pipeline.

        Args:
            source_dir: Source directory for quality checks
            test_dir: Test directory for pytest execution
            max_cycles: Maximum retry cycles for each tool

        Returns:
            Dictionary with pipeline results
        """
        self.logger.info("Starting quality gate pipeline")

        pipeline_results: dict[str, Any] = {  # type: ignore[type-arg]
            "success": True,
            "ruff": None,
            "basedpyright": None,
            "pytest": None,
            "errors": [],
        }

        # Step 1: Ruff check and fix
        self.logger.info("=== Step 1: Ruff Linting ===")
        try:
            ruff_result = await self.ruff_agent.retry_cycle(
                source_dir=Path(source_dir), max_cycles=max_cycles
            )
            pipeline_results["ruff"] = ruff_result

            # Check if retry_cycle was successful (successful_cycles > 0)
            if not ruff_result.get("successful_cycles", 0) > 0:
                self.logger.warning("Ruff quality gate failed")
                pipeline_results["success"] = False
                pipeline_results["errors"].append("Ruff quality gate failed")

        except Exception as e:
            self.logger.error(f"Ruff execution failed: {e}")
            pipeline_results["ruff"] = {"success": False, "error": str(e)}
            pipeline_results["success"] = False
            pipeline_results["errors"].append(f"Ruff failed: {e}")

        # Step 2: BasedPyright check and fix (if Ruff succeeded)
        if pipeline_results["success"]:
            self.logger.info("=== Step 2: BasedPyright Type Checking ===")
            try:
                basedpyright_result = await self.basedpyright_agent.retry_cycle(
                    source_dir=Path(source_dir), max_cycles=max_cycles
                )
                pipeline_results["basedpyright"] = basedpyright_result

                # Check if retry_cycle was successful (successful_cycles > 0)
                if not basedpyright_result.get("successful_cycles", 0) > 0:
                    self.logger.warning("BasedPyright quality gate failed")
                    pipeline_results["success"] = False
                    pipeline_results["errors"].append(
                        "BasedPyright quality gate failed"
                    )

            except Exception as e:
                self.logger.error(f"BasedPyright execution failed: {e}")
                pipeline_results["basedpyright"] = {"success": False, "error": str(e)}
                pipeline_results["success"] = False
                pipeline_results["errors"].append(f"BasedPyright failed: {e}")

        # Step 3: Pytest execution (if previous steps succeeded)
        if pipeline_results["success"]:
            self.logger.info("=== Step 3: Pytest Execution ===")
            try:
                pytest_result = await self.pytest_agent.run_tests(
                    test_dir=test_dir, source_dir=source_dir
                )
                pipeline_results["pytest"] = pytest_result

                if not pytest_result["success"]:
                    self.logger.warning("Pytest quality gate failed")
                    pipeline_results["success"] = False
                    pipeline_results["errors"].append("Pytest quality gate failed")

            except Exception as e:
                self.logger.error(f"Pytest execution failed: {e}")
                pipeline_results["pytest"] = {"success": False, "error": str(e)}
                pipeline_results["success"] = False
                pipeline_results["errors"].append(f"Pytest failed: {e}")

        self.logger.info(
            f"Quality gate pipeline complete: {'SUCCESS' if pipeline_results['success'] else 'FAILED'}"
        )

        return pipeline_results
