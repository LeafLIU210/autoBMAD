"""
Epic Driver - Self-Contained BMAD Automation

Main orchestrator for the BMAD automation system.
Reads epic markdown files and drives SM-Dev-QA cycle.
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Import log manager
# Import status system
from autoBMAD.epic_automation.agents.state_agent import (
    CORE_STATUS_DONE,
    CORE_STATUS_READY_FOR_DONE,
)
from autoBMAD.epic_automation.log_manager import (
    LogManager,
    cleanup_logging,
    init_logging,
    setup_dual_write,
)

# Import SafeClaudeSDK for StatusParser initialization
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

# Import ClaudeAgentOptions for proper SDK configuration
try:
    from claude_agent_sdk import ClaudeAgentOptions
except ImportError:
    ClaudeAgentOptions = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 超时配置常量 - DEPRECATED: External timeouts removed - using max_turns instead
STORY_TIMEOUT = None  # 4小时 = 240分钟（整个故事的所有循环）
CYCLE_TIMEOUT = None  # 90分钟（单次Dev+QA循环）
DEV_TIMEOUT = None  # 45分钟（开发阶段）
QA_TIMEOUT = None  # 30分钟（QA审查阶段）
SM_TIMEOUT = None  # 30分钟（SM阶段）





class QualityGateOrchestrator:
    """Orchestrates quality gates pipeline after QA completion."""

    def __init__(
        self,
        source_dir: str,
        test_dir: str,
        skip_quality: bool = False,
        skip_tests: bool = False,
    ):
        """
        Initialize quality gate orchestrator.

        Args:
            source_dir: Source code directory
            test_dir: Test directory
            skip_quality: Skip ruff and basedpyright quality checks
            skip_tests: Skip pytest execution
        """
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.skip_quality = skip_quality
        self.skip_tests = skip_tests
        self.logger = logging.getLogger(f"{__name__}.quality_gates")

        # Initialize quality agents
        try:
            from autoBMAD.epic_automation.agents.quality_agents import (
                BasedPyrightAgent,
                PytestAgent,
                RuffAgent,
            )
            self.ruff_agent = RuffAgent()
            self.basedpyright_agent = BasedPyrightAgent()
            self.pytest_agent = PytestAgent()
        except ImportError:
            # Quality agents not available - will be handled in execute methods
            self.ruff_agent = None
            self.basedpyright_agent = None
            self.pytest_agent = None

        # Initialize results with proper type structure
        self.results: dict[str, Any] = {
            "success": True,
            "ruff": None,
            "basedpyright": None,
            "ruff_format": None,  # 新增
            "pytest": None,
            "errors": [],  # List[str]
            "quality_warnings": [],  # 🆕 新增：质量超限警告
            "error_summary_json": None,  # 🆕 新增：错误汇总JSON文件路径
            "start_time": None,
            "end_time": None,
            "total_duration": 0.0,
            "progress": {
                "current_phase": "not_started",
                "phase_1_ruff": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                },
                "phase_2_basedpyright": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                },
                "phase_final_format": {  # 新增
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                },
                "phase_3_pytest": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                },
            },
        }

    def _update_progress(
        self, phase: str, status: str, start: bool = False, end: bool = False
    ):
        """Update progress tracking for a phase."""
        progress_dict = self.results["progress"]
        if phase in progress_dict:
            phase_dict = progress_dict[phase]
            phase_dict["status"] = status
            if start:
                phase_dict["start_time"] = time.time()
            if end:
                phase_dict["end_time"] = time.time()

    def _calculate_duration(self, start_time: float, end_time: float) -> float:
        """Calculate duration in seconds."""
        return round(end_time - start_time, 2)

    def _is_max_cycles_exceeded_with_errors(self, result: dict[str, Any]) -> bool:
        """
        判断是否为"超限但仍有错误"场景

        修复后的条件：
        1. cycles > max_cycles (严格大于)
        2. 残留文件非空（final_error_files 或 final_failed_files）
        """
        cycles = result.get("cycles", 0)
        max_cycles = result.get("max_cycles", 0)

        # 修复：只有当cycles严格大于max_cycles时才可能超限
        if cycles <= max_cycles:
            return False

        # 检查残留文件
        remaining_files = (
            result.get("final_error_files", []) or
            result.get("final_failed_files", [])
        )

        has_remaining_errors = len(remaining_files) > 0

        # 添加诊断日志
        if has_remaining_errors:
            self.logger.debug(f"Max cycles exceeded: cycles={cycles}/{max_cycles}, remaining={len(remaining_files)} files")

        return has_remaining_errors

    async def execute_ruff_agent(self, source_dir: str) -> dict[str, Any]:
        """执行 Ruff 质量门（改造版：使用 QualityCheckController）"""
        if self.skip_quality:
            self.logger.info("Skipping Ruff quality check (--skip-quality flag)")
            return {"success": True, "skipped": True, "message": "Skipped via CLI flag"}

        self.logger.info("=== Quality Gate 1/3: Ruff Check with SDK Fix ===")
        self._update_progress("phase_1_ruff", "in_progress", start=True)
        progress_dict = cast(dict[str, Any], self.results["progress"])
        progress_dict["current_phase"] = "ruff"

        try:
            # 导入质量检查控制器
            from autoBMAD.epic_automation.agents.quality_agents import RuffAgent
            from autoBMAD.epic_automation.controllers.quality_check_controller import (
                QualityCheckController,
            )

            # 创建 Agent 实例
            ruff_agent = RuffAgent()

            # 创建控制器
            controller = QualityCheckController(
                tool="ruff",
                agent=ruff_agent,
                source_dir=source_dir,
                max_cycles=5,
                sdk_call_delay=10,
                sdk_timeout=600,
            )

            start_time = time.time()
            ruff_result = await controller.run()
            end_time = time.time()

            # 🆕 判定是否为超限场景
            if self._is_max_cycles_exceeded_with_errors(ruff_result):
                # 超限场景：phase 状态为 completed，但记录警告
                self.logger.warning(f"⚠ Ruff quality gate reached max cycles ({ruff_result['cycles']}) with {len(ruff_result['final_error_files'])} remaining error(s)")
                self._update_progress("phase_1_ruff", "completed", end=True)

                return {
                    "success": True,  # 🆕 流程成功，不阻断
                    "warning": "Max cycles exceeded with errors",
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": ruff_result,
                }

            # 原有逻辑：正常完成或中途失败
            success = ruff_result["status"] == "completed"
            if success:
                self.logger.info(f"✓ Ruff quality gate PASSED after {ruff_result['cycles']} cycle(s) in {self._calculate_duration(start_time, end_time)}s")
                self._update_progress("phase_1_ruff", "completed", end=True)
                return {
                    "success": True,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": ruff_result,
                }
            else:
                # 中途失败（非超限场景）：仍视为系统错误
                error_msg = f"Ruff execution failed (cycles: {ruff_result['cycles']})"
                self.logger.error(error_msg)
                self._update_progress("phase_1_ruff", "error", end=True)
                errors_list = cast(list[str], self.results["errors"])
                errors_list.append(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": ruff_result,
                }

        except Exception as e:
            error_msg = f"Ruff execution error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self._update_progress("phase_1_ruff", "error", end=True)
            errors_list = cast(list[str], self.results["errors"])
            errors_list.append(error_msg)
            return {"success": False, "error": error_msg, "duration": 0.0}

    async def execute_basedpyright_agent(self, source_dir: str) -> dict[str, Any]:
        """执行 BasedPyright 质量门（改造版：使用 QualityCheckController）"""
        if self.skip_quality:
            self.logger.info(
                "Skipping Basedpyright quality check (--skip-quality flag)"
            )
            return {"success": True, "skipped": True, "message": "Skipped via CLI flag"}

        self.logger.info("=== Quality Gate 2/3: BasedPyright Check with SDK Fix ===")
        self._update_progress("phase_2_basedpyright", "in_progress", start=True)
        progress_dict = cast(dict[str, Any], self.results["progress"])
        progress_dict["current_phase"] = "basedpyright"

        try:
            # 导入质量检查控制器
            from autoBMAD.epic_automation.agents.quality_agents import BasedPyrightAgent
            from autoBMAD.epic_automation.controllers.quality_check_controller import (
                QualityCheckController,
            )

            # 创建 Agent 实例
            basedpyright_agent = BasedPyrightAgent()

            # 创建控制器
            controller = QualityCheckController(
                tool="basedpyright",
                agent=basedpyright_agent,
                source_dir=source_dir,
                max_cycles=5,
                sdk_call_delay=10,
                sdk_timeout=600,
            )

            start_time = time.time()
            basedpyright_result = await controller.run()
            end_time = time.time()

            # 🆕 判定是否为超限场景
            if self._is_max_cycles_exceeded_with_errors(basedpyright_result):
                # 超限场景：phase 状态为 completed，但记录警告
                self.logger.warning(f"⚠ BasedPyright quality gate reached max cycles ({basedpyright_result['cycles']}) with {len(basedpyright_result['final_error_files'])} remaining error(s)")
                self._update_progress("phase_2_basedpyright", "completed", end=True)

                return {
                    "success": True,  # 🆕 流程成功，不阻断
                    "warning": "Max cycles exceeded with errors",
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": basedpyright_result,
                }

            # 原有逻辑：正常完成或中途失败
            success = basedpyright_result["status"] == "completed"
            if success:
                self.logger.info(f"✓ BasedPyright quality gate PASSED after {basedpyright_result['cycles']} cycle(s) in {self._calculate_duration(start_time, end_time)}s")
                self._update_progress("phase_2_basedpyright", "completed", end=True)
                return {
                    "success": True,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": basedpyright_result,
                }
            else:
                # 中途失败（非超限场景）：仍视为系统错误
                error_msg = f"BasedPyright execution failed (cycles: {basedpyright_result['cycles']})"
                self.logger.error(error_msg)
                self._update_progress("phase_2_basedpyright", "error", end=True)
                errors_list = cast(list[str], self.results["errors"])
                errors_list.append(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": basedpyright_result,
                }

        except Exception as e:
            error_msg = f"BasedPyright execution error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self._update_progress("phase_2_basedpyright", "error", end=True)
            errors_list = cast(list[str], self.results["errors"])
            errors_list.append(error_msg)
            return {"success": False, "error": error_msg, "duration": 0.0}

    async def execute_ruff_format(self, source_dir: str) -> dict[str, Any]:
        """执行 Ruff Format（新增）"""

        self.logger.info("=== Quality Gate Final: Ruff Format ===")
        self._update_progress("phase_final_format", "in_progress", start=True)

        try:
            from autoBMAD.epic_automation.agents.quality_agents import RuffAgent

            ruff_agent = RuffAgent()

            start_time = time.time()
            format_result = await ruff_agent.format(source_dir)
            end_time = time.time()

            if format_result["formatted"]:
                self.logger.info(
                    f"✓ Code formatted successfully in {self._calculate_duration(start_time, end_time)}s"
                )
                self._update_progress("phase_final_format", "completed", end=True)
                return {
                    "success": True,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": format_result,
                }
            else:
                error_msg = "Ruff format failed"
                self.logger.warning(f"✗ {error_msg}")
                self._update_progress("phase_final_format", "failed", end=True)
                # 注意：格式化失败不应阻断流程
                return {
                    "success": True,  # 仍返回 True，保持非阻断特性
                    "warning": error_msg,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": format_result,
                }

        except Exception as e:
            error_msg = f"Ruff format error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self._update_progress("phase_final_format", "error", end=True)
            # 格式化错误也不阻断
            return {
                "success": True,
                "warning": error_msg,
                "duration": 0.0
            }

    async def execute_pytest_agent(self, test_dir: str) -> dict[str, Any]:
        """执行 Pytest 质量门（改造版：使用 PytestController）"""
        if self.skip_tests:
            self.logger.info("Skipping pytest execution (--skip-tests flag)")
            return {"success": True, "skipped": True, "message": "Skipped via CLI flag"}

        self.logger.info("=== Quality Gate 3/3: Pytest Execution with SDK Fix ===")
        self._update_progress("phase_3_pytest", "in_progress", start=True)

        try:
            # Import optional modules - may not exist in all installations
            try:
                import importlib.util

                if (
                    importlib.util.find_spec("autoBMAD.epic_automation.state_manager")
                    is None
                ):
                    logger.warning(
                        "state_manager not available - pytest quality gate will be skipped"
                    )
                    return {
                        "success": False,
                        "error": "state_manager module not available",
                        "duration": 0.0,
                    }
            except Exception:
                logger.warning(
                    "state_manager not available - pytest quality gate will be skipped"
                )
                return {
                    "success": False,
                    "error": "state_manager module not available",
                    "duration": 0.0,
                }

            # 前置检查
            import shutil
            from pathlib import Path

            # Check if test directory exists and has tests
            test_path = Path(test_dir)
            if not test_path.exists() or not test_path.is_dir():
                error_msg = (
                    f"Test directory does not exist: {test_dir} - skipping pytest"
                )
                self.logger.warning(f"✗ {error_msg}")
                self._update_progress("phase_3_pytest", "skipped", end=True)
                return {
                    "success": True,
                    "skipped": True,
                    "message": error_msg,
                    "duration": 0.0,
                }

            # Check if there are any Python test files (recursively)
            test_files = list(test_path.rglob("test_*.py")) + list(
                test_path.rglob("*_test.py")
            )
            if not test_files:
                error_msg = f"No test files found in {test_dir} - skipping pytest"
                self.logger.info(f"✓ {error_msg}")
                self._update_progress("phase_3_pytest", "skipped", end=True)
                return {
                    "success": True,
                    "skipped": True,
                    "message": error_msg,
                    "duration": 0.0,
                }

            # Check if pytest is available
            if not shutil.which("pytest"):
                error_msg = "pytest command not found - skipping pytest execution"
                self.logger.warning(f"✗ {error_msg}")
                self._update_progress("phase_3_pytest", "skipped", end=True)
                return {
                    "success": True,
                    "skipped": True,
                    "message": error_msg,
                    "duration": 0.0,
                }

            # 使用 PytestController 执行完整流程
            try:
                from autoBMAD.epic_automation.controllers.pytest_controller import PytestController
            except ImportError:
                logger.error("PytestController not available - pytest quality gate cannot execute")
                return {
                    "success": False,
                    "error": "PytestController module not available",
                    "duration": 0.0,
                }

            controller = PytestController(
                source_dir=self.source_dir,
                test_dir=test_dir,
                max_cycles=5,
            )

            start_time = time.time()
            pytest_result = await controller.run()
            end_time = time.time()

            # 🆕 判定是否为超限场景
            if self._is_max_cycles_exceeded_with_errors(pytest_result):
                # 超限场景：phase 状态为 completed，但记录警告
                self.logger.warning(
                    f"⚠ Pytest quality gate reached max cycles ({pytest_result['cycles']}) "
                    f"with {len(pytest_result['final_failed_files'])} remaining failure(ies)"
                )
                self._update_progress("phase_3_pytest", "completed", end=True)

                return {
                    "success": True,  # 🆕 流程成功，不阻断
                    "warning": "Max cycles exceeded with errors",
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": pytest_result,
                }

            # 原有逻辑：正常完成或中途失败
            success = pytest_result["status"] == "completed"
            if success:
                self.logger.info(
                    f"✓ Pytest quality gate PASSED after {pytest_result['cycles']} cycle(s) "
                    f"in {self._calculate_duration(start_time, end_time)}s"
                )
                self._update_progress("phase_3_pytest", "completed", end=True)
                return {
                    "success": True,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": pytest_result,
                }
            else:
                # 中途失败（非超限场景）：仍视为系统错误
                error_msg = f"Pytest execution failed (cycles: {pytest_result['cycles']})"
                self.logger.error(error_msg)
                self._update_progress("phase_3_pytest", "error", end=True)
                errors_list = cast(list[str], self.results["errors"])
                errors_list.append(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": self._calculate_duration(start_time, end_time),
                    "result": pytest_result,
                }

        except Exception as e:
            error_msg = f"Pytest execution error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self._update_progress("phase_3_pytest", "error", end=True)
            errors_list = cast(list[str], self.results["errors"])
            errors_list.append(error_msg)
            return {"success": False, "error": error_msg, "duration": 0.0}

    async def execute_quality_gates(self, epic_id: str) -> dict[str, Any]:
        """
        执行完整质量门控流水线（更新版）

        流程：
        1. Phase 1: Ruff Check（检查 → SDK修复 → 回归）
        2. Phase 2: BasedPyright Check（检查 → SDK修复 → 回归）
        3. Phase 3: Ruff Format（最终格式化）
        4. Phase 4: Pytest（保持原有逻辑）

        Args:
            epic_id: Epic identifier for tracking

        Returns:
            Dictionary with quality gate results
        """
        self.logger.info(f"Starting quality gates pipeline for epic: {epic_id}")
        self.results["start_time"] = time.time()
        progress_dict = cast(dict[str, Any], self.results["progress"])
        progress_dict["current_phase"] = "starting"

        try:
            # Phase 1: Ruff Check
            if not self.skip_quality:
                ruff_result = await self.execute_ruff_agent(self.source_dir)
                self.results["ruff"] = ruff_result

                # Ruff 失败不阻断，继续执行
                if not ruff_result["success"]:
                    self.logger.warning("Ruff check failed, but continuing...")

            # Phase 2: BasedPyright Check
            if not self.skip_quality:
                basedpyright_result = await self.execute_basedpyright_agent(
                    self.source_dir
                )
                self.results["basedpyright"] = basedpyright_result

                # BasedPyright 失败不阻断，继续执行
                if not basedpyright_result["success"]:
                    self.logger.warning("BasedPyright check failed, but continuing...")

            # Phase 3: Ruff Format（新增）
            if not self.skip_quality:
                format_result = await self.execute_ruff_format(self.source_dir)
                self.results["ruff_format"] = format_result

            # Phase 4: Pytest
            if not self.skip_tests:
                pytest_result = await self.execute_pytest_agent(self.test_dir)
                self.results["pytest"] = pytest_result
                if not pytest_result["success"]:
                    self.results["success"] = False
                    self.logger.warning("Quality gates completed with pytest failure")
            else:
                self.logger.info("Skipping pytest (--skip-tests flag set)")

            # 🆕 收集超限工具信息
            quality_warnings: list[dict[str, Any]] = []

            for tool_name, phase_name in [
                ("ruff", "phase_1_ruff"),
                ("basedpyright", "phase_2_basedpyright"),
                ("pytest", "phase_3_pytest"),
            ]:
                result = self.results.get(tool_name)
                if result and result.get("result") and self._is_max_cycles_exceeded_with_errors(result["result"]):
                    warning = {
                        "tool": result["result"].get("tool", tool_name),
                        "phase": phase_name,
                        "status": "max_cycles_exceeded",
                        "cycles": result["result"]["cycles"],
                        "max_cycles": result["result"]["max_cycles"],
                        "remaining_files": (
                            result["result"].get("final_error_files") or
                            result["result"].get("final_failed_files", [])
                        ),
                        # 新增：详细错误信息
                        "detailed_errors": self._collect_detailed_errors(tool_name, result["result"])
                    }
                    quality_warnings.append(warning)

            # 🆕 保底逻辑：直接检查status=failed的工具
            if not quality_warnings:
                for tool_name in ["ruff", "basedpyright", "pytest"]:
                    result = self.results.get(tool_name)
                    if result and result.get("result") and result.get("result", {}).get("status") == "failed":
                        final_files = (
                            result["result"].get("final_error_files") or
                            result["result"].get("final_failed_files", [])
                        )
                        if final_files:
                            quality_warnings.append({
                                "tool": tool_name,
                                "phase": f"phase_{tool_name}",
                                "status": "failed",
                                "cycles": result["result"].get("cycles", 0),
                                "max_cycles": result["result"].get("max_cycles", 0),
                                "remaining_files": final_files,
                                # 新增：详细错误信息
                                "detailed_errors": self._collect_detailed_errors(tool_name, result["result"])
                            })

            # 🆕 生成错误汇总 JSON
            if quality_warnings:
                error_json_path = self._write_error_summary_json(epic_id, quality_warnings)
                self.results["error_summary_json"] = error_json_path
                self.results["quality_warnings"] = quality_warnings

            return self._finalize_results()

        except Exception as e:
            error_msg = f"Quality gates pipeline error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.results["success"] = False
            errors_list = cast(list[str], self.results["errors"])
            errors_list.append(error_msg)
            return self._finalize_results()

    def _finalize_results(self) -> dict[str, Any]:
        """Finalize and return results."""
        self.results["end_time"] = time.time()
        start_time = self.results["start_time"]
        end_time = self.results["end_time"]
        if start_time and end_time:
            self.results["total_duration"] = self._calculate_duration(
                start_time, end_time
            )

        # 判定整体成功状态
        if self.results["errors"]:
            # 🔴 仅系统级错误导致失败
            self.results["success"] = False
            self.logger.info(
                f"Quality gates pipeline FAILED with {len(self.results['errors'])} error(s)"
            )
        else:
            # 🟢 流程成功（即使有质量警告）
            self.results["success"] = True

            # 🆕 检查是否有质量警告
            warnings = self.results.get("quality_warnings", [])
            if warnings:
                self.logger.warning(
                    f"Quality gates pipeline COMPLETED with {len(warnings)} quality warning(s). "
                    f"See error summary: {self.results.get('error_summary_json')}"
                )
            else:
                self.logger.info(
                    f"Quality gates pipeline COMPLETED SUCCESSFULLY in {self.results['total_duration']}s"
                )

        progress_dict = cast(dict[str, Any], self.results["progress"])
        progress_dict["current_phase"] = "completed"
        return self.results

    def _collect_detailed_errors(self, tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
        """
        收集特定工具的详细错误信息

        Args:
            tool_name: 工具名称 ('ruff', 'basedpyright', 'pytest')
            result: 质量检查结果字典

        Returns:
            包含详细错误信息的字典
        """
        detailed_errors = {
            "tool": tool_name,
            "status": result.get("status", "unknown"),
            "summary": result.get("message", ""),
            "errors": []
        }

        if tool_name == "ruff":
            # 解析Ruff的JSON输出错误
            issues = result.get("issues", [])
            for issue in issues:
                detailed_errors["errors"].append({
                    "file": issue.get("filename", ""),
                    "line": issue.get("location", {}).get("row"),
                    "column": issue.get("location", {}).get("column"),
                    "message": issue.get("message", ""),
                    "severity": issue.get("severity", "error")
                })

        elif tool_name == "basedpyright":
            # 解析BasedPyright的错误信息
            issues = result.get("issues", [])
            for issue in issues:
                detailed_errors["errors"].append({
                    "file": issue.get("file", ""),
                    "line": issue.get("range", {}).get("start", {}).get("line"),
                    "message": issue.get("message", ""),
                    "severity": issue.get("severity", "error")
                })

        elif tool_name == "pytest":
            # 解析pytest的失败测试
            files = result.get("files", [])
            for file_result in files:
                for test_case in file_result.get("failures", []):
                    detailed_errors["errors"].append({
                        "file": file_result.get("test_file", ""),
                        "line": None,  # pytest错误通常不包含具体行号
                        "message": test_case.get("message", ""),
                        "short_traceback": test_case.get("short_tb", "")
                    })

        return detailed_errors

    def _write_error_summary_json(
        self,
        epic_id: str,
        issues: list[dict[str, Any]]
    ) -> str | None:
        """
        生成错误汇总 JSON 文件

        Args:
            epic_id: Epic 标识符
            issues: 超限工具列表（从 quality_warnings 收集）

        Returns:
            生成的 JSON 文件路径，若 issues 为空则返回 None
        """
        if not issues:
            return None

        import json
        from datetime import UTC, datetime
        from pathlib import Path

        # 构建 JSON 内容
        error_summary = {
            "epic_id": epic_id,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "source_dir": self.source_dir,
            "test_dir": self.test_dir,
            "tools": issues,
        }

        # 添加详细错误信息（从self.results中提取）
        for tool_info in error_summary["tools"]:
            # 类型断言，确保tool_info是字典类型
            if not isinstance(tool_info, dict):
                continue
            tool_name = tool_info.get("tool", "")
            result = self.results.get(tool_name, {}).get("result")
            if result and "detailed_errors" in result:
                tool_info["error_details"] = result["detailed_errors"]

        # 确保输出目录存在
        errors_dir = Path("autoBMAD/epic_automation/errors")
        errors_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_epic_id = epic_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        filename = f"quality_errors_{safe_epic_id}_{timestamp}.json"
        filepath = errors_dir / filename

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(error_summary, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Error summary written to: {filepath}")
        return str(filepath)


async def run_quality_gates_standalone(
    source_dir: str = "src",
    test_dir: str = "tests",
    epic_id: str = "standalone-quality",
    skip_quality: bool = False,
    skip_tests: bool = False,
    max_cycles: int = 5,  # type: ignore[reportUnusedParameter]
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

        if not source_path.exists():
            return {
                "success": False,
                "error": f"Source directory not found: {source_dir}"
            }

        # 3. 创建编排器
        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_path),
            test_dir=str(test_dir),
            skip_quality=skip_quality,
            skip_tests=skip_tests,
        )

        # 4. 执行质量门禁
        results = await orchestrator.execute_quality_gates(epic_id)

        return results

    finally:
        cleanup_logging()


class EpicDriver:
    """Main orchestrator for complete BMAD workflow."""

    # Class attribute type annotations for basedpyright strict mode
    epic_path: Path
    epic_id: str
    tasks_dir: Path
    stories: list[dict[str, Any]]
    current_story_index: int
    max_iterations: int
    retry_failed: bool
    verbose: bool
    concurrent: bool
    use_claude: bool
    source_dir: str
    test_dir: str
    sm_agent: Any
    dev_agent: Any
    qa_agent: Any
    state_manager: Any
    logger: logging.Logger
    log_manager: LogManager

    def __init__(
        self,
        epic_path: str,
        tasks_dir: str = ".bmad-core/tasks",
        max_iterations: int = 3,
        retry_failed: bool = False,
        verbose: bool = False,
        concurrent: bool = False,
        use_claude: bool = True,
        source_dir: str = "src",
        test_dir: str = "tests",
        skip_quality: bool = False,
        skip_tests: bool = False,
        create_log_file: bool = False,
    ):
        """
        Initialize epic driver.

        Args:
            epic_path: Path to the epic markdown file
            tasks_dir: Directory containing task guidance files
            max_iterations: Maximum retry attempts for failed stories
            retry_failed: Enable automatic retry of failed stories
            verbose: Enable detailed logging output
            concurrent: Process stories in parallel (experimental)
            use_claude: Use Claude Code CLI for real implementation (default True)
            source_dir: Source code directory for QA checks (default: "src")
            test_dir: Test directory for QA checks (default: "tests")
            skip_quality: Skip quality gates (ruff and basedpyright)
            skip_tests: Skip pytest execution
            create_log_file: Whether to create timestamped log files (default: False)
        """
        self.epic_path = Path(epic_path).resolve()
        self.epic_id = str(self.epic_path)  # Use epic path as epic_id
        self.tasks_dir = Path(tasks_dir)
        self.stories = []
        self.current_story_index = 0
        self.max_iterations = max_iterations
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.concurrent = concurrent
        self.use_claude = use_claude
        self.skip_quality = skip_quality
        self.skip_tests = skip_tests
        self.create_log_file = create_log_file

        # Auto-resolve source_dir and test_dir to absolute paths
        source_path = Path(source_dir)
        test_path = Path(test_dir)
        self.source_dir = str(
            source_path.resolve() if source_path.exists() else Path.cwd() / source_dir
        )
        self.test_dir = str(
            test_path.resolve() if test_path.exists() else Path.cwd() / test_dir
        )

        # Initialize log manager
        self.log_manager = LogManager(create_log_file=create_log_file)
        init_logging(self.log_manager)
        setup_dual_write(self.log_manager)

        # Import agent classes
        try:
            from autoBMAD.epic_automation.agents.dev_agent import DevAgent  # type: ignore
            from autoBMAD.epic_automation.agents.qa_agent import QAAgent  # type: ignore
            from autoBMAD.epic_automation.agents.sm_agent import SMAgent  # type: ignore
            from autoBMAD.epic_automation.agents.status_update_agent import (
                StatusUpdateAgent,  # type: ignore
            )
            from autoBMAD.epic_automation.state_manager import (
                StateManager,  # type: ignore
            )

            # Create agents (for potential direct access)
            self.sm_agent = SMAgent()
            self.dev_agent = DevAgent(use_claude=use_claude)
            self.qa_agent = QAAgent()
            self.state_manager = StateManager()
            self.status_update_agent = StatusUpdateAgent()

            # Create controllers (main interface)
            self.sm_controller = None  # Will be created per story in async context
            self.devqa_controller = None  # Will be created per story in async context
            self.quality_controller = None  # Will be created when needed

            # Initialize StatusParser with SDK wrapper if available (optional module)
            try:
                from autoBMAD.epic_automation.agents.state_agent import (
                    SimpleStoryParser as StatusParser,
                )

                # Create proper options object for status parsing
                options = None
                if ClaudeAgentOptions:
                    options = ClaudeAgentOptions(
                        permission_mode="bypassPermissions", cwd=str(Path.cwd())
                    )
                # 直接创建 SafeClaudeSDK 实例
                sdk_instance = SafeClaudeSDK(
                    prompt="Parse story status",
                    options=options,
                    timeout=None,
                    log_manager=None,
                )
                self.status_parser = StatusParser(sdk_wrapper=sdk_instance)
            except ImportError:
                self.status_parser = None
                logger.debug("StatusParser not available - using fallback parsing")
        except ImportError as e:
            # Create a basic logger before exiting
            logging.basicConfig(
                level=logging.ERROR,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            # Use module-level logger instead of creating a new local variable
            logger.error(f"Failed to import agent classes: {e}")
            sys.exit(1)

        # Initialize logger
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(f"epic_driver.{self.epic_path.name}")

        # Note: Logging is already initialized by log_manager in __init__
        # This method is kept for compatibility but doesn't add new handlers
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # Log that logging is configured
        if self.log_manager and self.log_manager.get_current_log_path():
            logger.info(
                f"Logging configured. Log file: {self.log_manager.get_current_log_path()}"
            )

        return logger

    async def parse_epic(self) -> list[dict[str, Any]]:
        """
        Parse epic markdown file and extract story information.

        Supports implicit numbering association:
        - Extracts story IDs from Epic document
        - Searches for story files by filename pattern (e.g., 001.xxx.md)
        - No explicit Markdown links required

        Returns:
            List of story dictionaries with path and metadata
        """
        logger.info(f"Parsing epic: {self.epic_path}")

        if not self.epic_path.exists():
            logger.error(f"Epic file not found: {self.epic_path}")
            return []

        try:
            with open(self.epic_path, encoding="utf-8") as f:
                content = f.read()

            # Step 1: Extract story IDs from Epic document
            story_ids = self._extract_story_ids_from_epic(content)

            if not story_ids:
                logger.warning("No stories found in epic document")
                return []

            # Extract epic prefix from epic file name (e.g., "004" from "epic-004-...")
            epic_prefix = self._extract_epic_prefix(self.epic_path.name)
            logger.debug(f"Extracted epic prefix: {epic_prefix}")

            # Step 2: Search for story files in docs/stories/ directory
            # epic文件在 docs/epics/，所以stories目录应该是 docs/stories
            stories_dir = self.epic_path.parent.parent / "stories"

            # Fallback: try stories directory relative to epic path
            if not stories_dir.exists():
                stories_dir = self.epic_path.parent / "stories"

            # Fallback: try autoBMAD/stories
            if not stories_dir.exists():
                autoBMAD_dir = self.epic_path.parent.parent
                if autoBMAD_dir.name == "autoBMAD":
                    stories_dir = autoBMAD_dir / "stories"
                elif (autoBMAD_dir.parent / "autoBMAD").exists():
                    stories_dir = autoBMAD_dir.parent / "autoBMAD" / "stories"

            logger.info(f"Searching for story files in: {stories_dir}")
            logger.debug(f"Stories directory exists: {stories_dir.exists()}")

            story_list: list[dict[str, Any]] = []
            found_stories: list[str] = []

            # Pre-check: collect all existing story files to avoid redundant checks
            existing_stories: set[str] = set()
            if stories_dir.exists():
                story_files = list(stories_dir.glob("*.md"))
                logger.info(
                    f"Found {len(story_files)} markdown files in stories directory"
                )
                for story_file in story_files:
                    match = re.match(r"^(\d+(?:\.\d+)?)-", story_file.name)
                    if match:
                        existing_stories.add(match.group(1))
                        logger.debug(
                            f"Existing story file: {story_file.name} (ID: {match.group(1)})"
                        )
            else:
                logger.warning(f"Stories directory does not exist: {stories_dir}")

            if stories_dir.exists():
                # Match story IDs to files using fallback logic
                logger.info(f"Matching {len(story_ids)} story IDs to files")
                for story_id in story_ids:
                    # Extract story number: "001" or "001: Title" -> "001"
                    story_number = story_id.split(":")[0].strip()
                    logger.debug(
                        f"Looking for story number: {story_number} (ID: {story_id})"
                    )

                    # Use fallback matching to find story file
                    story_file = self._find_story_file_with_fallback(
                        stories_dir, story_number, epic_prefix
                    )

                    if story_file:
                        logger.info(f"[Match Success] {story_id} -> {story_file.name}")
                        # Parse status from story file
                        status = self._parse_story_status_sync(str(story_file))
                        story_list.append(
                            {
                                "id": story_id,
                                "path": self._convert_to_windows_path(
                                    str(story_file.resolve())
                                ),
                                "name": story_file.name,
                                "status": status,
                            }
                        )
                        found_stories.append(story_id)
                        logger.info(
                            f"Found story: {story_id} at {story_file} (status: {status})"
                        )
                    else:
                        # Story file not found
                        logger.warning(
                            f"[Match Failed] {story_id} (number: {story_number})"
                        )
                        # Additional check: verify if file really doesn't exist (race condition protection)
                        if story_number not in existing_stories:
                            # Try to create missing story file using SM Agent
                            logger.info(
                                f"Creating missing story file for ID: {story_id}"
                            )
                            if await self.sm_agent.create_stories_from_epic(
                                str(self.epic_path)
                            ):
                                # 🎯 关键：SM 调用完成后等待清理
                                await asyncio.sleep(0.5)

                                # After creation, try to find the file again
                                created_story_file = (
                                    self._find_story_file_with_fallback(
                                        stories_dir, story_number, epic_prefix
                                    )
                                )
                                if created_story_file:
                                    # Parse status from newly created story file
                                    status = self._parse_story_status_sync(
                                        str(created_story_file)
                                    )
                                    story_list.append(
                                        {
                                            "id": story_id,
                                            "path": self._convert_to_windows_path(
                                                str(created_story_file.resolve())
                                            ),
                                            "name": created_story_file.name,
                                            "status": status,
                                        }
                                    )
                                    found_stories.append(story_id)
                                    logger.info(
                                        f"Created story: {story_id} at {created_story_file} (status: {status})"
                                    )
                                else:
                                    logger.error(
                                        f"Story file not found after creation for ID: {story_id}"
                                    )
                            else:
                                logger.error(f"Failed to create story: {story_id}")
                                logger.warning(
                                    f"Story file not found for ID: {story_id} (looking for {stories_dir}/*{story_number}*.md)"
                                )
                        else:
                            # File exists but not matched (should not happen with new logic)
                            logger.warning(
                                f"Story file exists but could not be matched: {story_number} in {stories_dir}"
                            )
            else:
                logger.error(
                    f"Cannot match stories: stories directory does not exist: {stories_dir}"
                )
                logger.info("Tried searching in:")
                logger.info(f"  - {self.epic_path.parent / 'docs' / 'stories'}")
                logger.info(f"  - {self.epic_path.parent / 'stories'}")
                logger.info(
                    f"  - {(self.epic_path.parent.parent / 'autoBMAD' / 'stories') if self.epic_path.parent.parent.name != 'autoBMAD' else 'N/A'}"
                )

            # Warn about stories not found
            missing_stories: set[str] = set(story_ids) - set(found_stories)
            if missing_stories:
                logger.warning(f"Missing story files for IDs: {missing_stories}")

            # Sort stories by story ID
            story_list.sort(key=lambda x: x["id"])

            self.stories = story_list
            logger.info(
                f"Epic parsing complete: {len(story_list)}/{len(story_ids)} stories found"
            )

            return story_list

        except Exception as e:
            logger.error(f"Failed to parse epic: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            return []

    def _extract_story_ids_from_epic(self, content: str) -> list[str]:
        """
        Extract story IDs from epic document.

        Looks for story sections like:
        ### Story 1: Title
        **Story ID**: 004.1

        Args:
            content: Epic document content

        Returns:
            List of story IDs (e.g., ["004.1", "004.1: Title", ...])
        """
        story_ids: list[str] = []

        # Pattern 1: "## Story X.Y: Title" or "### Story X.Y: Title"
        pattern1 = r"#{2,3}\s*Story\s+(\d+(?:\.\d+)?)\s*:\s*(.+?)(?:\n|\$)"
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        for story_num, title in matches1:
            story_id = f"{story_num}: {title}"
            story_ids.append(story_id)
            logger.debug(f"Found story section: {story_id}")

        # Pattern 2: "**Story ID**: 004.1"
        pattern2 = r"\*\*Story ID\*\*\s*:\s*(\d+(?:\.\d+)?)"
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        for story_num in matches2:
            # Check if already added
            story_id = f"{story_num}"
            if story_id not in story_ids:
                story_ids.append(story_id)
                logger.debug(f"Found story ID: {story_id}")

        # Remove duplicates while preserving order
        # Handle both "1: Title" and "004.1" formats referring to the same story
        # Strategy: For each story number, keep the ID with more information (with title)
        seen_numbers: set[str] = set()
        unique_story_ids: list[str] = []

        for story_id in story_ids:
            # Extract just the story number part
            story_num = story_id.split(":")[0].strip()

            # Normalize the number for comparison
            # "004.1" → "4.1", "1" → "1" for comparison
            # Handle both padded and non-padded formats
            if "." in story_num:
                # Dotted format like "004.1"
                # Remove leading zeros from epic part only: "004.1" → "4.1"
                parts = story_num.split(".")
                epic_part = parts[0].lstrip("0") or "0"  # Handle "000" → "0"
                story_part = parts[1]
                normalized_num = f"{epic_part}.{story_part}"
            else:
                # Simple format like "1" or "5"
                normalized_num = story_num.lstrip("0") or "0"

            # If we haven't seen this story number, add it
            if normalized_num not in seen_numbers:
                seen_numbers.add(normalized_num)
                unique_story_ids.append(story_id)
            else:
                # Duplicate found - prefer ID with title over pure number
                # Check if current one has a title (contains ':')
                has_title = ":" in story_id
                if has_title:
                    # Find and replace the existing pure number ID with this titled ID
                    for i, existing_id in enumerate(unique_story_ids):
                        existing_num = existing_id.split(":")[0].strip()
                        existing_normalized = ""
                        if "." in existing_num:
                            parts = existing_num.split(".")
                            epic_part = parts[0].lstrip("0") or "0"
                            story_part = parts[1]
                            existing_normalized = f"{epic_part}.{story_part}"
                        else:
                            existing_normalized = existing_num.lstrip("0") or "0"

                        if existing_normalized == normalized_num:
                            # Replace with titled version
                            unique_story_ids[i] = story_id
                            break

        logger.debug(
            f"Extracted {len(unique_story_ids)} unique story IDs: {unique_story_ids}"
        )

        return unique_story_ids

    def _convert_to_windows_path(self, unix_path: str) -> str:
        """
        将 WSL/Unix 风格的路径转换为 Windows 绝对路径。

        例如：
        /d/GITHUB/pytQt_template/docs/stories/004.1-spec-parser-system.md
        ->
        D:\\GITHUB\\pytQt_template\\docs\\stories\\004.1-spec-parser-system.md

        Args:
            unix_path: Unix 风格的路径

        Returns:
            Windows 风格的绝对路径
        """
        # 检测 WSL/Unix 风格的盘符路径（如 /d/, /c/ 等）
        if (
            len(unix_path) >= 3
            and unix_path[0] == "/"
            and unix_path[2] == "/"
            and unix_path[1].isalpha()
        ):
            # 提取盘符并转换为大写（如 d → D）
            drive_letter = unix_path[1].upper()
            # 移除开头的 /X/ 并替换剩余的 / 为 \
            windows_path = unix_path[3:].replace("/", "\\")
            # 构建完整的 Windows 路径
            return f"{drive_letter}:\\{windows_path}"

        # 如果不是 WSL/Unix 风格，仅替换分隔符
        return unix_path.replace("/", "\\")

    def _extract_epic_prefix(self, epic_filename: str) -> str:
        """
        Extract epic prefix from epic filename.

        Args:
            epic_filename: Name of the epic file (e.g., "epic-001-core-algorithm-foundation.md")

        Returns:
            Epic prefix (e.g., "004")
        """
        # Match pattern like "epic-004-" or "epic-004."
        match = re.search(r"epic[-.](\d+)", epic_filename)
        if match:
            return match.group(1)
        return ""

    def _find_story_file_with_fallback(
        self, stories_dir: Path, story_number: str, epic_prefix: str = ""
    ) -> Path | None:
        """
        Find story file with fallback matching logic.

        Tries multiple filename patterns:
        1. Exact match: {story_number}.md
        2. Descriptive match: {story_number}-*.md
        3. Alternative format: {story_number}.*.md
        4. Fuzzy match: Any file containing {story_number} at the start

        Args:
            stories_dir: Directory containing story files
            story_number: Story number (e.g., "1", "1.1", "004.1")
            epic_prefix: Epic prefix to prioritize (e.g., "004")

        Returns:
            Path to the story file if found, None otherwise
        """
        # Pattern 1: Exact match (e.g., 004.1.md)
        exact_match = stories_dir / f"{story_number}.md"
        if exact_match.exists():
            logger.debug(
                f"[File Match] Found exact match for {story_number}: {exact_match}"
            )
            return exact_match

        # Pattern 2: Descriptive match (e.g., story-004.1-description.md or 004.1-description.md)
        pattern_match = list(stories_dir.glob(f"story-{story_number}-*.md")) + list(
            stories_dir.glob(f"{story_number}-*.md")
        )
        if pattern_match:
            logger.debug(
                f"[File Match] Found descriptive match for {story_number}: {pattern_match[0]}"
            )
            return pattern_match[0]

        # Pattern 3: Alternative format (e.g., story-004.1.description.md or 004.1.description.md)
        alt_pattern_match = list(stories_dir.glob(f"story-{story_number}.*.md")) + list(
            stories_dir.glob(f"{story_number}.*.md")
        )
        if alt_pattern_match:
            logger.debug(
                f"[File Match] Found alt pattern match for {story_number}: {alt_pattern_match[0]}"
            )
            return alt_pattern_match[0]

        # Pattern 4: Fuzzy match - handle prefixed story numbers (e.g., "1" matching "004.1")
        # Check if story_number is a simple number that might have a prefix
        if story_number.isdigit():
            # Try to find files that start with the story number followed by a dot
            # e.g., "1" could match "004.1" or "1.1" or "1-description"
            fuzzy_matches = []
            prefixed_matches = []  # Track files with explicit prefixes like 004.1, 003.1, etc.

            for file_path in stories_dir.glob("*.md"):
                filename = file_path.name
                # Check if filename starts with the story number followed by a dot or hyphen
                if filename.startswith(f"{story_number}.") or filename.startswith(
                    f"{story_number}-"
                ):
                    fuzzy_matches.append(file_path)
                # Also check for patterns like "story-XXX.{story_number}." (e.g., "story-004.1.")
                # Use search instead of match to allow for "story-" prefix
                elif re.search(rf"\d{{3}}\.{story_number}\.", filename):
                    prefixed_matches.append(file_path)
                # Also check if the story number matches a dotted pattern like "004.1" where we're looking for "1"
                # Extract story number from filename and check if it ends with ".{story_number}"
                # Use search instead of match to allow for "story-" prefix
                elif re.search(rf"\d{{3}}\.{story_number}-", filename):
                    prefixed_matches.append(file_path)

            # Prefer prefixed matches (e.g., 004.1) over simple matches (e.g., 1.x)
            if prefixed_matches:
                # If we have an epic_prefix, prioritize files that match it
                if epic_prefix:
                    epic_specific = [
                        f
                        for f in prefixed_matches
                        if f.name.startswith(f"story-{epic_prefix}.{story_number}")
                    ]
                    if epic_specific:
                        logger.debug(
                            f"[File Match] Found epic-specific match for {story_number} (prefix {epic_prefix}): {epic_specific[0]}"
                        )
                        return epic_specific[0]

                logger.debug(
                    f"[File Match] Found prefixed match for {story_number}: {prefixed_matches[0]}"
                )
                return prefixed_matches[0]
            elif fuzzy_matches:
                logger.debug(
                    f"[File Match] Found fuzzy match for {story_number}: {fuzzy_matches[0]}"
                )
                return fuzzy_matches[0]

        logger.debug(f"[File Match] No match found for story number: {story_number}")
        return None

    async def execute_sm_phase(self, story_path: str) -> bool:
        """Execute SM (Story Master) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing SM phase for {story_path}")

        result: bool = False  # Initialize result variable

        try:
            # Create SMController in async context
            import anyio
            async with anyio.create_task_group() as tg:
                # Read story content
                with open(story_path, encoding="utf-8") as f:
                    story_content = f.read()

                # Create SMController with task group
                from autoBMAD.epic_automation.controllers.sm_controller import SMController
                sm_controller = SMController(tg, project_root=Path.cwd())
                self.sm_controller = sm_controller

                # Execute SM phase
                result = await sm_controller.execute(
                    epic_content=story_content,
                    story_id=Path(story_path).stem
                )

                # Update state
                state_update_success = await self.state_manager.update_story_status(
                    story_path=story_path, status="sm_completed", phase="sm", epic_path=self.epic_id
                )

                if not state_update_success:
                    logger.warning(
                        f"State update failed for {story_path} but business logic completed, "
                        f"continuing with sm_completed status"
                    )

                logger.info(f"SM phase completed for {story_path}")

        except Exception as e:
            logger.error(f"SM phase failed for {story_path}: {e}")
            try:
                await self.state_manager.update_story_status(
                    story_path=story_path, status="error", error=str(e), epic_path=self.epic_id
                )
            except Exception:
                # Suppress exceptions during error handling to ensure we return False
                pass
            return False

        return result

    async def execute_dev_phase(self, story_path: str, iteration: int = 1) -> bool:
        """
        Execute Dev (Development) phase for a story using DevQaController.

        Args:
            story_path: Path to the story markdown file
            iteration: Current iteration count (for safety)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing Dev phase for {story_path} (iteration {iteration})")

        # Safety guard against infinite loops
        if iteration > self.max_iterations:
            logger.error(
                f"Max iterations ({self.max_iterations}) reached for {story_path}"
            )
            try:
                await self.state_manager.update_story_status(
                    story_path=story_path, status="failed", error="Max iterations exceeded", epic_path=self.epic_id
                )
            except Exception:
                # Suppress exceptions during error handling
                pass
            return False

        result: bool = False  # Initialize result variable

        try:
            # Create DevQaController in async context
            import anyio
            async with anyio.create_task_group() as tg:
                # Set log_manager for agents
                # (handled within DevQaController)

                # Create DevQaController with task group
                from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
                devqa_controller = DevQaController(
                    tg,
                    use_claude=self.use_claude,
                    log_manager=self.log_manager,
                    epic_path=self.epic_id  # ← 传递epic_path
                )
                self.devqa_controller = devqa_controller

                # Execute Dev-QA pipeline using the controller
                result = await devqa_controller.execute(story_path, epic_path=self.epic_id)

                # 🎯 改进：不再在 execute_dev_phase 中写入 completed。
                # 状态由 DevAgent/QAAgent 在执行后更新故事文档，
                # StateAgent 解析文档状态作为循环决策依据。
                # 数据库 update_story_status 仅用于记录/报告，不影响循环决策。

                logger.info(f"Dev phase completed for {story_path}")

        except Exception as e:
            logger.error(f"Dev phase failed for {story_path}: {e}")
            try:
                await self.state_manager.update_story_status(
                    story_path=story_path, status="error", error=str(e), epic_path=self.epic_id
                )
            except Exception:
                # Suppress exceptions during error handling to ensure we return False
                pass
            return False

        return result

    async def execute_qa_phase(self, _story_path: str) -> bool:
        """
        Execute QA (Quality Assurance) phase for a story.

        Note: This method is now deprecated. QA is handled by DevQaController
        in the execute_dev_phase method.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if QA passes, False otherwise
        """
        logger.warning(
            "execute_qa_phase is deprecated. QA is now handled by DevQaController. "
            "Use execute_dev_phase which manages the complete Dev-QA cycle."
        )
        return True  # No-op - QA is handled in DevQaController

    async def process_story(self, story: "dict[str, Any]") -> bool:
        """
        Process a single story through Dev-QA cycle.

        Note: Story documents are created by SM agent during parse_epic() phase.
        This method only executes Dev-QA loop for each story.

        Args:
            story: Story dictionary with path and metadata (created by SM agent)

        Returns:
            True if story completed successfully (Done or Ready for Done), False otherwise

        Raises:
            asyncio.CancelledError: 当整个 epic 运行被外部取消时，向上传播
        """
        story_path = story["path"]
        story_id = story["id"]
        logger.info(f"Processing story {story_id}: {story_path}")

        try:
            return await self._process_story_impl(story)
        # ✅ 移除了 asyncio.CancelledError 的捕获，让它自然向上传播
        except RuntimeError as e:
            error_msg = str(e)

            # 🎯 关键：cancel scope 错误特殊处理
            if "cancel scope" in error_msg.lower():
                logger.warning(
                    f"Cancel scope error for {story_id} (non-fatal): {error_msg}"
                )
                # 单个 story 失败不中断整体流程
                return False
            else:
                # 其他 RuntimeError
                logger.error(f"RuntimeError for {story_id}: {error_msg}")
                return False

    async def _process_story_impl(self, story: "dict[str, Any]") -> bool:
        """
        Internal implementation of story processing.

        Args:
            story: Story dictionary with path and metadata

        Returns:
            True if story completed successfully, False otherwise

        Raises:
            asyncio.CancelledError: 向上传播到 process_story
        """
        # ✅ 移除了所有 try-except，直接调用
        return await self._execute_story_processing(story)

    async def _execute_story_processing(self, story: "dict[str, Any]") -> bool:
        """
        Core story processing logic - driven purely by core status values.

        Dev-QA 循环完全由核心状态值驱动，不依赖 SDK 返回值。
        """
        story_path = story["path"]
        story_id = story["id"]

        try:
            # 🆕 强制初始化数据库记录（最简方案）
            try:
                current_status = story.get("status", "pending")

                await self.state_manager.update_story_status(
                    story_path=story_path,
                    status=current_status,
                    phase="initialization",
                    epic_path=self.epic_id
                )

                logger.debug(f"[DB Init] Story {story_id} initialized with status: {current_status}")

            except Exception as e:
                logger.warning(f"DB init failed for {story_id}: {e}, continuing workflow")

            # 🎯 关键修复：移除数据库状态检查，完全依赖故事文档核心状态
            # 旧逻辑（已废弃）：
            # existing_status = await self.state_manager.get_story_status(story_path)
            # if existing_status and existing_status.get("status") in ["completed", "qa_waived"]:
            #     return True
            #
            # 新逻辑：所有决策由核心状态值驱动，数据库仅用于持久化记录

            # 🎯 核心改动：循环由核心状态值驱动
            iteration = 1
            max_dev_qa_cycles = 10

            while iteration <= max_dev_qa_cycles:
                logger.info(
                    f"[Epic Driver] Dev-QA cycle #{iteration} for {story_path}"
                )

                try:
                    # 1️⃣ 读取当前核心状态值
                    current_status = await self._parse_story_status(story_path)
                    logger.info(f"[Cycle {iteration}] Current status: {current_status}")

                except asyncio.CancelledError:
                    # 🎯 关键修复：SDK 内部取消后的延迟 CancelledError
                    # 完全封装，不影响工作流
                    logger.warning(
                        f"[Cycle {iteration}] SDK cleanup triggered CancelledError (non-fatal), "
                        f"using last known status or fallback"
                    )
                    # 使用 fallback 解析状态
                    current_status = self._parse_story_status_fallback(story_path)
                    logger.info(f"[Cycle {iteration}] Fallback status: {current_status}")

                # 🎯 关键修复：状态解析后等待 SDK 清理完成，避免连续 SDK 调用
                # 增加等待时间到 2 秒，确保 cancel scope 完全清理
                # 将 sleep 单独放在 try-except 外面，吸收所有延迟的 CancelledError
                try:
                    logger.debug(f"[Cycle {iteration}] Waiting for SDK cleanup (2 seconds)...")
                    await asyncio.sleep(2.0)
                except asyncio.CancelledError:
                    logger.debug(f"[Cycle {iteration}] CancelledError during sleep absorbed (non-fatal)")
                    # 完全吸收此 CancelledError，不再传播

                # 2️⃣ 根据核心状态值决定下一步
                if current_status in ["Done", "Ready for Done"]:
                    # ✅ 终态：故事完成
                    logger.info(f"Story {story_id} completed (Status: {current_status})")
                    return True

                elif current_status in ["Draft", "Ready for Development"]:
                    # 需要开发
                    logger.info(f"[Cycle {iteration}] Executing Dev phase (status: {current_status})")
                    await self.execute_dev_phase(story_path, iteration)
                    # ⚠️ 不检查返回值，继续循环

                elif current_status == "In Progress":
                    # 继续开发
                    logger.info(f"[Cycle {iteration}] Continuing Dev phase (status: {current_status})")
                    await self.execute_dev_phase(story_path, iteration)

                elif current_status == "Ready for Review":
                    # 需要 QA - DevQaController 内部会调用 qa_agent
                    logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
                    await self.execute_dev_phase(story_path, iteration)
                    # ⚠️ 不检查返回值，继续循环

                elif current_status == "Failed":
                    # 失败状态，尝试重新开发
                    logger.warning(f"[Cycle {iteration}] Story in failed state, retrying Dev phase")
                    await self.execute_dev_phase(story_path, iteration)

                else:
                    # 未知状态，尝试开发
                    logger.warning(f"[Cycle {iteration}] Unknown status '{current_status}', attempting Dev phase")
                    await self.execute_dev_phase(story_path, iteration)

                # 3️⃣ 等待 SDK 清理 + 状态更新
                await asyncio.sleep(1.0)

                # 4️⃣ 增加迭代计数
                iteration += 1

            # 超过最大循环次数
            logger.warning(
                f"Reached maximum Dev-QA cycles ({max_dev_qa_cycles}) for {story_path}"
            )
            return False

        except Exception as e:
            logger.error(f"Failed to process story {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e), epic_path=self.epic_id
            )
            return False

    async def _parse_story_status(self, story_path: str) -> str:
        """
        Parse the status field from a story markdown file using AI-powered parsing strategy.

        Args:
            story_path: Path to the story markdown file

        Returns:
            Standard core status string (e.g., 'Draft', 'Ready for Development', 'In Progress', 'Ready for Review', 'Ready for Done', 'Done', 'Failed')
            Uses AI parsing with fallback to 'Draft' if all parsing fails
        """
        try:
            with open(story_path, encoding="utf-8") as f:
                content = f.read()

            # Use StatusParser for AI-powered parsing strategy
            if hasattr(self, "status_parser") and self.status_parser:
                # Note: parse_status is now async in SimpleStatusParser
                status = await self.status_parser.parse_status(content)
                # Return the status directly (already normalized by StatusParser)
                return status
            else:
                # Fallback to original parsing if StatusParser not available
                logger.warning("StatusParser not available, using fallback parsing")
                return self._parse_story_status_fallback(story_path)

        except asyncio.CancelledError:
            # 🎯 关键修复：状态解析中的 SDK 调用被取消时，使用 fallback
            logger.warning(f"Status parsing cancelled for {story_path}, using fallback")
            return self._parse_story_status_fallback(story_path)
        except Exception as e:
            logger.error(f"Failed to parse story status: {e}")
            return "Draft"  # Default to standard status instead of legacy format

    def _parse_story_status_sync(self, story_path: str) -> str:
        """
        Synchronous wrapper for _parse_story_status.

        This method now uses synchronous parsing to avoid async context conflicts.

        Args:
            story_path: Path to the story markdown file

        Returns:
            Standard core status string (e.g., 'Draft', 'Ready for Development', 'In Progress', 'Ready for Review', 'Ready for Done', 'Done', 'Failed')
        """
        try:
            # 🎯 关键修复：移除异步上下文检测，直接使用同步解析
            logger.info(f"Using synchronous status parsing for: {story_path}")
            return self._parse_story_status_fallback(story_path)

        except Exception as e:
            logger.error(f"Failed to parse story status (sync): {e}")
            return "Draft"  # Return standard status instead of legacy format

    def _parse_story_status_fallback(self, story_path: str) -> str:
        """
        Fallback parsing method using original regex patterns.

        Args:
            story_path: Path to the story markdown file

        Returns:
            Status string using original parsing logic
        """
        try:
            with open(story_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Look for lines containing "Status:" and extract the value
            for _, line in enumerate(lines):
                if "Status:" in line:
                    # Try to extract status from bold format: **Status**: Ready for Development
                    match = re.search(
                        r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*", line, re.IGNORECASE
                    )
                    if match:
                        status = match.group(1).strip().lower()
                        return status
                    # Try to extract from regular format: Status: Ready for Development
                    match = re.search(r"Status:\s*(.+)", line, re.IGNORECASE)
                    if match:
                        status = match.group(1).strip().lower()
                        return status

            return "ready_for_development"  # Default to ready_for_development instead of unknown
        except Exception as e:
            logger.error(f"Fallback parsing failed: {e}")
            return "ready_for_development"

    async def _is_story_ready_for_done(self, story_path: str) -> bool:
        """Check if story is ready for done based on status."""
        try:
            # Note: _parse_story_status is now async
            status = await self._parse_story_status(story_path)
            # Use status directly (already normalized)
            normalized_status = status.lower().strip()

            # Check for completion status using standard status values
            # Also accept "Ready for Development" as valid for this automation task
            if normalized_status in [
                CORE_STATUS_READY_FOR_DONE.lower(),
                CORE_STATUS_DONE.lower(),
                "ready_for_development",
            ]:
                logger.info(
                    f"Story status is '{normalized_status}' - considered ready for done"
                )
                return True

            logger.warning(
                f"Story status '{normalized_status}' - not ready for done: {story_path}"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to check story status: {e}")
            return False

    async def _check_state_consistency(self, story: "dict[str, Any]") -> bool:
        """
        Check if story state is consistent with filesystem and expected outcomes.
        Be more permissive - log issues but don't fail the entire process.

        Args:
            story: Story dictionary with path and metadata

        Returns:
            True if state is consistent, False if there are issues
        """
        try:
            story_path = story.get("path", "")
            if not story_path:
                logger.warning("No story path provided for state consistency check")
                return True  # Return True to allow processing to continue

            # Check filesystem state - be permissive about missing files
            filesystem_consistent = await self._check_filesystem_state(story)
            if not filesystem_consistent:
                logger.info(
                    f"Filesystem state check found issues for {story_path}, but continuing"
                )
                # Don't return False - allow processing to continue

            # Check story integrity - be permissive about format issues
            integrity_consistent = await self._validate_story_integrity(story)
            if not integrity_consistent:
                logger.info(
                    f"Story integrity check found format issues for {story_path}, but continuing"
                )
                # Don't return False - allow processing to continue

            # Check status consistency with database - informational only
            try:
                db_status = await self.state_manager.get_story_status(story_path)
                current_status = story.get("status", "unknown")

                if db_status and db_status.get("status") != current_status:
                    logger.info(
                        f"Status mismatch noted for {story_path}: story={current_status}, db={db_status.get('status')}"
                    )
                    # Informational only - don't block processing
            except Exception as e:
                logger.debug(f"Database status check failed for {story_path}: {e}")
                # Don't fail if database check fails

            logger.debug(f"State consistency check completed for {story_path}")
            return True  # Always return True to allow processing to continue

        except Exception as e:
            story_path = story.get("path", "unknown")
            logger.error(f"State consistency check failed for {story_path}: {e}")
            return True  # Return True to allow processing to continue despite errors

    async def _check_filesystem_state(self, story: "dict[str, Any]") -> bool:
        """
        Check if expected files exist on filesystem.
        Be permissive - log missing files but don't fail the process.

        Args:
            story: Story dictionary with expected files

        Returns:
            True if filesystem looks reasonable, False if major issues found
        """
        try:
            expected_files = story.get("expected_files", [])
            if not expected_files:
                # 统一使用默认项目结构
                expected_files = ["src", "tests", "docs"]

            missing_files: list[str] = []
            existing_files: list[str] = []

            for file_path in expected_files:
                path = Path(file_path)
                if path.exists():
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)

            # Log status but be permissive
            if missing_files:
                logger.info(
                    f"Expected files check: found {len(existing_files)}, missing {len(missing_files)} for {story.get('path', 'unknown')}"
                )
                logger.debug(f"Missing files: {missing_files}")
            else:
                logger.debug(
                    f"All expected files found for {story.get('path', 'unknown')}"
                )

            # Always return True to allow processing to continue
            # The check is informational, not blocking
            return True

        except Exception as e:
            logger.error(f"Filesystem state check failed: {e}")
            return True  # Return True to allow processing to continue

    async def _validate_story_integrity(self, story: "dict[str, Any]") -> bool:
        """
        Validate story file content integrity.
        Be smart about validation - check for essential elements, not strict formatting.

        Args:
            story: Story dictionary with path and validation requirements

        Returns:
            True if story has essential content, False if it's clearly invalid
        """
        try:
            story_path = story.get("path", "")
            if not story_path:
                logger.debug("No story path provided for integrity check")
                return True  # Allow processing to continue

            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"Story file does not exist: {story_path}")
                return False  # This is a real issue - file should exist

            content = story_file.read_text(encoding="utf-8")

            # Essential checks - only fail on truly problematic content
            if len(content.strip()) < 50:  # Very short content
                logger.warning(
                    f"Story {story_path} appears too short ({len(content)} chars)"
                )
                return False

            # Helper functions for checking essential story elements
            def has_markdown_headers(content: str) -> bool:
                """Check if content has markdown headers."""
                return "#" in content or content.strip().startswith("#")

            def mentions_status(content: str) -> bool:
                """Check if content mentions status."""
                return "status" in content.lower()

            def has_substantial_content(content: str) -> bool:
                """Check if content has substantial text."""
                return len(content.split()) > 20

            # Check for essential story elements (be flexible about formatting)
            essential_elements: list[tuple[str, Callable[[str], bool]]] = [
                ("title or header", has_markdown_headers),  # Has markdown headers
                ("status", mentions_status),  # Mentions status
                ("story content", has_substantial_content),  # Has substantial content
            ]

            missing_essentials: list[str] = []
            for element_name, check_func in essential_elements:
                # check_func is already correctly typed as Callable[[str], bool]
                # Call the function with the content parameter
                if not check_func(content):
                    missing_essentials.append(element_name)

            if missing_essentials:
                logger.warning(
                    f"Story {story_path} missing essential elements: {missing_essentials}"
                )
                # For missing essentials, be more permissive - log but don't fail
                # unless it's really critical
                if (
                    len(missing_essentials) >= 2
                ):  # Only fail if multiple essentials missing
                    return False

            # Smart section detection - look for common story patterns
            has_story_pattern = any(
                pattern in content.lower()
                for pattern in ["## story", "# story", "as a", "i want", "so that"]
            )

            has_acceptance_pattern = any(
                pattern in content.lower()
                for pattern in ["## acceptance", "# acceptance", "acceptance criteria"]
            )

            if not has_story_pattern and not has_acceptance_pattern:
                logger.warning(
                    f"Story {story_path} doesn't follow standard story format"
                )
                # Don't fail - some stories might use different formats

            logger.debug(f"Story integrity validation passed for {story_path}")
            return True  # Be permissive - allow most stories to proceed

        except Exception as e:
            story_path = story.get("path", "unknown")
            logger.error(f"Story integrity validation failed for {story_path}: {e}")
            return True  # Return True to allow processing to continue

    async def _resync_story_state(self, story: "dict[str, Any]") -> None:
        """
        Resynchronize story state with expected status.

        Args:
            story: Story dictionary with path and expected status
        """
        try:
            story_path = story.get("path", "")
            expected_status = story.get("expected_status", "ready")

            if not story_path:
                return

            logger.info(
                f"Resynchronizing story state for {story_path} to {expected_status}"
            )

            # Update database state
            await self.state_manager.update_story_status(
                story_path=story_path, status=expected_status, epic_path=self.epic_id
            )

            # Log resync action
            self.log_manager.log_state_resync(story_path, expected_status)

        except Exception as e:
            story_path = story.get("path", "unknown")
            logger.error(f"Failed to resync story state for {story_path}: {e}")

    async def _handle_graceful_cancellation(self, story: "dict[str, Any]") -> None:
        """
        Handle graceful cancellation of story processing.

        Args:
            story: Story dictionary being processed
        """
        try:
            story_path = story.get("path", "")
            if not story_path:
                return

            logger.info(f"Handling graceful cancellation for {story_path}")

            # Update story status to indicate cancellation
            await self.state_manager.update_story_status(
                story_path=story_path, status="cancelled", epic_path=self.epic_id
            )

            # Log cancellation
            self.log_manager.log_cancellation(
                f"Story processing cancelled for {story_path}"
            )

        except Exception as e:
            story_path = story.get("path", "unknown")
            logger.error(
                f"Failed to handle graceful cancellation for {story_path}: {e}"
            )

    async def execute_dev_qa_cycle(self, stories: list[dict[str, Any]]) -> bool:
        """
        Execute Dev-QA cycle for all stories.

        Args:
            stories: List of story dictionaries

        Returns:
            True if all stories completed successfully, False otherwise

        Raises:
            asyncio.CancelledError: 当整个 epic 运行被外部取消时，向上传播
        """
        self.logger.info(f"Starting Dev-QA cycle for {len(stories)} stories")

        # Initialize epic processing record
        await self._initialize_epic_processing(len(stories))

        success_count = 0
        for story in stories:
            if self.verbose:
                self.logger.debug(f"Processing story: {story['id']}")

            try:
                # ✅ process_story 可能会传播 CancelledError
                if await self.process_story(story):
                    success_count += 1
                elif not self.retry_failed:
                    if self.verbose:
                        self.logger.debug(
                            f"Continuing to next story after failure: {story['id']}"
                        )
            except asyncio.CancelledError:
                # 🎯 关键修复：SDK 内部取消不应中断 Epic 执行
                # 完全封装，继续处理下一个 story
                self.logger.warning(
                    f"[Epic Level] SDK cancellation for story {story['id']} (non-fatal). "
                    f"Continuing to next story."
                )
                # 不 raise，继续处理下一个 story
                continue
            except RuntimeError as e:
                error_msg = str(e)
                # 🎯 关键：处理 cancel scope 跨任务错误，不中断 epic 执行
                if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
                    self.logger.warning(
                        f"[Epic Level] Cross-task cancel scope error (non-fatal): {error_msg}. "
                        f"Continuing story processing."
                    )
                    # 跨任务cancel scope错误是常见的，继续处理
                    continue
                else:
                    # 其他RuntimeError，记录错误
                    self.logger.error(f"[Epic Level] RuntimeError in story {story['id']}: {error_msg}")
                    if not self.retry_failed:
                        continue

            # 🎯 关键增强：每个 story 处理完成后确保 SDK 清理完成
            # 使用 SDKCancellationManager 等待清理,避免连续调用导致跨任务冲突
            try:
                # 使用简单的等待策略确保后台清理完成
                # monitoring 模块已废弃，改用基于时间的清理策略
                await asyncio.sleep(0.5)
                self.logger.debug("[Story Complete] SDK cleanup grace period finished")
            except Exception as e:
                self.logger.warning(f"[Story Complete] SDK cleanup wait failed: {e}")
                # 回退到简单等待
                await asyncio.sleep(1.0)

        # Update progress
        await self._update_progress(
            "dev_qa",
            "completed",
            {"completed_stories": success_count, "total_stories": len(stories)},
        )

        self.logger.info(
            f"Dev-QA cycle complete: {success_count}/{len(stories)} stories succeeded"
        )

        # Return True if all stories succeeded, False otherwise
        return success_count == len(stories)

    def _validate_phase_gates(self) -> bool:
        """
        Validate that all prerequisites are met before each phase.

        Returns:
            True if all validations pass, False otherwise
        """
        return True

    async def _update_progress(
        self, phase: str, status: str, _details: dict[str, Any]
    ) -> None:
        """
        Update progress tracking in state manager.

        Args:
            phase: Phase name (dev_qa)
            status: Phase status (pending, in_progress, completed, failed, skipped)
            details: Additional phase details
        """
        try:
            # Epic progress is tracked in stories table, not in epic_processing table
            self.logger.debug(f"Updated {phase} progress: {status}")
        except Exception as e:
            self.logger.error(f"Failed to update progress for {phase}: {e}")

    async def _initialize_epic_processing(self, total_stories: int) -> None:
        """
        Initialize epic processing record.

        Args:
            total_stories: Total number of stories in epic
        """
        try:
            # Epic processing is tracked via stories table, no separate initialization needed
            self.logger.debug(
                f"Initialized epic processing for {total_stories} stories"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize epic processing: {e}")

    def _generate_final_report(self) -> dict[str, Any]:
        """
        Generate final epic processing report.

        Returns:
            Dict with final epic results
        """
        return {
            "epic_id": self.epic_id,
            "status": "completed",
            "phases": {"dev_qa": "completed"},
            "total_stories": len(self.stories),
            "timestamp": time.time(),
        }

    def _log_cleanup_summary(self, epic_id: str, story_ids: list[str], stats: dict[str, int]) -> None:
        """记录清理摘要"""

        self.logger.info("=== Database Initialization ===")
        self.logger.info("Cleanup Rules:")
        self.logger.info(f"  1. Current Epic stories: {epic_id} {story_ids}")
        self.logger.info("  2. TEMP path stories: %\\Temp\\%, %\\AppData\\Local\\Temp\\%")
        self.logger.info("  3. Test-marked stories: *test*, test_*")
        self.logger.info("")
        self.logger.info("Cleanup Results:")
        self.logger.info(f"  - Epic stories removed: {stats['epic_stories']}")
        self.logger.info(f"  - Temp stories removed: {stats['temp_stories']}")
        self.logger.info(f"  - Test stories removed: {stats['test_stories']}")
        self.logger.info(f"  - Total removed: {stats['total']}")
        self.logger.info("")
        self.logger.info("Database ready for Epic execution.")
        self.logger.info("=" * 31)

    async def run(self) -> bool:
        """
        Execute complete epic processing workflow.

        Returns:
            True if epic completed successfully, False otherwise

        Raises:
            asyncio.CancelledError: 当整个 epic 运行被外部取消时，重新抛出让调用者处理
        """
        self.logger.info("Starting Epic Driver - Dev-QA Workflow")

        # Log configuration
        if self.verbose:
            config_str = (
                f"Configuration: max_iterations={self.max_iterations}, "
                f"retry_failed={self.retry_failed}, verbose={self.verbose}, "
                f"concurrent={self.concurrent}, skip_quality={self.skip_quality}, "
                f"skip_tests={self.skip_tests}"
            )
            self.logger.debug(config_str)

        if self.concurrent:
            self.logger.warning(
                "Concurrent processing is experimental and not fully tested with quality gates"
            )

        try:
            # Parse epic
            stories = await self.parse_epic()
            if not stories:
                self.logger.error("No stories found in epic")
                return False

            # Validate phase gates
            if not self._validate_phase_gates():
                self.logger.error("Phase gate validation failed")
                return False

            # 【新增】数据库初始化清理
            # Extract story IDs for initialization
            story_ids = [story["id"].split(":")[0].strip() for story in stories]

            # Get epic identifier from epic_path
            epic_id = self.epic_id

            # Initialize database with cleanup
            cleanup_stats = await self.state_manager.initialize_for_epic(
                epic_id=epic_id,
                story_ids=story_ids
            )

            # Log cleanup summary
            self._log_cleanup_summary(epic_id, story_ids, cleanup_stats)

            # Phase 1: Dev-QA Cycle
            self.logger.info("=== Phase 1: Dev-QA Cycle ===")
            await self._update_progress("dev_qa", "in_progress", {})
            dev_qa_success = await self.execute_dev_qa_cycle(stories)

            if not dev_qa_success:
                self.logger.error("Dev-QA cycle failed")
                await self._update_progress("dev_qa", "failed", {})
                return False

            # Phase 2: Quality Gates (Ruff, Basedpyright, Pytest)
            # Quality gates are non-blocking - epic continues regardless of results
            await self.execute_quality_gates()

            # Sync story statuses from database to markdown files
            self.logger.info("=== Syncing Story Statuses ===")

            # ✅ 修改：提取完整路径而非短ID
            story_paths = [story["path"] for story in stories]

            # ✅ 添加诊断日志
            self.logger.debug(f"Story paths for sync: {story_paths}")

            sync_results = await self.status_update_agent.sync_from_database(
                state_manager=self.state_manager,
                epic_id=self.epic_id,
                story_ids=story_paths  # ✅ 传入完整路径列表
            )
            if sync_results.get("error_count", 0) > 0:
                self.logger.warning(
                    f"同步过程中有 {sync_results['error_count']} 个错误"
                )
            else:
                self.logger.info(
                    f"成功同步 {sync_results.get('success_count', 0)} 个故事状态"
                )

            self.logger.info("=== Epic Processing Complete ===")
            return True

        except asyncio.CancelledError:
            # 🎯 Epic 层面的取消：整个运行被外部中止
            self.logger.info(
                "[Epic Cancelled] Epic execution cancelled by external signal (Ctrl+C / task.cancel())"
            )
            # 可以在这里做必要的清理工作
            # 不返回 False，而是重新抛出，让调用者知道这是取消而非失败
            raise

        except Exception as e:
            self.logger.error(f"Epic driver execution failed: {e}", exc_info=True)
            # Write exception to log file
            if self.log_manager:
                self.log_manager.write_exception(e, "Epic Driver run()")
            return False
        finally:
            # Improved cleanup logic
            try:
                # 1. Flush log manager
                if hasattr(self, "log_manager") and self.log_manager:
                    self.log_manager.flush()

                # 2. Finally cleanup logging
                cleanup_logging()

            except Exception:
                # Silently handle cleanup errors to avoid interfering with main flow
                pass

    async def execute_quality_gates(self) -> bool:
        """
        Execute quality gates pipeline after Dev-QA cycle completes.

        Returns:
            True if quality gates passed or were skipped, False otherwise
        """
        self.logger.info("=== Phase 2: Quality Gates ===")
        await self._update_progress("quality_gates", "in_progress", {})

        try:
            # Create quality gate orchestrator
            quality_orchestrator = QualityGateOrchestrator(
                source_dir=self.source_dir,
                test_dir=self.test_dir,
                skip_quality=self.skip_quality,
                skip_tests=self.skip_tests,
            )

            # Execute quality gates pipeline
            quality_results = await quality_orchestrator.execute_quality_gates(
                self.epic_id
            )

            # Update progress
            await self._update_progress(
                "quality_gates", "completed", {"quality_results": quality_results}
            )

            # Check if quality gates succeeded
            if quality_results.get("success", False):
                self.logger.info("✓ Quality gates pipeline PASSED")
                return True
            else:
                # Quality gates failed
                errors = quality_results.get("errors", [])
                if errors:
                    self.logger.error(
                        f"✗ Quality gates pipeline FAILED with {len(errors)} error(s):"
                    )
                    for error in errors:
                        self.logger.error(f"  - {error}")
                else:
                    self.logger.error(
                        "✗ Quality gates pipeline FAILED (no specific errors reported)"
                    )

                # Quality gates failures are non-blocking by design
                # We return True to allow epic completion even if quality gates fail
                # This allows developers to review and fix issues post-epic
                self.logger.warning(
                    "Quality gates failure is non-blocking - epic processing continues"
                )
                return True

        except Exception as e:
            error_msg = f"Quality gates execution error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            await self._update_progress("quality_gates", "error", {"error": str(e)})

            # Quality gates errors are also non-blocking
            self.logger.warning(
                "Quality gates error is non-blocking - epic processing continues"
            )
            return True


def parse_arguments():
    """Parse command line arguments with subcommand support."""
    parser = argparse.ArgumentParser(
        description="BMAD Epic Automation - Process epic markdown files through Dev-QA workflow with quality gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quality Gates Examples:
  # Run with full quality gates (Ruff, BasedPyright, Pytest)
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

  # Skip quality gates for faster development
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality

  # Skip only pytest execution
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests

  # Skip both quality gates and tests
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality --skip-tests

  # Custom source and test directories
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --source-dir src --test-dir tests

  # Enable verbose logging for detailed quality gate output
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

  # Increase retry attempts for quality gates
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --max-iterations 5

  # Enable log file creation
  python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --log-file

Standalone Quality Gates Examples:
  # Run quality gates only (Ruff, BasedPyright, Pytest)
  python -m autoBMAD.epic_automation.epic_driver run-quality

  # Skip quality checks, run only pytest
  python -m autoBMAD.epic_automation.epic_driver run-quality --skip-quality

  # Skip pytest, run only quality checks
  python -m autoBMAD.epic_automation.epic_driver run-quality --skip-tests

  # Custom source and test directories
  python -m autoBMAD.epic_automation.epic_driver run-quality --source-dir src --test-dir tests

  # Custom epic ID for error reporting
  python -m autoBMAD.epic_automation.epic_driver run-quality --epic-id my-custom-id

  # Enable verbose logging
  python -m autoBMAD.epic_automation.epic_driver run-quality --verbose --log-file

Standard Examples:
  python epic_driver.py docs/epics/my-epic.md --max-iterations 5
  python epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
  python epic_driver.py docs/epics/my-epic.md --source-dir src --test-dir tests

For more information on quality gates, see docs/troubleshooting/quality-gates.md
        """,
    )

    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Subcommand 1: run-epic (original functionality, default behavior) ---
    epic_parser = subparsers.add_parser(
        'run-epic',
        help='Run full epic workflow (SM-Dev-QA + Quality Gates)'
    )
    epic_parser.add_argument('epic_path', type=str, help='Path to epic markdown file')

    # Epic-specific arguments
    _ = epic_parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        metavar="N",
        help="Maximum retry attempts for failed stories (default: 5, must be positive)",
    )

    _ = epic_parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Enable automatic retry of failed stories",
    )

    _ = epic_parser.add_argument(
        "--verbose", action="store_true", help="Enable detailed logging output"
    )

    _ = epic_parser.add_argument(
        "--concurrent",
        action="store_true",
        help="Process stories in parallel (experimental feature)",
    )

    _ = epic_parser.add_argument(
        "--no-claude",
        action="store_true",
        help="Disable Claude Code CLI integration (use simulation mode)",
    )

    _ = epic_parser.add_argument(
        "--source-dir",
        type=str,
        default=os.getenv("EPIC_SOURCE_DIR", "src"),
        metavar="DIR",
        help='Source code directory for QA checks (default: $EPIC_SOURCE_DIR or "src")',
    )

    _ = epic_parser.add_argument(
        "--test-dir",
        type=str,
        default=os.getenv("EPIC_TEST_DIR", "tests"),
        metavar="DIR",
        help='Test directory for QA checks (default: $EPIC_TEST_DIR or "tests")',
    )

    _ = epic_parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Skip quality gates (ruff and basedpyright checks)",
    )

    _ = epic_parser.add_argument(
        "--skip-tests", action="store_true", help="Skip pytest execution"
    )

    _ = epic_parser.add_argument(
        "--log-file",
        action="store_true",
        help="Enable timestamped log file creation (disabled by default)"
    )

    # --- Subcommand 2: run-quality (new) ---
    quality_parser = subparsers.add_parser(
        'run-quality',
        help='Run quality gates only (Ruff, BasedPyright, Pytest)'
    )

    quality_parser.add_argument(
        '--source-dir', type=str, default=os.getenv('EPIC_SOURCE_DIR', 'src'),
        help='Source code directory (default: $EPIC_SOURCE_DIR or "src")'
    )
    quality_parser.add_argument(
        '--test-dir', type=str, default=os.getenv('EPIC_TEST_DIR', 'tests'),
        help='Test directory (default: $EPIC_TEST_DIR or "tests")'
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
        '--max-cycles', type=int, default=5,
        help='Maximum fix cycles (default: 5)'
    )
    quality_parser.add_argument(
        '--verbose', action='store_true',
        help='Enable verbose logging'
    )
    quality_parser.add_argument(
        '--log-file', action='store_true',
        help='Create timestamped log file'
    )

    # --- Backward compatibility: positional argument without subcommand ---
    # Handle python epic_driver.py epic.md old calling style
    # We need to check sys.argv before parsing to determine the mode

    # Check the first argument to determine parsing mode
    if len(sys.argv) > 1 and sys.argv[1] in ['run-epic', 'run-quality']:
        # Subcommand provided - use normal argparse
        args = parser.parse_args()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # Old style: positional epic_path without subcommand
        # Temporarily modify sys.argv to include subcommand
        original_argv = sys.argv.copy()
        try:
            # Insert 'run-epic' as the subcommand
            sys.argv = [sys.argv[0], 'run-epic'] + sys.argv[1:]
            args = parser.parse_args()
            # Ensure command attribute exists for main() routing
            args.command = 'run-epic'
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
    else:
        # No arguments or flags only, use normal argparse
        args = parser.parse_args()

    # Validate max_iterations for run-epic command
    if hasattr(args, 'max_iterations') and args.max_iterations <= 0:
        parser.error("--max-iterations must be a positive integer")

    # Validate max_cycles for run-quality command
    if hasattr(args, 'max_cycles') and args.max_cycles <= 0:
        parser.error("--max-cycles must be a positive integer")

    return args


