"""
Agent base classes and configuration.

This module provides the base agent class and configuration that the
specific agents (DevAgent, QAAgent, SMAgent) inherit from.
"""

import os
import uuid
import logging
import subprocess
from typing import Dict, Any, Optional, List, Type
from pathlib import Path
from types import TracebackType

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)


class AgentConfig:
    """Configuration for agent instances."""

    def __init__(
        self,
        task_name: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
    ):
        """
        Initialize agent configuration.

        Args:
            task_name: Name of the task
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature
            model: Model name to use
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.task_name = task_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.api_key = api_key


class BaseAgent:
    """Base agent class that provides common functionality for all agents."""

    def __init__(self, config: AgentConfig):
        """
        Initialize base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.client = None

        # Initialize Anthropic client
        api_key = config.api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise RuntimeError("API key not found in config or environment")

        if Anthropic is None:
            logger.warning("Anthropic SDK not installed, client will be None")
        else:
            self.client = Anthropic(api_key=api_key)

    async def process_request(self, input_text: str) -> Dict[str, Any]:  # type: ignore[misc]
        """
        Process a request using the agent.

        Args:
            input_text: Input text to process

        Returns:
            Dictionary with response and metadata

        Raises:
            RuntimeError: If client is not initialized
        """
        if not self.client:
            raise RuntimeError("Claude SDK client not initialized")

        # This is a placeholder implementation
        # Actual agents should override this method
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[
                {"role": "user", "content": input_text}
            ]
        )

        # Extract text content from response
        response_text: str = ""
        if response.content:
            first_content: Any = response.content[0]  # type: ignore[assignment]
            # Handle different content types
            if first_content is not None:
                text_attr: Optional[str] = getattr(first_content, 'text', None)  # type: ignore[arg-type]
                if text_attr is not None:
                    response_text = str(text_attr)
                else:
                    thinking_attr: str = getattr(first_content, 'thinking', '')  # type: ignore[arg-type]
                    response_text = str(thinking_attr) if thinking_attr else ""

        return {
            "response": response_text,
            "session_id": self.session_id,
            "model": self.config.model,
        }

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.

        Returns:
            Dictionary with session information
        """
        return {
            "task_name": self.config.task_name,
            "session_id": self.session_id,
            "model": self.config.model,
            "client_initialized": self.client is not None,
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        """Context manager exit."""
        self.client = None
        return None

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"BaseAgent(task='{self.config.task_name}', session_id='{self.session_id}')"


# Configuration classes for specific agents
class DevConfig(AgentConfig):
    """Configuration for DevAgent."""

    def __init__(
        self,
        task_name: str = "develop-story",
        source_dir: str = "src",
        test_dir: str = "tests",
        test_framework: str = "pytest",
        run_tests: bool = True,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
    ):
        """
        Initialize Dev configuration.

        Args:
            task_name: Name of the task
            source_dir: Source code directory
            test_dir: Test directory
            test_framework: Test framework to use
            run_tests: Whether to run tests automatically
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature
            model: Model name to use
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        super().__init__(
            task_name=task_name,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            api_key=api_key,
        )
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.test_framework = test_framework
        self.run_tests = run_tests


class QAConfig(AgentConfig):
    """Configuration for QAAgent."""

    def __init__(
        self,
        task_name: str = "review-qa",
        qa_output_dir: str = "qa",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
    ):
        """Initialize QA configuration."""
        super().__init__(
            task_name=task_name,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            api_key=api_key,
        )
        self.qa_output_dir = qa_output_dir


class SMConfig(AgentConfig):
    """Configuration for SMAgent."""

    def __init__(
        self,
        task_name: str = "manage-story",
        story_output_dir: str = "stories",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
    ):
        """Initialize SM configuration."""
        super().__init__(
            task_name=task_name,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            api_key=api_key,
        )
        self.story_output_dir = story_output_dir


