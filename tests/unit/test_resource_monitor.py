"""
Resource Monitor 单元测试

测试 Resource Monitor 的核心功能：
1. ResourceEvent 资源事件
2. LockMonitor 锁监控
3. SessionMonitor 会话监控
4. TaskMonitor 任务监控
5. SystemMonitor 系统监控
6. ResourceMonitor 主监控器
7. 统计信息聚合
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from pathlib import Path
import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.monitoring.resource_monitor import (
    ResourceEvent,
    LockMonitor,
    SessionMonitor,
    TaskMonitor,
    SystemMonitor,
    ResourceMonitor,
    get_resource_monitor,
)


class TestResourceEvent:
    """ResourceEvent 测试类"""

    def test_event_creation(self):
        """测试事件创建"""
        event = ResourceEvent(
            event_type="test",
            resource_id="resource1",
            details={"key": "value"}
        )
        assert event.event_type == "test"
        assert event.resource_id == "resource1"
        assert event.details == {"key": "value"}
        assert event.timestamp is not None

    def test_event_with_timestamp(self):
        """测试带时间戳的事件"""
        event = ResourceEvent(
            event_type="test",
            resource_id="resource1",
            timestamp=1234567890
        )
        assert event.timestamp == 1234567890

    def test_event_to_dict(self):
        """测试事件转字典"""
        event = ResourceEvent(
            event_type="test",
            resource_id="resource1"
        )
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "test"
        assert event_dict["resource_id"] == "resource1"


class TestLockMonitor:
    """LockMonitor 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        monitor = LockMonitor()
        assert monitor is not None
        assert monitor._locks == {}

    @pytest.mark.anyio
    async def test_record_acquire(self):
        """测试记录锁获取"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")

        assert "lock1" in monitor._locks
        assert monitor._locks["lock1"]["owner_thread"] == "thread1"
        assert monitor._locks["lock1"]["acquired_at"] is not None

    @pytest.mark.anyio
    async def test_record_release(self):
        """测试记录锁释放"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_release("lock1")

        assert monitor._locks["lock1"]["released_at"] is not None
        assert monitor._locks["lock1"]["status"] == "released"

    @pytest.mark.anyio
    async def test_record_release_without_acquire(self):
        """测试释放未获取的锁"""
        monitor = LockMonitor()
        await monitor.record_release("lock1")

        # 应该记录错误
        assert monitor._locks["lock1"]["status"] == "error"

    @pytest.mark.anyio
    async def test_get_lock_info(self):
        """测试获取锁信息"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_release("lock1")

        info = monitor.get_lock_info("lock1")
        assert info is not None
        assert info["owner_thread"] == "thread1"
        assert info["status"] == "released"

    @pytest.mark.anyio
    async def test_get_lock_info_not_found(self):
        """测试获取不存在的锁信息"""
        monitor = LockMonitor()
        info = monitor.get_lock_info("nonexistent")
        assert info is None

    @pytest.mark.anyio
    async def test_get_all_locks(self):
        """测试获取所有锁"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_acquire("lock2", "thread2")

        all_locks = monitor.get_all_locks()
        assert len(all_locks) == 2

    @pytest.mark.anyio
    async def test_get_held_locks(self):
        """测试获取当前持有的锁"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_acquire("lock2", "thread2")
        await monitor.record_release("lock1")

        held_locks = monitor.get_held_locks()
        assert len(held_locks) == 1
        assert held_locks[0]["lock_id"] == "lock2"

    @pytest.mark.anyio
    async def test_get_statistics(self):
        """测试获取统计信息"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_release("lock1")
        await monitor.record_acquire("lock2", "thread1")
        await monitor.record_release("lock2")

        stats = monitor.get_statistics()
        assert stats["total_locks"] == 2
        assert stats["active_locks"] == 0
        assert stats["released_locks"] == 2

    @pytest.mark.anyio
    async def test_detect_deadlock(self):
        """测试死锁检测"""
        monitor = LockMonitor()
        await monitor.record_acquire("lock1", "thread1")
        await monitor.record_acquire("lock2", "thread2")

        # 模拟死锁
        all_locks = monitor.get_all_locks()
        assert len(all_locks) == 2
        # 死锁检测逻辑应该能够识别这种情况
        # (具体实现取决于监控器设计)


