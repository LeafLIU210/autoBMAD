"""ContextValidator framework for unified validation.

This module provides the ContextValidator framework with Strategy Pattern + Composite Pattern
for the ContextValidator unification refactor (EPIC-27).

Components:
- ValidationIssue: Data class for validation problems
- ValidationResult: Data class for validation outcomes
- ValidationStrategy: Abstract base class for validation strategies
- ValidationRuleRegistry: Registry for node-specific validation rules
- ContextValidator: Main facade class for all validation operations
"""

from __future__ import annotations

import json
import threading
from abc import ABC, abstractmethod
from collections.abc import Coroutine
from dataclasses import dataclass, field
from typing import Any, cast, override

# Default validation rules - used as fallback when node-specific rules are not defined
DEFAULT_VALIDATION_RULES: dict[str, Any] = {
    "min_word_count": 100,
    "required_sections": ["analysis"],
    "allow_empty_output": False,
}


@dataclass
class ValidationIssue:
    """Data class representing a validation issue.

    Attributes:
        field: Field path where the issue occurred (e.g., "deliverable.file_path")
        message: Human-readable description of the issue
        severity: Severity level - "error", "warning", or "info"
        code: Machine-readable error code (e.g., "MISSING_REQUIRED_FIELD")

    Example:
        >>> issue = ValidationIssue(
        ...     field="deliverable.title",
        ...     message="Title is required",
        ...     severity="error",
        ...     code="MISSING_TITLE",
        ... )
    """

    field: str
    message: str
    severity: str
    code: str


@dataclass
class ValidationResult:
    """Data class representing the result of a validation operation.

    Attributes:
        valid: Whether the validation passed (no errors)
        issues: List of error-level ValidationIssue objects
        warnings: List of warning/info-level ValidationIssue objects
        metadata: Additional context about the validation

    Example:
        >>> result = ValidationResult(valid=True)
        >>> result.add_error("field", "message", "CODE")
        >>> print(result.has_errors)  # True
    """

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues.

        Returns:
            True if there are errors in the issues list.
        """
        return len(self.issues) > 0

    def add_error(self, field: str, message: str, code: str) -> None:
        """Add an error issue and mark validation as invalid.

        Args:
            field: Field path where the error occurred
            message: Human-readable error description
            code: Machine-readable error code
        """
        self.issues.append(
            ValidationIssue(
                field=field,
                message=message,
                severity="error",
                code=code,
            )
        )
        self.valid = False

    def add_warning(self, field: str, message: str, code: str) -> None:
        """Add a warning issue without affecting valid status.

        Args:
            field: Field path where the warning occurred
            message: Human-readable warning description
            code: Machine-readable warning code
        """
        self.warnings.append(
            ValidationIssue(
                field=field,
                message=message,
                severity="warning",
                code=code,
            )
        )


class ValidationStrategy(ABC):
    """Abstract base class for validation strategies.

    Subclasses must implement the validate method to provide specific
    validation logic. Used with the Strategy Pattern for extensible
    validation rules.

    Example:
        >>> class MyStrategy(ValidationStrategy):
        ...     def validate(self, data, config=None):
        ...         return ValidationResult(valid=True)
        ...     @property
        ...     def strategy_name(self):
        ...         return "MyStrategy"
    """

    @abstractmethod
    def validate(
        self,
        data: Any,
        config: dict[str, Any] | None = None,
    ) -> ValidationResult | Coroutine[Any, Any, ValidationResult]:
        """Execute validation on the provided data.

        Args:
            data: The data to validate
            config: Optional configuration for validation rules

        Returns:
            ValidationResult containing validation outcome, or a Coroutine
            that resolves to ValidationResult for async implementations.
        """
        ...

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier for the strategy
        """
        ...


class PrivateFieldIsolationStrategy(ValidationStrategy):
    """Strategy for validating private field isolation.

    This strategy recursively checks data structures for private fields
    that should not be exposed to the Evaluator agent. Private fields
    are identified by the '_' prefix convention (but not dunder methods
    like '__init__' or '__dict__').

    The strategy handles nested dictionaries, lists, and circular references.

    Attributes:
        PRIVATE_FIELDS: List of field names considered private

    Example:
        >>> strategy = PrivateFieldIsolationStrategy()
        >>> result = strategy.validate({"public": "value", "_private": "secret"})
        >>> result.valid
        False
        >>> result.issues[0].field
        "_private"
    """

    # Private fields that must never be exposed to Evaluator agent
    PRIVATE_FIELDS: list[str] = [
        "private_reasoning",
        "tool_call_history",
        "iteration_feedback",
        "internal_notes",
    ]

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "PrivateFieldIsolationStrategy"
        """
        return "PrivateFieldIsolationStrategy"

    @override
    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate data does not contain private fields.

        Performs deep inspection to detect private fields at any nesting level.
        Uses a visited set to handle circular references safely.

        Args:
            data: The data dictionary to validate
            config: Optional configuration (not currently used)

        Returns:
            ValidationResult with issues for each private field leak found
        """
        result = ValidationResult(valid=True)
        visited: set[int] = set()

        self._check_recursive(data, [], result, visited)

        return result

    def _check_recursive(
        self,
        data: Any,
        path: list[str | int],
        result: ValidationResult,
        visited: set[int],
    ) -> None:
        """Recursively check for private fields in data structure.

        Args:
            data: The data to check (can be dict, list, or primitive)
            path: Current path in the data structure for error reporting
            result: ValidationResult to collect issues into
            visited: Set of object IDs already visited (for circular ref handling)
        """
        # Handle None
        if data is None:
            return

        # Handle circular references
        if isinstance(data, dict | list):
            obj_id = id(data)
            if obj_id in visited:
                return
            visited.add(obj_id)

        if isinstance(data, dict):
            # Check each key in the dictionary
            for key, value in data.items():
                key_str = str(key)

                # Check if key is a private field
                if self._is_private_field(key_str):
                    field_path = self._format_path(path + [key_str])
                    result.add_error(
                        field=field_path,
                        message=f"Private field '{key_str}' found at {field_path}",
                        code="PRIVATE_FIELD_LEAK",
                    )

                # Recursively check nested values
                self._check_recursive(value, path + [key_str], result, visited)

        elif isinstance(data, list):
            # Check each item in the list
            for idx, item in enumerate(data):
                self._check_recursive(item, path + [idx], result, visited)

        # Primitive types (str, int, float, bool) don't need checking

    def _is_private_field(self, key: str) -> bool:
        """Check if a field name is considered private.

        Private fields are identified by the '_' prefix, but dunder
        methods like '__init__' and '__dict__' are NOT considered private.

        Args:
            key: The field name to check

        Returns:
            True if the field is private, False otherwise
        """
        # Check against known private field names
        if key in self.PRIVATE_FIELDS:
            return True

        # Check for _ prefix but exclude dunder methods (double underscore)
        if key.startswith("_") and not key.startswith("__"):
            return True

        return False

    def _format_path(self, path: list[str | int]) -> str:
        """Format path list as string for error messages.

        Args:
            path: List of path components (strings or integers)

        Returns:
            Formatted path string like "['key1', 0, 'key2']"
        """
        return str(path)