# QA Result class
class QAResult:
    """QA validation result."""

    def __init__(
        self,
        gate: str,
        status_reason: str,
        quality_score: float = 0.0,
        reviewed_by: str = "QA Agent",
        top_issues: Optional[List[str]] = None,
        nfr_validation: Optional[Dict[str, Any]] = None,
        recommendations: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize QA result.

        Args:
            gate: QA gate status (PASS/CONCERNS/FAIL/WAIVED)
            status_reason: Reason for the status
            quality_score: Quality score (0-100)
            reviewed_by: Who reviewed this
            top_issues: List of top issues found
            nfr_validation: Non-functional requirements validation
            recommendations: Recommendations for improvement
        """
        self.gate = gate
        self.status_reason = status_reason
        self.quality_score = quality_score
        self.reviewed_by = reviewed_by
        self.top_issues = top_issues or []
        self.nfr_validation = nfr_validation or {}
        self.recommendations = recommendations or {}

    @property
    def status(self) -> str:
        """Backward compatibility - return gate as status."""
        return str(self.gate)

    @status.setter
    def status(self, value: str) -> None:
        """Backward compatibility - set gate from status."""
        self.gate = str(value)


# Agent implementations for testing
class DevAgent(BaseAgent):
    """Development agent for handling implementation tasks."""

    def __init__(self, config: Optional[DevConfig] = None):
        """Initialize Dev agent."""
        if config is None:
            config = DevConfig()
        super().__init__(config)
        self.name = "Dev Agent"
        # Type annotation for config to help type checkers
        self.config: DevConfig = self.config

    def implement_story(
        self,
        story_path: str,
        tasks: List[str],
        acceptance_criteria: List[str],
    ) -> Dict[str, Any]:
        """
        Implement a story based on tasks and acceptance criteria.

        Args:
            story_path: Path to the story file
            tasks: List of tasks to implement
            acceptance_criteria: List of acceptance criteria

        Returns:
            Dictionary with implementation results
        """
        if not self.client:
            raise RuntimeError("Claude SDK client not initialized")

        story_file = Path(story_path)
        if not story_file.exists():
            raise FileNotFoundError(f"Story file not found: {story_path}")

        # Read story content
        story_content = story_file.read_text()

        # Create implementation prompt
        prompt = f"""
        Implement the following story:

        Story Content:
        {story_content}

        Tasks to implement:
        {', '.join(tasks)}

        Acceptance Criteria:
        {', '.join(acceptance_criteria)}
        """

        # Call Claude API
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract implementation text from response
        implementation: str = ""
        if response.content:
            first_content: Any = response.content[0]  # type: ignore[assignment]
            # Handle different content types
            if hasattr(first_content, 'text'):  # type: ignore[arg-type]
                text_content: str = first_content.text  # type: ignore
                implementation = text_content
            elif hasattr(first_content, 'thinking'):  # type: ignore[arg-type]
                thinking_content: str = first_content.thinking  # type: ignore
                implementation = thinking_content

        return {
            "status": "success",
            "story_path": story_path,
            "tasks_completed": tasks,
            "acceptance_criteria": acceptance_criteria,
            "implementation": implementation,
        }

    def write_tests(  # type: ignore[misc]
        self,
        test_specs: List[Dict[str, Any]],
        test_type: str = "unit",
    ) -> Dict[str, Any]:
        """
        Write tests based on specifications.

        Args:
            test_specs: List of test specifications
            test_type: Type of tests (unit/integration/e2e)

        Returns:
            Dictionary with test writing results
        """
        if not self.client:
            raise RuntimeError("Claude SDK client not initialized")

        # Create test prompt
        prompt = f"""
        Write {test_type} tests for the following specifications:

        {test_specs}
        """

        # Call Claude API
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract tests text from response
        tests: str = ""
        if response.content:
            first_content: Any = response.content[0]  # type: ignore[assignment]
            # Handle different content types
            if hasattr(first_content, 'text'):  # type: ignore[arg-type]
                text_content: str = first_content.text  # type: ignore
                tests = text_content
            elif hasattr(first_content, 'thinking'):  # type: ignore[arg-type]
                thinking_content: str = first_content.thinking  # type: ignore
                tests = thinking_content

        return {
            "status": "success",
            "test_type": test_type,
            "specs_count": len(test_specs),
            "tests": tests,
        }

    def execute_validations(  # type: ignore[misc]
        self,
        source_files: List[str],
        test_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute validations on source and test files.

        Args:
            source_files: List of source files to validate
            test_files: List of test files to validate

        Returns:
            Dictionary with validation results
        """
        test_files = test_files or []
        validations: List[Dict[str, Any]] = []

        # Run type checking on source files
        for source_file in source_files:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", source_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                validations.append({
                    "file": source_file,
                    "type": "syntax_check",
                    "status": "pass" if result.returncode == 0 else "fail",
                    "output": result.stderr if result.returncode != 0 else "OK",
                })
            except subprocess.TimeoutExpired:
                validations.append({
                    "file": source_file,
                    "type": "syntax_check",
                    "status": "timeout",
                    "output": "Validation timed out",
                })
            except Exception as e:
                validations.append({
                    "file": source_file,
                    "type": "syntax_check",
                    "status": "error",
                    "output": str(e),
                })

        # Run pytest on test files if requested
        if test_files and self.config.run_tests:
            for test_file in test_files:
                try:
                    result = subprocess.run(
                        ["python", "-m", "pytest", test_file, "-v"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    validations.append({
                        "file": test_file,
                        "type": "test_execution",
                        "status": "pass" if result.returncode == 0 else "fail",
                        "output": result.stdout + result.stderr,
                    })
                except subprocess.TimeoutExpired:
                    validations.append({
                        "file": test_file,
                        "type": "test_execution",
                        "status": "timeout",
                        "output": "Test execution timed out",
                    })
                except Exception as e:
                    validations.append({
                        "file": test_file,
                        "type": "test_execution",
                        "status": "error",
                        "output": str(e),
                    })

        return {
            "status": "success",
            "results": {
                "source_files": source_files,
                "test_files": test_files,
                "validations": validations,
            },
        }

    def update_story_status(
        self,
        story_path: str,
        completed_tasks: List[str],
        file_list: List[str],
    ) -> Dict[str, Any]:
        """
        Update story file with completion status.

        Args:
            story_path: Path to the story file
            completed_tasks: List of completed tasks
            file_list: List of modified/created files

        Returns:
            Dictionary with update results
        """
        story_file = Path(story_path)
        if not story_file.exists():
            raise FileNotFoundError(f"Story file not found: {story_path}")

        # Read current story content
        story_content = story_file.read_text()

        # Create updated content
        updated_content = f"""# Story Status Update

## Completed Tasks
{chr(10).join(f'- [x] {task}' for task in completed_tasks)}

## Modified Files
{chr(10).join(f'- {f}' for f in file_list)}

## Original Story
{story_content}
"""

        # Write updated content
        story_file.write_text(updated_content)

        return {
            "status": "success",
            "story_path": story_path,
            "completed_tasks": completed_tasks,
            "file_list": file_list,
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.

        Returns:
            Dictionary with agent information
        """
        return {
            "agent_type": "Developer",
            "specialization": "Story implementation and TDD",
            "source_directory": self.config.source_dir,
            "test_directory": self.config.test_dir,
            "test_framework": self.config.test_framework,
            "task_name": self.config.task_name,
        }


class QAAgent(BaseAgent):
    """Quality Assurance agent for validating implementations."""

    def __init__(self, config: Optional[QAConfig] = None):
        """Initialize QA agent."""
        if config is None:
            config = QAConfig()
        super().__init__(config)
        self.name = "QA Agent"

    def validate_implementation(
        self,
        source_files: List[str],
        test_files: List[str],
    ) -> List[QAResult]:
        """
        Validate an implementation against requirements.

        Args:
            source_files: List of source files to validate
            test_files: List of test files to validate

        Returns:
            List of QA validation results
        """
        results: List[QAResult] = []

        # Check if source files exist
        for source_file in source_files:
            if not Path(source_file).exists():
                results.append(QAResult(
                    gate="FAIL",
                    status_reason=f"Source file not found: {source_file}",
                ))
            else:
                results.append(QAResult(
                    gate="PASS",
                    status_reason=f"Source file exists: {source_file}",
                ))

        # Check if test files exist
        for test_file in test_files:
            if not Path(test_file).exists():
                results.append(QAResult(
                    gate="FAIL",
                    status_reason=f"Test file not found: {test_file}",
                ))
            else:
                results.append(QAResult(
                    gate="PASS",
                    status_reason=f"Test file exists: {test_file}",
                ))

        return results

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "agent_type": "QA",
            "task_name": self.config.task_name,
        }


class SMAgent(BaseAgent):
    """Story Master agent for managing stories."""

    def __init__(
        self,
        config: Optional[SMConfig] = None,
        project_root: Optional[str] = None,
        tasks_path: Optional[str] = None,
    ):
        """Initialize SM agent."""
        if config is None:
            config = SMConfig()
        super().__init__(config)
        self.name = "SM Agent"
        self.project_root = project_root
        self.tasks_path = tasks_path

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "agent_type": "Story Master",
            "task_name": self.config.task_name,
            "project_root": self.project_root,
            "tasks_path": self.tasks_path,
        }