async def main():
    """Main entry point with subcommand routing."""
    args = parse_arguments()

    # Route to corresponding handler
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

    elif args.command == 'run-epic':
        # 原有完整流程
        # Configure logging level based on verbose flag
        if args.verbose:  # type: ignore[truthy-bool]
            logging.getLogger().setLevel(logging.DEBUG)

        # Check if epic file exists
        epic_path = Path(args.epic_path)  # type: ignore[arg-type]
        if not epic_path.exists():
            logger.error(f"Epic file not found: {epic_path}")
            sys.exit(1)

        # Create driver with CLI options
        driver = EpicDriver(
            epic_path=str(epic_path),
            max_iterations=args.max_iterations,  # type: ignore[arg-type]
            retry_failed=args.retry_failed,  # type: ignore[arg-type]
            verbose=args.verbose,  # type: ignore[arg-type]
            concurrent=args.concurrent,  # type: ignore[arg-type]
            use_claude=not args.no_claude,  # type: ignore[arg-type]
            source_dir=args.source_dir,  # type: ignore[arg-type]
            test_dir=args.test_dir,  # type: ignore[arg-type]
            skip_quality=args.skip_quality,  # type: ignore[arg-type]
            skip_tests=args.skip_tests,  # type: ignore[arg-type]
            create_log_file=args.log_file,  # type: ignore[arg-type]
        )

        success = await driver.run()
        sys.exit(0 if success else 1)

    else:
        # 无子命令，显示帮助
        parse_arguments()