class ValidationRuleRegistry:
    """Registry for node-specific validation rules.

    Maintains a mapping of node IDs to their validation configurations.
    Used by ContextValidator to look up rules for specific nodes.

    Features:
    - Thread-safe rule registration with threading.Lock
    - Shallow merge of node rules with DEFAULT_VALIDATION_RULES
    - Hot reloading support (new rules overwrite old)

    Example:
        >>> registry = ValidationRuleRegistry()
        >>> registry.register("node_1", {"min_word_count": 150})
        >>> config = registry.get_rules("node_1")  # Merged with defaults
    """

    def __init__(self) -> None:
        """Initialize the registry with empty rules dictionary and lock."""
        self._rules: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register(self, node_id: str, config: dict[str, Any]) -> None:
        """Register validation rules for a node.

        Thread-safe operation using internal lock. New rules overwrite
        existing rules for hot reloading support.

        Args:
            node_id: Unique identifier for the node
            config: Validation configuration dictionary
        """
        with self._lock:
            self._rules[node_id] = config

    def get(self, node_id: str) -> dict[str, Any]:
        """Get raw validation rules for a node (without defaults).

        Args:
            node_id: Unique identifier for the node

        Returns:
            Validation configuration dictionary, or empty dict if not found
        """
        with self._lock:
            return self._rules.get(node_id, {})

    def get_rules(self, node_id: str) -> dict[str, Any]:
        """Get merged validation rules for a node.

        Performs a shallow merge where node-specific rules override
        DEFAULT_VALIDATION_RULES. Thread-safe read operation.

        Args:
            node_id: Unique identifier for the node

        Returns:
            Merged validation configuration dictionary
        """
        with self._lock:
            node_rules = self._rules.get(node_id, {})
            # Shallow merge: node rules override defaults
            merged = {**DEFAULT_VALIDATION_RULES, **node_rules}
            return merged

    def has_rules(self, node_id: str) -> bool:
        """Check if a node has registered validation rules.

        Args:
            node_id: Unique identifier for the node

        Returns:
            True if node has explicit rules registered, False otherwise
        """
        with self._lock:
            return node_id in self._rules


