"""SummaryAgent implementation - Story 36.1, 36.2.

This module provides the SummaryAgent class which:
- Pre-processes referenced documents to generate structured LLM summaries
- Caches document context for reuse by all 5 pipeline nodes
- Implements concurrent processing with semaphore (max 3 concurrent LLM calls)
- Processes critical files (containing "requirement") sequentially before normal files
- Provides graceful error handling and retry logic
- Uses YAML configuration for all settings (Story 36.2)

Example:
    >>> from autoBMAD.docuswarm.agents.summary import SummaryAgent, create_summary_agent
    >>> from autoBMAD.docuswarm.llm.session_manager import SessionManager
    >>> from autoBMAD.docuswarm.config import Config
    >>>
    >>> config = Config()
    >>> session_manager = SessionManager()
    >>> agent = create_summary_agent(config=config, session_manager=session_manager)
    >>>
    >>> original_context = {"content": "Please read `requirements.md` for context."}
    >>> summaries = await agent.summarize_context(original_context)
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import structlog

from autoBMAD.docuswarm.agents.base import BaseAgent
from autoBMAD.docuswarm.config.summary_agent_config import (
    SummaryAgentConfig,
    SummaryAgentConfigLoader,
)
from autoBMAD.docuswarm.llm.session_manager import SessionManager

if TYPE_CHECKING:
    # Import Config from the dynamically loaded module for type checking
    from _config_module import Config as AgentConfig

logger = structlog.get_logger(__name__)

# Constants for file processing
ALLOWED_EXTENSIONS = frozenset([".md", ".txt", ".yaml", ".yml", ".json"])
MAX_FILE_SIZE_BYTES = 500 * 1024  # 500KB
MAX_CONCURRENT_LLM_CALLS = 3
LLM_TIMEOUT_SECONDS = 30
MAX_RETRIES = 2
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1000

# JSON Schema for LLM output
SUMMARY_SCHEMA = {
    "summary": "2-5 sentence core summary of the document",
    "key_points": ["3-7 key points extracted from the document"],
    "structure": {
        "sections": ["list of main sections"],
        "concepts": ["key concepts mentioned"],
    },
}


@dataclass
class DocumentSummary:
    """Dataclass representing a document summary.

    Attributes:
        filename: The name of the file.
        path: The relative path to the file.
        size_bytes: The size of the file in bytes.
        summary: A concise summary of the document content.
        key_points: Key points extracted from the document.
        structure: Document structure containing sections and concepts.
        truncated: Whether the content was truncated.
        llm_tokens_used: Number of LLM tokens used for generation.
    """

    filename: str
    path: str
    size_bytes: int
    summary: str
    key_points: list[str] = field(default_factory=list)
    structure: dict[str, Any] = field(default_factory=dict)
    truncated: bool = False
    llm_tokens_used: int = 0

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.filename:
            raise ValueError("filename cannot be empty")
        if not self.path:
            raise ValueError("path cannot be empty")
        if self.size_bytes < 0:
            raise ValueError("size_bytes cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialize DocumentSummary to dictionary.

        Returns:
            Dictionary representation of the document summary.
        """
        return {
            "filename": self.filename,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "summary": self.summary,
            "key_points": self.key_points,
            "structure": self.structure,
            "truncated": self.truncated,
            "llm_tokens_used": self.llm_tokens_used,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentSummary:
        """Create DocumentSummary from dictionary.

        Args:
            data: Dictionary containing document summary data.

        Returns:
            DocumentSummary instance.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["filename", "path", "size_bytes", "summary"]
        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        return cls(
            filename=data["filename"],
            path=data["path"],
            size_bytes=data["size_bytes"],
            summary=data["summary"],
            key_points=data.get("key_points", []),
            structure=data.get("structure", {}),
            truncated=data.get("truncated", False),
            llm_tokens_used=data.get("llm_tokens_used", 0),
        )


class SummaryAgentError(Exception):
    """Base exception for SummaryAgent errors."""

    pass


class FileDiscoveryError(SummaryAgentError):
    """Raised when file discovery fails."""

    pass


class LLMSummaryError(SummaryAgentError):
    """Raised when LLM summary generation fails."""

    pass


class SummaryAgent(BaseAgent):
    """Agent for generating structured summaries of referenced documents.

    This agent:
    - Extracts referenced filenames from original_context content
    - Discovers files in docs/ directory (preferring shallowest paths)
    - Generates structured summaries using LLM calls
    - Processes critical files (containing "requirement") sequentially first
    - Uses asyncio semaphore for max 3 concurrent LLM calls (configurable)
    - Implements retry logic with exponential backoff
    - Uses YAML configuration for all settings (Story 36.2)

    Attributes:
        config: Agent configuration object.
        session_manager: SessionManager for LLM interactions.
        project_root: Root directory for file discovery.
        summary_config: SummaryAgentConfig with all agent-specific settings.
        _semaphore: Semaphore for limiting concurrent LLM calls.
    """

    def __init__(
        self,
        config: AgentConfig,
        session_manager: SessionManager,
        project_root: Path | None = None,
        summary_config: SummaryAgentConfig | None = None,
    ) -> None:
        """Initialize the SummaryAgent.

        Args:
            config: Agent configuration object.
            session_manager: SessionManager for LLM interactions.
            project_root: Root directory for file discovery. Defaults to cwd.
            summary_config: Optional SummaryAgentConfig. If not provided, loads from YAML file.

        Raises:
            ValueError: If session_manager is None.
        """
        super().__init__(config, session_manager=session_manager)
        self.project_root = project_root or Path.cwd()

        # Load or use provided SummaryAgentConfig
        if summary_config is None:
            self.summary_config = self._load_config()
        else:
            self.summary_config = summary_config

        # Create semaphore for concurrency control based on config
        self._semaphore = asyncio.Semaphore(
            self.summary_config.performance.max_concurrent_documents
        )

        # Rebind logger with agent name
        self.logger: structlog.stdlib.BoundLogger = structlog.get_logger().bind(
            agent=self.__class__.__name__,
        )

    def _load_config(self) -> SummaryAgentConfig:
        """Load SummaryAgent configuration from YAML file.

        Returns:
            SummaryAgentConfig with loaded configuration values.
            Returns default config if file cannot be loaded.
        """
        loader = SummaryAgentConfigLoader()
        return loader.load_with_defaults()

    def _format_system_prompt(self) -> str:
        """Format system prompt for summary generation.

        Returns:
            Formatted system prompt string.
        """
        schema_str = json.dumps(SUMMARY_SCHEMA, indent=2)
        return f"""You are a professional technical document analyst.

Your task is to analyze the provided document and generate a structured summary.

You MUST respond with ONLY a valid JSON object matching this exact schema:

{schema_str}

Requirements:
- summary: 2-5 sentences capturing the core content
- key_points: 3-7 bullet points of important information
- structure.sections: List of main section titles
- structure.concepts: List of key concepts mentioned

The response must be parseable by json.loads(). Do not include markdown formatting or explanatory text outside the JSON."""

    def _extract_referenced_files(self, original_context: dict[str, Any]) -> list[str]:
        """Extract referenced filenames from original_context content.

        Searches for:
        - Backtick format: `filename.md`
        - Bare filenames: filename.md

        Args:
            original_context: Original context dictionary containing 'content'.

        Returns:
            List of unique referenced filenames with allowed extensions.
        """
        referenced_files: set[str] = set()

        # P1 Fix: Include explicit context_file if provided
        context_file = original_context.get("context_file")
        if context_file:
            referenced_files.add(str(context_file))

        content = original_context.get("content", "")
        if not content:
            return list(referenced_files)

        # Regex patterns for filename extraction
        patterns = [
            r"`([^`]+\.(?:md|txt|yaml|yml|json))`",  # backtick format
            r"\b([\w.-]+\.(?:md|txt|yaml|yml|json))\b",  # bare filename
        ]

        # Use config values for allowed extensions
        allowed_extensions = frozenset(self.summary_config.file_discovery.allowed_extensions)

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower()
                if any(match_lower.endswith(ext) for ext in allowed_extensions):
                    referenced_files.add(match)

        return list(referenced_files)

    def _find_file_in_docs(self, filename: str) -> dict[str, Any] | None:
        """Find a file in the docs/ directory.

        Searches recursively and prefers the shallowest path when multiple
        files have the same name.

        Args:
            filename: The filename to search for.

        Returns:
            Dict with file info (filename, relative_path, content, size_bytes)
            or None if not found/accessible.
        """
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return None

        # Handle relative paths (e.g., docs/calc-one-plus-one/calc-context.md)
        filepath = self.project_root / filename
        if filepath.exists() and filepath.is_file():
            candidates = [filepath]
        else:
            # Find all matching files (sorted by path depth, shallow first)
            candidates = sorted(docs_dir.rglob(Path(filename).name), key=lambda p: len(p.parts))

        for candidate in candidates:
            if not candidate.is_file():
                continue

            # Check extension is allowed (use config values)
            allowed_extensions = frozenset(self.summary_config.file_discovery.allowed_extensions)
            if candidate.suffix.lower() not in allowed_extensions:
                continue

            # Check file size (use config value)
            try:
                size_bytes = candidate.stat().st_size
                max_file_size = self.summary_config.performance.max_file_size_bytes
                if size_bytes > max_file_size:
                    self.logger.warning(
                        "file_too_large_skipped",
                        filename=filename,
                        path=str(candidate.relative_to(self.project_root)),
                        size_bytes=size_bytes,
                        max_size=max_file_size,
                    )
                    continue

                # Read file content
                try:
                    content = candidate.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    # Skip binary files
                    self.logger.warning(
                        "binary_file_skipped",
                        filename=filename,
                        path=str(candidate),
                    )
                    continue
                relative_path = candidate.relative_to(self.project_root).as_posix()

                return {
                    "filename": filename,
                    "relative_path": relative_path,
                    "content": content,
                    "size_bytes": size_bytes,
                }

            except (OSError, UnicodeDecodeError) as e:
                self.logger.warning(
                    "file_read_failed",
                    filename=filename,
                    path=str(candidate),
                    error=str(e),
                )
                continue

        return None

    def _validate_summary_schema(self, data: dict[str, Any]) -> bool:
        """Validate that summary data matches expected schema.

        Args:
            data: Parsed JSON data from LLM response.

        Returns:
            True if valid, False otherwise.
        """
        required_top_level = ["summary", "key_points", "structure"]
        for field_name in required_top_level:
            if field_name not in data:
                return False

        # Validate types
        if not isinstance(data["summary"], str):
            return False
        if not isinstance(data["key_points"], list):
            return False
        if not isinstance(data["structure"], dict):
            return False

        return True

    async def _call_llm_for_summary(
        self,
        filename: str,
        content: str,
    ) -> dict[str, Any] | None:
        """Call LLM to generate summary for a single document.

        Uses configuration values for timeout and retry settings.
        Implements retry logic with exponential backoff.

        Args:
            filename: Name of the file being summarized.
            content: File content to summarize.

        Returns:
            Dict with summary data or None if failed.
        """
        system_prompt = self._format_system_prompt()

        # Use config values for LLM settings
        llm_config = self.summary_config.llm
        perf_config = self.summary_config.performance

        # Truncate content if too long (rough estimate: ~4 chars per token)
        max_chars = llm_config.max_tokens * 4
        truncated = False
        if len(content) > max_chars:
            content = content[:max_chars]
            truncated = True

        user_prompt = f"""Please analyze this document and provide a structured summary.

Filename: {filename}

Content:
```
{content}
```

Remember to respond with ONLY valid JSON matching the required schema."""

        last_error: Exception | None = None
        max_retries = perf_config.max_retries

        for attempt in range(max_retries + 1):  # Initial + retries
            try:
                if self.session_manager is None:
                    raise LLMSummaryError("Session manager not available")

                # Call LLM with configurable timeout (enforced via asyncio.wait_for)
                response = await asyncio.wait_for(
                    self.session_manager.single_prompt(
                        prompt=user_prompt,
                        mode=llm_config.mode,
                        yolo=True,
                        system_prompt=system_prompt,
                    ),
                    timeout=perf_config.timeout_per_document_seconds,
                )

                # Extract content from response
                summary_text = self._extract_text_from_response(response)
                if not summary_text:
                    raise LLMSummaryError("Empty response from LLM")

                # Parse JSON
                try:
                    data = json.loads(summary_text)
                except json.JSONDecodeError as e:
                    raise LLMSummaryError(f"Invalid JSON response: {e}") from e

                # Validate schema
                if not self._validate_summary_schema(data):
                    raise LLMSummaryError("Response does not match required schema")

                # Add metadata
                data["truncated"] = truncated
                data["llm_tokens_used"] = len(content) // 4  # Rough estimate

                return data

            except TimeoutError:
                last_error = LLMSummaryError(
                    f"Timeout after {perf_config.timeout_per_document_seconds}s"
                )
                self.logger.warning(
                    "llm_timeout",
                    filename=filename,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    timeout_seconds=perf_config.timeout_per_document_seconds,
                )
            except Exception as e:
                last_error = e
                self.logger.warning(
                    "llm_call_failed",
                    filename=filename,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    error_type=type(e).__name__,
                )

            # Exponential backoff (1s, 2s, ...)
            if attempt < max_retries:
                backoff = 2**attempt
                await asyncio.sleep(backoff)

        # All retries exhausted
        self.logger.error(
            "llm_retries_exhausted",
            filename=filename,
            error=str(last_error) if last_error else "Unknown error",
        )
        return None

    def _extract_text_from_response(self, response: list[dict[str, Any]]) -> str | None:
        """Extract text content from LLM response.

        Args:
            response: List of message dicts from LLM.

        Returns:
            Extracted text or None.
        """
        for msg in reversed(response):
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        return block.get("text", "")
            elif isinstance(content, str):
                return content
        return None

    async def _process_single_document(
        self,
        file_info: dict[str, Any],
    ) -> DocumentSummary | None:
        """Process a single document to generate summary.

        Args:
            file_info: Dict with file information.

        Returns:
            DocumentSummary or None if processing failed.
        """
        filename = file_info["filename"]
        content = file_info["content"]

        self.logger.debug(
            "processing_document",
            filename=filename,
            size_bytes=file_info["size_bytes"],
        )

        # Call LLM for summary
        summary_data = await self._call_llm_for_summary(filename, content)
        if summary_data is None:
            return None

        # Create DocumentSummary
        return DocumentSummary(
            filename=filename,
            path=file_info["relative_path"],
            size_bytes=file_info["size_bytes"],
            summary=summary_data["summary"],
            key_points=summary_data.get("key_points", []),
            structure=summary_data.get("structure", {}),
            truncated=summary_data.get("truncated", False),
            llm_tokens_used=summary_data.get("llm_tokens_used", 0),
        )

    async def summarize_context(
        self,
        original_context: dict[str, Any],
    ) -> list[DocumentSummary]:
        """Generate structured summaries for all referenced documents.

        This is the main entry point for the SummaryAgent. It:
        1. Extracts referenced filenames from original_context
        2. Discovers files in docs/ directory
        3. Processes critical files (containing "requirement") sequentially first
        4. Processes remaining files concurrently (max 3 concurrent LLM calls)
        5. Returns list of DocumentSummary objects

        Args:
            original_context: Original context dictionary containing 'content'.

        Returns:
            List of DocumentSummary objects (failed files excluded).
        """
        # Extract referenced filenames
        referenced_files = self._extract_referenced_files(original_context)
        if not referenced_files:
            self.logger.info("no_referenced_files_found")
            return []

        self.logger.info(
            "starting_summary_generation",
            file_count=len(referenced_files),
            files=referenced_files,
        )

        # Find files in docs/
        file_infos: list[dict[str, Any]] = []
        for filename in referenced_files:
            file_info = self._find_file_in_docs(filename)
            if file_info:
                file_infos.append(file_info)
            else:
                self.logger.warning(
                    "file_not_found",
                    filename=filename,
                )

        if not file_infos:
            self.logger.warning("no_files_found_in_docs")
            return []

        # Categorize files: critical (contains "requirement") vs normal
        critical_files = [f for f in file_infos if "requirement" in f["filename"].lower()]
        normal_files = [f for f in file_infos if "requirement" not in f["filename"].lower()]

        self.logger.info(
            "file_categorization",
            critical_count=len(critical_files),
            normal_count=len(normal_files),
        )

        results: list[DocumentSummary] = []

        # Process critical files sequentially first
        if critical_files:
            self.logger.info(
                "processing_critical_files",
                count=len(critical_files),
            )
            for file_info in critical_files:
                try:
                    summary = await self._process_single_document(file_info)
                    if summary:
                        results.append(summary)
                except Exception as e:
                    self.logger.warning(
                        "critical_file_processing_failed",
                        filename=file_info["filename"],
                        error=str(e),
                    )

        # Process normal files concurrently with semaphore
        if normal_files:
            max_concurrent = self.summary_config.performance.max_concurrent_documents
            self.logger.info(
                "processing_normal_files",
                count=len(normal_files),
                max_concurrent=max_concurrent,
            )

            async def process_with_limit(file_info: dict[str, Any]) -> DocumentSummary | None:
                async with self._semaphore:
                    try:
                        return await self._process_single_document(file_info)
                    except Exception as e:
                        self.logger.warning(
                            "normal_file_processing_failed",
                            filename=file_info["filename"],
                            error=str(e),
                        )
                        return None

            # Process all normal files concurrently
            normal_results = await asyncio.gather(*[process_with_limit(f) for f in normal_files])

            # Filter out None results
            results.extend([r for r in normal_results if r is not None])

        # Calculate totals
        total_tokens = sum(r.llm_tokens_used for r in results)
        success_count = len(results)
        failure_count = len(file_infos) - success_count

        self.logger.info(
            "summary_generation_complete",
            total_files=len(file_infos),
            success_count=success_count,
            failure_count=failure_count,
            total_tokens=total_tokens,
        )

        return results

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic (required by BaseAgent).

        This method wraps summarize_context for compatibility with BaseAgent.

        Args:
            context: Execution context containing input data.

        Returns:
            Dict with 'summaries' key containing list of DocumentSummary objects.
        """
        summaries = await self.summarize_context(context)
        return {
            "summaries": [s.to_dict() for s in summaries],
            "count": len(summaries),
        }

    @classmethod
    def _create_test_agent(
        cls,
        project_root: Path | None = None,
        summary_config: SummaryAgentConfig | None = None,
    ) -> SummaryAgent:
        """Create a test agent with mocked dependencies.

        This is a helper method for testing purposes.

        Args:
            project_root: Optional project root path.
            summary_config: Optional SummaryAgentConfig for testing.

        Returns:
            SummaryAgent instance with mocked session_manager.
        """
        mock_config = MagicMock()
        mock_session_manager = MagicMock()

        agent = cls.__new__(cls)
        agent.config = mock_config
        agent.session_manager = mock_session_manager
        agent.project_root = project_root or Path.cwd()
        agent.logger = structlog.get_logger().bind(agent=cls.__name__)

        # Use provided config or create default
        agent.summary_config = summary_config or SummaryAgentConfig()

        # Create semaphore from config
        agent._semaphore = asyncio.Semaphore(
            agent.summary_config.performance.max_concurrent_documents
        )

        return agent


def create_summary_agent(
    config: AgentConfig,
    session_manager: SessionManager,
    project_root: Path | None = None,
    summary_config: SummaryAgentConfig | None = None,
) -> SummaryAgent:
    """Factory function to create a SummaryAgent instance.

    Args:
        config: Agent configuration.
        session_manager: SessionManager for LLM interactions.
        project_root: Optional project root path.
        summary_config: Optional SummaryAgentConfig. If not provided, loads from YAML file.

    Returns:
        Configured SummaryAgent instance.
    """
    return SummaryAgent(
        config=config,
        session_manager=session_manager,
        project_root=project_root,
        summary_config=summary_config,
    )


__all__ = [
    "SummaryAgent",
    "DocumentSummary",
    "SummaryAgentError",
    "FileDiscoveryError",
    "LLMSummaryError",
    "create_summary_agent",
    "SummaryAgentConfig",
    "SummaryAgentConfigLoader",
]
