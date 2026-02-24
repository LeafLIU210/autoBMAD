"""Context validation module for node execution."""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any


class ContextValidator:
    """Validates input context files before node execution.

    This validator ensures that context files contain the required fields
    and are valid JSON before node execution begins.

    Required fields:
        - project_description: str
        - requirements: list or str

    Optional fields (validated but not required):
        - goals: list
        - constraints: list
        - assumptions: list
    """

    REQUIRED_FIELDS = ["project_description", "requirements"]
    OPTIONAL_FIELDS = ["goals", "constraints", "assumptions"]
    HASH_LENGTH = 16

    def __init__(self) -> None:
        """Initialize the ContextValidator."""
        pass

    async def validate_context(self, context_file: Path) -> dict[str, Any]:
        """Validate a context file.

        Args:
            context_file: Path to the context JSON file.

        Returns:
            The parsed context dictionary.

        Raises:
            FileNotFoundError: If the context file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            ValueError: If required fields are missing.
        """
        # Check file exists
        if not context_file.exists():
            raise FileNotFoundError(f"Context file not found: {context_file}")

        # Read and parse JSON (async for consistency with other async operations)
        content = await self._read_file(context_file)

        try:
            context = json.loads(content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in context file: {e.msg}", e.doc, e.pos
            ) from e

        # Validate required fields
        self._validate_required_fields(context)

        return context

    async def _read_file(self, file_path: Path) -> str:
        """Read file contents asynchronously.

        Args:
            file_path: Path to the file to read.

        Returns:
            The file contents as a string.
        """
        # Use asyncio.to_thread for modern async file I/O (Python 3.9+)
        return await asyncio.to_thread(file_path.read_text, "utf-8")

    def _validate_required_fields(self, context: dict[str, Any]) -> None:
        """Validate that all required fields are present.

        Args:
            context: The parsed context dictionary.

        Raises:
            ValueError: If any required field is missing.
        """
        missing_fields: list[str] = []

        for field in self.REQUIRED_FIELDS:
            if field not in context:
                missing_fields.append(field)

        if missing_fields:
            field_list = ", ".join(missing_fields)
            raise ValueError(f"Missing required fields in context: {field_list}")

    async def generate_context_hash(self, context_file: Path) -> str:
        """Generate a SHA256 hash for context chaining.

        The hash is generated from the raw file bytes to ensure
        deterministic results (same file = same hash).

        Args:
            context_file: Path to the context file.

        Returns:
            A 16-character hexadecimal hash string.
        """
        if not context_file.exists():
            raise FileNotFoundError(f"Context file not found: {context_file}")

        # Read raw bytes for deterministic hashing using asyncio.to_thread
        file_bytes = await asyncio.to_thread(context_file.read_bytes)

        # Generate SHA256 hash
        hash_obj = hashlib.sha256(file_bytes)
        full_hash = hash_obj.hexdigest()

        # Return first 16 characters
        return full_hash[: self.HASH_LENGTH]
