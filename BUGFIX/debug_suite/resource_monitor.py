"""
资源监控器 - Resource Monitor

监控系统资源使用情况，包括锁、会话、任务等资源的状态和生命周期。
"""

import asyncio
import gc
import logging
import psutil
import sys
import time
import traceback
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import weakref


class ResourceEvent:
    """资源事件"""

    def __init__(self, event_type: str, resource_type: str, resource_id: str, details: Dict[str, Any]):
        self.event_type = event_type  # acquire, release, timeout, error
        self.resource_type = resource_type  # lock, session, task, memory
        self.resource_id = resource_id
        self.timestamp = datetime.now()
        self.details = details.copy()
        self.stack_trace = traceback.format_stack()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "stack_trace": "".join(self.stack_trace)
        }


class LockMonitor:
    """锁监控器"""

    def __init__(self):
        self.acquired_locks: Dict[str, Dict[str, Any]] = {}
        self.lock_history: List[ResourceEvent] = []
        self.lock_timeouts: List[ResourceEvent] = []
        self.max_lock_duration = 30.0  # 30秒超时

    def acquire_lock(self, lock_name: str, owner_task_id: int, owner_task_name: str):
        """记录锁获取"""
        self.acquired_locks[lock_name] = {
            "acquired_at": datetime.now(),
            "owner_task_id": owner_task_id,
            "owner_task_name": owner_task_name,
            "acquisition_count": self.acquired_locks.get(lock_name, {}).get("acquisition_count", 0) + 1
        }

        event = ResourceEvent("acquire", "lock", lock_name, {
            "owner_task_id": owner_task_id,
            "owner_task_name": owner_task_name,
            "acquisition_count": self.acquired_locks[lock_name]["acquisition_count"]
        })
        self.lock_history.append(event)

    def release_lock(self, lock_name: str):
        """记录锁释放"""
        if lock_name in self.acquired_locks:
            lock_info = self.acquired_locks.pop(lock_name)
            duration = (datetime.now() - lock_info["acquired_at"]).total_seconds()

            event = ResourceEvent("release", "lock", lock_name, {
                "duration": duration,
                "owner_task_id": lock_info["owner_task_id"],
                "owner_task_name": lock_info["owner_task_name"]
            })
            self.lock_history.append(event)

            # 检查超时
            if duration > self.max_lock_duration:
                timeout_event = ResourceEvent("timeout", "lock", lock_name, {
                    "duration": duration,
                    "max_allowed": self.max_lock_duration,
                    "owner_task_id": lock_info["owner_task_id"]
                })
                self.lock_timeouts.append(timeout_event)

    def get_active_locks(self) -> List[Dict[str, Any]]:
        """获取活动锁列表"""
        locks = []
        for lock_name, lock_info in self.acquired_locks.items():
            duration = (datetime.now() - lock_info["acquired_at"]).total_seconds()
            locks.append({
                "lock_name": lock_name,
                "duration": duration,
                "owner_task_id": lock_info["owner_task_id"],
                "owner_task_name": lock_info["owner_task_name"],
                "acquisition_count": lock_info["acquisition_count"],
                "is_timeout": duration > self.max_lock_duration
            })
        return locks

    def get_statistics(self) -> Dict[str, Any]:
        """获取锁统计信息"""
        total_acquisitions = len([e for e in self.lock_history if e.event_type == "acquire"])
        total_releases = len([e for e in self.lock_history if e.event_type == "release"])
        timeouts = len(self.lock_timeouts)

        if total_acquisitions > 0:
            durations = [
                e.details["duration"]
                for e in self.lock_history
                if e.event_type == "release"
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
        else:
            avg_duration = 0
            max_duration = 0

        return {
            "total_acquisitions": total_acquisitions,
            "total_releases": total_releases,
            "active_locks": len(self.acquired_locks),
            "timeout_count": timeouts,
            "avg_duration": avg_duration,
            "max_duration": max_duration,
            "leak_count": total_acquisitions - total_releases  # 未释放的锁
        }


class SessionMonitor:
    """会话监控器"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_history: List[ResourceEvent] = []
        self.session_errors: List[ResourceEvent] = []

    def create_session(self, session_id: str, session_type: str, owner_agent: str):
        """记录会话创建"""
        self.active_sessions[session_id] = {
            "session_type": session_type,
            "owner_agent": owner_agent,
            "created_at": datetime.now(),
            "status": "created"
        }

        event = ResourceEvent("create", "session", session_id, {
            "session_type": session_type,
            "owner_agent": owner_agent
        })
        self.session_history.append(event)

    def update_session_status(self, session_id: str, status: str, error: Optional[str] = None):
        """更新会话状态"""
        if session_id not in self.active_sessions:
            return

        self.active_sessions[session_id]["status"] = status
        self.active_sessions[session_id]["last_updated"] = datetime.now()

        event = ResourceEvent("update", "session", session_id, {
            "status": status,
            "error": error
        })
        self.session_history.append(event)

        if status in ["failed", "cancelled", "error"]:
            self.session_errors.append(event)

    def close_session(self, session_id: str):
        """记录会话关闭"""
        if session_id not in self.active_sessions:
            return

        session_info = self.active_sessions.pop(session_id)
        duration = (datetime.now() - session_info["created_at"]).total_seconds()

        event = ResourceEvent("close", "session", session_id, {
            "duration": duration,
            "session_type": session_info["session_type"],
            "owner_agent": session_info["owner_agent"],
            "final_status": session_info["status"]
        })
        self.session_history.append(event)

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活动会话"""
        sessions = []
        for session_id, info in self.active_sessions.items():
            duration = (datetime.now() - info["created_at"]).total_seconds()
            sessions.append({
                "session_id": session_id,
                "session_type": info["session_type"],
                "owner_agent": info["owner_agent"],
                "duration": duration,
                "status": info["status"]
            })
        return sessions

    def get_statistics(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        total_sessions = len(self.session_history)
        created_sessions = len([e for e in self.session_history if e.event_type == "create"])
        closed_sessions = len([e for e in self.session_history if e.event_type == "close"])
        error_sessions = len(self.session_errors)

        success_rate = 0
        if closed_sessions > 0:
            successful_closes = len([
                e for e in self.session_history
                if e.event_type == "close" and e.details.get("final_status") == "completed"
            ])
            success_rate = successful_closes / closed_sessions

        return {
            "total_sessions": total_sessions,
            "active_sessions": len(self.active_sessions),
            "created_sessions": created_sessions,
            "closed_sessions": closed_sessions,
            "error_sessions": error_sessions,
            "success_rate": success_rate,
            "error_rate": error_sessions / created_sessions if created_sessions > 0 else 0
        }


class TaskMonitor:
    """任务监控器"""

    def __init__(self):
        self.tasks: Dict[int, Dict[str, Any]] = {}
        self.task_history: List[ResourceEvent] = []
        self.long_running_tasks: List[ResourceEvent] = []

    def track_task_creation(self, task_id: int, task_name: str, coro_info: str):
        """跟踪任务创建"""
        self.tasks[task_id] = {
            "task_name": task_name,
            "created_at": datetime.now(),
            "status": "running",
            "coro_info": coro_info
        }

        event = ResourceEvent("create", "task", str(task_id), {
            "task_name": task_name,
            "coro_info": coro_info
        })
        self.task_history.append(event)

    def track_task_completion(self, task_id: int, status: str = "completed"):
        """跟踪任务完成"""
        if task_id not in self.tasks:
            return

        task_info = self.tasks.pop(task_id)
        duration = (datetime.now() - task_info["created_at"]).total_seconds()

        event = ResourceEvent("complete", "task", str(task_id), {
            "duration": duration,
            "status": status,
            "task_name": task_info["task_name"]
        })
        self.task_history.append(event)

        # 检查长任务
        if duration > 10.0:  # 超过10秒的任务
            long_task_event = ResourceEvent("long_running", "task", str(task_id), {
                "duration": duration,
                "task_name": task_info["task_name"]
            })
            self.long_running_tasks.append(long_task_event)

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取活动任务"""
        tasks = []
        for task_id, info in self.tasks.items():
            duration = (datetime.now() - info["created_at"]).total_seconds()
            tasks.append({
                "task_id": task_id,
                "task_name": info["task_name"],
                "duration": duration,
                "status": info["status"],
                "coro_info": info["coro_info"]
            })
        return tasks

    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        total_tasks = len(self.task_history)
        completed_tasks = len([e for e in self.task_history if e.event_type == "complete"])
        active_tasks = len(self.tasks)
        long_running = len(self.long_running_tasks)

        return {
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "long_running_tasks": long_running,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
        }


class SystemMonitor:
    """系统资源监控器"""

    def __init__(self):
        self.cpu_samples: deque = deque(maxlen=100)
        self.memory_samples: deque = deque(maxlen=100)
        self.monitor_start = datetime.now()

    def collect_system_stats(self):
        """收集系统统计信息"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_samples.append((datetime.now(), cpu_percent))

        # 内存使用率
        memory = psutil.virtual_memory()
        self.memory_samples.append((datetime.now(), memory.percent))

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        if not self.cpu_samples or not self.memory_samples:
            return {}

        avg_cpu = sum(sample[1] for sample in self.cpu_samples) / len(self.cpu_samples)
        avg_memory = sum(sample[1] for sample in self.memory_samples) / len(self.memory_samples)

        current_memory = psutil.virtual_memory()
        process = psutil.Process()

        return {
            "monitoring_duration": (datetime.now() - self.monitor_start).total_seconds(),
            "cpu": {
                "current": self.cpu_samples[-1][1] if self.cpu_samples else 0,
                "average": avg_cpu,
                "samples_count": len(self.cpu_samples)
            },
            "memory": {
                "current_percent": self.memory_samples[-1][1] if self.memory_samples else 0,
                "average_percent": avg_memory,
                "available_gb": current_memory.available / (1024**3),
                "used_gb": current_memory.used / (1024**3),
                "total_gb": current_memory.total / (1024**3)
            },
            "process": {
                "memory_mb": process.memory_info().rss / (1024**2),
                "cpu_percent": process.cpu_percent()
            }
        }


class ResourceMonitor:
    """资源监控器主类"""

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path("resource_monitor.log")
        self.lock_monitor = LockMonitor()
        self.session_monitor = SessionMonitor()
        self.task_monitor = TaskMonitor()
        self.system_monitor = SystemMonitor()

        # 设置日志
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("resource_monitor")
        logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    @asynccontextmanager
    async def monitor_lock(self, lock_name: str):
        """监控锁的上下文管理器"""
        task = asyncio.current_task()
        owner_task_id = id(task) if task else 0
        owner_task_name = task.get_name() if task else "no_task"

        self.lock_monitor.acquire_lock(lock_name, owner_task_id, owner_task_name)
        self.logger.debug(f"Lock acquired: {lock_name} by {owner_task_name}")

        try:
            yield
        finally:
            self.lock_monitor.release_lock(lock_name)
            self.logger.debug(f"Lock released: {lock_name}")

    @asynccontextmanager
    async def monitor_session(self, session_id: str, session_type: str, owner_agent: str):
        """监控会话的上下文管理器"""
        self.session_monitor.create_session(session_id, session_type, owner_agent)
        self.logger.debug(f"Session created: {session_id} ({session_type})")

        try:
            yield
        except Exception as e:
            self.session_monitor.update_session_status(session_id, "failed", str(e))
            self.logger.error(f"Session failed: {session_id} - {e}")
            raise
        else:
            self.session_monitor.update_session_status(session_id, "completed")
            self.logger.debug(f"Session completed: {session_id}")
        finally:
            self.session_monitor.close_session(session_id)
            self.logger.debug(f"Session closed: {session_id}")

    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """获取综合统计信息"""
        # 收集系统统计
        self.system_monitor.collect_system_stats()
        system_stats = self.system_monitor.get_system_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "locks": self.lock_monitor.get_statistics(),
            "sessions": self.session_monitor.get_statistics(),
            "tasks": self.task_monitor.get_statistics(),
            "system": system_stats,
            "active_resources": {
                "locks": self.lock_monitor.get_active_locks(),
                "sessions": self.session_monitor.get_active_sessions(),
                "tasks": self.task_monitor.get_active_tasks()
            }
        }

    def generate_report(self) -> Dict[str, Any]:
        """生成资源监控报告"""
        report = self.get_comprehensive_statistics()

        # 保存报告
        report_file = self.log_file.with_suffix(".report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Resource monitor report saved to {report_file}")

        return report

    def print_summary(self):
        """打印资源监控摘要"""
        print("\n" + "="*70)
        print("资源监控摘要")
        print("="*70)

        stats = self.get_comprehensive_statistics()

        # 锁统计
        lock_stats = stats["locks"]
        print(f"锁统计:")
        print(f"  活动锁: {lock_stats['active_locks']}")
        print(f"  总获取: {lock_stats['total_acquisitions']}")
        print(f"  平均持续时间: {lock_stats['avg_duration']:.2f}s")
        print(f"  超时次数: {lock_stats['timeout_count']}")
        print(f"  泄漏数量: {lock_stats['leak_count']}")

        if lock_stats['active_locks'] > 0:
            print(f"\n活动锁详情:")
            for lock in self.lock_monitor.get_active_locks():
                print(f"  - {lock['lock_name']}: {lock['duration']:.1f}s ({lock['owner_task_name']})")
                if lock['is_timeout']:
                    print(f"    ⚠️  已超时!")

        # 会话统计
        session_stats = stats["sessions"]
        print(f"\n会话统计:")
        print(f"  活动会话: {session_stats['active_sessions']}")
        print(f"  总会话数: {session_stats['created_sessions']}")
        print(f"  成功率: {session_stats['success_rate']:.2%}")
        print(f"  错误率: {session_stats['error_rate']:.2%}")

        if session_stats['error_sessions'] > 0:
            print(f"  ⚠️  {session_stats['error_sessions']} 个失败会话!")

        # 任务统计
        task_stats = stats["tasks"]
        print(f"\n任务统计:")
        print(f"  活动任务: {task_stats['active_tasks']}")
        print(f"  总任务数: {task_stats['total_tasks']}")
        print(f"  长任务数: {task_stats['long_running_tasks']}")
        print(f"  完成率: {task_stats['completion_rate']:.2%}")

        # 系统统计
        if "system" in stats and stats["system"]:
            system = stats["system"]
            print(f"\n系统资源:")
            print(f"  CPU: {system['cpu']['current']:.1f}% (平均: {system['cpu']['average']:.1f}%)")
            print(f"  内存: {system['memory']['current_percent']:.1f}% (平均: {system['memory']['average_percent']:.1f}%)")
            print(f"  可用内存: {system['memory']['available_gb']:.1f}GB")
            print(f"  进程内存: {system['process']['memory_mb']:.1f}MB")

        print("="*70)


# 全局资源监控器实例
_global_resource_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor(log_file: Optional[Path] = None) -> ResourceMonitor:
    """获取全局资源监控器实例"""
    global _global_resource_monitor
    if _global_resource_monitor is None:
        _global_resource_monitor = ResourceMonitor(log_file)
    return _global_resource_monitor


if __name__ == "__main__":
    # 测试用例
    async def test_resource_monitor():
        monitor = ResourceMonitor(Path("test_resource.log"))

        # 测试锁监控
        async with monitor.monitor_lock("test_lock"):
            await asyncio.sleep(0.1)

        # 测试会话监控
        async with monitor.monitor_session("test_session", "sdk", "test_agent"):
            await asyncio.sleep(0.1)

        monitor.print_summary()
        report = monitor.generate_report()
        print(f"\n报告已保存到: {monitor.log_file.with_suffix('.report.json')}")

    asyncio.run(test_resource_monitor())
