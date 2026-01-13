"""
Pytest 质量门控控制器

职责：
- 控制 pytest ↔ SDK 修复 的多轮循环
- 维护失败文件列表和汇总 JSON
- 决定循环终止条件
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, List, cast

logger = logging.getLogger(__name__)


class PytestController:
    """
    Pytest 质量门控控制器

    职责：
    - 控制 pytest ↔ SDK 修复 的多轮循环
    - 维护失败文件列表和汇总 JSON
    - 决定循环终止条件
    """

    def __init__(
        self,
        source_dir: str,
        test_dir: str,
        max_cycles: int = 3,
        summary_json_path: str | None = None,
    ):
        """
        初始化 PytestController

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录
            max_cycles: 最大修复循环次数
            summary_json_path: 汇总 JSON 文件路径
        """
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.max_cycles = max_cycles
        self.summary_json_path = summary_json_path or "pytest_summary.json"

        # 状态
        self.current_cycle: int = 0
        self.failed_files: List[str] = []
        self.initial_failed_files: List[str] = []
        self.sdk_fix_errors: List[dict[str, Any]] = []

        # Agent 实例
        from ..agents.quality_agents import PytestAgent
        self.pytest_agent = PytestAgent()

        logger.info(f"PytestController initialized (max_cycles={max_cycles})")

    async def run(self) -> dict[str, Any]:
        """
        主入口：执行完整的 pytest ↔ SDK 修复 循环

        Returns:
            {
                "status": "completed" | "failed",
                "cycles": int,  # 实际执行的循环次数
                "initial_failed_files": list[str],
                "final_failed_files": list[str],
                "summary_json": str,
                "sdk_fix_attempted": bool,
                "sdk_fix_errors": list[dict],
            }
        """
        logger.info(f"Starting pytest ↔ SDK fix loop (max_cycles={self.max_cycles})")

        try:
            # 1. 首轮全量测试
            self.current_cycle = 1
            failed_files = await self._run_test_phase_all_files(round_index=1)
            self.initial_failed_files = failed_files.copy()

            logger.info(f"Initial test phase completed: {len(failed_files)} file(s) failed")

            # 2. 无失败则直接成功
            if not failed_files:
                logger.info("No failed files - pytest quality gate PASSED")
                return self._build_success_result()

            # 3. 进入修复循环
            while failed_files and self.current_cycle <= self.max_cycles:
                logger.info(f"Starting cycle {self.current_cycle}/{self.max_cycles}")

                # SDK 修复阶段
                await self._run_sdk_phase(failed_files, round_index=self.current_cycle)

                # 回归测试阶段
                failed_files = await self._run_test_phase_failed_files(
                    failed_files,
                    round_index=self.current_cycle + 1
                )

                self.current_cycle += 1
                logger.info(f"Cycle {self.current_cycle - 1} completed: {len(failed_files)} file(s) still failing")

            # 4. 构造最终结果
            self.failed_files = failed_files
            return self._build_final_result()

        except Exception as e:
            logger.error(f"PytestController execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "cycles": self.current_cycle,
                "initial_failed_files": self.initial_failed_files,
                "final_failed_files": self.failed_files,
                "summary_json": self.summary_json_path,
                "sdk_fix_attempted": True,
                "sdk_fix_errors": self.sdk_fix_errors + [{
                    "error": f"Controller execution error: {str(e)}",
                    "round_index": self.current_cycle,
                }],
            }

    async def _run_test_phase_all_files(self, round_index: int) -> List[str]:
        """
        遍历 tests/ 下所有测试文件，依次执行 pytest

        Args:
            round_index: 轮次索引（用于 JSON 记录）

        Returns:
            有 FAIL/ERROR 的测试文件路径列表
        """
        logger.info(f"Phase {round_index}: Testing all files")

        # 1. 递归枚举测试文件
        test_files = self._discover_test_files()

        if not test_files:
            logger.warning("No test files discovered")
            return []

        logger.info(f"Discovered {len(test_files)} test files")

        # 2. 调用 pytest agent 顺序执行
        round_result = await self.pytest_agent.run_tests_sequential(
            test_files=test_files,
            timeout_per_file=180,
            round_index=round_index,
            round_type="initial",
        )

        # 3. 提取失败文件列表
        files_list = cast(List[dict[str, Any]], round_result["files"])
        failed_files = [
            item["test_file"]
            for item in files_list
            if item["status"] in ["failed", "error", "timeout"]
        ]

        # 4. 写入汇总 JSON
        self._append_round_to_summary_json(
            round_index=round_index,
            round_type="initial",
            round_result=round_result,
        )

        return failed_files

    async def _run_test_phase_failed_files(
        self,
        failed_files: List[str],
        round_index: int,
    ) -> List[str]:
        """
        仅对失败文件执行回归 pytest

        Args:
            failed_files: 上一轮失败的测试文件列表
            round_index: 轮次索引

        Returns:
            本轮仍然 FAIL/ERROR 的测试文件列表
        """
        logger.info(f"Phase {round_index}: Regression testing {len(failed_files)} file(s)")

        round_result = await self.pytest_agent.run_tests_sequential(
            test_files=failed_files,
            timeout_per_file=600,
            round_index=round_index,
            round_type="retry",
        )

        files_list = cast(List[dict[str, Any]], round_result["files"])
        new_failed_files = [
            item["test_file"]
            for item in files_list
            if item["status"] in ["failed", "error", "timeout"]
        ]

        self._append_round_to_summary_json(
            round_index=round_index,
            round_type="retry",
            round_result=round_result,
        )

        return new_failed_files

    async def _run_sdk_phase(
        self,
        failed_files: List[str],
        round_index: int,
    ) -> None:
        """
        针对失败文件，依次触发 SDK 修复调用

        核心流程（每个文件）：
        1. 构造 Prompt（文件内容 + 失败信息）
        2. 调用 SDK（通过 pytest_agent）
        3. 收到 ResultMessage（完成信号）
        4. 触发取消 SDK 调用
        5. 等待取消确认成功
        6. 处理下一个文件

        Args:
            failed_files: 需要修复的测试文件列表
            round_index: 当前循环轮次
        """
        logger.info(f"SDK Fix Phase {round_index}: Processing {len(failed_files)} file(s)")

        for test_file in failed_files:
            try:
                logger.info(f"Processing SDK fix for: {test_file}")

                # 调用 pytest agent 的 SDK 修复接口
                result = await self.pytest_agent.run_sdk_fix_for_file(
                    test_file=test_file,
                    source_dir=self.source_dir,
                    summary_json_path=self.summary_json_path,
                    round_index=round_index,
                )

                if not result.get("success"):
                    # 记录 SDK 调用层面的错误
                    error_info = {
                        "test_file": test_file,
                        "error": result.get("error", "Unknown SDK error"),
                        "round_index": round_index,
                    }
                    self.sdk_fix_errors.append(error_info)
                    logger.warning(f"SDK fix failed for {test_file}: {error_info['error']}")

            except Exception as e:
                # 捕获意外异常，不中断后续文件的修复
                error_info = {
                    "test_file": test_file,
                    "error": f"SDK phase exception: {str(e)}",
                    "round_index": round_index,
                }
                self.sdk_fix_errors.append(error_info)
                logger.error(f"SDK fix exception for {test_file}: {e}", exc_info=True)

    def _discover_test_files(self) -> List[str]:
        """递归枚举 test_dir 下所有测试文件，按字典序排序"""
        test_path = Path(self.test_dir)

        if not test_path.exists():
            logger.warning(f"Test directory not found: {self.test_dir}")
            return []

        test_files = sorted(
            list(test_path.rglob("test_*.py")) +
            list(test_path.rglob("*_test.py"))
        )

        return [str(f) for f in test_files]

    def _append_round_to_summary_json(
        self,
        round_index: int,
        round_type: str,
        round_result: dict[str, Any],
    ) -> None:
        """
        将本轮测试结果追加到汇总 JSON

        JSON 结构：
        {
          "summary": {...},
          "rounds": [
            {
              "round_index": 1,
              "round_type": "initial" | "retry",
              "failed_files": [
                {
                  "test_file": "...",
                  "status": "failed" | "error" | "timeout",
                  "failures": [
                    {
                      "nodeid": "...",
                      "failure_type": "...",
                      "message": "...",
                      "short_tb": "..."
                    }
                  ]
                }
              ]
            }
          ]
        }
        """
        # 加载现有 JSON
        summary_data = self._load_summary_json()

        # 添加轮次信息
        round_entry = {
            "round_index": round_index,
            "round_type": round_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "failed_files": [
                {
                    "test_file": item["test_file"],
                    "status": item["status"],
                    "failures": item.get("failures", []),
                }
                for item in round_result["files"]
                if item["status"] in ["failed", "error", "timeout"]
            ]
        }

        summary_data["rounds"].append(round_entry)

        # 更新汇总信息
        initial_failed: list[Any] = summary_data["rounds"][0]["failed_files"] if summary_data["rounds"] else []
        final_failed: list[Any] = summary_data["rounds"][-1]["failed_files"] if summary_data["rounds"] else []
        round_files = cast(List[dict[str, Any]], round_result["files"])

        summary_data["summary"] = {
            "total_files": len(round_files),
            "failed_files_initial": len(initial_failed),
            "failed_files_final": len(final_failed),
            "cycles": self.current_cycle,
        }

        # 写回文件
        with open(self.summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Updated summary JSON: {self.summary_json_path}")

    def _load_summary_json(self) -> dict[str, Any]:
        """加载现有汇总 JSON，如果不存在则创建新结构"""
        if Path(self.summary_json_path).exists():
            try:
                with open(self.summary_json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to load summary JSON: {e} - creating new structure")

        # 返回新结构
        return {
            "summary": {
                "total_files": 0,
                "failed_files_initial": 0,
                "failed_files_final": 0,
                "cycles": 0,
            },
            "rounds": [],
        }

    def _build_success_result(self) -> dict[str, Any]:
        """构造成功结果结构"""
        return {
            "status": "completed",
            "cycles": self.current_cycle,
            "initial_failed_files": self.initial_failed_files,
            "final_failed_files": [],
            "summary_json": self.summary_json_path,
            "sdk_fix_attempted": False,
            "sdk_fix_errors": [],
        }

    def _build_final_result(self) -> dict[str, Any]:
        """构造最终结果结构"""
        return {
            "status": "completed" if not self.failed_files else "failed",
            "cycles": self.current_cycle,
            "initial_failed_files": self.initial_failed_files,
            "final_failed_files": self.failed_files,
            "summary_json": self.summary_json_path,
            "sdk_fix_attempted": True,
            "sdk_fix_errors": self.sdk_fix_errors,
        }