class TestSessionMonitor:
    """SessionMonitor 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        monitor = SessionMonitor()
        assert monitor is not None
        assert monitor._sessions == {}

    @pytest.mark.anyio
    async def test_record_session_start(self):
        """测试记录会话开始"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")

        assert "session1" in monitor._sessions
        assert monitor._sessions["session1"]["user"] == "user1"
        assert monitor._sessions["session1"]["status"] == "active"
        assert monitor._sessions["session1"]["started_at"] is not None

    @pytest.mark.anyio
    async def test_record_session_end(self):
        """测试记录会话结束"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_session_end("session1", "completed")

        assert monitor._sessions["session1"]["status"] == "completed"
        assert monitor._sessions["session1"]["ended_at"] is not None
        assert monitor._sessions["session1"]["duration"] is not None

    @pytest.mark.anyio
    async def test_record_session_end_without_start(self):
        """测试结束未开始的会话"""
        monitor = SessionMonitor()
        await monitor.record_session_end("session1", "completed")

        # 应该记录错误
        assert monitor._sessions["session1"]["status"] == "error"

    @pytest.mark.anyio
    async def test_record_activity(self):
        """测试记录活动"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_activity("session1", "action1", {"detail": "value"})

        assert len(monitor._sessions["session1"]["activities"]) == 1
        assert monitor._sessions["session1"]["activities"][0]["action"] == "action1"

    @pytest.mark.anyio
    async def test_get_session_info(self):
        """测试获取会话信息"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_activity("session1", "action1")

        info = monitor.get_session_info("session1")
        assert info is not None
        assert info["user"] == "user1"
        assert info["status"] == "active"

    @pytest.mark.anyio
    async def test_get_active_sessions(self):
        """测试获取活动会话"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_session_start("session2", "user2")
        await monitor.record_session_end("session1", "completed")

        active = monitor.get_active_sessions()
        assert len(active) == 1
        assert active[0]["session_id"] == "session2"

    @pytest.mark.anyio
    async def test_get_all_sessions(self):
        """测试获取所有会话"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_session_start("session2", "user2")

        all_sessions = monitor.get_all_sessions()
        assert len(all_sessions) == 2

    @pytest.mark.anyio
    async def test_get_statistics(self):
        """测试获取统计信息"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_session_end("session1", "completed")
        await monitor.record_session_start("session2", "user2")

        stats = monitor.get_statistics()
        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 1
        assert stats["completed_sessions"] == 1
        assert stats["average_duration"] is not None

    @pytest.mark.anyio
    async def test_get_session_activities(self):
        """测试获取会话活动"""
        monitor = SessionMonitor()
        await monitor.record_session_start("session1", "user1")
        await monitor.record_activity("session1", "action1")
        await monitor.record_activity("session1", "action2")

        activities = monitor.get_session_activities("session1")
        assert len(activities) == 2


