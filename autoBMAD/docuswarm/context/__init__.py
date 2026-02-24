"""Context management module."""

from autoBMAD.docuswarm.context.audit import (
    EVENT_TYPE_CONTEXT_BUILD,
    EVENT_TYPE_FILTER,
    EVENT_TYPE_VIOLATION,
    AuditEvent,
    IsolationAuditLogger,
)
from autoBMAD.docuswarm.context.filter import ContextFilter
from autoBMAD.docuswarm.context.isolation import (
    PRIVATE_FIELDS,
    ContextIsolationError,
    ContextManager,
)
from autoBMAD.docuswarm.context.memory import MemoryManager, MemoryScope

__all__ = [
    "AuditEvent",
    "EVENT_TYPE_CONTEXT_BUILD",
    "EVENT_TYPE_FILTER",
    "EVENT_TYPE_VIOLATION",
    "IsolationAuditLogger",
    "ContextFilter",
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
    "MemoryManager",
    "MemoryScope",
]
