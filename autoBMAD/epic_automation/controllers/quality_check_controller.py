"""
质量检查控制器 - QualityCheckController

实现检查 → SDK 修复 → 回归检查的闭环流程

主要职责：
1. 控制多轮循环执行
2. 维护错误文件列表
3. 调用 SDK 进行自动修复
4. 决定循环终止条件

作者: autoBMAD Team
日期: 2026-01-13
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from autoBMAD.epic_automation.agents.quality_agents import BaseQualityAgent


class QualityCheckController:
    """
    通用质量检查控制器

    职责：
    - 控制 检查 ↔ SDK 修复 的多轮循环
    - 维护错误文件列表
    - 决定循环终止条件
    - 支持 Ruff 和 BasedPyright 两种工具
    """

    def __init__(
        self,
        tool: str,  # 'ruff' | 'basedpyright'
        agent: BaseQualityAgent,
        source_dir: str,
        max_cycles: int = 3,
        sdk_call_delay: int = 60,
        sdk_timeout: int = 600,
    ):
        """
        初始化质量检查控制器

        Args:
            tool: 工具类型 ('ruff' 或 'basedpyright')
            agent: 对应的 Agent 实例
            source_dir: 源代码目录
            max_cycles: 最大循环次数
            sdk_call_delay: SDK调用间延时（秒）
            sdk_timeout: SDK超时时间（秒）
        """
        # 添加类型注解
        self.tool: str = tool
        self.agent: BaseQualityAgent = agent
        self.source_dir: str = source_dir
        self.max_cycles: int = max_cycles
        self.sdk_call_delay: int = sdk_call_delay
        self.sdk_timeout: int = sdk_timeout

        # 状态
        self.current_cycle: int = 0
        self.error_files: dict[str, list[dict[str, object]]] = {}
        self.initial_error_files: list[str] = []
        self.final_error_files: list[str] = []
        self.sdk_fix_errors: list[dict[str, object]] = []

        self.logger: logging.Logger = logging.getLogger(f"{__name__}.{tool}_controller")

    async def run(self) -> dict[str, Any]:
        """
        主入口：执行完整的检查 ↔ SDK 修复循环

        Returns:
            {
                "status": "completed" | "failed",
                "tool": "ruff" | "basedpyright",
                "cycles": int,
                "initial_error_files": List[str],
                "final_error_files": List[str],
                "sdk_fix_attempted": bool,
                "sdk_fix_errors": List[dict],
            }
        """
        # 1. 首轮全量检查
        self.current_cycle = 1
        error_files = await self._run_check_phase()
        self.initial_error_files = list(error_files.keys())

        self.logger.info(
            f"{self.tool} initial check: "
            f"{len(error_files)} files with errors"
        )

        # 2. 无错误则直接成功
        if not error_files:
            return self._build_success_result()

        # 3. 进入修复循环（最多 3 轮）
        while error_files and self.current_cycle <= self.max_cycles:
            self.logger.info(
                f"{self.tool} cycle {self.current_cycle}/{self.max_cycles}: "
                f"Fixing {len(error_files)} files"
            )

            # SDK 修复阶段
            await self._run_sdk_fix_phase(error_files)

            # 回归检查阶段
            error_files = await self._run_check_phase()

            self.current_cycle += 1

        # 4. 构造最终结果
        self.final_error_files = list(error_files.keys())
        return self._build_final_result()

    async def _run_check_phase(self) -> dict[str, list[dict[str, object]]]:
        """
        执行质量检查，返回按文件分组的错误

        Returns:
            {
                "src/module.py": [
                    {"line": 10, "message": "...", "code": "F401"},
                    {"line": 25, "message": "...", "code": "E501"}
                ],
                "src/utils.py": [...]
            }
        """
        self.logger.info(f"Running {self.tool} check...")

        try:
            # 1. 调用 Agent 执行检查
            result = await self.agent.execute(source_dir=self.source_dir)

            # 2. 检查执行失败
            if result["status"] != "completed":
                self.logger.error(
                    f"{self.tool} check failed: {result.get('error')}"
                )
                return {}

            # 3. 提取按文件分组的错误
            issues: list[object] = result.get("issues", [])
            if not issues:
                self.logger.info(f"{self.tool} check passed: no errors found")
                return {}

            # 4. 解析错误
            errors_by_file: dict[str, list[dict[str, object]]] = self.agent.parse_errors_by_file(issues)

            self.logger.info(
                f"{self.tool} found {len(issues)} errors "
                f"in {len(errors_by_file)} files"
            )

            return errors_by_file

        except Exception as e:
            self.logger.error(f"{self.tool} check exception: {e}", exc_info=True)
            return {}

    async def _run_sdk_fix_phase(
        self,
        error_files: dict[str, list[dict[str, object]]]
    ) -> None:
        """
        针对每个错误文件，调用 SDK 修复

        核心流程（每个文件）：
        1. 读取文件内容
        2. 构造修复 Prompt
        3. 调用 SafeClaudeSDK
        4. 接收 ResultMessage
        5. 触发取消并等待确认
        6. 延时 1 分钟后处理下一个文件

        Args:
            error_files: {"文件路径": [错误列表]}
        """
        total_files: int = len(error_files)

        for idx, (file_path, errors) in enumerate(error_files.items(), 1):
            self.logger.info(
                f"[{idx}/{total_files}] Fixing {file_path} "
                f"({len(errors)} errors) - Cycle {self.current_cycle}"
            )

            try:
                # 1. 读取文件内容
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception as e:
                    self.logger.error(f"Failed to read {file_path}: {e}")
                    self.sdk_fix_errors.append({
                        "file": file_path,
                        "error": f"File read error: {str(e)}",
                        "cycle": self.current_cycle,
                    })
                    continue

                # 2. 构造 Prompt
                prompt = self.agent.build_fix_prompt(
                    tool=self.tool,
                    file_path=file_path,
                    file_content=file_content,
                    errors=errors,
                )

                # 3. 调用 SDK
                sdk_result = await self._execute_sdk_fix(
                    prompt=prompt,
                    file_path=file_path,
                )

                if not sdk_result.get("success"):
                    self.sdk_fix_errors.append({
                        "file": file_path,
                        "error": sdk_result.get("error"),
                        "cycle": self.current_cycle,
                    })

                # 4. 延时 1 分钟（除最后一个文件）
                if idx < total_files:
                    self.logger.debug(
                        f"Waiting {self.sdk_call_delay}s before next SDK call..."
                    )
                    await asyncio.sleep(self.sdk_call_delay)

            except Exception as e:
                self.logger.error(
                    f"SDK fix failed for {file_path}: {e}",
                    exc_info=True
                )
                self.sdk_fix_errors.append({
                    "file": file_path,
                    "error": str(e),
                    "cycle": self.current_cycle,
                })

    async def _execute_sdk_fix(
        self,
        prompt: str,
        file_path: str,
    ) -> dict[str, Any]:
        """
        执行单个文件的 SDK 修复调用

        流程：
        1. 使用 sdk_helper.execute_sdk_call() 统一接口
        2. 自动处理 ClaudeAgentOptions 类型转换
        3. 使用 SDKResult 统一结果处理
        4. 移除冗余的 SafeClaudeSDK 包装逻辑
        """
        try:
            # 使用 sdk_helper 统一接口
            from ..agents.sdk_helper import execute_sdk_call

            # 统一调用，自动处理类型转换
            result = await execute_sdk_call(
                prompt=prompt,
                agent_name=f"{self.tool.capitalize()}Agent",
                timeout=float(self.sdk_timeout),
                permission_mode="bypassPermissions"
            )

            # 使用 SDKResult 判断成功
            if result.is_success():
                self.logger.info(f"SDK fix completed for {file_path}")
                return {
                    "success": True,
                    "result": result,
                    "duration": result.duration_seconds
                }
            else:
                self.logger.error(
                    f"SDK fix failed for {file_path}: "
                    f"{result.error_type.value} - {result.errors}"
                )
                return {
                    "success": False,
                    "error": f"{result.error_type.value}: {', '.join(result.errors)}"
                }

        except Exception as e:
            self.logger.error(f"SDK execution failed for {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _build_success_result(self) -> dict[str, Any]:
        """构造成功结果"""
        return {
            "status": "completed",
            "tool": self.tool,
            "cycles": self.current_cycle,
            "max_cycles": self.max_cycles,
            "initial_error_files": self.initial_error_files,
            "final_error_files": [],
            "sdk_fix_attempted": False,
            "sdk_fix_errors": [],
        }

    def _build_final_result(self) -> dict[str, Any]:
        """构造最终结果"""
        success = len(self.final_error_files) == 0

        return {
            "status": "completed" if success else "failed",
            "tool": self.tool,
            "cycles": self.current_cycle,
            "max_cycles": self.max_cycles,
            "initial_error_files": self.initial_error_files,
            "final_error_files": self.final_error_files,
            "sdk_fix_attempted": True,
            "sdk_fix_errors": self.sdk_fix_errors,
        }
