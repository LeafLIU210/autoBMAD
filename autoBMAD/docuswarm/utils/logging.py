"""Logging infrastructure module - Story 1.9.

Provides structured logging with:
- Console output at INFO level with color formatting
- File output at DEBUG level with rotating log files
- Context binding for run_id and node_id
- JSON format option for tooling integration
- Configurable log level via LOG_LEVEL environment variable
- Sensitive data filtering (API keys, tokens, passwords)
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol, cast

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import BoundLogger
from structlog.types import EventDict


class _Processor(Protocol):
    """Protocol for structlog processors."""

    def __call__(
        self,
        logger: BoundLogger,
        method: str,
        event_dict: EventDict,
    ) -> EventDict: ...


class _BeijingTimeStamper:
    """Custom structlog processor that stamps events with Beijing time (GMT+8)."""

    def __call__(
        self,
        _logger: BoundLogger,
        _method: str,
        event_dict: EventDict,
    ) -> EventDict:
        event_dict["timestamp"] = datetime.now(BEIJING_TZ).isoformat()
        return event_dict


# Beijing timezone (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# Default sensitive keys to filter
DEFAULT_SENSITIVE_KEYS = [
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "private_key",
    "access_token",
    "refresh_token",
    "authorization",
    "x-api-key",
]

# Global logger instance and configuration flag
_logger: BoundLogger | None = None
_configured: bool = False

# Log file configuration
_log_file: Path | None = None
_log_file_handler: logging.handlers.RotatingFileHandler | None = None
_json_mode: bool = False

# Log rotation settings (defaults from acceptance criteria)
_max_bytes: int = 10 * 1024 * 1024  # 10MB
_backup_count: int = 5

# Custom sensitive keys (set via configure_logging)
_sensitive_keys: list[str] = []


import re

# Patterns for content-level redaction inside line_preview
_LINE_REDACTION_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_-]+"),
    re.compile(r"Bearer\s+\S+"),
    re.compile(r"(?i)(api_key|token|secret|password)\s*=\s*\S+"),
]


def _redact_line_content(line: str) -> str:
    """Redact sensitive patterns inside a line string."""
    for pattern in _LINE_REDACTION_PATTERNS:
        line = pattern.sub("[REDACTED]", line)
    return line


def _redact_sensitive_fields(
    _logger: BoundLogger,
    _method: str,
    event_dict: EventDict,
) -> dict[str, Any]:
    """Redact sensitive fields from log output."""
    redacted: dict[str, Any] = dict(event_dict)
    # Use custom keys if provided, otherwise use defaults
    sensitive_keys_to_use = _sensitive_keys if _sensitive_keys else DEFAULT_SENSITIVE_KEYS
    for key in list(redacted.keys()):
        key_lower: str = key.lower()
        for sensitive in sensitive_keys_to_use:
            if sensitive in key_lower:
                redacted[key] = "[REDACTED]"
                break
    # Content-level redaction for line_preview (stderr callback)
    line_preview = redacted.get("line_preview")
    if isinstance(line_preview, str):
        redacted["line_preview"] = _redact_line_content(line_preview)
    return redacted


def get_log_level() -> str:
    """Get log level from environment variable or return default.

    Returns:
        Log level string (DEBUG, INFO, WARNING, ERROR)
    """
    return os.environ.get("LOG_LEVEL", "INFO").upper()


def _write_to_file(event_dict: EventDict) -> None:
    """Write log event to file using rotating file handler."""
    global _log_file_handler, _json_mode

    if _log_file_handler is None:
        return

    try:
        # Get values from event dict safely
        def safe_get(key: str, default: str = "-") -> str:
            value: object = cast(object, event_dict.get(key, default))
            return str(value) if value is not None else default

        run_id = safe_get("run_id")
        node_id = safe_get("node_id")
        level = safe_get("level", "INFO")
        event_val: object | None = cast(object | None, event_dict.get("event"))
        message_val: object = cast(object, event_dict.get("message", ""))
        message = str(event_val) if event_val is not None else str(message_val)

        timestamp = datetime.now(BEIJING_TZ).isoformat()

        if _json_mode:
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "run_id": run_id,
                "node_id": node_id,
                "message": message,
            }
            # Add other fields
            for key, value in event_dict.items():  # type: ignore[assignment]
                key_str: str = str(key)
                value_obj: object = cast(object, value)
                if key_str not in [
                    "event",
                    "level",
                    "run_id",
                    "node_id",
                    "timestamp",
                    "message",
                ]:
                    log_entry[key_str] = value_obj
            line = json.dumps(log_entry)
        else:
            extra_parts = []
            for key, value in event_dict.items():
                key_str: str = str(key)
                if key_str not in [
                    "event",
                    "level",
                    "run_id",
                    "node_id",
                    "timestamp",
                    "message",
                ]:
                    extra_parts.append(f"{key_str}={value}")
            extra = " ".join(extra_parts)
            if extra:
                line = f'{timestamp} [{level}] run_id={run_id} node_id={node_id} message="{message}" {extra}\n'
            else:
                line = f'{timestamp} [{level}] run_id={run_id} node_id={node_id} message="{message}"\n'

        # Use the rotating file handler
        _log_file_handler.emit(logging.makeLogRecord({"msg": line}))
    except Exception:
        # Silently ignore file write errors
        pass


class _FileWriterProcessor:
    """Processor that writes log events to a file."""

    def __call__(self, _: Any, __: str, event_dict: EventDict) -> EventDict:
        _write_to_file(event_dict)
        return event_dict


def configure_logging(
    log_level: str | None = None,
    log_dir: Path | None = None,
    json_format: bool = False,
    sensitive_keys: list[str] | None = None,
    max_bytes: int | None = None,
    backup_count: int | None = None,
) -> BoundLogger:
    """Configure structured logging with dual output (console + file).

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to env var or INFO.
        log_dir: Directory for log files. Defaults to ./logs/
        json_format: Whether to use JSON format for file output.
        sensitive_keys: Additional keys to treat as sensitive.
        max_bytes: Maximum log file size before rotation (default 10MB).
        backup_count: Number of backup files to keep (default 5).

    Returns:
        Configured structlog bound logger
    """
    global _logger, _configured, _log_file, _log_file_handler, _json_mode, _sensitive_keys
    global _max_bytes, _backup_count

    # If already configured, just return existing logger
    if _configured:
        assert _logger is not None
        return _logger

    # Store config
    _json_mode = json_format

    # Store custom sensitive keys
    if sensitive_keys:
        _sensitive_keys = sensitive_keys

    # Store rotation settings
    if max_bytes is not None:
        _max_bytes = max_bytes
    if backup_count is not None:
        _backup_count = backup_count

    # Determine log level
    log_level = log_level.upper() if log_level else get_log_level()

    # Determine log directory
    log_directory = log_dir if log_dir else Path("./logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    # Create date-based log filename (using Beijing time)
    date_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    _log_file = log_directory / f"docuswarm-{date_str}.log"

    # Create rotating file handler
    _log_file_handler = logging.handlers.RotatingFileHandler(
        filename=str(_log_file),
        maxBytes=_max_bytes,
        backupCount=_backup_count,
        encoding="utf-8",
    )
    # Set handler level to DEBUG to capture all logs
    _log_file_handler.setLevel(logging.DEBUG)
    # Disable formatter since we handle formatting in _write_to_file
    _log_file_handler.setFormatter(logging.Formatter("%(message)s"))

    # Configure processors for console output
    processors: list[_Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        _redact_sensitive_fields,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        _BeijingTimeStamper(),
        _FileWriterProcessor(),  # Write to file
    ]

    # Add console renderer for console output
    if not json_format:
        processors.append(  # type: ignore[arg-type]
            structlog.dev.ConsoleRenderer(colors=True)
        )
    else:
        processors.append(JSONRenderer())  # type: ignore[arg-type]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Create the base logger
    _logger = cast(BoundLogger, structlog.get_logger())

    # Store configuration
    _configured = True

    # Assert logger is not None for return type
    assert _logger is not None
    return _logger


def bind_context(
    logger: BoundLogger,
    run_id: str | None = None,
    node_id: str | None = None,
    **kwargs: object,
) -> BoundLogger:
    """Bind context (run_id, node_id) to logger for async safety.

    Uses structlog.contextvars for async-safe context binding.

    Args:
        logger: The logger to bind context to
        run_id: The run ID to bind
        node_id: The node ID to bind
        **kwargs: Additional context key-value pairs

    Returns:
        Logger with bound context
    """
    context: dict[str, object] = {}
    if run_id:
        context["run_id"] = run_id
    if node_id:
        context["node_id"] = node_id
    context.update(kwargs)

    # Bind context using contextvars for async safety
    _: dict[str, object] = structlog.contextvars.bind_contextvars(**context)

    return logger


def get_logger(name: str | None = None) -> BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Optional logger name

    Returns:
        Configured structlog logger
    """
    global _logger, _configured

    if not _configured:
        _ = configure_logging()

    # After configuration, _logger is guaranteed to be set
    assert _logger is not None, "Logger not configured"

    if name:
        return _logger.bind(_module=name)

    return _logger