class NodeExecutionContextStrategy(ValidationStrategy):
    """Strategy for validating NodeExecutionContext protocol.

    Validates that execution contexts contain all required identity fields
    with valid values before agent execution. This prevents runtime errors
    by catching incomplete or malformed contexts early.

    Required identity fields:
        - pipeline_id: str - Non-empty pipeline identifier
        - node_id: str - Must be one of: analyst, pm, ux, architect, po
        - node_name: str - Non-empty node name
        - node_order: int - Integer between 1 and 5 (inclusive)

    Attributes:
        ALLOWED_NODE_IDS: Set of valid node_id values
        MIN_NODE_ORDER: Minimum allowed node_order value (1)
        MAX_NODE_ORDER: Maximum allowed node_order value (5)

    Example:
        >>> strategy = NodeExecutionContextStrategy()
        >>> context = {
        ...     "pipeline_id": "pipe-123",
        ...     "node_id": "analyst",
        ...     "node_name": "Analyst Node",
        ...     "node_order": 1,
        ... }
        >>> result = strategy.validate(context)
        >>> result.valid
        True
    """

    ALLOWED_NODE_IDS: set[str] = {"analyst", "pm", "ux", "architect", "po"}
    MIN_NODE_ORDER: int = 1
    MAX_NODE_ORDER: int = 5

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "NodeExecutionContextStrategy"
        """
        return "NodeExecutionContextStrategy"

    @override
    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate a NodeExecutionContext dictionary.

        Validates all required identity fields are present and have valid values.
        Collects all validation errors rather than failing fast on the first issue.

        Args:
            data: The execution context dictionary to validate
            config: Optional configuration (not currently used)

        Returns:
            ValidationResult with issues for each validation failure
        """
        result = ValidationResult(valid=True)

        # Validate required identity fields
        self._validate_required_fields(data, result)

        # Validate node_id against allowed values
        self._validate_node_id(data, result)

        # Validate node_order type and range
        self._validate_node_order(data, result)

        return result

    def _validate_required_fields(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate all required identity fields are present and non-empty.

        Args:
            data: The execution context dictionary
            result: ValidationResult to collect issues into
        """
        required_fields = ["pipeline_id", "node_id", "node_name", "node_order"]

        for field_name in required_fields:
            if field_name not in data:
                result.add_error(
                    field=field_name,
                    message=f"Required field '{field_name}' is missing",
                    code="MISSING_REQUIRED_FIELD",
                )
            elif data[field_name] == "":
                result.add_error(
                    field=field_name,
                    message=f"Required field '{field_name}' is empty",
                    code="EMPTY_REQUIRED_FIELD",
                )
            elif data[field_name] is None:
                result.add_error(
                    field=field_name,
                    message=f"Required field '{field_name}' is null",
                    code="NULL_REQUIRED_FIELD",
                )

    def _validate_node_id(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate node_id is in the allowed set of values.

        Args:
            data: The execution context dictionary
            result: ValidationResult to collect issues into
        """
        # Skip validation if node_id is missing (already reported as missing)
        if "node_id" not in data or data["node_id"] is None or data["node_id"] == "":
            return

        node_id = data["node_id"]

        if node_id not in self.ALLOWED_NODE_IDS:
            allowed_list = ", ".join(sorted(self.ALLOWED_NODE_IDS))
            result.add_error(
                field="node_id",
                message=f"Invalid node_id '{node_id}'. Must be one of: {allowed_list}",
                code="INVALID_NODE_ID",
            )

    def _validate_node_order(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate node_order is an integer between MIN_NODE_ORDER and MAX_NODE_ORDER.

        Args:
            data: The execution context dictionary
            result: ValidationResult to collect issues into
        """
        # Skip validation if node_order is missing (already reported as missing)
        if "node_order" not in data or data["node_order"] is None:
            return

        node_order = data["node_order"]

        # Check type - must be int (not float, not string, not bool)
        if not isinstance(node_order, int) or isinstance(node_order, bool):
            result.add_error(
                field="node_order",
                message=f"node_order must be an integer, got {type(node_order).__name__}",
                code="INVALID_NODE_ORDER_TYPE",
            )
            return

        # Check range
        if node_order < self.MIN_NODE_ORDER:
            result.add_error(
                field="node_order",
                message=f"node_order ({node_order}) is below minimum ({self.MIN_NODE_ORDER})",
                code="NODE_ORDER_TOO_LOW",
            )
        elif node_order > self.MAX_NODE_ORDER:
            result.add_error(
                field="node_order",
                message=f"node_order ({node_order}) is above maximum ({self.MAX_NODE_ORDER})",
                code="NODE_ORDER_TOO_HIGH",
            )


class IndependentOutputValidationStrategy(ValidationStrategy):
    """Strategy for validating IndependentAgent output.

    Validates that the output conforms to the expected schema for
    IndependentAgent deliverables including:
    - deliverable with title, file_path, sha256
    - questions list with proper structure
    - optional private_reasoning

    Supports node-specific rules via config parameter:
    - min_word_count: Minimum word count for content/summary
    - required_sections: Required sections in deliverable

    Example:
        >>> strategy = IndependentOutputValidationStrategy()
        >>> output = {
        ...     "deliverable": {
        ...         "title": "Test",
        ...         "file_path": "output/test.md",
        ...         "sha256": "abc123",
        ...     },
        ...     "questions": [],
        ... }
        >>> result = strategy.validate(output)
        >>> result.valid
        True
    """

    # Valid question priorities
    VALID_PRIORITIES: set[str] = {"blocking", "clarifying", "optional"}

    # Valid action values for submit_execution_report format
    VALID_ACTIONS: set[str] = {"create_deliverable"}

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "IndependentOutputValidationStrategy"
        """
        return "IndependentOutputValidationStrategy"

    @override
    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate IndependentAgent output structure.

        Args:
            data: The IndependentAgent output dictionary
            config: Optional configuration with node-specific rules
                (e.g., min_word_count, required_sections)

        Returns:
            ValidationResult containing validation outcome
        """
        result = ValidationResult(valid=True)
        config = config or {}

        # Check for format detection: presence of 'action' field indicates submit_execution_report format
        is_submit_report_format = "action" in data

        # Validate action field if present (submit_execution_report format)
        if is_submit_report_format:
            self._validate_action(data, result)

        # Validate deliverable structure (both formats)
        self._validate_deliverable(data, result, is_submit_report_format)

        # Validate questions structure (both formats)
        self._validate_questions(data, result, is_submit_report_format)

        # Validate private_reasoning if present
        self._validate_private_reasoning(data, result)

        # Apply node-specific rules
        self._apply_node_rules(data, config, result)

        return result

    def _validate_action(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate action field for submit_execution_report format.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        action = data.get("action")

        # Check type
        if not isinstance(action, str):
            result.add_error(
                field="action",
                message=f"action: must be a string, got {type(action).__name__}",
                code="INVALID_ACTION_TYPE",
            )
            return

        # Check value against valid enum
        if action not in self.VALID_ACTIONS:
            valid_list = ", ".join(sorted(self.VALID_ACTIONS))
            result.add_error(
                field="action",
                message=f"action: invalid value '{action}'. Must be one of: {valid_list}",
                code="INVALID_ACTION_VALUE",
            )

    def _validate_deliverable(
        self, data: dict[str, Any], result: ValidationResult, _is_submit_report_format: bool = False
    ) -> None:
        """Validate deliverable field structure.

        F1 Fix: 支持 multi-document 格式验证

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
            is_submit_report_format: Whether this is submit_execution_report format
        """
        # Check deliverable exists
        if "deliverable" not in data:
            result.add_error(
                field="deliverable",
                message="deliverable: required field missing",
                code="MISSING_DELIVERABLE",
            )
            return

        deliverable = data["deliverable"]

        # Check deliverable is a dict
        if not isinstance(deliverable, dict):
            result.add_error(
                field="deliverable",
                message="deliverable: must be a dict",
                code="INVALID_DELIVERABLE_TYPE",
            )
            return

        # F1 Fix: 检测多文档格式并路由到相应的验证逻辑
        if deliverable.get("type") == "multi-document":
            self._validate_multi_document_deliverable(deliverable, result)
        else:
            self._validate_single_document_deliverable(deliverable, result)

    def _validate_multi_document_deliverable(
        self, deliverable: dict[str, Any], result: ValidationResult
    ) -> None:
        """验证多文档格式的 deliverable.
        
        F1 Fix: 多文档格式不要求顶层 file_path 和 sha256，
        而是验证 documents 数组中的每个子文档。
        
        Args:
            deliverable: The deliverable dictionary
            result: ValidationResult to collect issues into
        """
        # 验证 title (required)
        if "title" not in deliverable:
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: required field missing",
                code="MISSING_TITLE",
            )
        elif not isinstance(deliverable["title"], str):
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: must be a string",
                code="INVALID_TITLE_TYPE",
            )
        elif not deliverable["title"].strip():
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: cannot be empty",
                code="EMPTY_TITLE",
            )

        # 验证 documents 数组 (required for multi-document)
        if "documents" not in deliverable:
            result.add_error(
                field="deliverable.documents",
                message="deliverable.documents: required field missing for multi-document",
                code="MISSING_DOCUMENTS_ARRAY",
            )
            return

        documents = deliverable["documents"]
        if not isinstance(documents, list):
            result.add_error(
                field="deliverable.documents",
                message="deliverable.documents: must be a list",
                code="INVALID_DOCUMENTS_TYPE",
            )
            return

        if len(documents) == 0:
            result.add_error(
                field="deliverable.documents",
                message="deliverable.documents: cannot be empty",
                code="EMPTY_DOCUMENTS_ARRAY",
            )
            return

        # 验证每个子文档
        for idx, doc in enumerate(documents):
            self._validate_sub_document(doc, idx, result)

    def _validate_sub_document(
        self, doc: Any, index: int, result: ValidationResult
    ) -> None:
        """验证多文档中的单个子文档.
        
        Args:
            doc: 子文档字典
            index: 子文档在数组中的索引
            result: ValidationResult to collect issues into
        """
        prefix = f"deliverable.documents[{index}]"

        # 验证子文档是字典
        if not isinstance(doc, dict):
            result.add_error(
                field=prefix,
                message=f"{prefix}: must be a dict",
                code="INVALID_SUB_DOCUMENT_TYPE",
            )
            return

        # 子文档必须包含 file_path
        if "file_path" not in doc:
            result.add_error(
                field=f"{prefix}.file_path",
                message=f"{prefix}.file_path: required field missing",
                code="MISSING_FILE_PATH",
            )
        elif not isinstance(doc["file_path"], str):
            result.add_error(
                field=f"{prefix}.file_path",
                message=f"{prefix}.file_path: must be a string",
                code="INVALID_FILE_PATH_TYPE",
            )
        elif not doc["file_path"].strip():
            result.add_error(
                field=f"{prefix}.file_path",
                message=f"{prefix}.file_path: cannot be empty",
                code="EMPTY_FILE_PATH",
            )

        # 子文档必须包含 sha256
        if "sha256" not in doc:
            result.add_error(
                field=f"{prefix}.sha256",
                message=f"{prefix}.sha256: required field missing",
                code="MISSING_SHA256",
            )
        elif not isinstance(doc["sha256"], str):
            result.add_error(
                field=f"{prefix}.sha256",
                message=f"{prefix}.sha256: must be a string",
                code="INVALID_SHA256_TYPE",
            )
        elif not doc["sha256"].strip():
            result.add_error(
                field=f"{prefix}.sha256",
                message=f"{prefix}.sha256: cannot be empty",
                code="EMPTY_SHA256",
            )

        # 验证 title (optional but must be string if present)
        if "title" in doc and not isinstance(doc["title"], str):
            result.add_error(
                field=f"{prefix}.title",
                message=f"{prefix}.title: must be a string",
                code="INVALID_TITLE_TYPE",
            )

        # 验证 content_summary (optional but must be string if present)
        if "content_summary" in doc and not isinstance(doc["content_summary"], str):
            result.add_error(
                field=f"{prefix}.content_summary",
                message=f"{prefix}.content_summary: must be a string",
                code="INVALID_CONTENT_SUMMARY_TYPE",
            )

        # 验证 word_count (optional but must be int if present)
        if "word_count" in doc and not isinstance(doc["word_count"], int):
            result.add_error(
                field=f"{prefix}.word_count",
                message=f"{prefix}.word_count: must be an integer",
                code="INVALID_WORD_COUNT_TYPE",
            )

    def _validate_single_document_deliverable(
        self, deliverable: dict[str, Any], result: ValidationResult
    ) -> None:
        """验证单文档格式的 deliverable (原有的验证逻辑).
        
        Args:
            deliverable: The deliverable dictionary
            result: ValidationResult to collect issues into
        """
        # Validate title (required, must be string, non-empty)
        if "title" not in deliverable:
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: required field missing",
                code="MISSING_TITLE",
            )
        elif not isinstance(deliverable["title"], str):
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: must be a string",
                code="INVALID_TITLE_TYPE",
            )
        elif not deliverable["title"].strip():
            result.add_error(
                field="deliverable.title",
                message="deliverable.title: cannot be empty",
                code="EMPTY_TITLE",
            )

        # Validate file_path (required, must be string, non-empty)
        if "file_path" not in deliverable:
            result.add_error(
                field="deliverable.file_path",
                message="deliverable.file_path: required field missing",
                code="MISSING_FILE_PATH",
            )
        elif not isinstance(deliverable["file_path"], str):
            result.add_error(
                field="deliverable.file_path",
                message="deliverable.file_path: must be a string",
                code="INVALID_FILE_PATH_TYPE",
            )
        elif not deliverable["file_path"].strip():
            result.add_error(
                field="deliverable.file_path",
                message="deliverable.file_path: cannot be empty",
                code="EMPTY_FILE_PATH",
            )

        # Validate sha256 (required, must be string, non-empty)
        if "sha256" not in deliverable:
            result.add_error(
                field="deliverable.sha256",
                message="deliverable.sha256: required field missing",
                code="MISSING_SHA256",
            )
        elif not isinstance(deliverable["sha256"], str):
            result.add_error(
                field="deliverable.sha256",
                message="deliverable.sha256: must be a string",
                code="INVALID_SHA256_TYPE",
            )
        elif not deliverable["sha256"].strip():
            result.add_error(
                field="deliverable.sha256",
                message="deliverable.sha256: cannot be empty",
                code="EMPTY_SHA256",
            )

        # Validate summary if present (must be string)
        if "summary" in deliverable and not isinstance(deliverable["summary"], str):
            result.add_error(
                field="deliverable.summary",
                message="deliverable.summary: must be a string",
                code="INVALID_SUMMARY_TYPE",
            )

        # Validate content if present (must be string)
        if "content" in deliverable and not isinstance(deliverable["content"], str):
            result.add_error(
                field="deliverable.content",
                message="deliverable.content: must be a string",
                code="INVALID_CONTENT_TYPE",
            )

        # Validate metadata if present (must be dict)
        if "metadata" in deliverable and not isinstance(deliverable["metadata"], dict):
            result.add_error(
                field="deliverable.metadata",
                message="deliverable.metadata: must be a dict",
                code="INVALID_METADATA_TYPE",
            )

        # Validate content_summary if present (must be string)
        if "content_summary" in deliverable and not isinstance(deliverable["content_summary"], str):
            result.add_error(
                field="deliverable.content_summary",
                message="deliverable.content_summary: must be a string",
                code="INVALID_CONTENT_SUMMARY_TYPE",
            )

    def _validate_questions(
        self, data: dict[str, Any], result: ValidationResult, is_submit_report_format: bool = False
    ) -> None:
        """Validate questions field structure.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
            is_submit_report_format: Whether this is submit_execution_report format
        """
        # Check questions exists
        # For submit_execution_report format, questions is optional
        # For old format, questions is required
        if "questions" not in data:
            if is_submit_report_format:
                # Questions is optional in submit_execution_report format
                return
            result.add_error(
                field="questions",
                message="questions: required field missing",
                code="MISSING_QUESTIONS",
            )
            return

        questions = data["questions"]

        # Check questions is a list
        if not isinstance(questions, list):
            result.add_error(
                field="questions",
                message="questions: must be a list",
                code="INVALID_QUESTIONS_TYPE",
            )
            return

        # Validate each question
        for i, question_dict in enumerate(questions):
            if not isinstance(question_dict, dict):
                result.add_error(
                    field=f"questions[{i}]",
                    message=f"questions[{i}]: must be a dict",
                    code="INVALID_QUESTION_TYPE",
                )
                continue

            # Validate priority (required)
            if "priority" not in question_dict:
                result.add_error(
                    field=f"questions[{i}].priority",
                    message=f"questions[{i}].priority: required field missing",
                    code="MISSING_QUESTION_PRIORITY",
                )
            elif question_dict["priority"] not in self.VALID_PRIORITIES:
                valid_list = ", ".join(sorted(self.VALID_PRIORITIES))
                result.add_error(
                    field=f"questions[{i}].priority",
                    message=f"questions[{i}].priority: invalid value '{question_dict['priority']}'. Must be one of: {valid_list}",
                    code="INVALID_QUESTION_PRIORITY",
                )

            # Validate question text (required, must be string)
            if "question" not in question_dict:
                result.add_error(
                    field=f"questions[{i}].question",
                    message=f"questions[{i}].question: required field missing",
                    code="MISSING_QUESTION_TEXT",
                )
            elif not isinstance(question_dict["question"], str):
                result.add_error(
                    field=f"questions[{i}].question",
                    message=f"questions[{i}].question: must be a string",
                    code="INVALID_QUESTION_TEXT_TYPE",
                )

            # Validate context (required, must be string)
            if "context" not in question_dict:
                result.add_error(
                    field=f"questions[{i}].context",
                    message=f"questions[{i}].context: required field missing",
                    code="MISSING_QUESTION_CONTEXT",
                )
            elif not isinstance(question_dict["context"], str):
                result.add_error(
                    field=f"questions[{i}].context",
                    message=f"questions[{i}].context: must be a string",
                    code="INVALID_QUESTION_CONTEXT_TYPE",
                )

    def _validate_private_reasoning(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate private_reasoning field if present.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "private_reasoning" in data and data["private_reasoning"] is not None:
            if not isinstance(data["private_reasoning"], str):
                result.add_error(
                    field="private_reasoning",
                    message="private_reasoning: must be a string",
                    code="INVALID_PRIVATE_REASONING_TYPE",
                )

    def _apply_node_rules(
        self,
        data: dict[str, Any],
        config: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Apply node-specific validation rules.

        Args:
            data: The output data dictionary
            config: Node-specific configuration rules
            result: ValidationResult to collect warnings into
        """
        deliverable = data.get("deliverable", {})

        # Check min_word_count rule
        min_word_count = config.get("min_word_count")
        if min_word_count is not None:
            content = deliverable.get("summary") or deliverable.get("content", "")
            if isinstance(content, str):
                word_count = len(content.split())
                if word_count < min_word_count:
                    result.add_warning(
                        field="deliverable.summary",
                        message=f"Word count ({word_count}) is below minimum ({min_word_count})",
                        code="WORD_COUNT_LOW",
                    )


class EvaluatorOutputValidationStrategy(ValidationStrategy):
    """Strategy for validating EvaluatorAgent output.

    Validates that the output conforms to the expected schema for
    EvaluatorAgent evaluation results including:
    - criterion_scores: Dict[str, float] with values 0.0-1.0
    - alignment_score: float 0.0-1.0
    - verdict: "APPROVED" | "NEEDS_REVISION" | "BLOCKED"
    - issues_found: List[str]
    - suggestions: List[str]

    Supports node-specific rules via config parameter:
    - min_confidence_threshold: Minimum alignment score threshold

    Example:
        >>> strategy = EvaluatorOutputValidationStrategy()
        >>> output = {
        ...     "criterion_scores": {"quality": 0.9},
        ...     "alignment_score": 0.85,
        ...     "verdict": "APPROVED",
        ...     "issues_found": [],
        ...     "suggestions": [],
        ... }
        >>> result = strategy.validate(output)
        >>> result.valid
        True
    """

    # Valid verdict values
    VALID_VERDICTS: set[str] = {"APPROVED", "NEEDS_REVISION", "BLOCKED"}

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "EvaluatorOutputValidationStrategy"
        """
        return "EvaluatorOutputValidationStrategy"

    @override
    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate EvaluatorAgent output structure.

        Args:
            data: The EvaluatorAgent output dictionary
            config: Optional configuration with node-specific rules
                (e.g., min_confidence_threshold)

        Returns:
            ValidationResult containing validation outcome
        """
        result = ValidationResult(valid=True)
        config = config or {}

        # Validate criterion_scores
        self._validate_criterion_scores(data, result)

        # Validate alignment_score
        self._validate_alignment_score(data, result)

        # Validate verdict
        self._validate_verdict(data, result)

        # Validate issues_found
        self._validate_issues_found(data, result)

        # Validate suggestions
        self._validate_suggestions(data, result)

        # Apply node-specific rules
        self._apply_node_rules(data, config, result)

        return result

    def _validate_criterion_scores(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate criterion_scores field.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "criterion_scores" not in data:
            result.add_error(
                field="criterion_scores",
                message="criterion_scores: required field missing",
                code="MISSING_CRITERION_SCORES",
            )
            return

        criterion_scores = data["criterion_scores"]

        if not isinstance(criterion_scores, dict):
            result.add_error(
                field="criterion_scores",
                message="criterion_scores: must be a dict",
                code="INVALID_CRITERION_SCORES_TYPE",
            )
            return

        # Validate each score
        for key, value in criterion_scores.items():
            if not isinstance(value, int | float):
                result.add_error(
                    field=f"criterion_scores['{key}']",
                    message=f"criterion_scores['{key}']: must be a number, got {type(value).__name__}",
                    code="INVALID_CRITERION_SCORE_TYPE",
                )
            elif not (0.0 <= value <= 1.0):
                result.add_error(
                    field=f"criterion_scores['{key}']",
                    message=f"criterion_scores['{key}']: must be between 0.0 and 1.0, got {value}",
                    code="CRITERION_SCORE_OUT_OF_RANGE",
                )

    def _validate_alignment_score(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate alignment_score field.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "alignment_score" not in data:
            result.add_error(
                field="alignment_score",
                message="alignment_score: required field missing",
                code="MISSING_ALIGNMENT_SCORE",
            )
            return

        alignment_score = data["alignment_score"]

        if not isinstance(alignment_score, int | float):
            result.add_error(
                field="alignment_score",
                message="alignment_score: must be a number",
                code="INVALID_ALIGNMENT_SCORE_TYPE",
            )
            return

        if not (0.0 <= alignment_score <= 1.0):
            result.add_error(
                field="alignment_score",
                message=f"alignment_score: must be between 0.0 and 1.0, got {alignment_score}",
                code="ALIGNMENT_SCORE_OUT_OF_RANGE",
            )

    def _validate_verdict(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate verdict field.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "verdict" not in data:
            result.add_error(
                field="verdict",
                message="verdict: required field missing",
                code="MISSING_VERDICT",
            )
            return

        verdict = data["verdict"]

        if verdict not in self.VALID_VERDICTS:
            valid_list = ", ".join(sorted(self.VALID_VERDICTS))
            result.add_error(
                field="verdict",
                message=f"verdict: invalid value '{verdict}'. Must be one of: {valid_list}",
                code="INVALID_VERDICT",
            )

    def _validate_issues_found(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate issues_found field.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "issues_found" not in data:
            result.add_error(
                field="issues_found",
                message="issues_found: required field missing",
                code="MISSING_ISSUES_FOUND",
            )
            return

        issues_found = data["issues_found"]

        if not isinstance(issues_found, list):
            result.add_error(
                field="issues_found",
                message="issues_found: must be a list",
                code="INVALID_ISSUES_FOUND_TYPE",
            )
            return

        # Validate each issue is a string
        for i, issue in enumerate(issues_found):
            if not isinstance(issue, str):
                result.add_error(
                    field=f"issues_found[{i}]",
                    message=f"issues_found[{i}]: must be a string",
                    code="INVALID_ISSUE_TYPE",
                )

    def _validate_suggestions(self, data: dict[str, Any], result: ValidationResult) -> None:
        """Validate suggestions field.

        Args:
            data: The output data dictionary
            result: ValidationResult to collect issues into
        """
        if "suggestions" not in data:
            result.add_error(
                field="suggestions",
                message="suggestions: required field missing",
                code="MISSING_SUGGESTIONS",
            )
            return

        suggestions = data["suggestions"]

        if not isinstance(suggestions, list):
            result.add_error(
                field="suggestions",
                message="suggestions: must be a list",
                code="INVALID_SUGGESTIONS_TYPE",
            )
            return

        # Validate each suggestion is a string
        for i, suggestion in enumerate(suggestions):
            if not isinstance(suggestion, str):
                result.add_error(
                    field=f"suggestions[{i}]",
                    message=f"suggestions[{i}]: must be a string",
                    code="INVALID_SUGGESTION_TYPE",
                )

    def _apply_node_rules(
        self,
        data: dict[str, Any],
        config: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Apply node-specific validation rules.

        Args:
            data: The output data dictionary
            config: Node-specific configuration rules
            result: ValidationResult to collect warnings into
        """
        # Check min_confidence_threshold rule
        min_confidence = config.get("min_confidence_threshold")
        if min_confidence is not None:
            alignment_score = data.get("alignment_score")
            if isinstance(alignment_score, int | float):
                if alignment_score < min_confidence:
                    result.add_warning(
                        field="alignment_score",
                        message=f"Alignment score ({alignment_score}) is below threshold ({min_confidence})",
                        code="LOW_CONFIDENCE",
                    )


class MaxDeliverablesValidationStrategy(ValidationStrategy):
    """Strategy for validating max_deliverables constraint.

        Validates that the number of documents in a deliverable does not exceed
    the node's configured max_deliverables limit. This supports both single-
        document nodes (analyst/pm/ux) and multi-document nodes (architect/po).

        Document count detection:
        - Single-document format: deliverable without document_total field (count=1)
        - Multi-document format: deliverable with document_total field (count=document_total)

        Example:
            >>> strategy = MaxDeliverablesValidationStrategy()
            >>> output = {
            ...     "deliverable": {
            ...         "title": "Doc",
            ...         "file_path": "output/doc.md",
            ...         "sha256": "abc123",
            ...         "document_index": 2,
            ...         "document_total": 2,
            ...     },
            ...     "questions": [],
            ... }
            >>> result = strategy.validate(output, {"max_deliverables": 1})
            >>> result.valid
            False
    """

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "MaxDeliverablesValidationStrategy"
        """
        return "MaxDeliverablesValidationStrategy"

    @override
    def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate deliverable count against max_deliverables limit.

        Args:
            data: The IndependentAgent output dictionary
            config: Optional configuration with max_deliverables rule
                (default: 1 for backward compatibility)

        Returns:
            ValidationResult containing validation outcome
        """
        result = ValidationResult(valid=True)
        config = config or {}

        # Get max_deliverables (default to 1 for backward compatibility)
        max_deliverables = config.get("max_deliverables", 1)
        node_id = config.get("node_id", "unknown")

        # Check if deliverable exists
        if "deliverable" not in data:
            result.add_error(
                field="deliverable",
                message="deliverable: required field missing",
                code="MISSING_DELIVERABLE",
            )
            return result

        deliverable = data["deliverable"]
        if not isinstance(deliverable, dict):
            result.add_error(
                field="deliverable",
                message="deliverable: must be a dict",
                code="INVALID_DELIVERABLE_TYPE",
            )
            return result

        # Detect document count
        document_count = self._detect_document_count(deliverable)

        # Validate against max_deliverables
        if document_count > max_deliverables:
            result.add_error(
                field="deliverable",
                message=(
                    f"Document count constraint violated for node '{node_id}': "
                    f"attempted {document_count} documents, but max_deliverables is {max_deliverables}"
                ),
                code="MAX_DELIVERABLES_EXCEEDED",
            )

        return result

    def _detect_document_count(self, deliverable: dict[str, Any]) -> int:
        """Detect the number of documents from deliverable metadata.

        F1 Fix: 支持多文档格式，优先使用 documents 数组长度
        
        For multi-document format:
        - If documents array exists, use its length
        - Otherwise fallback to document_total field
        For single-document format, returns 1.

        Args:
            deliverable: The deliverable dictionary

        Returns:
            Number of documents (>= 1)
        """
        # F1 Fix: 多文档格式优先使用 documents 数组长度
        if deliverable.get("type") == "multi-document":
            documents = deliverable.get("documents")
            if isinstance(documents, list):
                return len(documents)
            # Fallback to document_total if documents array is not available
            document_total = deliverable.get("document_total")
            if document_total is not None and isinstance(document_total, int):
                return document_total
            return 0  # Invalid multi-document without documents array

        # Check for document_total (single document format with explicit count)
        document_total = deliverable.get("document_total")
        if document_total is not None and isinstance(document_total, int):
            return document_total

        # Single document format (no document_total means count=1)
        return 1


class LLMContextValidationStrategy(ValidationStrategy):
    """Strategy for LLM-based semantic context validation.

    This strategy uses an LLM to validate that the context has sufficient
    information and clear objectives before starting pipeline execution.
    Implements a fail-open approach: if the LLM call fails or returns
    unparseable data, validation passes by default.

    The prompt template asks the LLM to check:
    1. If there's a clear objective (what to create)
    2. If scope is defined (requirements stated)
    3. If there's sufficient detail to start

    Attributes:
        CONTEXT_VALIDATION_PROMPT: The prompt template sent to the LLM

    Example:
        >>> strategy = LLMContextValidationStrategy()
        >>> mock_session = MagicMock()
        >>> result = await strategy.validate(
        ...     {"task": "Create PRD"},
        ...     {"session_manager": mock_session}
        ... )
    """

    # Context validation prompt template
    CONTEXT_VALIDATION_PROMPT: str = """You are a technical context validator. Analyze the context and output ONLY a JSON object.

**Context to validate:**
{subject_context}

**Validation rules:**
1. Check if there's a clear objective (what to create)
2. Check if scope is defined (requirements stated)
3. Check if there's sufficient detail to start

**Output format (respond with ONLY this JSON, no markdown blocks, no other text):**

{{
  "valid": true,
  "reason": "Brief validation reason",
  "missing_info": []
}}

**Important:**
- Do NOT call any tools
- Do NOT use markdown code blocks
- Output ONLY the JSON object
- Use lowercase true/false for booleans
"""

    @property
    @override
    def strategy_name(self) -> str:
        """Return the name of this strategy.

        Returns:
            String identifier: "LLMContextValidationStrategy"
        """
        return "LLMContextValidationStrategy"

    @override
    async def validate(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Execute LLM-based validation on the provided context.

        Uses the configured session_manager to call an LLM for semantic
        validation of the context. Handles various failure modes with
        a fail-open approach.

        Args:
            data: The context dictionary to validate
            config: Must contain "session_manager" for LLM calls

        Returns:
            ValidationResult containing validation outcome

        Raises:
            RuntimeError: If session_manager is not provided in config
        """
        if config is None or config.get("session_manager") is None:
            raise RuntimeError("session_manager is required for LLM validation")

        session_manager = config["session_manager"]

        # Format the prompt with subject context
        context_str = json.dumps(data, indent=2)
        prompt = self.CONTEXT_VALIDATION_PROMPT.format(subject_context=context_str)

        try:
            # Call LLM with agent mode using session_manager
            messages = await session_manager.single_prompt(
                prompt=prompt,
                mode="agent",
                yolo=True,
            )

            # Parse the response
            return self._parse_validation_response(messages)

        except Exception as e:
            # Fail open - allow pipeline to proceed if LLM is unavailable
            return ValidationResult(
                valid=True,
                metadata={
                    "reason": f"LLM validation failed: {e}, defaulting to valid",
                    "error": str(e),
                },
            )

    def _parse_validation_response(self, messages: list[Any]) -> ValidationResult:
        """Parse LLM response and create ValidationResult.

        Handles various response formats including markdown code blocks.
        Falls open if parsing fails.

        Args:
            messages: List of message dictionaries from LLM

        Returns:
            ValidationResult based on parsed response
        """
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        try:
            # Extract content from messages using unified utility
            content = extract_text_from_messages(messages)

            if not content:
                raise ValueError("Empty response from LLM")

            # Clean up markdown code blocks
            content = self._extract_json_from_markdown(content.strip())

            # Parse JSON
            result_data = json.loads(content)

            # Check if validation passed
            is_valid = result_data.get("valid", False)
            reason = result_data.get("reason", "No reason provided")
            missing_info = result_data.get("missing_info", [])

            if is_valid:
                return ValidationResult(
                    valid=True,
                    metadata={"reason": reason, "missing_info": missing_info},
                )
            else:
                # Create validation result with error issue
                result = ValidationResult(valid=False)
                missing_str = ", ".join(missing_info) if missing_info else "None"
                result.add_error(
                    field="context",
                    message=f"{reason}. Missing info: [{missing_str}]",
                    code="CONTEXT_VALIDATION_FAILED",
                )
                result.metadata = {"reason": reason, "missing_info": missing_info}
                return result

        except (json.JSONDecodeError, ValueError) as e:
            # Fail open if we can't parse the response
            return ValidationResult(
                valid=True,
                metadata={
                    "reason": f"Could not parse validation response, defaulting to valid: {e}",
                    "error": str(e),
                },
            )

    def _extract_json_from_markdown(self, content: str) -> str:
        """Extract JSON from markdown code blocks.

        Args:
            content: The content string that may contain markdown

        Returns:
            Clean JSON string
        """
        # Handle potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()


class ContextValidator:
    """Main facade for context validation operations.

    Provides a unified interface for all validation needs in the system:
    - NodeExecutionContext validation
    - Data isolation (private field) validation
    - IndependentAgent output validation
    - EvaluatorAgent output validation
    - LLM-based semantic context validation

    Uses Strategy Pattern internally for extensible validation logic.

    This class implements the Singleton pattern via get_instance() for
    global access to a shared validator instance.

    Attributes:
        _registry: ValidationRuleRegistry for node-specific rules
        _session_manager: Optional session manager for LLM validation
        _node_execution_strategy: Strategy for context validation (placeholder)
        _isolation_strategy: Strategy for isolation validation (placeholder)
        _independent_output_strategy: Strategy for IndependentAgent output (placeholder)
        _evaluator_output_strategy: Strategy for EvaluatorAgent output (placeholder)
        _llm_validation_strategy: Strategy for LLM validation (placeholder)
        _instance: Class-level singleton instance
        _lock: Class-level lock for thread-safe singleton creation

    Example:
        >>> validator = ContextValidator.get_instance()
        >>> validator.load_node_rules("node_1", {"rules": []})
        >>> result = validator.validate_execution_context(context, "node_1")
        >>> print(result.valid)
    """

    # Singleton instance storage
    _instance: ContextValidator | None = None
    _lock = threading.Lock()

    def __init__(self, session_manager: Any | None = None) -> None:
        """Initialize ContextValidator.

        Args:
            session_manager: Optional session manager for LLM validation.
                Required for validate_context_with_llm method.
        """
        self._registry = ValidationRuleRegistry()
        self._session_manager = session_manager

        # Strategy initialization
        self._node_execution_strategy: ValidationStrategy = NodeExecutionContextStrategy()
        self._isolation_strategy: ValidationStrategy = PrivateFieldIsolationStrategy()
        self._independent_output_strategy: ValidationStrategy = (
            IndependentOutputValidationStrategy()
        )
        self._evaluator_output_strategy: ValidationStrategy = EvaluatorOutputValidationStrategy()
        # Initialize LLM strategy if session_manager is provided
        self._llm_validation_strategy: LLMContextValidationStrategy | None = (
            LLMContextValidationStrategy() if session_manager else None
        )

    @classmethod
    def get_instance(cls, session_manager: Any | None = None) -> ContextValidator:
        """Get the singleton instance of ContextValidator.

        Thread-safe singleton creation using double-checked locking pattern.
        Once created, the instance is reused for all subsequent calls.

        Args:
            session_manager: Optional session manager for LLM validation.
                Only used when creating the initial instance.

        Returns:
            The singleton ContextValidator instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = cls(session_manager=session_manager)
                elif session_manager is not None:
                    # Update session_manager if provided and instance already exists
                    cls._instance._session_manager = session_manager
                    if cls._instance._llm_validation_strategy is None:
                        cls._instance._llm_validation_strategy = LLMContextValidationStrategy()
        elif session_manager is not None:
            # Update session_manager if provided and instance already exists
            with cls._lock:
                cls._instance._session_manager = session_manager
                if cls._instance._llm_validation_strategy is None:
                    cls._instance._llm_validation_strategy = LLMContextValidationStrategy()
        return cls._instance

    def load_node_rules(self, node_id: str, config: dict[str, Any]) -> None:
        """Load validation rules for a specific node.

        Delegates to the internal ValidationRuleRegistry.

        Args:
            node_id: Unique identifier for the node
            config: Validation configuration dictionary
        """
        self._registry.register(node_id, config)

    def validate_execution_context(
        self,
        context: dict[str, Any],
    ) -> ValidationResult:
        """Validate a NodeExecutionContext protocol.

        Uses NodeExecutionContextStrategy to validate that the context
        contains all required identity fields with valid values.

        Args:
            context: The execution context dictionary to validate

        Returns:
            ValidationResult containing validation outcome
        """
        return cast(ValidationResult, self._node_execution_strategy.validate(context))

    def validate_isolation(self, data: dict[str, Any]) -> ValidationResult:
        """Validate data does not contain private fields.

        Checks for private field isolation to prevent data leakage
        between IndependentAgent and EvaluatorAgent.

        Args:
            data: The data dictionary to validate

        Returns:
            ValidationResult containing validation outcome
        """
        return cast(ValidationResult, self._isolation_strategy.validate(data))

    def validate_max_deliverables(
        self,
        output: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """Validate deliverable count against node's max_deliverables limit.

        Validates that the number of documents in the deliverable does not
        exceed the node's configured max_deliverables limit. Supports both
        single-document nodes (analyst/pm/ux) and multi-document nodes
        (architect/po).

        Args:
            output: The IndependentAgent output dictionary containing deliverable
            node_id: Optional node ID for looking up node-specific rules

        Returns:
            ValidationResult containing validation outcome
        """
        # Get node-specific rules
        config = self._registry.get_rules(node_id) if node_id else {}
        config["node_id"] = node_id

        # Create strategy and validate
        strategy = MaxDeliverablesValidationStrategy()
        result = cast(ValidationResult, strategy.validate(output, config))

        # Add metadata
        result.metadata["node_id"] = node_id
        result.metadata["validation_type"] = "max_deliverables"

        return result

    def validate_independent_output(
        self,
        output: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """Validate IndependentAgent output structure.

        Validates that the output conforms to the expected schema
        for IndependentAgent deliverables. Delegates to
        IndependentOutputValidationStrategy.

        Args:
            output: The IndependentAgent output dictionary
            node_id: Optional node ID for node-specific rules

        Returns:
            ValidationResult containing validation outcome
        """
        # Get node-specific rules if node_id provided
        config = self._registry.get_rules(node_id) if node_id else {**DEFAULT_VALIDATION_RULES}

        # Delegate to strategy
        result = cast(ValidationResult, self._independent_output_strategy.validate(output, config))

        # Add metadata
        result.metadata["node_id"] = node_id
        result.metadata["validation_type"] = "independent_output"

        return result

    def validate_evaluator_output(
        self,
        output: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """Validate EvaluatorAgent output structure.

        Validates that the output conforms to the expected schema
        for EvaluatorAgent evaluation results. Delegates to
        EvaluatorOutputValidationStrategy.

        Args:
            output: The EvaluatorAgent output dictionary
            node_id: Optional node ID for node-specific rules

        Returns:
            ValidationResult containing validation outcome
        """
        # Get node-specific rules if node_id provided
        config = self._registry.get_rules(node_id) if node_id else {**DEFAULT_VALIDATION_RULES}

        # Delegate to strategy
        result = cast(ValidationResult, self._evaluator_output_strategy.validate(output, config))

        # Add metadata
        result.metadata["node_id"] = node_id
        result.metadata["validation_type"] = "evaluator_output"

        return result

    async def validate_context_with_llm(
        self,
        subject_context: dict[str, Any],
        node_id: str = "",
    ) -> ValidationResult:
        """Perform LLM-based semantic validation of context.

        Uses LLM to validate that context has sufficient information
        and clear objectives. Delegates to LLMContextValidationStrategy.

        Args:
            subject_context: The context dictionary to validate
            node_id: Optional node ID for node-specific rules

        Returns:
            ValidationResult containing validation outcome

        Raises:
            RuntimeError: If session_manager was not provided
            ContextValidationError: If validation fails (valid=False)
        """
        if self._session_manager is None or self._llm_validation_strategy is None:
            raise RuntimeError("session_manager is required for LLM validation")

        # Delegate to strategy
        config = {"session_manager": self._session_manager}
        result = await self._llm_validation_strategy.validate(subject_context, config)

        # Add metadata
        result.metadata["node_id"] = node_id
        result.metadata["validation_type"] = "llm_context"

        # Raise exception if validation failed
        if not result.valid:
            from autoBMAD.docuswarm.exceptions import ContextValidationError

            error_msg = result.issues[0].message if result.issues else "Context validation failed"
            raise ContextValidationError(error_msg)

        return result


__all__ = [
    "ContextValidator",
    "DEFAULT_VALIDATION_RULES",
    "EvaluatorOutputValidationStrategy",
    "IndependentOutputValidationStrategy",
    "LLMContextValidationStrategy",
    "MaxDeliverablesValidationStrategy",
    "NodeExecutionContextStrategy",
    "PrivateFieldIsolationStrategy",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRuleRegistry",
    "ValidationStrategy",
]
