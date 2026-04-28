"""Custom exceptions for DocuSwarm.

This module provides a comprehensive exception hierarchy for the DocuSwarm
multi-agent document orchestration system. All exceptions support context
information storage for debugging and logging purposes.

Exception Hierarchy:
    DocuSwarmError (base)
    ├── ConfigurationError
    ├── StorageError
    ├── LLMError
    ├── PipelineError
    └── ContextIsolationError

Usage:
    from autoBMAD.docuswarm.exceptions import (
        DocuSwarmError,
        ConfigurationError,
        StorageError,
        LLMError,
        PipelineError,
        ContextIsolationError,
    )

    # Simple usage
    raise ConfigurationError("Invalid API key")

    # With context
    raise LLMError(
        "API rate limit exceeded",
        model_name="gpt-4",
        api_error_type="RateLimitError",
        raw_response={"error": {"code": 429}}
    )

    # Catch by base
    try:
        ...
    except DocuSwarmError as e:
        print(f"DocuSwarm error: {e}, context: {e.context}")
"""

from __future__ import annotations

from typing import Any, override


class DocuSwarmError(Exception):
    """Base exception for all DocuSwarm errors.

    This is the root exception class for the DocuSwarm system. All custom
    exceptions should inherit from this class to enable easy error catching
    and hierarchical error handling.

    Attributes:
        message: The error message.
        context: Dictionary containing additional context information
            such as operation details, related IDs, or original errors.

    Example:
        >>> try:
        ...     raise DocuSwarmError("Something went wrong", context={"id": 123})
        ... except DocuSwarmError as e:
        ...     print(e.context)  # {'id': 123}
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize DocuSwarmError.

        Args:
            message: The error message. If None, uses the class docstring.
            context: Optional dictionary with additional context information.
            **kwargs: Additional context fields stored directly in context.
        """
        super().__init__(message or "An error occurred")
        self._message = message or "An error occurred"
        # Build context from explicit param and kwargs
        self._context = context.copy() if context else {}
        self._context.update(kwargs)

    @property
    def context(self) -> dict[str, Any]:
        """Get the context dictionary for this exception.

        Returns:
            Dictionary containing context information about the error.
        """
        return self._context

    @context.setter
    def context(self, value: dict[str, Any]) -> None:
        """Set the context dictionary."""
        self._context = value

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for logging/serialization.

        Returns:
            Dictionary with keys: type, message, context.
        """
        return {
            "type": self.__class__.__name__,
            "message": self._message,
            "context": self._context,
        }

    @override
    def __reduce__(self) -> tuple[type, tuple[str, dict[str, Any]]]:
        """Support pickling for async task queue support.

        Returns:
            Tuple of (class, args) for pickling.
        """
        return (self.__class__, (self._message, self._context))

    @override
    def __repr__(self) -> str:
        """Return string representation with context."""
        ctx_str = f", context={self._context}" if self._context else ""
        return f"{self.__class__.__name__}({self._message!r}{ctx_str})"


class ConfigurationError(DocuSwarmError):
    """Raised when configuration is invalid, missing, or malformed.

    This exception is used for all configuration-related errors including
    missing required fields, invalid values, and environment variable issues.

    Attributes:
        config_key: The configuration key that caused the error.
        config_source: The source of the configuration (e.g., 'environment',
            'file', 'default').

    Example:
        >>> raise ConfigurationError(
        ...     "Missing required API key",
        ...     config_key="openai_api_key",
        ...     config_source="environment"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        config_key: str | None = None,
        config_source: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize ConfigurationError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            config_key: The configuration key that caused the error.
            config_source: Source of the config (e.g., 'environment', 'file').
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if config_key is not None:
            self._context["config_key"] = config_key
        if config_source is not None:
            self._context["config_source"] = config_source

    @property
    def config_key(self) -> str | None:
        """Get the configuration key that caused the error."""
        return self._context.get("config_key")

    @property
    def config_source(self) -> str | None:
        """Get the source of the configuration."""
        return self._context.get("config_source")


class StorageError(DocuSwarmError):
    """Raised when a storage or database operation fails.

    This exception covers file system operations, database queries, and
    any persistent storage failures. It captures operation type and
    relevant path/table information for debugging.

    Attributes:
        operation_type: Type of operation (e.g., 'read', 'write', 'delete').
        file_path: File path involved in the operation (if applicable).
        table_name: Database table name (if applicable).

    Example:
        >>> raise StorageError(
        ...     "Failed to read user data",
        ...     operation_type="read",
        ...     file_path="/data/users.json"
        ... )

        >>> raise StorageError(
        ...     "Database query failed",
        ...     operation_type="read",
        ...     table_name="documents"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        operation_type: str | None = None,
        file_path: str | None = None,
        table_name: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize StorageError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            operation_type: Type of storage operation ('read', 'write', 'delete').
            file_path: File path involved in the operation.
            table_name: Database table name.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if operation_type is not None:
            self._context["operation_type"] = operation_type
        if file_path is not None:
            self._context["file_path"] = file_path
        if table_name is not None:
            self._context["table_name"] = table_name

    @property
    def operation_type(self) -> str | None:
        """Get the type of storage operation."""
        return self._context.get("operation_type")

    @property
    def file_path(self) -> str | None:
        """Get the file path involved in the operation."""
        return self._context.get("file_path")

    @property
    def table_name(self) -> str | None:
        """Get the database table name."""
        return self._context.get("table_name")


class LLMError(DocuSwarmError):
    """Raised when an LLM API call fails or returns an error.

    This exception captures information about LLM-related failures including
    the model name, API error type, and raw response for debugging.

    Attributes:
        model_name: Name of the LLM model (e.g., 'gpt-4', 'claude-3').
        api_error_type: Type of API error (e.g., 'RateLimitError',
            'AuthenticationError', 'TimeoutError').
        raw_response: Raw API response dictionary if available.

    Example:
        >>> raise LLMError(
        ...     "API rate limit exceeded",
        ...     model_name="gpt-4",
        ...     api_error_type="RateLimitError",
        ...     raw_response={"error": {"message": "Rate limit", "code": 429}}
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        model_name: str | None = None,
        api_error_type: str | None = None,
        raw_response: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize LLMError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            model_name: Name of the LLM model.
            api_error_type: Type of API error.
            raw_response: Raw API response dictionary.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if model_name is not None:
            self._context["model_name"] = model_name
        if api_error_type is not None:
            self._context["api_error_type"] = api_error_type
        if raw_response is not None:
            self._context["raw_response"] = raw_response

    @property
    def model_name(self) -> str | None:
        """Get the LLM model name."""
        return self._context.get("model_name")

    @property
    def api_error_type(self) -> str | None:
        """Get the API error type."""
        return self._context.get("api_error_type")

    @property
    def raw_response(self) -> dict[str, Any] | None:
        """Get the raw API response."""
        return self._context.get("raw_response")


class PipelineError(DocuSwarmError):
    """Raised when a pipeline operation fails.

    This exception captures information about pipeline execution failures,
    including pipeline ID, node ID, and current state for debugging.

    Attributes:
        pipeline_id: Unique identifier of the pipeline.
        node_id: Identifier of the node where the error occurred.
        current_state: Current state of the pipeline/node when error occurred.

    Example:
        >>> raise PipelineError(
        ...     "Node execution failed",
        ...     pipeline_id="pipeline-123",
        ...     node_id="node-456",
        ...     current_state="processing"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        pipeline_id: str | None = None,
        node_id: str | None = None,
        current_state: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize PipelineError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            pipeline_id: Unique pipeline identifier.
            node_id: Node identifier where error occurred.
            current_state: Current state when error occurred.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if pipeline_id is not None:
            self._context["pipeline_id"] = pipeline_id
        if node_id is not None:
            self._context["node_id"] = node_id
        if current_state is not None:
            self._context["current_state"] = current_state

    @property
    def pipeline_id(self) -> str | None:
        """Get the pipeline ID."""
        return self._context.get("pipeline_id")

    @property
    def node_id(self) -> str | None:
        """Get the node ID."""
        return self._context.get("node_id")

    @property
    def current_state(self) -> str | None:
        """Get the current state when error occurred."""
        return self._context.get("current_state")


class OrchestratorError(DocuSwarmError):
    """Base exception for orchestrator errors.

    This exception serves as the base class for all orchestrator-related
    errors, providing a common exception type for pipeline orchestration
    failures.

    Example:
        >>> raise OrchestratorError("Pipeline execution failed")
    """

    pass


class ContextIsolationError(DocuSwarmError):
    """Raised when context isolation principles are violated.

    This critical exception enforces the "dumb agent" isolation principle.
    It captures detailed information about context violations including
    the agent involved, violation type, and source/target contexts.

    This is critical for maintaining the architectural principle that
    agents should not have access to each other's internal state or
    violate context boundaries.

    Attributes:
        violation_type: Type of violation (e.g., 'unauthorized_access',
            'state_leak', 'memory_leak', 'cross_context_access').
        agent_id: Identifier of the agent that caused the violation.
        source_context: The context that was accessed inappropriately.
        target_context: The target context that should not have been accessed.
        attempted_access: Type of access attempted ('read', 'write', 'execute').
        resource: The specific resource that was accessed inappropriately.

    Example:
        >>> raise ContextIsolationError(
        ...     "Agent accessed unauthorized context",
        ...     violation_type="unauthorized_access",
        ...     agent_id="agent-001",
        ...     source_context="agent_memory",
        ...     target_context="global_state",
        ...     resource="system_prompt"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        violation_type: str | None = None,
        agent_id: str | None = None,
        source_context: str | None = None,
        target_context: str | None = None,
        attempted_access: str | None = None,
        resource: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize ContextIsolationError.

        Args:
            message: The error message describing the violation.
            context: Optional context dictionary.
            violation_type: Type of isolation violation.
            agent_id: ID of agent that caused the violation.
            source_context: Context that was accessed from.
            target_context: Context that was accessed inappropriately.
            attempted_access: Type of access attempted.
            resource: Specific resource that was accessed.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if violation_type is not None:
            self._context["violation_type"] = violation_type
        if agent_id is not None:
            self._context["agent_id"] = agent_id
        if source_context is not None:
            self._context["source_context"] = source_context
        if target_context is not None:
            self._context["target_context"] = target_context
        if attempted_access is not None:
            self._context["attempted_access"] = attempted_access
        if resource is not None:
            self._context["resource"] = resource

    @property
    def violation_type(self) -> str | None:
        """Get the type of isolation violation."""
        return self._context.get("violation_type")

    @property
    def agent_id(self) -> str | None:
        """Get the agent ID that caused the violation."""
        return self._context.get("agent_id")

    @property
    def source_context(self) -> str | None:
        """Get the source context."""
        return self._context.get("source_context")

    @property
    def target_context(self) -> str | None:
        """Get the target context."""
        return self._context.get("target_context")

    @property
    def attempted_access(self) -> str | None:
        """Get the type of access attempted."""
        return self._context.get("attempted_access")

    @property
    def resource(self) -> str | None:
        """Get the specific resource accessed."""
        return self._context.get("resource")


class NodeExecutionError(PipelineError):
    """Raised when a node execution fails.

    This exception is an alias for PipelineError, provided for semantic clarity
    when the error specifically relates to node execution failures such as
    timeouts, validation failures, or state transition errors.

    Example:
        >>> raise NodeExecutionError(
        ...     "Node timeout during execution",
        ...     node_id="node-456",
        ...     current_state="processing"
        ... )
    """

    pass


class ContextValidationError(OrchestratorError):
    """Raised when context validation fails.

    This exception is used when the context provided to the pipeline
    does not meet validation requirements. This can include:
    - Missing required fields
    - Invalid field types or values
    - Insufficient context for pipeline execution

    Attributes:
        validation_errors: List of specific validation error messages.

    Example:
        >>> raise ContextValidationError(
        ...     "Context validation failed",
        ...     validation_errors=["Missing required field 'subject'"]
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        validation_errors: list[str] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize ContextValidationError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            validation_errors: List of specific validation error messages.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if validation_errors is not None:
            self._context["validation_errors"] = validation_errors

    @property
    def validation_errors(self) -> list[str] | None:
        """Get the list of validation errors."""
        return self._context.get("validation_errors")


class FileToolError(DocuSwarmError):
    """Raised when a file tool operation fails.

    This exception serves as the base class for all file tool-related errors,
    providing a common exception type for file reading and listing operations.

    Attributes:
        file_path: Path to the file that caused the error.
        operation: The operation being performed (e.g., 'read', 'list').

    Example:
        >>> raise FileToolError(
        ...     "File operation failed",
        ...     file_path="/docs/file.txt",
        ...     operation="read"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        file_path: str | None = None,
        operation: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize FileToolError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            file_path: Path to the file that caused the error.
            operation: The operation being performed.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if file_path is not None:
            self._context["file_path"] = file_path
        if operation is not None:
            self._context["operation"] = operation

    @property
    def file_path(self) -> str | None:
        """Get the file path that caused the error."""
        return self._context.get("file_path")

    @property
    def operation(self) -> str | None:
        """Get the operation being performed."""
        return self._context.get("operation")


class PathNotAllowedError(FileToolError):
    """Raised when a path is outside allowed directories.

    This exception enforces the security boundary for file operations,
    preventing path traversal attacks and unauthorized access attempts.

    Attributes:
        requested_path: The path that was requested.
        allowed_dirs: List of directories that are allowed to be accessed.

    Example:
        >>> raise PathNotAllowedError(
        ...     "Path not in allowed directories",
        ...     requested_path="/etc/passwd",
        ...     allowed_dirs=["/docs", "/docs/research"]
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        requested_path: str | None = None,
        allowed_dirs: list[str] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize PathNotAllowedError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            requested_path: The path that was requested.
            allowed_dirs: List of allowed directories.
            **kwargs: Additional context fields.
        """
        if message is None and requested_path is not None:
            message = f"Path not in allowed directories: {requested_path}"

        super().__init__(message, context, **kwargs)
        if requested_path is not None:
            self._context["requested_path"] = requested_path
        if allowed_dirs is not None:
            self._context["allowed_dirs"] = allowed_dirs

    @property
    def requested_path(self) -> str | None:
        """Get the requested path."""
        return self._context.get("requested_path")

    @property
    def allowed_dirs(self) -> list[str]:
        """Get the list of allowed directories."""
        return self._context.get("allowed_dirs", [])

    @override
    def __str__(self) -> str:
        """Return formatted error message with allowed directories."""
        base_msg = self._message
        allowed = self.allowed_dirs
        if allowed:
            allowed_str = ", ".join(f"'{d}'" for d in allowed)
            return f"{base_msg}. Allowed directories: [{allowed_str}]"
        return base_msg


class FileTooLargeError(FileToolError):
    """Raised when a file exceeds the size limit.

    This exception prevents memory issues when attempting to read
    excessively large files.

    Attributes:
        file_path: Path to the file that exceeded the limit.
        file_size: Actual size of the file in characters.
        max_size: Maximum allowed size in characters.

    Example:
        >>> raise FileTooLargeError(
        ...     "File exceeds size limit",
        ...     file_path="/docs/large.txt",
        ...     file_size=100000,
        ...     max_size=50000
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        file_path: str | None = None,
        file_size: int | None = None,
        max_size: int | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize FileTooLargeError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            file_path: Path to the file.
            file_size: Actual size of the file.
            max_size: Maximum allowed size.
            **kwargs: Additional context fields.
        """
        if message is None and file_size is not None and max_size is not None:
            message = f"File size ({file_size}) exceeds maximum allowed ({max_size})"

        super().__init__(message, context, **kwargs)
        if file_path is not None:
            self._context["file_path"] = file_path
        if file_size is not None:
            self._context["file_size"] = file_size
        if max_size is not None:
            self._context["max_size"] = max_size

    @property
    def file_size(self) -> int | None:
        """Get the file size."""
        return self._context.get("file_size")

    @property
    def max_size(self) -> int | None:
        """Get the maximum allowed size."""
        return self._context.get("max_size")


class SearchToolError(DocuSwarmError):
    """Raised when a search tool operation fails.

    This exception serves as the base class for all search tool-related errors,
    providing a common exception type for grep and glob search operations.

    Attributes:
        search_dirs: List of directories being searched.
        operation: The operation being performed (e.g., 'grep', 'glob').

    Example:
        >>> raise SearchToolError(
        ...     "Search operation failed",
        ...     search_dirs=["/docs"],
        ...     operation="grep"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        search_dirs: list[str] | None = None,
        operation: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize SearchToolError.

        Args:
            message: The error message.
            context: Optional context dictionary.
            search_dirs: List of directories being searched.
            operation: The operation being performed.
            **kwargs: Additional context fields.
        """
        super().__init__(message, context, **kwargs)
        if search_dirs is not None:
            self._context["search_dirs"] = search_dirs
        if operation is not None:
            self._context["operation"] = operation

    @property
    def search_dirs(self) -> list[str] | None:
        """Get the search directories."""
        return self._context.get("search_dirs")

    @property
    def operation(self) -> str | None:
        """Get the operation being performed."""
        return self._context.get("operation")


# Define public API
__all__ = [
    "DocuSwarmError",
    "ConfigurationError",
    "StorageError",
    "LLMError",
    "PipelineError",
    "NodeExecutionError",
    "ContextIsolationError",
    "ContextValidationError",
    "OrchestratorError",
    "FileToolError",
    "PathNotAllowedError",
    "FileTooLargeError",
    "SearchToolError",
]
