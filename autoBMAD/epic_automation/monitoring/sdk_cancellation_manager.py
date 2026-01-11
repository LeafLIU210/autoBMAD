"""
SDK 取消管理器 - Unified SDK Cancellation Manager

统一管理 SDK 取消过程的检查、监控和清理机制。
"""

# type: ignore[reportArgumentType]

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Union
import json
import uuid

from .cancel_scope_tracker import CancelScopeTracker, get_tracker
from .resource_monitor import ResourceMonitor, get_resource_monitor
# AsyncDebugger 已移除 - 调试功能不再集成到此模块

logger = logging.getLogger(__name__)


class SDKCancellationManager:
    """SDK 取消管理器"""

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        enable_tracking: bool = True,
        enable_monitoring: bool = True,
        enable_debugging: bool = True
    ):
        """
        初始化 SDK 取消管理器

        Args:
            log_dir: 日志目录
            enable_tracking: 启用 cancel scope 追踪
            enable_monitoring: 启用资源监控
            enable_debugging: 已弃用参数（保留以保持向下兼容，调试功能已移除）
        """
        self.log_dir = log_dir or Path("autoBMAD/epic_automation/logs/monitoring")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 初始化组件
        self.tracker = (
            get_tracker(self.log_dir / "cancel_scope_tracker.log")
            if enable_tracking
            else None
        )

        self.resource_monitor = (
            get_resource_monitor()
            if enable_monitoring
            else None
        )

        # 注意：enable_debugging 参数保留以保持向下兼容，但调试功能已被移除
        # self.debugger 字段不再创建 - 2026-01-10

        # 状态跟踪
        self.active_sdk_calls: Dict[str, Dict[str, Any]] = {}
        self.completed_calls: List[Dict[str, Any]] = []
        self.cancelled_calls: List[Dict[str, Any]] = []
        self.failed_calls: List[Dict[str, Any]] = []

        # 统计信息
        self.stats: Dict[str, Union[int, float]] = {
            "total_sdk_calls": 0,
            "successful_completions": 0,
            "cancellations": 0,
            "cancel_after_success": 0,
            "failures": 0,
            "cross_task_violations": 0
        }

        logger.info(
            f"SDK Cancellation Manager initialized "
            f"(tracking={enable_tracking}, monitoring={enable_monitoring})"
        )

    @asynccontextmanager
    async def track_sdk_execution(
        self,
        call_id: str,
        operation_name: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        追踪 SDK 执行的上下文管理器

        使用方法:
        ```python
        async with manager.track_sdk_execution("parse_status", "status_parsing"):
            result = await sdk.execute()
        ```

        Args:
            call_id: 调用唯一标识
            operation_name: 操作名称
            context: 上下文信息
        """
        start_time = datetime.now()
        scope_id = None

        # 进入 cancel scope 追踪
        if self.tracker:
            scope_id = self.tracker.enter_scope(name=f"sdk_{operation_name}")

        # 记录 SDK 调用开始
        call_info: Dict[str, Any] = {
            "call_id": call_id,
            "operation": operation_name,
            "scope_id": scope_id,
            "start_time": start_time,
            "context": context or {},
            "status": "in_progress",
            "result": None,
            "result_received_at": None,
            "exception": None,
            "cancel_type": None
        }

        self.active_sdk_calls[call_id] = call_info
        self.stats["total_sdk_calls"] += 1

        logger.info(
            f"[SDK Tracking] Started: {operation_name} "
            f"(call_id={call_id[:8]}..., scope={scope_id[:8] if scope_id else 'none'}...)"
        )

        try:
            # 执行 SDK 操作
            yield call_info

            # 成功完成
            call_info["status"] = "completed"
            call_info["end_time"] = datetime.now()
            duration_value = (call_info["end_time"] - start_time).total_seconds()
            call_info["duration"] = duration_value

            self.stats["successful_completions"] += 1
            self.completed_calls.append(call_info.copy())

            logger.info(
                f"[SDK Tracking] Completed: {operation_name} "
                f"(duration={call_info['duration']:.2f}s)"
            )

        except asyncio.CancelledError as e:
            # 取消检测
            call_info["status"] = "cancelled"
            call_info["end_time"] = datetime.now()
            call_info["exception"] = str(e)
            duration_value = (call_info["end_time"] - start_time).total_seconds()
            call_info["duration"] = duration_value

            # 🎯 关键：检查是否是"成功后取消"
            if call_info.get("result") is not None:
                call_info["cancel_type"] = "after_success"
                self.stats["cancel_after_success"] += 1

                logger.warning(
                    f"[SDK Tracking] ⚠️ Cancelled AFTER success: {operation_name} "
                    f"(duration={call_info['duration']:.2f}s, "
                    f"result={str(call_info['result'])[:50]})"
                )
            else:
                call_info["cancel_type"] = "before_completion"

                logger.info(
                    f"[SDK Tracking] Cancelled: {operation_name} "
                    f"(duration={call_info['duration']:.2f}s)"
                )

            self.stats["cancellations"] += 1
            self.cancelled_calls.append(call_info.copy())

            # 重新抛出，让上层决定如何处理
            raise

        except Exception as e:
            # 错误处理
            call_info["status"] = "failed"
            call_info["end_time"] = datetime.now()
            call_info["exception"] = str(e)
            duration_value = (call_info["end_time"] - start_time).total_seconds()
            call_info["duration"] = duration_value

            self.stats["failures"] += 1
            self.failed_calls.append(call_info.copy())

            logger.error(
                f"[SDK Tracking] Failed: {operation_name} "
                f"(duration={call_info['duration']:.2f}s, error={e})"
            )

            raise

        finally:
            # 清理
            if call_id in self.active_sdk_calls:
                del self.active_sdk_calls[call_id]

            # 🎯 标记清理完成
            if call_info["status"] == "cancelled":
                call_info["cleanup_completed"] = True
                logger.debug(
                    f"[SDK Tracking] Cleanup completed for {call_id[:8]}..."
                )

            # 退出 cancel scope - 捕获跨任务cancel scope错误
            if self.tracker and scope_id:
                exception = call_info.get("exception")
                try:
                    self.tracker.exit_scope(
                        scope_id,
                        name=f"sdk_{operation_name}",
                        exception=Exception(exception) if exception else None
                    )
                except RuntimeError as e:
                    # 忽略跨任务cancel scope错误 - 这是已知的SDK清理问题
                    if "cancel scope" in str(e).lower() and "different task" in str(e).lower():
                        logger.debug(
                            f"[SDK Tracking] Ignored cross-task cancel scope error during cleanup "
                            f"(expected behavior for SDK operations)"
                        )
                    else:
                        # 重新抛出其他RuntimeError
                        raise

    def mark_result_received(self, call_id: str, result: Any):
        """
        标记 SDK 结果已接收

        🎯 关键方法：在 SDK 成功返回结果后立即调用
        用于检测"成功后取消"场景

        Args:
            call_id: 调用标识
            result: SDK 返回的结果
        """
        if call_id in self.active_sdk_calls:
            self.active_sdk_calls[call_id]["result"] = result
            self.active_sdk_calls[call_id]["result_received_at"] = datetime.now()

            result_preview = str(result)[:100]
            logger.debug(
                f"[SDK Tracking] Result received for {call_id[:8]}...: "
                f"{result_preview}"
            )

            # 🎯 增强：立即记录结果接收，用于 cancel scope 错误恢复
            logger.info(
                f"[SDK Tracking] ✅ Result confirmed for {call_id[:8]}... "
                f"(result_preview: {result_preview})"
            )

    async def wait_for_cancellation_complete(
        self,
        call_id: str,
        timeout: float = 5.0
    ) -> bool:
        """
        等待 SDK 取消完全完成

        🎯 强制同步点：Agent 必须等待此方法返回 True 才能继续

        Args:
            call_id: 调用标识
            timeout: 超时时间（秒）

        Returns:
            True if cancellation completed successfully
        """
        if call_id not in self.active_sdk_calls:
            # 已经清理完成
            return True

        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            if call_id not in self.active_sdk_calls:
                logger.info(f"[SDK Tracking] Cancellation completed for {call_id[:8]}...")
                return True

            # ⚠️ 等待时间延长至 0.5s，确保资源清理完全完成
            await asyncio.sleep(0.5)

        logger.warning(
            f"[SDK Tracking] Cancellation timeout for {call_id[:8]}... "
            f"after {timeout}s"
        )
        return False

    def confirm_safe_to_proceed(self, call_id: str) -> bool:
        """
        确认 SDK 可以安全继续

        🎯 Agent 在继续执行前必须调用此方法

        Args:
            call_id: 调用标识

        Returns:
            True if safe to proceed, False otherwise
        """
        # 检查是否还在活动列表中
        if call_id in self.active_sdk_calls:
            logger.warning(
                f"[SDK Tracking] Not safe to proceed - {call_id[:8]}... "
                f"still active"
            )
            return False

        # 检查是否在取消列表中且未完全清理
        for cancelled_call in self.cancelled_calls:
            if cancelled_call["call_id"] == call_id:
                # 检查清理标志
                if not cancelled_call.get("cleanup_completed", False):
                    logger.warning(
                        f"[SDK Tracking] Not safe to proceed - {call_id[:8]}... "
                        f"cleanup not completed"
                    )
                    return False

        logger.debug(f"[SDK Tracking] Safe to proceed for {call_id[:8]}...")
        return True

    def check_cancellation_type(
        self,
        call_id: str
    ) -> Literal["before_completion", "after_success", "unknown"]:
        """
        检查取消类型

        Args:
            call_id: 调用标识

        Returns:
            取消类型：
            - "after_success": 成功后被取消
            - "before_completion": 完成前被取消
            - "unknown": 未知
        """
        # 检查已取消的调用
        for call in self.cancelled_calls:
            if call["call_id"] == call_id:
                return call.get("cancel_type", "unknown")

        # 检查活动调用
        if call_id in self.active_sdk_calls:
            call_info = self.active_sdk_calls[call_id]
            if call_info.get("result") is not None:
                return "after_success"

        return "unknown"

    def detect_cross_task_risk(self, call_id: str) -> bool:
        """
        检测跨 Task 风险

        🎯 增强监控：检测 SDK 调用是否可能在不同 Task 中被清理

        Args:
            call_id: 调用标识

        Returns:
            True if cross-task risk detected, False otherwise
        """
        if call_id not in self.active_sdk_calls:
            return False

        call_info = self.active_sdk_calls[call_id]
        creation_task = call_info.get("creation_task_id")
        current_task = asyncio.current_task()

        # 检查是否有任务跟踪信息
        if not creation_task:
            # 如果没有创建任务ID，记录当前任务作为创建任务
            call_info["creation_task_id"] = str(id(current_task))
            call_info["creation_task_name"] = current_task.get_name() if current_task else "no_task"
            return False

        # 检查当前任务是否与创建任务相同
        current_task_id = str(id(current_task)) if current_task else "no_task"

        if creation_task != current_task_id:
            logger.warning(
                f"[Risk Detected] SDK call {call_id[:8]}... "
                f"may be cleaned up in different task "
                f"(created: {call_info.get('creation_task_name', 'unknown')}, "
                f"current: {current_task.get_name() if current_task else 'no_task'})"
            )
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats: Dict[str, Any] = {
            "total_sdk_calls": self.stats["total_sdk_calls"],
            "successful_completions": self.stats["successful_completions"],
            "cancellations": self.stats["cancellations"],
            "cancel_after_success": self.stats["cancel_after_success"],
            "failures": self.stats["failures"],
            "cross_task_violations": self.stats["cross_task_violations"]
        }

        # 计算比率
        total = stats["total_sdk_calls"]
        if total > 0:
            stats["success_rate"] = stats["successful_completions"] / total
            stats["cancellation_rate"] = stats["cancellations"] / total
            stats["failure_rate"] = stats["failures"] / total
            stats["cancel_after_success_rate"] = stats["cancel_after_success"] / total
        else:
            stats["success_rate"] = 0.0
            stats["cancellation_rate"] = 0.0
            stats["failure_rate"] = 0.0
            stats["cancel_after_success_rate"] = 0.0

        # 添加跨任务清理统计
        if self.tracker:
            tracker_stats = self.tracker.get_scope_statistics()
            stats["cross_task_cleanups"] = tracker_stats.get("cross_task_cleanups", 0)

        # 🎯 新增：检查活动调用中的跨任务风险
        cross_task_risks = 0
        for call_id in self.active_sdk_calls:
            if self.detect_cross_task_risk(call_id):
                cross_task_risks += 1

        stats["active_cross_task_risks"] = cross_task_risks

        return stats

    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """
        生成诊断报告

        Args:
            save_to_file: 是否保存到文件

        Returns:
            完整的诊断报告
        """
        report: Dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0.0",
                "system_version": "BMAD 2.0.0"
            },
            "summary": self.get_statistics(),
            "active_operations": [
                {
                    "call_id": call_id,
                    "operation": info["operation"],
                    "duration": (
                        datetime.now() - info["start_time"]
                    ).total_seconds(),
                    "status": info["status"]
                }
                for call_id, info in self.active_sdk_calls.items()
            ],
            "completed_calls": self.completed_calls[-10:],  # 最近 10 个
            "cancelled_calls": self.cancelled_calls,
            "failed_calls": self.failed_calls,
            "recommendations": []
        }

        # 添加 cancel scope 分析
        if self.tracker:
            report["cancel_scope_analysis"] = {
                "statistics": self.tracker.get_scope_statistics(),
                "active_scopes": self.tracker.get_active_scopes_info()
            }

        # 添加资源使用情况
        if self.resource_monitor:
            report["resource_usage"] = {
                "locks": self.resource_monitor.lock_monitor.get_statistics(),
                "sdk_sessions": {
                    "total": len(self.resource_monitor.session_monitor.active_sessions),
                    "active": len([
                        s for s in self.resource_monitor.session_monitor.active_sessions.values()
                        if s["status"] == "executing"
                    ])
                }
            }

        # 生成建议
        recommendations = self._generate_recommendations(report)
        report["recommendations"] = recommendations

        # 保存到文件
        if save_to_file:
            report_file = self.log_dir / f"sdk_cancellation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Cancellation report saved to {report_file}")

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        summary = report["summary"]

        # 检查成功后取消
        if summary["cancel_after_success"] > 0:
            recommendations.append(
                f"⚠️ {summary['cancel_after_success']} cancellations occurred after "
                f"successful completion - consider suppressing these cancellations"
            )

        # 检查跨任务违规
        if summary["cross_task_violations"] > 0:
            recommendations.append(
                f"❌ {summary['cross_task_violations']} cross-task cancel scope "
                f"violations detected - review task isolation"
            )

        # 检查成功率
        if summary["success_rate"] < 0.8:
            recommendations.append(
                f"⚠️ Success rate is low ({summary['success_rate']:.1%}) - "
                f"investigate failure causes"
            )
        elif summary["success_rate"] > 0.9:
            recommendations.append(
                f"✅ Success rate is healthy ({summary['success_rate']:.1%})"
            )

        # 检查取消率
        if summary["cancellation_rate"] > 0.2:
            recommendations.append(
                f"⚠️ High cancellation rate ({summary['cancellation_rate']:.1%}) - "
                f"consider timeout adjustments"
            )

        return recommendations

    def print_summary(self):
        """打印摘要到控制台"""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("          SDK Cancellation Manager - Live Status")
        print("=" * 70)

        print(f"Statistics:")
        print(f"  Total SDK Calls:      {stats['total_sdk_calls']}")
        print(f"  Successful:           {stats['successful_completions']} "
              f"({stats['success_rate']:.1%})")
        print(f"  Cancelled:            {stats['cancellations']} "
              f"({stats['cancellation_rate']:.1%})")
        print(f"    └─ After Success:   {stats['cancel_after_success']} "
              f"({stats['cancel_after_success_rate']:.1%})")
        print(f"  Failed:               {stats['failures']} "
              f"({stats['failure_rate']:.1%})")

        # 活动操作
        active_ops = [
            {
                "call_id": call_id,
                "operation": info["operation"],
                "duration": (datetime.now() - info["start_time"]).total_seconds()
            }
            for call_id, info in self.active_sdk_calls.items()
        ]

        print(f"\nActive Operations: {len(active_ops)}")
        for op in active_ops:
            print(f"  • {op['call_id'][:8]}... ({op['operation']}) - "
                  f"Running for {op['duration']:.1f}s")

        # Cancel Scope 状态
        if self.tracker:
            scope_stats = self.tracker.get_scope_statistics()
            print(f"\nCancel Scope Status:")
            print(f"  Active Scopes:        {scope_stats['active_scopes']}")
            print(f"  Cross-task Cleanups:  {scope_stats.get('cross_task_cleanups', 0)}")

        print("=" * 70)


# 全局单例
_global_manager: Optional[SDKCancellationManager] = None


def get_cancellation_manager(
    log_dir: Optional[Path] = None,
    enable_tracking: bool = True,
    enable_monitoring: bool = True,
    enable_debugging: bool = True
) -> SDKCancellationManager:
    """
    获取全局 SDK 取消管理器实例

    Args:
        log_dir: 日志目录
        enable_tracking: 启用 cancel scope 追踪
        enable_monitoring: 启用资源监控
        enable_debugging: 已弃用参数（保留以保持向下兼容，调试功能已移除）

    Returns:
        全局管理器实例
    """
    global _global_manager

    if _global_manager is None:
        _global_manager = SDKCancellationManager(
            log_dir=log_dir,
            enable_tracking=enable_tracking,
            enable_monitoring=enable_monitoring,
            enable_debugging=enable_debugging
        )

    return _global_manager


def reset_cancellation_manager():
    """重置全局管理器（用于测试）"""
    global _global_manager
    _global_manager = None
