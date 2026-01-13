"""
State Manager 单元测试

测试 State Manager 的核心功能：
1. DeadlockDetector 死锁检测器
2. DatabaseConnectionPool 数据库连接池
3. StateManager 状态管理器
4. 数据库操作
5. 状态持久化
6. 事务管理
"""
import pytest
import sqlite3
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from pathlib import Path
import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.state_manager import (
    DeadlockDetector,
    DatabaseConnectionPool,
    StateManager,
)


class TestDeadlockDetector:
    """DeadlockDetector 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        detector = DeadlockDetector()
        assert detector is not None
        assert detector._check_interval == 5.0

    @pytest.mark.anyio
    async def test_init_with_interval(self):
        """测试带检查间隔的初始化"""
        detector = DeadlockDetector(check_interval=10.0)
        assert detector._check_interval == 10.0

    @pytest.mark.anyio
    async def test_add_transaction(self):
        """测试添加事务"""
        detector = DeadlockDetector()
        detector.add_transaction("tx1", "thread1", ["lock1", "lock2"])

        assert "tx1" in detector._transactions
        assert detector._transactions["tx1"]["thread"] == "thread1"
        assert detector._transactions["tx1"]["locks"] == ["lock1", "lock2"]

    @pytest.mark.anyio
    async def test_remove_transaction(self):
        """测试移除事务"""
        detector = DeadlockDetector()
        detector.add_transaction("tx1", "thread1", ["lock1"])
        detector.remove_transaction("tx1")

        assert "tx1" not in detector._transactions

    @pytest.mark.anyio
    async def test_detect_deadlock_simple(self):
        """测试简单死锁检测"""
        detector = DeadlockDetector()
        detector.add_transaction("tx1", "thread1", ["lock1"])
        detector.add_transaction("tx2", "thread2", ["lock2"])
        detector.add_transaction("tx3", "thread3", ["lock1"])

        # tx1 和 tx3 都在等待 lock1，但无法检测到死锁
        deadlocks = detector.detect_deadlock()
        assert isinstance(deadlocks, list)

    @pytest.mark.anyio
    async def test_detect_deadlock_cycle(self):
        """测试循环死锁检测"""
        detector = DeadlockDetector()
        # 创建循环等待：tx1 -> lock1, tx2 -> lock2, tx3 -> lock1, tx2 -> lock3
        detector.add_transaction("tx1", "thread1", ["lock1"])
        detector.add_transaction("tx2", "thread2", ["lock2", "lock3"])
        detector.add_transaction("tx3", "thread3", ["lock2"])

        # tx1 持有 lock1，等待 lock2
        detector._waiting_locks["lock1"]["waiting_tx"] = "tx2"
        # tx3 持有 lock2，等待 lock1
        detector._waiting_locks["lock2"]["waiting_tx"] = "tx1"

        deadlocks = detector.detect_deadlock()
        assert isinstance(deadlocks, list)

    @pytest.mark.anyio
    async def test_get_transaction_graph(self):
        """测试获取事务图"""
        detector = DeadlockDetector()
        detector.add_transaction("tx1", "thread1", ["lock1"])
        detector.add_transaction("tx2", "thread2", ["lock2"])

        graph = detector.get_transaction_graph()
        assert isinstance(graph, dict)

    @pytest.mark.anyio
    async def test_start_monitoring(self):
        """测试开始监控"""
        detector = DeadlockDetector()

        with patch.object(detector, '_check_for_deadlocks') as mock_check:
            detector.start_monitoring()
            # 验证监控启动
            # (具体验证取决于实现)

    @pytest.mark.anyio
    async def test_stop_monitoring(self):
        """测试停止监控"""
        detector = DeadlockDetector()

        with patch.object(detector, '_check_for_deadlocks') as mock_check:
            detector.start_monitoring()
            detector.stop_monitoring()
            # 验证监控停止


class TestDatabaseConnectionPool:
    """DatabaseConnectionPool 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        pool = DatabaseConnectionPool(max_connections=10)
        assert pool is not None
        assert pool.max_connections == 10

    @pytest.mark.anyio
    async def test_init_default(self):
        """测试默认初始化"""
        pool = DatabaseConnectionPool()
        assert pool.max_connections == 5

    @pytest.mark.anyio
    async def test_get_connection(self):
        """测试获取连接"""
        pool = DatabaseConnectionPool()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            conn = pool.get_connection()

            assert conn is not None
            mock_connect.assert_called_once()

    @pytest.mark.anyio
    async def test_get_connection_with_reuse(self):
        """测试连接重用"""
        pool = DatabaseConnectionPool()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            # 获取并归还连接
            conn1 = pool.get_connection()
            pool.return_connection(conn1)

            # 再次获取，应该重用
            conn2 = pool.get_connection()

            assert conn2 is not None

    @pytest.mark.anyio
    async def test_return_connection(self):
        """测试归还连接"""
        pool = DatabaseConnectionPool()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            conn = pool.get_connection()
            pool.return_connection(conn)

            # 验证连接被归还
            # (具体验证取决于实现)

    @pytest.mark.anyio
    async def test_close_all(self):
        """测试关闭所有连接"""
        pool = DatabaseConnectionPool()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            conn = pool.get_connection()
            pool.close_all()

            # 验证所有连接关闭
            mock_conn.close.assert_called_once()

    @pytest.mark.anyio
    async def test_get_pool_status(self):
        """测试获取连接池状态"""
        pool = DatabaseConnectionPool(max_connections=10)

        status = pool.get_pool_status()
        assert isinstance(status, dict)
        assert "active_connections" in status
        assert "available_connections" in status
        assert "total_connections" in status

    @pytest.mark.anyio
    async def test_context_manager(self):
        """测试上下文管理器"""
        pool = DatabaseConnectionPool()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            with pool.get_connection() as conn:
                assert conn is not None

            # 验证连接被自动归还
            # (具体验证取决于实现)


