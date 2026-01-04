"""
Base Agent Class for BMAD SM-Dev-QA Cycle Automation

This module provides a shared base class for all BMAD agents, implementing
common functionality including task guidance loading and Claude SDK integration.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from anthropic import Anthropic
from anthropic.types import MessageParam


class BaseAgent:
    """
    Base class for all BMAD agents.

    Provides common functionality for loading task guidance from .bmad-core
    and creating fresh Claude SDK clients per session.
    """

    def __init__(self, agent_name: str, task_type: str):
        """
        Initialize the BaseAgent.

        Args:
            agent_name: Name of the agent (e.g., 'sm', 'dev', 'qa')
            task_type: Type of task (e.g., 'create-next-story', 'develop-story', 'review-story')
        """
        self.agent_name = agent_name
        self.task_type = task_type
        self.logger = logging.getLogger(f"bmad.{agent_name}_agent")
        self._task_guidance: Optional[str] = None
        self._claude_client: Optional[Anthropic] = None

    def load_task_guidance(self) -> str:
        """
        Load task guidance from .bmad-core/tasks/*.md file.

        Returns:
            The task guidance content as a string.

        Raises:
            FileNotFoundError: If the task guidance file doesn't exist.
            Exception: If there's an error reading the file.
        """
        if self._task_guidance is not None:
            return self._task_guidance

        # Construct path to task guidance file
        project_root = Path(__file__).parent.parent.parent
        task_file_path = project_root / ".bmad-core" / "tasks" / f"{self.task_type}.md"

        self.logger.info(f"Loading task guidance from: {task_file_path}")

        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                self._task_guidance = f.read()
            self.logger.info(f"Successfully loaded {len(self._task_guidance)} characters of guidance")
            return self._task_guidance
        except FileNotFoundError:
            error_msg = f"Task guidance file not found: {task_file_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Error reading task guidance file: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def create_claude_client(self) -> Anthropic:
        """
        Create a fresh Claude SDK client for this session.

        Returns:
            Configured Anthropic client instance.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._claude_client is not None:
            return self._claude_client

        try:
            # Try to get API key from environment
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                # For development/testing, allow manual key or use a placeholder
                api_key = os.getenv('CLAUDE_API_KEY', 'placeholder-key-for-development')

            self._claude_client = Anthropic(api_key=api_key)
            self.logger.info("Created fresh Claude SDK client")
            return self._claude_client
        except Exception as e:
            error_msg = f"Failed to create Claude SDK client: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    async def call_claude(
        self,
        messages: list[MessageParam],
        max_tokens: int = 4096,
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Claude API with the provided messages.

        Args:
            messages: List of message parameters for the API
            max_tokens: Maximum tokens to generate
            model: Claude model to use
            **kwargs: Additional arguments for the API

        Returns:
            The response from Claude API.

        Raises:
            Exception: If the API call fails.
        """
        try:
            client = self.create_claude_client()
            self.logger.info(f"Calling Claude API with {len(messages)} messages using model {model}")

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs
            )

            self.logger.info(f"Claude API call successful, response: {len(response.content)} content blocks")
            return {
                "content": response.content,
                "usage": response.usage,
                "stop_reason": response.stop_reason,
                "stop_sequence": response.stop_sequence
            }
        except Exception as e:
            error_msg = f"Claude API call failed: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            The system prompt combining task guidance and agent-specific instructions.
        """
        task_guidance = self.load_task_guidance()

        agent_specific_instructions = f"""
You are a {self.agent_name.upper()} agent in the BMAD (Breakthrough Method of Agile AI-driven Development) system.

Your role is to {self._get_agent_role_description()}

Always follow the task guidance provided below and maintain high quality standards.
Always cite your sources when referencing documentation or guidelines.
"""

        return f"{agent_specific_instructions}\n\n---\n\n{task_guidance}"

    def _get_agent_role_description(self) -> str:
        """
        Get role-specific description for this agent.

        Returns:
            Description of the agent's role and responsibilities.
        """
        role_descriptions = {
            'sm': 'prepare comprehensive, actionable story documents based on epic definitions',
            'dev': 'implement story requirements using TDD methodology with comprehensive testing',
            'qa': 'perform comprehensive quality assessment and provide structured gate decisions'
        }
        return role_descriptions.get(self.agent_name, 'perform specialized tasks')

    def reset_session(self) -> None:
        """
        Reset the agent session, clearing cached task guidance and client.

        This should be called at the start of each new session to ensure
        fresh state and avoid cross-session contamination.
        """
        self.logger.info(f"Resetting {self.agent_name} agent session")
        self._task_guidance = None
        self._claude_client = None