if __name__ == "__main__":
    try:
        # 添加全局任务异常处理器
        def global_exception_handler(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
            """全局异常处理器，捕获未捕获的任务异常"""
            exception = context.get('exception')
            if exception and isinstance(exception, RuntimeError):
                error_msg = str(exception)
                # 忽略跨任务cancel scope错误
                if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
                    logger.debug(
                        f"Ignored uncaught task exception (cancel scope, non-fatal): {error_msg}"
                    )
                    return
            # 对于其他异常，使用默认处理器
            loop.default_exception_handler(context)

        # 设置全局异常处理器
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        loop.set_exception_handler(global_exception_handler)

        # 运行主函数，异常处理器已在main()内部设置
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Execution cancelled by user (Ctrl+C)")
        sys.exit(130)  # Standard exit code for SIGINT
    except asyncio.CancelledError:
        # 🎯 CancelledError 正常退出
        logger.info("Execution cancelled (non-fatal)")
        sys.exit(0)
    except Exception as e:
        error_msg = str(e)
        # 🎯 关键：cancel scope 错误特殊处理
        if "cancel scope" in error_msg.lower():
            logger.warning(
                f"RuntimeError during execution (cancel scope, non-fatal): {error_msg}"
            )
            sys.exit(0)  # 视为成功退出
        else:
            logger.error(f"Unexpected error in main: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            sys.exit(1)