# Convenience functions for logging
def debug(message: str, **kwargs: object) -> None:
    """Log a debug message."""
    logger = get_logger()
    logger.debug(message, **kwargs)


def info(message: str, **kwargs: object) -> None:
    """Log an info message."""
    logger = get_logger()
    logger.info(message, **kwargs)


def warning(message: str, **kwargs: object) -> None:
    """Log a warning message."""
    logger = get_logger()
    logger.warning(message, **kwargs)


def error(message: str, **kwargs: object) -> None:
    """Log an error message."""
    logger = get_logger()
    logger.error(message, **kwargs)


def set_log_context(run_id: str | None = None, node_id: str | None = None) -> None:
    """Set logging context for the current execution.

    Uses contextvars for async-safe context propagation.

    Args:
        run_id: The run ID to bind to logs
        node_id: The node ID to bind to logs
    """
    context: dict[str, object] = {}
    if run_id:
        context["run_id"] = run_id
    if node_id:
        context["node_id"] = node_id

    if context:
        _: dict[str, object] = structlog.contextvars.bind_contextvars(**context)


def clear_log_context() -> None:
    """Clear all logging context.

    Removes any bound run_id, node_id, or other context variables.
    """
    # Clear all bound context variables
    structlog.contextvars.clear_contextvars()


def reset_logging() -> None:
    """Reset logging configuration.

    Useful for testing or reconfiguration.
    """
    global _logger, _configured, _log_file, _log_file_handler

    # Close the file handler
    if _log_file_handler is not None:
        _log_file_handler.close()
        _log_file_handler = None

    _logger = None
    _configured = False
    _log_file = None
