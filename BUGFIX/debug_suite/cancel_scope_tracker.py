"""
Cancel Scope追踪器 - Cancel Scope Tracker

专门用于追踪和诊断cancel scope相关的问题，特别是跨任务cancel scope错误。
"""

import asyncio
import logging
import traceback
import weakref
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import uuid


class ScopeEvent:
    """Cancel scope事件"""

    def __init__(self, event_type: str, scope_id: str, task_id: int, details: Dict[str, Any]):
        self.event_type = event_type  # enter, exit, cancel, error
        self.scope_id = scope_id
        self.task_id = task_id
        self.timestamp = datetime.now()
        self.details = details.copy()
        self.stack_trace = traceback.format_stack()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "scope_id": self.scope_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "stack_trace": "".join(self.stack_trace)
        }


class CancelScopeTracker:
    """Cancel Scope追踪器"""

    def __init__(self, log_file: Optional[Path] = None):
        self.active_scopes: Dict[str, Dict[str, Any]] = {}
        self.events: List[ScopeEvent] = []
        self.scope_to_tasks: Dict[str, Set[int]] = {}
        self.errors: List[ScopeEvent] = []
        self.log_file = log_file or Path("cancel_scope_tracker.log")

        # 设置日志
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("cancel_scope_tracker")
        logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _get_current_task_id(self) -> int:
        """获取当前任务ID"""
        task = asyncio.current_task()
        return id(task) if task else 0

    def _get_current_task_name(self) -> str:
        """获取当前任务名称"""
        task = asyncio.current_task()
        return task.get_name() if task else "no_task"

    def enter_scope(self, scope_id: Optional[str] = None, name: str = "unnamed") -> str:
        """进入cancel scope"""
        if scope_id is None:
            scope_id = str(uuid.uuid4())

        task_id = self._get_current_task_id()
        task_name = self._get_current_task_name()

        # 记录scope信息
        self.active_scopes[scope_id] = {
            "name": name,
            "entered_by_task": task_id,
            "entered_by_task_name": task_name,
            "entered_at": datetime.now(),
            "cancel_requested": False
        }

        # 记录任务与scope的关联
        if scope_id not in self.scope_to_tasks:
            self.scope_to_tasks[scope_id] = set()
        self.scope_to_tasks[scope_id].add(task_id)

        # 记录事件
        event = ScopeEvent(
            "enter",
            scope_id,
            task_id,
            {
                "name": name,
                "task_name": task_name,
                "active_scopes_count": len(self.active_scopes)
            }
        )
        self.events.append(event)
        self.logger.debug(f"Entered scope {scope_id} ({name}) in task {task_name}")

        return scope_id

    def exit_scope(self, scope_id: str, name: Optional[str] = None, exception: Optional[Exception] = None):
        """退出cancel scope"""
        if scope_id not in self.active_scopes:
            self.logger.warning(f"Attempted to exit non-existent scope: {scope_id}")
            return

        task_id = self._get_current_task_id()
        task_name = self._get_current_task_name()
        scope_info = self.active_scopes[scope_id]

        # 检查是否是跨任务访问
        if scope_info["entered_by_task"] != task_id:
            error_msg = (
                f"Cross-task cancel scope access detected! "
                f"Scope {scope_id} entered by task {scope_info['entered_by_task_name']} "
                f"but exited by task {task_name}"
            )
            self.logger.error(error_msg)

            # 记录错误事件
            error_event = ScopeEvent(
                "error",
                scope_id,
                task_id,
                {
                    "error_type": "cross_task_access",
                    "error_message": error_msg,
                    "original_task": scope_info["entered_by_task"],
                    "original_task_name": scope_info["entered_by_task_name"],
                    "current_task": task_id,
                    "current_task_name": task_name
                }
            )
            self.errors.append(error_event)

        # 记录退出事件
        exit_event = ScopeEvent(
            "exit",
            scope_id,
            task_id,
            {
                "name": name or scope_info["name"],
                "task_name": task_name,
                "duration_ms": (datetime.now() - scope_info["entered_at"]).total_seconds() * 1000,
                "exception": str(exception) if exception else None,
                "cancel_requested": scope_info["cancel_requested"]
            }
        )
        self.events.append(exit_event)

        # 清理
        del self.active_scopes[scope_id]
        if scope_id in self.scope_to_tasks:
            self.scope_to_tasks[scope_id].discard(task_id)
            if not self.scope_to_tasks[scope_id]:
                del self.scope_to_tasks[scope_id]

        self.logger.debug(f"Exited scope {scope_id} ({name or scope_info['name']})")

    def request_cancel(self, scope_id: str):
        """请求取消scope"""
        if scope_id in self.active_scopes:
            self.active_scopes[scope_id]["cancel_requested"] = True
            task_id = self._get_current_task_id()

            event = ScopeEvent(
                "cancel",
                scope_id,
                task_id,
                {
                    "requested_by_task": self._get_current_task_name()
                }
            )
            self.events.append(event)
            self.logger.debug(f"Cancel requested for scope {scope_id}")

    def check_cross_task_violations(self) -> List[Dict[str, Any]]:
        """检查跨任务违规"""
        violations = []

        for event in self.events:
            if event.event_type == "error" and event.details.get("error_type") == "cross_task_access":
                violations.append(event.to_dict())

        return violations

    def get_active_scopes_info(self) -> List[Dict[str, Any]]:
        """获取活动scope信息"""
        scopes_info = []
        for scope_id, info in self.active_scopes.items():
            scopes_info.append({
                "scope_id": scope_id,
                "name": info["name"],
                "entered_by_task": info["entered_by_task"],
                "entered_by_task_name": info["entered_by_task_name"],
                "entered_at": info["entered_at"].isoformat(),
                "duration_ms": (datetime.now() - info["entered_at"]).total_seconds() * 1000,
                "cancel_requested": info["cancel_requested"],
                "associated_tasks": list(self.scope_to_tasks.get(scope_id, set()))
            })
        return scopes_info

    def get_scope_statistics(self) -> Dict[str, Any]:
        """获取scope统计信息"""
        total_events = len(self.events)
        enter_events = [e for e in self.events if e.event_type == "enter"]
        exit_events = [e for e in self.events if e.event_type == "exit"]
        cancel_events = [e for e in self.events if e.event_type == "cancel"]
        error_events = [e for e in self.events if e.event_type == "error"]

        return {
            "total_events": total_events,
            "active_scopes": len(self.active_scopes),
            "enter_events": len(enter_events),
            "exit_events": len(exit_events),
            "cancel_events": len(cancel_events),
            "error_events": len(error_events),
            "error_rate": len(error_events) / total_events if total_events > 0 else 0,
            "cross_task_violations": len(self.check_cross_task_violations())
        }

    def generate_report(self) -> Dict[str, Any]:
        """生成报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_scope_statistics(),
            "active_scopes": self.get_active_scopes_info(),
            "errors": [e.to_dict() for e in self.errors],
            "cross_task_violations": self.check_cross_task_violations(),
            "recent_events": [e.to_dict() for e in self.events[-10:]]  # 最近10个事件
        }

        # 保存报告
        report_file = self.log_file.with_suffix(".report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Cancel scope report saved to {report_file}")

        return report

    def print_summary(self):
        """打印摘要"""
        print("\n" + "="*70)
        print("Cancel Scope 追踪摘要")
        print("="*70)

        stats = self.get_scope_statistics()

        print(f"统计信息:")
        print(f"  总事件数: {stats['total_events']}")
        print(f"  活动Scopes: {stats['active_scopes']}")
        print(f"  进入事件: {stats['enter_events']}")
        print(f"  退出事件: {stats['exit_events']}")
        print(f"  取消事件: {stats['cancel_events']}")
        print(f"  错误事件: {stats['error_events']}")
        print(f"  错误率: {stats['error_rate']:.2%}")
        print(f"  跨任务违规: {stats['cross_task_violations']}")

        if stats['active_scopes'] > 0:
            print(f"\n活动Scopes:")
            for scope in self.get_active_scopes_info():
                duration = scope['duration_ms']
                print(f"  - {scope['name']} (ID: {scope['scope_id'][:8]})")
                print(f"    任务: {scope['entered_by_task_name']}")
                print(f"    持续时间: {duration:.1f}ms")
                if scope['cancel_requested']:
                    print(f"    ⚠️  已请求取消")

        if stats['cross_task_violations'] > 0:
            print(f"\n❌ 发现 {stats['cross_task_violations']} 个跨任务违规!")
            for violation in self.check_cross_task_violations():
                print(f"  - {violation['details']['error_message']}")

        if stats['error_events'] > 0:
            print(f"\n⚠️  总共 {stats['error_events']} 个错误事件")

        print("="*70)

    def save_events_log(self):
        """保存事件日志"""
        events_file = self.log_file.with_suffix(".events.json")
        events_data = [event.to_dict() for event in self.events]

        with open(events_file, "w") as f:
            json.dump(events_data, f, indent=2, default=str)

        self.logger.info(f"Events log saved to {events_file}")


# 全局追踪器实例
_global_tracker: Optional[CancelScopeTracker] = None


def get_tracker(log_file: Optional[Path] = None) -> CancelScopeTracker:
    """获取全局追踪器实例"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CancelScopeTracker(log_file)
    return _global_tracker


