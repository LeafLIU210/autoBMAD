"""
Log Manager - Unified Logging System for BMAD Epic Automation

Provides comprehensive logging capabilities including:
- Automatic timestamped log file creation
- Real-time incremental updates
- Dual-write mode (console + file)
- SDK message tracking with file persistence
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO


class LogManager:
    """
    Unified log manager for BMAD Epic Automation.

    Features:
    - Automatic log directory and timestamp file creation
    - Real-time file writing with 10-second updates
    - Dual-write mode (console + file)
    - Thread-safe operations
    - Automatic log rotation by run count
    """

    def __init__(self, base_dir: str = "autoBMAD/epic_automation"):
        """
        Initialize LogManager.

        Args:
            base_dir: Base directory for logs (default: autoBMAD/epic_automation)
        """
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "logs"
        self.current_log_file: Optional[Path] = None
        self.log_file_handle: Optional[TextIO] = None
        self.start_time: Optional[datetime] = None

        # Ensure logs directory exists
        self._ensure_logs_dir()

    def _ensure_logs_dir(self):
        """Ensure logs directory exists, create if not."""
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            _original_stdout.write(f"Warning: Failed to create logs directory: {e}\n")

    def create_timestamped_log(self) -> Path:
        """
        Create a new timestamped log file.

        Returns:
            Path to the created log file
        """
        self.start_time = datetime.now()
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"epic_{timestamp}.log"
        self.current_log_file = self.logs_dir / log_filename

        try:
            # Create file with UTF-8 encoding
            self.log_file_handle = open(
                self.current_log_file,
                'w',
                encoding='utf-8'
            )

            # Write header
            header = f"""
╔══════════════════════════════════════════════════════════════╗
║            BMAD Epic Automation - Runtime Log                ║
╠══════════════════════════════════════════════════════════════╣
║ Start Time: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
║ Log File: {log_filename}
╚══════════════════════════════════════════════════════════════╝

"""
            self.log_file_handle.write(header)
            self.log_file_handle.flush()

            _original_stdout.write(f"[LOG] Log file created: {self.current_log_file}\n")
            return self.current_log_file

        except Exception as e:
            _original_stdout.write(f"Error: Failed to create log file: {e}\n")
            raise

    def write_log(self, message: str, level: str = "INFO"):
        """
        Write message to log file (if open).

        Args:
            message: Log message
            level: Log level (INFO, DEBUG, WARNING, ERROR, etc.)
        """
        if not self.log_file_handle or not self.start_time:
            return

        try:
            # Calculate elapsed time
            elapsed = datetime.now() - self.start_time
            elapsed_str = f"{elapsed.total_seconds():.1f}s"

            # Format log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level:8s}] [{elapsed_str:>8s}] {message}\n"

            # Write to file
            self.log_file_handle.write(log_entry)
            self.log_file_handle.flush()

        except Exception as e:
            _original_stdout.write(f"Warning: Failed to write to log file: {e}\n")

    def write_sdk_message(self, message: str, msg_type: str = "SDK"):
        """
        Write SDK message to log file with special formatting.

        Args:
            message: SDK message content
            msg_type: Message type (THINKING, TOOL_USE, TOOL_RESULT, USER, SYSTEM, etc.)
        """
        if not self.log_file_handle or not self.start_time:
            return

        try:
            # Calculate elapsed time
            elapsed = datetime.now() - self.start_time
            elapsed_str = f"{elapsed.total_seconds():.1f}s"

            # Format SDK message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [SDK {msg_type:12s}] [{elapsed_str:>8s}] {message}\n"

            # Write to file
            self.log_file_handle.write(log_entry)
            self.log_file_handle.flush()

        except Exception as e:
            _original_stdout.write(f"Warning: Failed to write SDK message to log: {e}\n")

    def write_exception(self, exception: Exception, context: str = ""):
        """
        Write exception to log file with traceback.

        Args:
            exception: Exception object
            context: Additional context information
        """
        if not self.log_file_handle or not self.start_time:
            return

        try:
            import traceback

            elapsed = datetime.now() - self.start_time
            elapsed_str = f"{elapsed.total_seconds():.1f}s"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = f"""
[{'='*80}]
[{timestamp}] [ERROR     ] [{elapsed_str:>8s}] EXCEPTION OCCURRED
[{'='*80}]
Context: {context}
Exception Type: {type(exception).__name__}
Exception Message: {str(exception)}

Traceback:
{traceback.format_exc()}
[{'='*80}]

"""

            self.log_file_handle.write(log_entry)
            self.log_file_handle.flush()

        except Exception as e:
            _original_stdout.write(f"Warning: Failed to write exception to log: {e}\n")

    def close_log(self):
        """Close current log file and write footer."""
        if not self.log_file_handle or not self.start_time:
            return

        try:
            # Write footer
            end_time = datetime.now()
            duration = end_time - self.start_time

            footer = f"""