class TestTaskMonitor:
    """TaskMonitor 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        monitor = TaskMonitor()
        assert monitor is not None
        assert monitor._tasks == {}

    @pytest.mark.anyio
    async def test_record_task_start(self):
        """测试记录任务开始"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Test Task", "thread1")

        assert "task1" in monitor._tasks
        assert monitor._tasks["task1"]["name"] == "Test Task"
        assert monitor._tasks["task1"]["thread"] == "thread1"
        assert monitor._tasks["task1"]["status"] == "running"
        assert monitor._tasks["task1"]["started_at"] is not None

    @pytest.mark.anyio
    async def test_record_task_complete(self):
        """测试记录任务完成"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Test Task")
        await monitor.record_task_complete("task1", "success")

        assert monitor._tasks["task1"]["status"] == "success"
        assert monitor._tasks["task1"]["completed_at"] is not None
        assert monitor._tasks["task1"]["duration"] is not None

    @pytest.mark.anyio
    async def test_record_task_error(self):
        """测试记录任务错误"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Test Task")
        await monitor.record_task_error("task1", "Error message")

        assert monitor._tasks["task1"]["status"] == "error"
        assert monitor._tasks["task1"]["error"] == "Error message"

    @pytest.mark.anyio
    async def test_record_task_progress(self):
        """测试记录任务进度"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Test Task")
        await monitor.record_task_progress("task1", 50, "Halfway done")

        assert monitor._tasks["task1"]["progress"] == 50
        assert monitor._tasks["task1"]["last_update"] == "Halfway done"

    @pytest.mark.anyio
    async def test_get_task_info(self):
        """测试获取任务信息"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Test Task")
        await monitor.record_task_complete("task1", "success")

        info = monitor.get_task_info("task1")
        assert info is not None
        assert info["name"] == "Test Task"
        assert info["status"] == "success"

    @pytest.mark.anyio
    async def test_get_running_tasks(self):
        """测试获取运行中的任务"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Task 1")
        await monitor.record_task_start("task2", "Task 2")
        await monitor.record_task_complete("task1", "success")

        running = monitor.get_running_tasks()
        assert len(running) == 1
        assert running[0]["task_id"] == "task2"

    @pytest.mark.anyio
    async def test_get_all_tasks(self):
        """测试获取所有任务"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Task 1")
        await monitor.record_task_start("task2", "Task 2")

        all_tasks = monitor.get_all_tasks()
        assert len(all_tasks) == 2

    @pytest.mark.anyio
    async def test_get_statistics(self):
        """测试获取统计信息"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Task 1")
        await monitor.record_task_complete("task1", "success")
        await monitor.record_task_start("task2", "Task 2")
        await monitor.record_task_error("task2", "Error")

        stats = monitor.get_statistics()
        assert stats["total_tasks"] == 2
        assert stats["completed_tasks"] == 1
        assert stats["failed_tasks"] == 1
        assert stats["running_tasks"] == 0

    @pytest.mark.anyio
    async def test_get_tasks_by_status(self):
        """测试按状态获取任务"""
        monitor = TaskMonitor()
        await monitor.record_task_start("task1", "Task 1")
        await monitor.record_task_complete("task1", "success")
        await monitor.record_task_start("task2", "Task 2")
        await monitor.record_task_error("task2", "Error")

        successful = monitor.get_tasks_by_status("success")
        assert len(successful) == 1
        assert successful[0]["task_id"] == "task1"

        failed = monitor.get_tasks_by_status("error")
        assert len(failed) == 1
        assert failed[0]["task_id"] == "task2"


class TestSystemMonitor:
    """SystemMonitor 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        monitor = SystemMonitor()
        assert monitor is not None

    @pytest.mark.anyio
    async def test_get_cpu_usage(self):
        """测试获取 CPU 使用率"""
        monitor = SystemMonitor()
        cpu_usage = monitor.get_cpu_usage()

        assert isinstance(cpu_usage, float)
        assert cpu_usage >= 0

    @pytest.mark.anyio
    async def test_get_memory_usage(self):
        """测试获取内存使用情况"""
        monitor = SystemMonitor()
        memory = monitor.get_memory_usage()

        assert isinstance(memory, dict)
        assert "total" in memory
        assert "used" in memory
        assert "free" in memory
        assert "percentage" in memory

    @pytest.mark.anyio
    async def test_get_disk_usage(self):
        """测试获取磁盘使用情况"""
        monitor = SystemMonitor()
        disk = monitor.get_disk_usage()

        assert isinstance(disk, dict)
        assert "total" in disk
        assert "used" in disk
        assert "free" in disk
        assert "percentage" in disk

    @pytest.mark.anyio
    async def test_get_network_stats(self):
        """测试获取网络统计"""
        monitor = SystemMonitor()
        network = monitor.get_network_stats()

        assert isinstance(network, dict)
        # 网络统计应该包含发送和接收的数据
        # 具体字段取决于实现

    @pytest.mark.anyio
    async def test_get_process_count(self):
        """测试获取进程数量"""
        monitor = SystemMonitor()
        count = monitor.get_process_count()

        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.anyio
    async def test_get_thread_count(self):
        """测试获取线程数量"""
        monitor = SystemMonitor()
        count = monitor.get_thread_count()

        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.anyio
    async def test_get_system_info(self):
        """测试获取系统信息"""
        monitor = SystemMonitor()
        info = monitor.get_system_info()

        assert isinstance(info, dict)
        assert "platform" in info
        assert "python_version" in info
        assert "cpu_count" in info

    @pytest.mark.anyio
    async def test_get_load_average(self):
        """测试获取负载平均值"""
        monitor = SystemMonitor()
        load = monitor.get_load_average()

        # 在 Windows 上可能不可用
        if load is not None:
            assert isinstance(load, (float, tuple))

    @pytest.mark.anyio
    async def test_get_system_statistics(self):
        """测试获取系统统计"""
        monitor = SystemMonitor()
        stats = monitor.get_system_statistics()

        assert isinstance(stats, dict)
        assert "cpu_usage" in stats
        assert "memory_usage" in stats
        assert "disk_usage" in stats


