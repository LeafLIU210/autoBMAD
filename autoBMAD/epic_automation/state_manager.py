"""
修复后的状态管理器 - Fixed State Manager

解决锁管理和异步资源管理问题。
基于原版本：d:/GITHUB/pytQt_template/autoBMAD/epic_automation/state_manager.py

主要修复：
1. 优化锁获取和释放机制
2. 增强异步资源管理
3. 改进错误处理和恢复
4. 添加死锁检测
5. 优化数据库操作性能
"""

import asyncio
import json
import logging
import re
import shutil
import sqlite3
import warnings
from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, Union, cast, List, Dict

from autoBMAD.epic_automation.agents.config import StoryStatus, QAResult

logger = logging.getLogger(__name__)

# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])

__all__ = ['StateManager', 'StoryStatus', 'QAResult']


def deprecated(reason: str) -> Callable[[F], F]:
    """标记方法为废弃"""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(
                    f"{func.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2
                )
                return await func(*args, **kwargs)
            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(
                    f"{func.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2
                )
                return func(*args, **kwargs)
            return cast(F, wrapper)
    return decorator


class DeadlockDetector:
    """死锁检测器"""

    def __init__(self):
        self.lock_waiters: Dict[str, asyncio.Task[None]] = {}
        self.lock_timeout: float = 30.0  # 30秒超时
        self.deadlock_detected: bool = False

    async def wait_for_lock(self, lock_name: str, lock: asyncio.Lock) -> bool:
        """等待锁，带死锁检测"""
        task = asyncio.current_task()
        if not task:
            return False

        self.lock_waiters[lock_name] = task

        try:
            # 使用超时等待
            result = await asyncio.wait_for(lock.acquire(), timeout=self.lock_timeout)
            return result
        except TimeoutError:
            logger.error(f"Deadlock detected for lock: {lock_name}")
            self.deadlock_detected = True
            return False
        finally:
            self.lock_waiters.pop(lock_name, None)


