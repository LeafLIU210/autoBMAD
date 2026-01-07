"""
Debug Dashboard

提供实时调试监控仪表板，显示异步操作、cancel scope错误、
性能指标和系统资源使用情况。

Version: 1.0.0
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.operations: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.cancel_scope_errors: List[Dict[str, Any]] = []
        self.max_history = 1000

    def add_operation(
        self,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加操作指标"""
        op_data = {
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }

        self.operations.append(op_data)

        # 保持历史记录限制
        if len(self.operations) > self.max_history:
            self.operations = self.operations[-self.max_history:]

    def add_error(
        self,
        error_type: str,
        message: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加错误指标"""
        error_data = {
            "error_type": error_type,
            "message": message,
            "operation": operation,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }

        self.errors.append(error_data)

        # 保持历史记录限制
        if len(self.errors) > self.max_history:
            self.errors = self.errors[-self.max_history:]

        # 如果是cancel scope错误，也添加到专门列表
        if "cancel" in error_type.lower():
            self.cancel_scope_errors.append(error_data)
            if len(self.cancel_scope_errors) > self.max_history:
                self.cancel_scope_errors = self.cancel_scope_errors[-self.max_history:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        now = time.time()

        # 计算成功率
        total_ops = len(self.operations)
        successful_ops = sum(1 for op in self.operations if op["success"])
        success_rate = (successful_ops / total_ops) if total_ops > 0 else 0

        # 计算平均持续时间
        avg_duration = (
            sum(op["duration"] for op in self.operations) / total_ops
            if total_ops > 0 else 0
        )

        # 计算错误率
        error_rate = (len(self.errors) / total_ops) if total_ops > 0 else 0

        # 计算最近1分钟的指标
        recent_ops = [
            op for op in self.operations
            if now - op["timestamp"] < 60
        ]
        recent_success = sum(1 for op in recent_ops if op["success"])
        recent_success_rate = (
            (recent_success / len(recent_ops)) if recent_ops else 0
        )

        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "failed_operations": total_ops - successful_ops,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "error_rate": error_rate,
            "total_errors": len(self.errors),
            "cancel_scope_errors": len(self.cancel_scope_errors),
            "recent_operations": len(recent_ops),
            "recent_success_rate": recent_success_rate
        }


class SystemMonitor:
    """系统资源监控"""

    def __init__(self):
        self.process = psutil.Process() if PSUTIL_AVAILABLE else None

    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_mb": 0,
                "threads": 0,
                "status": "psutil not available"
            }

        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            process = self.process
            threads = process.num_threads() if process else 0

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_mb": memory.used / (1024 * 1024),
                "total_memory_mb": memory.total / (1024 * 1024),
                "threads": threads,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_mb": 0,
                "threads": 0,
                "status": f"error: {e}"
            }


class DebugDashboard:
    """调试仪表板主类"""

    def __init__(self, port: int = 8080, update_interval: float = 5.0):
        """
        初始化调试仪表板

        Args:
            port: 仪表板端口号
            update_interval: 更新间隔（秒）
        """
        self.port = port
        self.update_interval = update_interval
        self.running = False

        # 初始化组件
        self.metrics = MetricsCollector()
        self.system_monitor = SystemMonitor()

        # 状态
        self.status = {
            "running": False,
            "start_time": None,
            "last_update": None,
            "version": "1.0.0"
        }

        # 日志
        self.logger = logging.getLogger("debug_dashboard")

    async def start(self):
        """启动仪表板"""
        self.logger.info(f"Starting debug dashboard on port {self.port}")

        self.status["running"] = True
        self.status["start_time"] = time.time()

        # 启动主循环
        await self._main_loop()

    async def stop(self):
        """停止仪表板"""
        self.logger.info("Stopping debug dashboard")

        self.status["running"] = False

    async def _main_loop(self):
        """主循环"""
        while self.status["running"]:
            try:
                # 更新状态
                self.status["last_update"] = time.time()

                # 等待下一次更新
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(1)

    def update_metrics(
        self,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """更新指标"""
        self.metrics.add_operation(operation, duration, success, metadata)

    def record_error(
        self,
        error_type: str,
        message: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """记录错误"""
        self.metrics.add_error(error_type, message, operation, metadata)

        # 记录日志
        self.logger.error(f"Error recorded: {error_type} - {message}")

    def record_cancel_scope_error(
        self,
        message: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """记录cancel scope错误"""
        self.record_error(
            "CANCEL_SCOPE_ERROR",
            message,
            operation,
            metadata
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        # 收集所有指标
        metrics = self.metrics.get_statistics()
        system = self.system_monitor.get_system_metrics()

        # 计算运行时间
        uptime = (
            time.time() - self.status["start_time"]
            if self.status["start_time"] else 0
        )

        # 组合数据
        data = {
            "timestamp": datetime.now().isoformat(),
            "status": self.status,
            "metrics": metrics,
            "system": system,
            "operations": {
                "recent": self.metrics.operations[-10:] if self.metrics.operations else [],
                "slowest": self._get_slowest_operations(5),
                "most_frequent": self._get_most_frequent_operations(5)
            },
            "errors": {
                "recent": self.metrics.errors[-10:] if self.metrics.errors else [],
                "by_type": self._get_errors_by_type()
            },
            "cancel_scope": {
                "total_errors": len(self.metrics.cancel_scope_errors),
                "recent_errors": self.metrics.cancel_scope_errors[-5:] if self.metrics.cancel_scope_errors else [],
                "error_rate": self._calculate_cancel_scope_rate()
            }
        }

        return data

    def _get_slowest_operations(self, count: int) -> List[Dict[str, Any]]:
        """获取最慢的操作"""
        sorted_ops = sorted(
            self.metrics.operations,
            key=lambda x: x["duration"],
            reverse=True
        )
        return sorted_ops[:count]

    def _get_most_frequent_operations(self, count: int) -> List[Dict[str, Any]]:
        """获取最频繁的操作"""
        op_counts = {}
        for op in self.metrics.operations:
            op_name = op["operation"]
            if op_name not in op_counts:
                op_counts[op_name] = {
                    "operation": op_name,
                    "count": 0,
                    "total_duration": 0,
                    "success_count": 0
                }
            op_counts[op_name]["count"] += 1
            op_counts[op_name]["total_duration"] += op["duration"]
            if op["success"]:
                op_counts[op_name]["success_count"] += 1

        # 计算平均值并排序
        for op_data in op_counts.values():
            op_data["avg_duration"] = op_data["total_duration"] / op_data["count"]
            op_data["success_rate"] = op_data["success_count"] / op_data["count"]

        sorted_ops = sorted(
            op_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )

        return sorted_ops[:count]

    def _get_errors_by_type(self) -> Dict[str, int]:
        """按类型统计错误"""
        error_types = {}
        for error in self.metrics.errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types

    def _calculate_cancel_scope_rate(self) -> float:
        """计算cancel scope错误率"""
        total_ops = len(self.metrics.operations)
        cancel_scope_errors = len(self.metrics.cancel_scope_errors)

        return (cancel_scope_errors / total_ops) if total_ops > 0 else 0

    async def save_report(self, filepath: Path):
        """保存报告到文件"""
        data = self.get_dashboard_data()

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.info(f"Report saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}", exc_info=True)

    def print_summary(self):
        """打印摘要到控制台"""
        data = self.get_dashboard_data()
        metrics = data["metrics"]
        system = data["system"]

        print("\n" + "=" * 80)
        print("DEBUG DASHBOARD SUMMARY")
        print("=" * 80)

        print(f"\nOperations:")
        print(f"  Total: {metrics['total_operations']}")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Avg Duration: {metrics['avg_duration']:.2f}s")
        print(f"  Error Rate: {metrics['error_rate']:.2%}")

        print(f"\nErrors:")
        print(f"  Total Errors: {metrics['total_errors']}")
        print(f"  Cancel Scope Errors: {metrics['cancel_scope_errors']}")

        print(f"\nSystem:")
        print(f"  CPU: {system['cpu_percent']:.1f}%")
        print(f"  Memory: {system['memory_percent']:.1f}%")
        print(f"  Memory Used: {system['memory_mb']:.0f} MB")

        print("=" * 80 + "\n")


# 全局仪表板实例
_dashboard: Optional[DebugDashboard] = None


def get_dashboard(
    port: int = 8080,
    update_interval: float = 5.0
) -> DebugDashboard:
    """
    获取全局仪表板实例

    Args:
        port: 端口号
        update_interval: 更新间隔

    Returns:
        DebugDashboard实例
    """
    global _dashboard
    if _dashboard is None:
        _dashboard = DebugDashboard(port, update_interval)
    return _dashboard


async def start_dashboard(
    port: int = 8080,
    update_interval: float = 5.0
) -> DebugDashboard:
    """
    启动调试仪表板

    Args:
        port: 端口号
        update_interval: 更新间隔

    Returns:
        DebugDashboard实例
    """
    dashboard = get_dashboard(port, update_interval)
    await dashboard.start()
    return dashboard


if __name__ == "__main__":
    # 简单的演示
    async def demo():
        dashboard = DebugDashboard()

        # 模拟一些操作
        import random

        operations = ["sdk_session", "qa_review", "state_update", "cancel_scope_check"]

        for i in range(20):
            op = random.choice(operations)
            duration = random.uniform(0.1, 5.0)
            success = random.random() > 0.1  # 90% success rate

            dashboard.update_metrics(op, duration, success)

            if not success:
                dashboard.record_error(
                    "OPERATION_ERROR",
                    f"Operation {op} failed",
                    op
                )

            await asyncio.sleep(0.5)

        # 显示摘要
        dashboard.print_summary()

        # 保存报告
        await dashboard.save_report(Path("debug_dashboard_report.json"))

    asyncio.run(demo())
