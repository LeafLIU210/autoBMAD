"""SQLite database management for DocuSwarm - Story 1.4.

Features:
- WAL mode enabled for concurrent reads during pipeline execution
- Foreign key constraints enforced
- Busy timeout configured to 5000ms for graceful concurrent access
- Connection pooling with singleton pattern
- Thread-safe initialization using threading.Lock
- Idempotent schema creation with CREATE TABLE IF NOT EXISTS
- Context manager for proper resource cleanup
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from autoBMAD.docuswarm.exceptions import StorageError

# Default busy timeout in milliseconds
DEFAULT_BUSY_TIMEOUT_MS = 5000


class DatabaseManager:
    """Manages SQLite database connections with WAL mode and connection pooling.

    This class provides thread-safe database access with WAL mode for concurrent
    reads, foreign key enforcement, and connection pooling via a singleton pattern.

    Args:
        db_path: Path to the SQLite database file. Defaults to "docuswarm.db".

    Example:
        >>> db = DatabaseManager(db_path=Path("mydb.db"))
        >>> with db.acquire() as conn:
        ...     conn.execute("SELECT 1")
    """

    _instances: dict[str, DatabaseManager] = {}
    _lock: threading.Lock = threading.Lock()

    def __init__(self, db_path: Path | str = "docuswarm.db") -> None:
        """Initialize DatabaseManager.

        Args:
            db_path: Path to the SQLite database file.

        Raises:
            StorageError: If the database cannot be created or configured.
        """
        self._db_path = Path(db_path)
        self._pool_lock = threading.Lock()
        self._pool: list[sqlite3.Connection] = []
        self._pool_size = 5
        self._initialized = False
        self._init_lock = threading.Lock()

        # Perform initial setup
        self._initialize()

    @classmethod
    def get_instance(cls, db_path: Path | str = "docuswarm.db") -> DatabaseManager:
        """Get or create a DatabaseManager instance for the given db_path.

        P0-F4: Uses per-path caching instead of global singleton to avoid
        cross-database contamination.

        Args:
            db_path: Path to the SQLite database file.

        Returns:
            The DatabaseManager instance for the given path.
        """
        resolved = str(Path(db_path).resolve())
        if resolved not in cls._instances:
            with cls._lock:
                if resolved not in cls._instances:
                    cls._instances[resolved] = cls(db_path=db_path)
        return cls._instances[resolved]

    @classmethod
    def reset_instance(cls) -> None:
        """Reset all cached instances. Primarily for testing."""
        with cls._lock:
            for instance in cls._instances.values():
                instance.close_all()
            cls._instances.clear()

    @property
    def db_path(self) -> str:
        """Get the resolved database file path."""
        return str(self._db_path.resolve())

    def _initialize(self) -> None:
        """Initialize the database with schema and pragmas.

        Thread-safe initialization that only runs once.

        Raises:
            StorageError: If initialization fails.
        """
        with self._init_lock:
            if self._initialized:
                return
            try:
                conn = self._create_connection()
                try:
                    self._init_schema(conn)
                    conn.commit()
                finally:
                    conn.close()
                self._initialized = True
            except sqlite3.Error as e:
                raise StorageError(
                    f"Failed to initialize database at '{self._db_path}': {e}",
                    operation_type="initialize",
                    file_path=str(self._db_path),
                ) from e

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with proper settings.

        Returns:
            A configured sqlite3.Connection.

        Raises:
            sqlite3.Error: If connection cannot be created.
        """
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        self._configure_pragmas(conn)
        return conn

    def _configure_pragmas(self, conn: sqlite3.Connection) -> None:
        """Configure SQLite pragmas for optimal performance and safety.

        Pragma execution order:
        1. WAL mode (requires exclusive lock)
        2. Busy timeout
        3. Foreign keys
        4. Synchronous mode

        Args:
            conn: The SQLite connection to configure.
        """
        # WAL mode first - allows concurrent readers while writer is active
        _ = conn.execute("PRAGMA journal_mode=WAL")
        # Busy timeout - wait up to 5000ms instead of failing immediately
        _ = conn.execute(f"PRAGMA busy_timeout={DEFAULT_BUSY_TIMEOUT_MS}")
        # Foreign key enforcement - not enabled by default in SQLite
        _ = conn.execute("PRAGMA foreign_keys=ON")
        # Synchronous NORMAL - good balance of safety and performance with WAL
        _ = conn.execute("PRAGMA synchronous=NORMAL")

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        """Create database tables if they don't exist.

        Uses CREATE TABLE IF NOT EXISTS for idempotent initialization.

        Args:
            conn: The SQLite connection to use for schema creation.
        """
        _ = conn.execute("""
            CREATE TABLE IF NOT EXISTS pipelines (
                pipeline_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                current_node TEXT,
                state_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        _ = conn.execute("""
            CREATE TABLE IF NOT EXISTS node_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                iteration INTEGER NOT NULL DEFAULT 1,
                deliverable_json TEXT,
                questions_json TEXT,
                evaluation_json TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id)
                    ON DELETE CASCADE
            )
        """)

        # Node runs table for per-node run tracking (Story 3.9)
        _ = conn.execute("""
            CREATE TABLE IF NOT EXISTS node_runs (
                run_id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                context_hash TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'running',
                deliverable_json TEXT,
                questions_json TEXT,
                evaluation_json TEXT
            )
        """)

        # Create indexes for node_runs table
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_runs_node_id ON node_runs(node_id)
        """)
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_runs_context_hash ON node_runs(context_hash)
        """)

        # Node run metrics table for quality tracking (Story 5.6)
        _ = conn.execute("""
            CREATE TABLE IF NOT EXISTS node_run_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                final_score REAL NOT NULL,
                iterations INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                force_completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for node_run_metrics table
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_run_metrics_run_id ON node_run_metrics(run_id)
        """)
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_run_metrics_node_id ON node_run_metrics(node_id)
        """)

        # Shared context history table for change tracking (Story 35.6)
        _ = conn.execute("""
            CREATE TABLE IF NOT EXISTS shared_context_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_id TEXT NOT NULL,
                node_id TEXT,
                operation TEXT NOT NULL,
                key TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                timestamp TEXT NOT NULL,
                version INTEGER NOT NULL,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id)
                    ON DELETE CASCADE
            )
        """)

        # Create indexes for shared_context_history table
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_pipeline ON shared_context_history(pipeline_id)
        """)
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_timestamp ON shared_context_history(timestamp DESC)
        """)
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_node ON shared_context_history(node_id)
        """)
        _ = conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_key ON shared_context_history(key)
        """)

    @contextmanager
    def acquire(self) -> Generator[sqlite3.Connection]:
        """Acquire a database connection from the pool.

        Returns the connection to the pool when done. Configures pragmas
        on each acquired connection to ensure correct settings.

        Yields:
            A configured sqlite3.Connection.

        Raises:
            StorageError: If a connection cannot be acquired.

        Example:
            >>> with db.acquire() as conn:
            ...     cursor = conn.execute("SELECT * FROM pipelines")
            ...     rows = cursor.fetchall()
        """
        conn: sqlite3.Connection | None = None
        try:
            conn = self._get_connection()
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn is not None:
                conn.rollback()
            raise StorageError(
                f"Database operation failed: {e}",
                operation_type="query",
                file_path=str(self._db_path),
            ) from e
        finally:
            if conn is not None:
                self._return_connection(conn)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool or create a new one.

        Returns:
            A configured sqlite3.Connection.
        """
        with self._pool_lock:
            if self._pool:
                return self._pool.pop()
        return self._create_connection()

    def _return_connection(self, conn: sqlite3.Connection) -> None:
        """Return a connection to the pool.

        Args:
            conn: The connection to return.
        """
        with self._pool_lock:
            if len(self._pool) < self._pool_size:
                self._pool.append(conn)
            else:
                conn.close()

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._pool_lock:
            for conn in self._pool:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
            self._pool.clear()
