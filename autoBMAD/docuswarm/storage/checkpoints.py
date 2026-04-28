"""Checkpoint storage for LangGraph state persistence."""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import aiosqlite

# Beijing timezone (UTC+8)
_BEIJING_TZ = timezone(timedelta(hours=8))
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class CheckpointManager:
    """Manages checkpoint storage and retrieval for pipeline state persistence.

    This class provides a high-level interface for checkpoint operations,
    abstracting away the underlying LangGraph checkpointer details.

    Attributes:
        db_path: Path to the SQLite database file.
        _checkpointer: The underlying AsyncSqliteSaver instance.
        _thread_id_map: Maps pipeline_id to thread_id for checkpoint retrieval.

    Example:
        >>> manager = CheckpointManager(":memory:")
        >>> checkpoint = await manager.get_latest_checkpoint("pipeline-123")
        >>> checkpoints = await manager.list_checkpoints("pipeline-123")
    """

    def __init__(self, db_path: str | Path = "checkpoints.db") -> None:
        """Initialize the CheckpointManager.

        Args:
            db_path: Path to the SQLite database file. Use ":memory:" for in-memory.
        """
        self.db_path = str(db_path)
        self._checkpointer: AsyncSqliteSaver | None = None
        self._thread_id_map: dict[str, str] = {}

    async def initialize(self) -> None:
        """Initialize the checkpointer connection.

        Must be called before any checkpoint operations.
        """
        aconn = await aiosqlite.connect(self.db_path)

        # Execute PRAGMA statements and properly close cursors
        cursor = await aconn.execute("PRAGMA journal_mode=WAL")
        await cursor.close()
        cursor = await aconn.execute("PRAGMA synchronous=NORMAL")
        await cursor.close()

        # Patch aiosqlite connection to add is_alive method for langgraph compatibility
        # langgraph's AsyncSqliteSaver expects this method but aiosqlite doesn't have it
        # We use a simple function that returns True since aiosqlite connections
        # are inherently alive when they're created successfully
        if not hasattr(aconn, "is_alive"):

            def _is_alive() -> bool:
                """Check if connection is alive (simplified for aiosqlite)."""
                return True

            aconn.is_alive = _is_alive  # type: ignore[attr-defined]

        self._checkpointer = AsyncSqliteSaver(conn=aconn)

    def _get_or_create_thread_id(self, pipeline_id: str) -> str:
        """Get or create a thread_id for a pipeline_id.

        Args:
            pipeline_id: The pipeline identifier.

        Returns:
            The associated thread_id.
        """
        if pipeline_id not in self._thread_id_map:
            self._thread_id_map[pipeline_id] = generate_thread_id(pipeline_id)
        return self._thread_id_map[pipeline_id]

    async def get_latest_checkpoint(
        self,
        pipeline_id: str,
    ) -> dict[str, Any] | None:
        """Get the latest checkpoint for a pipeline.

        Args:
            pipeline_id: The pipeline identifier to get checkpoint for.

        Returns:
            The checkpoint dict with state and metadata, or None if not found.
        """
        if self._checkpointer is None:
            await self.initialize()

        # Assert checkpointer is not None for type safety
        assert self._checkpointer is not None, "Checkpointer should be initialized"

        thread_id = self._get_or_create_thread_id(pipeline_id)
        config = create_checkpoint_config(thread_id)

        # Get the latest checkpoint using alist
        config_dict: dict[str, Any] = cast(dict[str, Any], cast(object, config))
        checkpoint_tuple = None
        async for cp in self._checkpointer.alist(config_dict, limit=1):
            checkpoint_tuple = cp
            break

        if checkpoint_tuple is None:
            return None

        # CheckpointTuple has .config and .checkpoint attributes
        checkpoint_data = checkpoint_tuple.checkpoint
        # checkpoint_data is always a dict per LangGraph's type definitions
        checkpoint_id = checkpoint_data.get("id", "unknown")

        # Extract the actual state from channel_values
        state = checkpoint_data.get("channel_values", checkpoint_data)

        return {
            "checkpoint_id": checkpoint_id,
            "thread_id": thread_id,
            "pipeline_id": pipeline_id,
            "state": state,
            "timestamp": datetime.now(_BEIJING_TZ).isoformat(),
        }

    async def list_checkpoints(
        self,
        pipeline_id: str,
    ) -> list[dict[str, Any]]:
        """List all checkpoints for a pipeline (for audit/recovery).

        Args:
            pipeline_id: The pipeline identifier to list checkpoints for.

        Returns:
            List of checkpoint metadata dicts with checkpoint_id and timestamp.
        """
        if self._checkpointer is None:
            await self.initialize()

        # Assert checkpointer is not None for type safety
        assert self._checkpointer is not None, "Checkpointer should be initialized"

        thread_id = self._get_or_create_thread_id(pipeline_id)
        config = create_checkpoint_config(thread_id)

        config_dict: dict[str, Any] = cast(dict[str, Any], cast(object, config))
        checkpoints: list[dict[str, Any]] = []

        async for cp in self._checkpointer.alist(config_dict):
            # CheckpointTuple has .config and .checkpoint attributes
            checkpoint_data = cp.checkpoint
            # checkpoint_data is always a dict per LangGraph's type definitions
            checkpoint_id = checkpoint_data.get("id", "unknown")
            checkpoints.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "thread_id": thread_id,
                    "pipeline_id": pipeline_id,
                    "timestamp": datetime.now(_BEIJING_TZ).isoformat(),
                }
            )

        return checkpoints

    async def close(self) -> None:
        """Close the checkpointer connection."""
        if self._checkpointer is not None:
            await self._checkpointer.conn.close()
            self._checkpointer = None