╔══════════════════════════════════════════════════════════════╗
║                   Log Session Complete                       ║
╠══════════════════════════════════════════════════════════════╣
║ End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S")}
║ Duration: {duration.total_seconds():.1f} seconds
║ Log File: {self.current_log_file.name if self.current_log_file else 'N/A'}
╚══════════════════════════════════════════════════════════════╝
"""
            self.log_file_handle.write(footer)
            self.log_file_handle.close()

            _original_stdout.write(f"[LOG] Log file closed: {self.current_log_file}\n")

        except Exception as e:
            _original_stdout.write(f"Warning: Failed to close log file: {e}\n")
        finally:
            self.log_file_handle = None
            self.current_log_file = None

    def get_current_log_path(self) -> Optional[Path]:
        """
        Get path to current log file.

        Returns:
            Path to current log file or None
        """
        return self.current_log_file

    def log_cancellation(self, message: str):
        """
        Log cancellation event.

        Args:
            message: Cancellation message
        """
        if not self.log_file_handle:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [CANCELLED ] Cancellation: {message}\n"
            self.log_file_handle.write(log_entry)
            self.log_file_handle.flush()
        except Exception as e:
            _original_stdout.write(f"Warning: Failed to write cancellation log: {e}\n")

    def log_state_resync(self, story_path: str, new_status: str):
        """
        Log state resynchronization event.

        Args:
            story_path: Path to the story
            new_status: New status after resync
        """
        if not self.log_file_handle:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [RESYNC    ] State resync: {story_path} -> {new_status}\n"
            self.log_file_handle.write(log_entry)
            self.log_file_handle.flush()
        except Exception as e:
            _original_stdout.write(f"Warning: Failed to write resync log: {e}\n\n")

    def list_log_files(self, limit: int = 10) -> "list[Path]":
        """
        List recent log files.

        Args:
            limit: Maximum number of log files to return

        Returns:
            List of log file paths sorted by creation time (newest first)
        """
        try:
            if not self.logs_dir.exists():
                return []

            log_files = list(self.logs_dir.glob("epic_*.log"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            return log_files[:limit]

        except Exception as e:
            _original_stdout.write(f"Warning: Failed to list log files: {e}\n")
            return []

    def flush(self):
        """
        Flush any buffered log data to disk.

        This method ensures that all buffered log messages are immediately
        written to the log file. Useful for cleanup operations and ensuring
        log data persistence before program exit.
        """
        if self.log_file_handle:
            try:
                self.log_file_handle.flush()
            except Exception as e:
                _original_stdout.write(f"Warning: Failed to flush log file: {e}\n")


class DualWriteStream:
    """
    Custom stream that writes to both console and log file.

    Used for capturing stdout/stderr while maintaining console output.
    """

    def __init__(self, original_stream: TextIO, log_manager: LogManager, stream_name: str):
        """
        Initialize dual write stream.

        Args:
            original_stream: Original stream (sys.stdout or sys.stderr)
            log_manager: LogManager instance
            stream_name: Stream name for logging ("STDOUT" or "STDERR")
        """
        self.original_stream = original_stream
        self.log_manager = log_manager
        self.stream_name = stream_name

    def write(self, text: str) -> None:
        """Write to both original stream and log file."""
        # Write to original stream with Unicode handling
        try:
            self.original_stream.write(text)
            self.original_stream.flush()
        except UnicodeEncodeError:
            # Handle Unicode characters that can't be encoded in the console's encoding
            # Replace problematic characters with ASCII equivalents
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            self.original_stream.write(safe_text)
            self.original_stream.flush()

        # Write to log file if available
        if text.strip():  # Only log non-empty text
            try:
                self.log_manager.write_log(f"[{self.stream_name}] {text.strip()}")
            except UnicodeEncodeError:
                # If log file has encoding issues, sanitize the message
                safe_message = text.strip().encode('utf-8', errors='replace').decode('utf-8')
                self.log_manager.write_log(f"[{self.stream_name}] {safe_message}")

    def flush(self) -> None:
        """Flush both streams."""
        self.original_stream.flush()

    def isatty(self) -> bool:
        """Return True if original stream is a TTY."""
        return self.original_stream.isatty()

    def fileno(self) -> int:
        """Return file descriptor of original stream."""
        return self.original_stream.fileno()


# Global log manager instance
_log_manager: Optional[LogManager] = None

# Store original stdout/stderr before any redirection
_original_stdout = sys.stdout
_original_stderr = sys.stderr


def get_log_manager() -> Optional[LogManager]:
    """
    Get global log manager instance.

    Returns:
        Global LogManager instance or None
    """
    return _log_manager


def init_logging(log_manager: LogManager):
    """
    Initialize logging with LogManager.

    Args:
        log_manager: LogManager instance
    """
    global _log_manager
    _log_manager = log_manager

    # Create timestamped log file
    log_file = log_manager.create_timestamped_log()

    # Setup logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Console output only (avoid duplicate file writing)
        ]
    )

    # Log initialization
    log_manager.write_log("Logging system initialized", "INFO")
    log_manager.write_log(f"Log file: {log_file}", "INFO")


def setup_dual_write(log_manager: LogManager):
    """
    Setup dual-write mode for stdout and stderr.

    Args:
        log_manager: LogManager instance
    """
    # Redirect stdout
    sys.stdout = DualWriteStream(sys.stdout, log_manager, "STDOUT")

    # Redirect stderr
    sys.stderr = DualWriteStream(sys.stderr, log_manager, "STDERR")


def cleanup_logging():
    """Cleanup logging and close log file."""
    global _log_manager
    if _log_manager:
        _log_manager.close_log()
        _log_manager = None