class DatabaseConnectionPool:
    """数据库连接池"""

    def __init__(self, max_connections: int = 5):
        self.max_connections: int = max_connections
        self.connections: asyncio.Queue[sqlite3.Connection] = asyncio.Queue(
            maxsize=max_connections
        )
        self.connection_params: Dict[str, Any] = {}

    async def initialize(self, db_path: Path):
        """初始化连接池"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode=WAL")  # 启用WAL模式提高并发性能
            conn.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全性
            conn.execute("PRAGMA cache_size=10000")  # 设置缓存大小
            conn.execute("PRAGMA temp_store=memory")  # 临时表存储在内存中
            await self.connections.put(conn)

    async def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        try:
            conn: sqlite3.Connection = await asyncio.wait_for(
                self.connections.get(), timeout=5.0
            )
            return conn
        except TimeoutError:
            raise RuntimeError("Database connection pool exhausted")

    async def return_connection(self, conn: sqlite3.Connection):
        """归还数据库连接"""
        try:
            await self.connections.put(conn)
        except asyncio.QueueFull:
            conn.close()


class StateManager:
    """修复后的SQLite-based状态管理器，用于跟踪故事进度。"""

    def __init__(self, db_path: str = "progress.db", use_connection_pool: bool = True):
        """
        初始化状态管理器。

        Args:
            db_path: SQLite数据库文件路径
            use_connection_pool: 是否使用连接池
        """
        self.db_path: Path = Path(db_path)
        self._lock: asyncio.Lock = asyncio.Lock()
        self._deadlock_detector: DeadlockDetector = DeadlockDetector()
        self._connection_pool: DatabaseConnectionPool | None = (
            DatabaseConnectionPool() if use_connection_pool else None
        )

        self._init_db_sync()

        # 延迟初始化连接池，避免在同步上下文中创建任务
        # 连接池将在第一次使用时初始化
        self._connection_pool_initialized: bool = False

    async def _ensure_connection_pool_initialized(self):
        """确保连接池在使用前被初始化"""
        if self._connection_pool and not self._connection_pool_initialized:
            await self._connection_pool.initialize(self.db_path)
            # 对于内存数据库，确保表结构存在
            if str(self.db_path) == ":memory:":
                # 获取一个连接来初始化表结构
                conn = await self._connection_pool.get_connection()
                try:
                    cursor = conn.cursor()
                    # 为内存数据库创建表
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS stories (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            epic_path TEXT NOT NULL,
                            story_path TEXT NOT NULL UNIQUE,
                            status TEXT NOT NULL,
                            iteration INTEGER DEFAULT 0,
                            qa_result TEXT,
                            error_message TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            phase TEXT,
                            version INTEGER DEFAULT 1
                        )
                    """)
                    conn.commit()
                finally:
                    await self._connection_pool.return_connection(conn)
            self._connection_pool_initialized = True

    def _init_db_sync(self):
        """初始化数据库模式（同步）。"""
        # 创建数据库连接
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建stories表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                epic_path TEXT NOT NULL,
                story_path TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                iteration INTEGER DEFAULT 0,
                qa_result TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                phase TEXT,
                version INTEGER DEFAULT 1
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_path
            ON stories(story_path)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON stories(status)
        """)

        # Database migration: ensure version column exists
        try:
            cursor.execute("SELECT version FROM stories LIMIT 1")
            logger.info("Database migration: version column exists")
        except sqlite3.OperationalError:
            logger.info("Database migration: adding version column")
            cursor.execute("ALTER TABLE stories ADD COLUMN version INTEGER DEFAULT 1")

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.db_path}")

    @asynccontextmanager
    async def _get_db_connection(self):
        """获取数据库连接的上下文管理器"""
        # 确保连接池在使用前被初始化
        if self._connection_pool:
            await self._ensure_connection_pool_initialized()

        if self._connection_pool:
            conn = await self._connection_pool.get_connection()
            try:
                yield conn
            finally:
                await self._connection_pool.return_connection(conn)
        else:
            conn = sqlite3.connect(self.db_path)
            try:
                # 确保表结构存在（对于内存数据库或新的文件数据库）
                if str(self.db_path) == ":memory:":
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS stories (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            epic_path TEXT NOT NULL,
                            story_path TEXT NOT NULL UNIQUE,
                            status TEXT NOT NULL,
                            iteration INTEGER DEFAULT 0,
                            qa_result TEXT,
                            error_message TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            phase TEXT,
                            version INTEGER DEFAULT 1
                        )
                    """)
                    conn.commit()
                yield conn
            finally:
                conn.close()

    async def update_story_status(
        self,
        story_path: str,
        status: str,
        phase: str | None = None,
        iteration: int | None = None,
        qa_result: Union["dict[str, Any]", None] = None,
        error: str | None = None,
        epic_path: str | None = None,
        lock_timeout: float = 30.0,
        expected_version: int | None = None,
    ) -> "tuple[bool, int | None]":
        """
        更新或插入故事状态，优化锁管理和错误处理。

        Args:
            story_path: 故事文件路径
            status: 当前状态
            phase: 当前阶段
            iteration: 当前迭代次数
            qa_result: QA结果字典
            error: 错误消息
            epic_path: Epic文件路径 (必须传递，否则报错)
            lock_timeout: 锁获取超时时间（秒）
            expected_version: 期望的版本号（用于乐观锁）

        Returns:
            (success, current_version): (是否成功, 当前版本号)
            
        Raises:
            ValueError: epic_path为None时报错
        """
        # ✅ 参数校验：确保 epic_path 非空
        if epic_path is None:
            raise ValueError(
                f"epic_path is required for story '{story_path}'. "
                f"Caller must provide epic_path to ensure database integrity."
            )
        try:
            # Use a simple approach with timeout
            # _update_story_internal already has lock protection
            return await asyncio.wait_for(
                self._update_story_internal(
                    story_path,
                    status,
                    phase,
                    iteration,
                    qa_result,
                    error,
                    epic_path,
                    expected_version,
                ),
                timeout=lock_timeout,
            )

        except TimeoutError:
            logger.warning(
                f"Update operation timeout for {story_path} (>{lock_timeout}s)"
            )
            return False, None
        except asyncio.CancelledError:
            logger.warning(f"Update operation cancelled for {story_path}")
            return False, None
        except Exception as e:
            logger.error(f"Failed to update story status for {story_path}: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return False, None

    async def _update_story_internal(
        self,
        story_path: str,
        status: str,
        phase: str | None,
        iteration: int | None,
        qa_result: Union["dict[str, Any]", None],
        error: str | None,
        epic_path: str | None,
        expected_version: int | None,
    ) -> "tuple[bool, int | None]":
        """内部更新逻辑 - 使用锁保护"""
        # Use lock to protect database operations
        async with self._lock:
            async with self._get_db_connection() as conn:
                cursor = conn.cursor()

                # 检查故事是否存在
                cursor.execute(
                    "SELECT id, version FROM stories WHERE story_path = ?",
                    (story_path,),
                )
                existing = cursor.fetchone()

                # 清理qa_result
                qa_result_str = None
                if qa_result:
                    qa_result_str = self._clean_qa_result_for_json(qa_result)

                if existing:
                    _, current_version = existing

                    # 乐观锁检查
                    if (
                        expected_version is not None
                        and current_version != expected_version
                    ):
                        logger.warning(
                            f"Version conflict for {story_path}: "
                            f"expected {expected_version}, got {current_version}"
                        )
                        return False, current_version

                    # 更新现有记录
                    cursor.execute(
                        """
                        UPDATE stories
                        SET status = ?,
                            phase = ?,
                            iteration = ?,
                            qa_result = ?,
                            error_message = ?,
                            updated_at = CURRENT_TIMESTAMP,
                            version = version + 1
                        WHERE story_path = ?
                    """,
                        (status, phase, iteration, qa_result_str, error, story_path),
                    )
                    logger.info(
                        f"Updated status for {story_path}: {status} (version {current_version + 1})"
                    )
                    current_version = current_version + 1
                else:
                    # 插入新记录
                    cursor.execute(
                        """
                        INSERT INTO stories
                        (epic_path, story_path, status, phase, iteration, qa_result, error_message, version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                        (
                            epic_path,
                            story_path,
                            status,
                            phase,
                            iteration or 0,
                            qa_result_str,
                            error,
                        ),
                    )
                    logger.info(
                        f"Inserted new record for {story_path}: {status} (version 1)"
                    )
                    current_version = 1

                conn.commit()
                return True, current_version

    def _clean_qa_result_for_json(self, qa_result: Any) -> str | None:
        """清理QA结果以便JSON序列化"""
        try:
            # 移除不可序列化的对象
            def clean_for_json(obj: Any) -> Any:
                if hasattr(obj, "value"):
                    return obj.value
                elif isinstance(obj, dict):
                    return {k: clean_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_for_json(v) for v in obj]
                else:
                    return obj

            cleaned_qa_result = clean_for_json(qa_result)
            return json.dumps(cleaned_qa_result)
        except Exception as e:
            logger.warning(f"Failed to clean QA result for JSON: {e}")
            return None

    @asynccontextmanager
    async def managed_operation(self):
        """
        异步上下文管理器，用于安全锁管理。

        确保即使发生取消也能正确释放锁。
        """
        try:
            # 使用死锁检测器监控锁等待
            async with self._lock:
                yield self
        except asyncio.CancelledError:
            logger.warning("Managed operation cancelled")
            # 不重新抛出以避免cancel scope错误
            return
        except Exception as e:
            logger.error(f"Managed operation failed: {e}")
            raise

    async def get_story_status(self, story_path: str) -> Union["dict[str, Any]", None]:
        """
        获取故事状态。

        Args:
            story_path: 故事文件路径

        Returns:
            包含故事状态和元数据的字典，如果未找到则返回None
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase, version
                        FROM stories
                        WHERE story_path = ?
                    """,
                        (story_path,),
                    )

                    row = cursor.fetchone()

                    if row:
                        result = {
                            "epic_path": row[0],
                            "story_path": row[1],
                            "status": row[2],
                            "iteration": row[3],
                            "created_at": row[6],
                            "updated_at": row[7],
                            "phase": row[8],
                            "version": row[9],
                        }

                        if row[4]:  # qa_result
                            try:
                                result["qa_result"] = json.loads(row[4])
                            except json.JSONDecodeError:
                                result["qa_result"] = row[4]

                        if row[5]:  # error_message
                            result["error"] = row[5]

                        return result

                    return None

        except Exception as e:
            logger.error(f"Failed to get story status: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return None

    async def get_all_stories(self) -> "list[dict[str, Any]]":
        """
        获取所有故事。

        Returns:
            故事字典列表
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase, version
                        FROM stories
                        ORDER BY created_at
                    """)

                    rows = cursor.fetchall()
                    stories = []

                    for row in rows:
                        story = {
                            "epic_path": row[0],
                            "story_path": row[1],
                            "status": row[2],
                            "iteration": row[3],
                            "created_at": row[6],
                            "updated_at": row[7],
                            "phase": row[8],
                            "version": row[9],
                        }

                        if row[4]:  # qa_result
                            try:
                                story["qa_result"] = json.loads(row[4])
                            except json.JSONDecodeError:
                                story["qa_result"] = row[4]

                        if row[5]:  # error_message
                            story["error"] = row[5]

                        stories.append(story)

                    return stories

        except Exception as e:
            logger.error(f"Failed to get all stories: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return []

    async def get_stories_by_status(self, status: str) -> "list[dict[str, Any]]":
        """
        Get stories filtered by status.

        Args:
            status: Status to filter by

        Returns:
            List of stories with the specified status
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase, version
                        FROM stories
                        WHERE status = ?
                        ORDER BY created_at
                    """, (status,))

                    rows = cursor.fetchall()
                    stories = []

                    for row in rows:
                        story = {
                            "epic_path": row[0],
                            "story_path": row[1],
                            "status": row[2],
                            "iteration": row[3],
                            "created_at": row[6],
                            "updated_at": row[7],
                            "phase": row[8],
                            "version": row[9],
                        }

                        if row[4]:  # qa_result
                            try:
                                story["qa_result"] = json.loads(row[4])
                            except json.JSONDecodeError:
                                story["qa_result"] = row[4]

                        if row[5]:  # error_message
                            story["error"] = row[5]

                        stories.append(story)

                    return stories

        except Exception as e:
            logger.error(f"Failed to get stories by status: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return []

    async def get_stats(self) -> "dict[str, int]":
        """
        获取故事状态统计。

        Returns:
            包含状态计数的字典
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT status, COUNT(*) as count
                        FROM stories
                        GROUP BY status
                    """)

                    rows = cursor.fetchall()
                    stats = {}
                    for status, count in rows:
                        stats[status] = count

                    return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return {}

    async def create_backup(self) -> str | None:
        """
        创建数据库备份。

        Returns:
            备份文件路径，如果失败则返回None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = (
                self.db_path.parent
                / f"{self.db_path.stem}_backup_{timestamp}{self.db_path.suffix}"
            )

            # 使用文件复制而不是数据库备份，因为SQLite支持热备份
            shutil.copy2(self.db_path, backup_path)

            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return None

    async def delete_story(self, story_path: str) -> bool:
        """
        Delete a story from the database.

        Args:
            story_path: Path to the story file

        Returns:
            True if successful, False otherwise
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    # Delete the story
                    cursor.execute(
                        "DELETE FROM stories WHERE story_path = ?",
                        (story_path,)
                    )

                    conn.commit()

                    return True

        except Exception as e:
            logger.error(f"Failed to delete story {story_path}: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return False

    async def cleanup_old_records(self, days: int = 30) -> int:
        """
        清理旧记录。

        Args:
            days: 保留天数

        Returns:
            清理的记录数
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    # 清理旧的stories记录
                    cursor.execute(
                        f"""
                        DELETE FROM stories
                        WHERE updated_at < datetime('now', '-{days} days')
                        AND status IN ('completed', 'failed')
                    """
                    )

                    deleted_count = cursor.rowcount

                    conn.commit()

                    logger.info(f"Cleaned up {deleted_count} old records")
                    return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return 0

    async def cleanup_epic_stories(self, epic_id: str, story_ids: List[str]) -> int:
        """
        清理当前 Epic 相关 Story 的历史记录

        Args:
            epic_id: Epic 标识
            story_ids: Story ID 列表

        Returns:
            删除的记录数
        """
        if not story_ids:
            logger.info("[Cleanup] No stories to cleanup")
            return 0

        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    # 构建参数化查询 - 使用LIKE匹配story_path中的故事ID
                    query = f"""
                        DELETE FROM stories
                        WHERE epic_path LIKE ?
                          AND ({' OR '.join([f'story_path LIKE ?' for _ in story_ids])})
                    """
                    # epic_id 作为匹配模式
                    epic_pattern = f"%{epic_id}%" if not epic_id.startswith('%') and not epic_id.endswith('%') else epic_id
                    # story_id 匹配模式 - 匹配任何包含该ID的路径
                    story_patterns = [f"%{sid}%" for sid in story_ids]
                    params = [epic_pattern] + story_patterns

                    cursor.execute(query, params)
                    deleted_count = cursor.rowcount
                    conn.commit()

                    logger.info(
                        f"[Cleanup] Removed {deleted_count} old records for "
                        f"Epic '{epic_id}' Stories {story_ids}"
                    )

                    return deleted_count
        except Exception as e:
            logger.error(f"[Cleanup] Failed to cleanup epic stories: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return 0

    async def cleanup_temp_stories(self) -> int:
        """
        清理临时目录下的 Story 记录

        Returns:
            删除的记录数
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    query = """
                        DELETE FROM stories
                        WHERE story_path LIKE '%\\Temp\\%'
                           OR story_path LIKE '%\\AppData\\Local\\Temp\\%'
                           OR story_path LIKE '/tmp/%'
                           OR story_path LIKE '%TEMP%'
                           OR story_path LIKE '%Temp%'
                    """

                    cursor.execute(query)
                    deleted_count = cursor.rowcount
                    conn.commit()

                    logger.info(f"[Cleanup] Removed {deleted_count} temp story records")

                    return deleted_count
        except Exception as e:
            logger.error(f"[Cleanup] Failed to cleanup temp stories: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return 0

    async def cleanup_test_stories(self) -> int:
        """
        清理带测试标记的 Story 记录

        Returns:
            删除的记录数
        """
        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    query = """
                        DELETE FROM stories
                        WHERE story_path LIKE '%test%'
                           OR story_path LIKE '%Test%'
                           OR story_path LIKE '%TEST%'
                           OR story_path LIKE 'test_%'
                           OR story_path LIKE 'Test_%'
                    """

                    cursor.execute(query)
                    deleted_count = cursor.rowcount
                    conn.commit()

                    logger.info(f"[Cleanup] Removed {deleted_count} test story records")

                    return deleted_count
        except Exception as e:
            logger.error(f"[Cleanup] Failed to cleanup test stories: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return 0

    def _execute_delete(self, query: str, params: List[Any]) -> int:
        """
        执行删除操作（内部方法）

        Args:
            query: SQL删除查询
            params: 查询参数

        Returns:
            删除的记录数
        """
        # Note: This method is kept for compatibility but logic is inlined above
        # Keeping for potential future use
        raise NotImplementedError("Use async versions directly")

    async def initialize_for_epic(self, epic_id: str, story_ids: List[str]) -> Dict[str, int]:
        """
        为当前 Epic 运行初始化数据库

        执行清理：
        1. 当前 Epic Story 的旧记录
        2. TEMP 路径记录
        3. 测试标记记录

        Args:
            epic_id: 当前 Epic 标识
            story_ids: 当前 Epic 的 Story 列表

        Returns:
            清理统计：{
                'epic_stories': 删除数,
                'temp_stories': 删除数,
                'test_stories': 删除数,
                'total': 总删除数
            }
        """
        logger.info(f"[Init] Starting database initialization for Epic '{epic_id}'")

        stats: Dict[str, int] = {}

        # 清理 1：当前 Epic Story 旧记录
        stats['epic_stories'] = await self.cleanup_epic_stories(epic_id, story_ids)

        # 清理 2：TEMP 路径
        stats['temp_stories'] = await self.cleanup_temp_stories()

        # 清理 3：测试标记
        stats['test_stories'] = await self.cleanup_test_stories()

        # 汇总
        stats['total'] = sum(stats.values())

        logger.info(
            f"[Init] Database cleanup completed: "
            f"{stats['total']} records removed "
            f"(Epic: {stats['epic_stories']}, "
            f"Temp: {stats['temp_stories']}, "
            f"Test: {stats['test_stories']})"
        )

        return stats

    async def get_stories_by_ids(self, epic_path: str, story_ids: List[str]) -> "list[dict[str, Any]]":
        """
        根据 Epic 路径和 Story ID 列表查询处理状态。

        这是为了支持 StatusUpdateAgent 的范围限制功能，避免同步全库记录。

        Args:
            epic_path: Epic 文件路径
            story_ids: Story ID 列表

        Returns:
            符合条件的 Story 记录列表（含最新处理状态）

        Raises:
            ValueError: 如果 story_ids 为空列表
        """
        if not story_ids:
            logger.warning("get_stories_by_ids called with empty story_ids list")
            return []

        try:
            async with self._lock:
                async with self._get_db_connection() as conn:
                    cursor = conn.cursor()

                    # 构建参数化查询
                    placeholders = ','.join(['?'] * len(story_ids))
                    query = f"""
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase, version
                        FROM stories
                        WHERE epic_path = ? AND story_path IN ({placeholders})
                        ORDER BY updated_at DESC
                    """
                    params = [epic_path] + story_ids

                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    stories = []
                    for row in rows:
                        story = {
                            "epic_path": row[0],
                            "story_path": row[1],
                            "status": row[2],
                            "iteration": row[3],
                            "created_at": row[6],
                            "updated_at": row[7],
                            "phase": row[8],
                            "version": row[9],
                        }

                        if row[4]:  # qa_result
                            try:
                                story["qa_result"] = json.loads(row[4])
                            except json.JSONDecodeError:
                                story["qa_result"] = row[4]

                        if row[5]:  # error_message
                            story["error"] = row[5]

                        stories.append(story)

                    logger.debug(
                        f"get_stories_by_ids: Found {len(stories)} stories for epic {epic_path} "
                        f"with IDs: {str(story_ids)}"
                    )
                    return stories

        except Exception as e:
            logger.error(f"Failed to get stories by IDs: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return []

    def get_health_status(self) -> "dict[str, Any]":
        """
        获取数据库健康状态。

        Returns:
            健康状态字典
        """
        try:
            return {
                "db_path": str(self.db_path),
                "db_exists": self.db_path.exists(),
                "lock_locked": self._lock.locked(),
                "deadlock_detected": self._deadlock_detector.deadlock_detected,
                "connection_pool_enabled": self._connection_pool is not None,
                "connection_pool_size": self._connection_pool.max_connections
                if self._connection_pool
                else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {"error": str(e)}

    async def update_story_processing_status(
        self,
        story_id: str,
        processing_status: str,
        timestamp: datetime,
        epic_id: str,
        metadata: Dict[str, Any] | None = None
    ) -> bool:
        """
        更新故事的处理状态（方案2实现）

        Args:
            story_id: Story标识（story_path）
            processing_status: 处理状态（'in_progress', 'review', 'completed'）
            timestamp: 更新时间
            epic_id: Epic标识（epic_path）- **必需参数**
            metadata: 额外元数据（如错误信息、重试次数等）

        Returns:
            是否更新成功

        Raises:
            ValueError: epic_id为空时抛出异常
        """
        # ✅ 新增参数校验
        if not epic_id:
            raise ValueError(
                f"epic_id is required for story '{story_id}'. "
                f"Caller must provide epic_id to update processing status."
            )

        # 参数校验
        valid_statuses = {'in_progress', 'review', 'completed'}
        if processing_status not in valid_statuses:
            logger.error(f"Invalid processing_status: {processing_status}")
            raise ValueError(f"Invalid processing_status: {processing_status}. Must be one of {valid_statuses}")

        try:
            # 使用现有的update_story_status方法，传递epic_path参数
            success, _ = await self.update_story_status(
                story_path=story_id,
                status=processing_status,
                phase=processing_status,
                epic_path=epic_id,  # ← 保证非空
            )

            if success:
                logger.info(
                    f"[StateTransition] Story {story_id}: "
                    f"processing_status updated to '{processing_status}' "
                    f"(epic: {epic_id}, timestamp: {timestamp.isoformat()})"
                )
                if metadata:
                    logger.debug(f"[StateTransition] Metadata: {metadata}")
            else:
                logger.error(f"[StateTransition] Failed to update processing_status for {story_id}")

            return success

        except Exception as e:
            logger.error(f"[StateTransition] Error updating processing_status for {story_id}: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return False

    @deprecated("StateManager should not modify story documents directly. Use StatusUpdateAgent instead.")
    async def sync_story_statuses_to_markdown(self) -> "dict[str, Any]":
        """
        [DEPRECATED] 将数据库中的故事状态同步到markdown文件。

        Returns:
            同步结果字典，包含成功和失败的故事数量
        """
        logger.info("开始同步故事状态到markdown文件")
        results: Dict[str, Any] = {
            "success_count": 0,
            "error_count": 0,
            "errors": [],  # type: ignore[assignment]
        }

        try:
            # 获取所有故事记录
            stories = await self.get_all_stories()
            logger.info(f"找到 {len(stories)} 个故事记录")

            for story in stories:
                story_path = story.get("story_path")
                db_status = story.get("status")

                if not story_path or not db_status:
                    logger.warning(f"跳过无效的故事记录: {story}")
                    continue

                try:
                    await self._update_markdown_status(story_path, db_status)
                    results["success_count"] = int(results["success_count"]) + 1  # type: ignore[arg-type]
                    logger.info(f"已更新 {story_path} 状态为 {db_status}")
                except Exception as e:
                    results["error_count"] = int(results["error_count"]) + 1  # type: ignore[arg-type]
                    error_msg = f"更新 {story_path} 失败: {str(e)}"
                    errors_list = results["errors"]  # type: ignore[assignment]
                    errors_list.append(error_msg)
                    logger.error(error_msg)

            logger.info(
                f"同步完成: 成功 {results['success_count']}, 失败 {results['error_count']}"
            )
            return results

        except Exception as e:
            error_msg = f"同步故事状态失败: {str(e)}"
            logger.error(error_msg)
            errors_list = results["errors"]  # type: ignore[assignment]
            errors_list.append(error_msg)
            return results

    @deprecated("StateManager should not modify story documents directly. Use StatusUpdateAgent instead.")
    async def _update_markdown_status(self, story_path: str, db_status: str) -> None:
        """
        [DEPRECATED] 更新markdown文件中的Status字段。
        将数据库状态映射为适当的markdown状态。

        Args:
            story_path: 故事文件路径
            db_status: 数据库状态
        """
        try:
            # 单向映射：数据库状态 → Markdown文档状态
            DATABASE_TO_MARKDOWN_MAPPING = {
                # 故事状态
                "pending": "Draft",
                "in_progress": "In Progress",
                "review": "Ready for Review",
                "completed": "Done",
                "failed": "Failed",
                "cancelled": "Draft",

                # QA状态
                "qa_pass": "Done",  # QA通过表示故事已完成
                "qa_concerns": "Ready for Review",  # QA关注需要继续
                "qa_fail": "Failed",  # QA失败表示故事失败
                "qa_waived": "Done",  # QA豁免表示故事完成

                # 特殊状态
                "error": "Failed",
            }

            # 获取markdown状态，如果未映射则使用原状态
            markdown_status = DATABASE_TO_MARKDOWN_MAPPING.get(db_status, "Draft")

            story_file = Path(story_path)
            if not story_file.exists():
                # 如果文件不存在，尝试查找实际存在的文件
                actual_file = self._find_actual_story_file(story_path)
                if actual_file:
                    story_file = actual_file
                else:
                    # 如果找不到实际文件，记录警告并跳过，而不是抛出异常
                    logger.warning(f"跳过不存在的故事文件: {story_path}")
                    return

            # 读取文件内容
            with open(story_file, encoding="utf-8") as f:
                content = f.read()

            # 更新Status字段的正则表达式 - 支持多种格式（按优先级排序）
            status_patterns = [
                # 格式4: **<key>: Draft** -> **<key>: Done** (最具体，先匹配)
                r"\*\*([^*]+)\*\*:\s*Draft",
                # 格式1: ### Status\n**Status**: <value>
                r"(^### Status\s*\n\s*\*\*Status\*\*:\s*\*\*).*?(\*\*?)",
                # 格式2: ### Status\n**<value>**
                r"(^### Status\s*\n\s*\*\*)(.*?)(\*\*?)",
                # 格式3: ## Status\n**<value>** (兼容旧格式)
                r"(^## Status\s*\n\s*\*\*)(.*?)(\*\*?)",
            ]

            updated_content = content

            for pattern in status_patterns:
                match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
                if match:
                    # 使用正则表达式的替换功能
                    if r"Status\*\*:" in pattern and len(match.groups()) == 2:
                        # 格式1: **Status**: <value> - 替换整个值部分
                        updated_content = re.sub(
                            pattern,
                            f"\\g<1>{markdown_status}\\2",
                            content,
                            flags=re.MULTILINE,
                        )
                    elif "Draft" in pattern and len(match.groups()) == 1:
                        # 格式4: **<key>: Draft** -> **<key>: Done**
                        replacement = r"**\1**: " + markdown_status
                        updated_content = re.sub(
                            pattern,
                            replacement,
                            content,
                            flags=re.MULTILINE,
                        )
                    elif len(match.groups()) == 2 and r"Status\*\*:" not in pattern:
                        # 格式4 (alternative): **<key>: Draft** -> **<key>: Done**
                        replacement = r"**\1**: " + markdown_status
                        updated_content = re.sub(
                            pattern,
                            replacement,
                            content,
                            flags=re.MULTILINE,
                        )
                    elif len(match.groups()) == 3:
                        # 格式2/3: **<value>** - 替换中间的值部分
                        updated_content = re.sub(
                            pattern,
                            f"\\g<1>{markdown_status}\\3",
                            content,
                            flags=re.MULTILINE,
                        )

                    if updated_content != content:
                        logger.debug(f"Updated status using pattern: {pattern}")
                        break

            # 如果没有找到任何模式，使用默认方法

            # 检查是否有更改
            if updated_content == content:
                # 如果没有找到Status字段，仅记录警告，不插入新内容
                logger.warning(f"Status字段未找到，跳过更新: {story_path}")

            # 写回文件
            with open(story_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

            logger.debug(
                f"已更新 {story_path} 的Status字段为 {markdown_status} (从 {db_status} 映射)"
            )

        except Exception as e:
            logger.error(f"更新markdown状态失败 {story_path}: {str(e)}")
            raise

    @deprecated("StateManager should not modify story documents directly. Use StatusUpdateAgent instead.")
    def _find_actual_story_file(self, db_story_path: str) -> Path | None:
        """
        [DEPRECATED] 根据数据库中的故事路径，查找实际存在的故事文件。

        Args:
            db_story_path: 数据库中存储的故事路径

        Returns:
            实际存在的故事文件路径，如果找不到则返回None
        """
        try:
            db_path = Path(db_story_path)

            # 如果文件直接存在，返回它
            if db_path.exists():
                return db_path

            # 从数据库路径中提取文件名
            filename = db_path.name

            # 尝试不同的文件名转换格式

            # 格式1: 1.1.module-foundation.md -> 1.1-project-setup-infrastructure.md
            # 将点号替换为连字符，并尝试匹配实际存在的文件
            if "." in filename:
                base_name = filename.replace(".md", "")

                # 尝试在stories目录中查找匹配的文件
                stories_dir = db_path.parent
                if stories_dir.exists():
                    for story_file in stories_dir.glob("*.md"):
                        # 检查文件名前缀是否匹配（数字部分）
                        story_base = story_file.stem

                        # 提取数字部分进行比较
                        db_numbers = re.findall(r"\d+(?:\.\d+)?", base_name)
                        story_numbers = re.findall(r"\d+(?:\.\d+)?", story_base)

                        if (
                            db_numbers
                            and story_numbers
                            and db_numbers[0] == story_numbers[0]
                        ):
                            # 数字部分匹配，可能是同一个故事
                            logger.debug(
                                f"找到可能匹配的故事文件: {db_story_path} -> {story_file}"
                            )
                            return story_file

            # 格式2: 直接在数据库路径的目录中查找
            parent_dir = db_path.parent
            if parent_dir.exists():
                # 尝试精确匹配文件名
                exact_match = parent_dir / filename
                if exact_match.exists():
                    return exact_match

                # 尝试带连字符的版本
                hyphen_version = filename.replace(".", "-")
                hyphen_match = parent_dir / hyphen_version
                if hyphen_match.exists():
                    return hyphen_match

            logger.debug(f"未找到匹配的故事文件: {db_story_path}")
            return None

        except Exception as e:
            logger.debug(f"查找实际故事文件时出错 {db_story_path}: {str(e)}")
            return None