@asynccontextmanager
async def tracked_cancel_scope(name: str = "unnamed"):
    """追踪cancel scope的上下文管理器"""
    tracker = get_tracker()
    scope_id = tracker.enter_scope(name=name)

    try:
        yield scope_id
    except Exception as e:
        tracker.exit_scope(scope_id, name, e)
        raise
    else:
        tracker.exit_scope(scope_id, name)


def track_scope_enter(name: str = "unnamed") -> str:
    """追踪进入scope"""
    tracker = get_tracker()
    return tracker.enter_scope(name=name)


def track_scope_exit(scope_id: str, name: Optional[str] = None, exception: Optional[Exception] = None):
    """追踪退出scope"""
    tracker = get_tracker()
    tracker.exit_scope(scope_id, name, exception)


if __name__ == "__main__":
    # 测试用例
    async def test_cross_task_violation():
        """测试跨任务违规检测"""
        tracker = CancelScopeTracker(Path("test_cancel_scope.log"))

        async def task_that_enters():
            async with tracked_cancel_scope("task_scope"):
                await asyncio.sleep(0.1)
                return "Task completed"

        # 创建任务
        task1 = asyncio.create_task(task_that_enters())
        task2 = asyncio.create_task(task_that_enters())

        await asyncio.gather(task1, task2)

        tracker.print_summary()
        report = tracker.generate_report()
        print(f"\n报告已保存")
        print(f"跨任务违规: {len(report['cross_task_violations'])}")

    asyncio.run(test_cross_task_violation())