async def create_checkpointer(
    db_path: str | Path = "checkpoints.db",
) -> AsyncSqliteSaver:
    """Create an AsyncSqliteSaver checkpointer with proper async support.

    Args:
        db_path: Path to the SQLite database file. Use ":memory:" for in-memory.

    Returns:
        Configured AsyncSqliteSaver instance with WAL mode enabled.

    Example:
        >>> checkpointer = await create_checkpointer(":memory:")
        >>> config = create_checkpoint_config(thread_id="my-thread")
    """
    # Convert to string if Path
    db_path_str = str(db_path)

    # Connect using aiosqlite for async support
    aconn = await aiosqlite.connect(db_path_str)

    # Enable WAL mode for better concurrent access - properly close cursors
    cursor = await aconn.execute("PRAGMA journal_mode=WAL")
    await cursor.close()
    cursor = await aconn.execute("PRAGMA synchronous=NORMAL")
    await cursor.close()

    # Patch aiosqlite connection to add is_alive method for langgraph compatibility
    # langgraph's AsyncSqliteSaver expects this method but aiosqlite doesn't have it
    # We use a simple function that returns True since aiosqlite connections
    # are inherently alive when they're created successfully
    if not hasattr(aconn, "is_alive"):

        def _is_alive() -> bool:
            """Check if connection is alive (simplified for aiosqlite)."""
            return True

        aconn.is_alive = _is_alive  # type: ignore[attr-defined]

    # Create the async checkpointer
    checkpointer = AsyncSqliteSaver(conn=aconn)

    return checkpointer


def generate_thread_id(pipeline_id: str | None = None) -> str:
    """Generate a unique thread_id for pipeline isolation.

    Each pipeline execution should use a unique thread_id to prevent
    state bleeding between concurrent pipelines.

    Args:
        pipeline_id: Optional pipeline ID to include in the thread_id.
                     If not provided, a random UUID will be used.

    Returns:
        A unique thread_id string.

    Example:
        >>> thread_id = generate_thread_id("pipeline-123")
        >>> thread_id = generate_thread_id()  # Random UUID
    """
    if pipeline_id:
        return f"{pipeline_id}_{uuid.uuid4().hex[:8]}"
    return uuid.uuid4().hex


def create_checkpoint_config(thread_id: str) -> RunnableConfig:
    """Create a checkpoint configuration dict for LangGraph invocations.

    Args:
        thread_id: The unique thread identifier for this pipeline execution.

    Returns:
        Configuration dict with thread_id and configurable settings.

    Example:
        >>> config = create_checkpoint_config("my-thread-123")
        >>> graph.invoke(inputs, config)
    """
    return cast(
        RunnableConfig,
        cast(
            object,
            {
                "configurable": {
                    "thread_id": thread_id,
                },
                # Include thread_id at top level as well for LangGraph compatibility
                "thread_id": thread_id,
            },
        ),
    )


async def get_checkpoint(
    checkpointer: AsyncSqliteSaver,
    thread_id: str,
    checkpoint_id: str | None = None,
) -> dict[str, Any] | None:
    """Get a checkpoint from the checkpointer.

    Args:
        checkpointer: The AsyncSqliteSaver instance.
        thread_id: The thread ID to get checkpoint for.
        checkpoint_id: Optional specific checkpoint ID. If None, gets latest.

    Returns:
        The checkpoint dict or None if not found.
    """
    config = create_checkpoint_config(thread_id)

    if checkpoint_id:
        configurable = config.get("configurable")
        if configurable is not None:
            configurable["checkpoint_id"] = checkpoint_id

    # Get the checkpoint - cast RunnableConfig to dict via object
    config_dict: dict[str, Any] = cast(dict[str, Any], cast(object, config))
    async for checkpoint_tuple in checkpointer.alist(config_dict, limit=1):
        # CheckpointTuple has .checkpoint attribute
        checkpoint_data = checkpoint_tuple.checkpoint
        # Return the channel_values which contains the actual state
        # checkpoint_data is always a dict per LangGraph's type definitions
        return checkpoint_data.get("channel_values", checkpoint_data)

    return None


async def close_checkpointer(checkpointer: AsyncSqliteSaver) -> None:
    """Close the checkpointer connection.

    Args:
        checkpointer: The AsyncSqliteSaver instance to close.
    """
    await checkpointer.conn.close()


__all__ = [
    "CheckpointManager",
    "create_checkpointer",
    "generate_thread_id",
    "create_checkpoint_config",
    "get_checkpoint",
    "close_checkpointer",
]