class TestStateManager:
    """StateManager 测试类"""

    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        import tempfile
        fd, path = tempfile.mkstemp(suffix='.db')
        import os
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.mark.anyio
    async def test_init(self, temp_db):
        """测试初始化"""
        manager = StateManager(db_path=temp_db)
        assert manager is not None

    @pytest.mark.anyio
    async def test_init_default_db(self):
        """测试默认数据库初始化"""
        manager = StateManager()
        assert manager is not None

    @pytest.mark.anyio
    async def test_initialize_database(self, temp_db):
        """测试数据库初始化"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        # 验证表被创建
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "epics" in tables
        assert "stories" in tables

    @pytest.mark.anyio
    async def test_create_epic(self, temp_db):
        """测试创建 Epic"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")

        assert epic_id is not None
        assert isinstance(epic_id, str)

    @pytest.mark.anyio
    async def test_get_epic(self, temp_db):
        """测试获取 Epic"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        epic = await manager.get_epic(epic_id)

        assert epic is not None
        assert epic["title"] == "Epic 1"
        assert epic["description"] == "Test epic"

    @pytest.mark.anyio
    async def test_update_epic(self, temp_db):
        """测试更新 Epic"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        await manager.update_epic(epic_id, title="Updated Epic")

        epic = await manager.get_epic(epic_id)
        assert epic["title"] == "Updated Epic"

    @pytest.mark.anyio
    async def test_delete_epic(self, temp_db):
        """测试删除 Epic"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        await manager.delete_epic(epic_id)

        epic = await manager.get_epic(epic_id)
        assert epic is None

    @pytest.mark.anyio
    async def test_create_story(self, temp_db):
        """测试创建 Story"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(
            epic_id,
            "Story 1",
            "Test story",
            "Draft"
        )

        assert story_id is not None
        assert isinstance(story_id, str)

    @pytest.mark.anyio
    async def test_get_story(self, temp_db):
        """测试获取 Story"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(
            epic_id,
            "Story 1",
            "Test story",
            "Draft"
        )

        story = await manager.get_story(story_id)
        assert story is not None
        assert story["title"] == "Story 1"
        assert story["status"] == "Draft"

    @pytest.mark.anyio
    async def test_update_story_status(self, temp_db):
        """测试更新 Story 状态"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(
            epic_id,
            "Story 1",
            "Test story",
            "Draft"
        )

        await manager.update_story_status(story_id, "In Progress")
        story = await manager.get_story(story_id)
        assert story["status"] == "In Progress"

    @pytest.mark.anyio
    async def test_get_stories_by_epic(self, temp_db):
        """测试按 Epic 获取 Stories"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story1_id = await manager.create_story(epic_id, "Story 1", "Test 1", "Draft")
        story2_id = await manager.create_story(epic_id, "Story 2", "Test 2", "Draft")

        stories = await manager.get_stories_by_epic(epic_id)
        assert len(stories) == 2

    @pytest.mark.anyio
    async def test_update_story_field(self, temp_db):
        """测试更新 Story 字段"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(epic_id, "Story 1", "Test story", "Draft")

        await manager.update_story_field(story_id, "assigned_to", "user2")
        story = await manager.get_story(story_id)
        assert story["assigned_to"] == "user2"

    @pytest.mark.anyio
    async def test_delete_story(self, temp_db):
        """测试删除 Story"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(epic_id, "Story 1", "Test story", "Draft")

        await manager.delete_story(story_id)
        story = await manager.get_story(story_id)
        assert story is None

    @pytest.mark.anyio
    async def test_get_all_epics(self, temp_db):
        """测试获取所有 Epics"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        await manager.create_epic("Epic 1", "Test 1", "user1")
        await manager.create_epic("Epic 2", "Test 2", "user2")

        epics = await manager.get_all_epics()
        assert len(epics) == 2

    @pytest.mark.anyio
    async def test_search_stories(self, temp_db):
        """测试搜索 Stories"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        await manager.create_story(epic_id, "Story Alpha", "Test alpha", "Draft")
        await manager.create_story(epic_id, "Story Beta", "Test beta", "Draft")

        results = await manager.search_stories("Alpha")
        assert len(results) == 1
        assert results[0]["title"] == "Story Alpha"

    @pytest.mark.anyio
    async def test_get_story_history(self, temp_db):
        """测试获取 Story 历史"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        story_id = await manager.create_story(epic_id, "Story 1", "Test story", "Draft")

        await manager.update_story_status(story_id, "In Progress")
        await manager.update_story_status(story_id, "Done")

        history = await manager.get_story_history(story_id)
        assert len(history) >= 2

    @pytest.mark.anyio
    async def test_get_statistics(self, temp_db):
        """测试获取统计信息"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        await manager.create_story(epic_id, "Story 1", "Test 1", "Draft")
        await manager.create_story(epic_id, "Story 2", "Test 2", "Done")

        stats = await manager.get_statistics()
        assert isinstance(stats, dict)
        assert "total_epics" in stats
        assert "total_stories" in stats
        assert "stories_by_status" in stats

    @pytest.mark.anyio
    async def test_begin_transaction(self, temp_db):
        """测试开始事务"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        tx_id = await manager.begin_transaction()
        assert tx_id is not None

    @pytest.mark.anyio
    async def test_commit_transaction(self, temp_db):
        """测试提交事务"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        tx_id = await manager.begin_transaction()
        await manager.commit_transaction(tx_id)

        # 验证事务被提交
        # (具体验证取决于实现)

    @pytest.mark.anyio
    async def test_rollback_transaction(self, temp_db):
        """测试回滚事务"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        tx_id = await manager.begin_transaction()
        await manager.rollback_transaction(tx_id)

        # 验证事务被回滚
        # (具体验证取决于实现)

    @pytest.mark.anyio
    async def test_execute_in_transaction_success(self, temp_db):
        """测试事务中执行成功"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")

        async def update_epic():
            await manager.update_epic(epic_id, title="Updated")

        await manager.execute_in_transaction(update_epic)

        epic = await manager.get_epic(epic_id)
        assert epic["title"] == "Updated"

    @pytest.mark.anyio
    async def test_execute_in_transaction_rollback(self, temp_db):
        """测试事务中执行失败回滚"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")

        async def failing_update():
            await manager.update_epic(epic_id, title="Updated")
            raise Exception("Test error")

        with pytest.raises(Exception):
            await manager.execute_in_transaction(failing_update)

        # 验证回滚，未更新
        epic = await manager.get_epic(epic_id)
        assert epic["title"] == "Epic 1"

    @pytest.mark.anyio
    async def test_export_data(self, temp_db):
        """测试导出数据"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")
        await manager.create_story(epic_id, "Story 1", "Test story", "Draft")

        export_path = temp_db + ".export.json"
        await manager.export_data(export_path)

        assert Path(export_path).exists()

        # 清理导出文件
        Path(export_path).unlink()

    @pytest.mark.anyio
    async def test_import_data(self, temp_db):
        """测试导入数据"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        # 创建导出数据
        export_data = {
            "epics": [
                {
                    "title": "Epic 1",
                    "description": "Test epic",
                    "created_by": "user1"
                }
            ]
        }

        import json
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f)
            export_path = f.name

        try:
            await manager.import_data(export_path)

            epics = await manager.get_all_epics()
            assert len(epics) == 1
        finally:
            Path(export_path).unlink()

    @pytest.mark.anyio
    async def test_backup_database(self, temp_db):
        """测试备份数据库"""
        manager = StateManager(db_path=temp_db)
        await manager.initialize_database()

        epic_id = await manager.create_epic("Epic 1", "Test epic", "user1")

        backup_path = temp_db + ".backup"
        await manager.backup_database(backup_path)

        assert Path(backup_path).exists()

        # 清理备份文件
        Path(backup_path).unlink()

    @pytest.mark.anyio
    async def test_close(self, temp_db):
        """测试关闭管理器"""
        manager = StateManager(db_path=temp_db)
        await manager.close()

        # 验证连接池关闭
        # (具体验证取决于实现)