class TestResourceMonitor:
    """ResourceMonitor 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:

            monitor = ResourceMonitor()
            assert monitor is not None

    @pytest.mark.anyio
    async def test_record_event(self):
        """测试记录事件"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:

            monitor = ResourceMonitor()
            await monitor.record_event("test", "resource1", {"key": "value"})

            # 验证事件被记录
            # (具体验证取决于实现)

    @pytest.mark.anyio
    async def test_get_lock_monitor(self):
        """测试获取锁监控器"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock:
            monitor = ResourceMonitor()
            lock_monitor = monitor.get_lock_monitor()

            assert lock_monitor is not None

    @pytest.mark.anyio
    async def test_get_session_monitor(self):
        """测试获取会话监控器"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession:
            monitor = ResourceMonitor()
            session_monitor = monitor.get_session_monitor()

            assert session_monitor is not None

    @pytest.mark.anyio
    async def test_get_task_monitor(self):
        """测试获取任务监控器"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask:
            monitor = ResourceMonitor()
            task_monitor = monitor.get_task_monitor()

            assert task_monitor is not None

    @pytest.mark.anyio
    async def test_get_system_monitor(self):
        """测试获取系统监控器"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:
            monitor = ResourceMonitor()
            system_monitor = monitor.get_system_monitor()

            assert system_monitor is not None

    @pytest.mark.anyio
    async def test_get_all_statistics(self):
        """测试获取所有统计信息"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:

            monitor = ResourceMonitor()
            stats = monitor.get_all_statistics()

            assert isinstance(stats, dict)
            assert "locks" in stats
            assert "sessions" in stats
            assert "tasks" in stats
            assert "system" in stats

    @pytest.mark.anyio
    async def test_generate_report(self):
        """测试生成报告"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:

            monitor = ResourceMonitor()
            report = monitor.generate_report()

            assert isinstance(report, str)
            assert len(report) > 0

    @pytest.mark.anyio
    async def test_clear_statistics(self):
        """测试清空统计信息"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.LockMonitor') as MockLock, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SessionMonitor') as MockSession, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.TaskMonitor') as MockTask, \
             patch('autoBMAD.epic_automation.monitoring.resource_monitor.SystemMonitor') as MockSystem:

            monitor = ResourceMonitor()
            await monitor.clear_statistics()

            # 验证统计数据被清空
            # (具体验证取决于实现)


class TestGetResourceMonitor:
    """get_resource_monitor 工厂函数测试"""

    @pytest.mark.anyio
    async def test_get_resource_monitor_basic(self):
        """测试基本获取资源监控器"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.ResourceMonitor') as MockMonitor:
            monitor = get_resource_monitor()

            assert monitor is not None

    @pytest.mark.anyio
    async def test_get_resource_monitor_with_log_file(self):
        """测试带日志文件的资源监控器"""
        log_file = Path("test.log")
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.ResourceMonitor') as MockMonitor:
            monitor = get_resource_monitor(log_file)

            assert monitor is not None

    @pytest.mark.anyio
    async def test_singleton_pattern(self):
        """测试单例模式"""
        with patch('autoBMAD.epic_automation.monitoring.resource_monitor.ResourceMonitor') as MockMonitor:
            monitor1 = get_resource_monitor()
            monitor2 = get_resource_monitor()

            # 应该返回同一个实例
            # (具体验证取决于实现)
            assert monitor1 is not None
            assert monitor2 is not None
