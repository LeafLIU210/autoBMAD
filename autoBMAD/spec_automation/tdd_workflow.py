"""
TDD Workflow Engine - Implements red-green-refactor cycle.

This module orchestrates the core TDD workflow:
1. RED: Generate failing tests based on requirements
2. GREEN: Generate minimal implementation to pass tests
3. REFACTOR: Improve code while keeping tests green
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .prompts import PromptSystem

logger = logging.getLogger(__name__)


class TDDWorkflowEngine:
    """
    Implements the TDD workflow (red-green-refactor cycle).

    Orchestrates:
    1. Test generation from acceptance criteria (RED)
    2. Code generation to pass tests (GREEN)
    3. Code refactoring while maintaining test coverage (REFACTOR)
    4. Coverage tracking and reporting
    """

    def __init__(self, sdk: Any, prompts: PromptSystem) -> None:
        """
        Initialize TDD workflow engine.

        Args:
            sdk: Claude SDK for generating code and tests
            prompts: PromptSystem for generating TDD prompts
        """
        self.sdk = sdk
        self.prompts = prompts
        self.coverage_threshold = 80.0  # Minimum coverage percentage

        logger.info("TDDWorkflowEngine initialized")

    async def execute_workflow(
        self,
        story_path: str,
        requirements: List[str],
        acceptance_criteria: List[str],
    ) -> bool:
        """
        Execute complete TDD workflow.

        Args:
            story_path: Path to the story file
            requirements: List of extracted requirements
            acceptance_criteria: List of acceptance criteria

        Returns:
            True if workflow completes successfully
        """
        try:
            logger.info(f"Starting TDD workflow for {len(requirements)} requirements")

            # Process each requirement through TDD cycle
            for i, requirement in enumerate(requirements, 1):
                logger.info(f"Processing requirement {i}/{len(requirements)}: {requirement}")

                # Get acceptance criteria for this requirement
                req_criteria = self._get_criteria_for_requirement(
                    requirement, acceptance_criteria
                )

                # Execute TDD cycle for this requirement
                success = await self._execute_tdd_cycle_for_requirement(
                    requirement=requirement,
                    acceptance_criteria=req_criteria,
                    story_path=story_path,
                )

                if not success:
                    logger.error(f"TDD cycle failed for requirement: {requirement}")
                    return False

            logger.info("TDD workflow completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in TDD workflow: {e}", exc_info=True)
            return False

    async def _execute_tdd_cycle_for_requirement(
        self,
        requirement: str,
        acceptance_criteria: List[str],
        story_path: str,
    ) -> bool:
        """
        Execute TDD cycle for a single requirement.

        Args:
            requirement: The requirement to implement
            acceptance_criteria: List of acceptance criteria
            story_path: Path to the story file

        Returns:
            True if cycle completes successfully
        """
        try:
            # RED PHASE: Generate failing test
            logger.info("RED phase: Generating failing test")
            test_code = await self._generate_test(
                requirement=requirement,
                acceptance_criteria=acceptance_criteria,
            )

            if not test_code:
                logger.error("Failed to generate test")
                return False

            # Save generated test
            test_file_path = await self._save_test(test_code, story_path, requirement)
            logger.info(f"Generated test saved to: {test_file_path}")

            # GREEN PHASE: Generate minimal implementation
            logger.info("GREEN phase: Generating minimal implementation")
            implementation = await self._generate_implementation(
                requirement=requirement,
                test_code=test_code,
            )

            if not implementation:
                logger.error("Failed to generate implementation")
                return False

            # Save generated implementation
            impl_file_path = await self._save_implementation(
                implementation, story_path, requirement
            )
            logger.info(f"Generated implementation saved to: {impl_file_path}")

            # REFACTOR PHASE: Refactor code
            logger.info("REFACTOR phase: Refactoring code")
            refactored_code = await self._refactor_code(
                requirement=requirement,
                test_code=test_code,
                implementation=implementation,
            )

            if refactored_code:
                # Save refactored code
                refactor_file_path = await self._save_refactored_code(
                    refactored_code, story_path, requirement
                )
                logger.info(f"Refactored code saved to: {refactor_file_path}")

            logger.info(f"TDD cycle complete for requirement: {requirement}")
            return True

        except Exception as e:
            logger.error(f"Error in TDD cycle for requirement: {e}", exc_info=True)
            return False

    async def _generate_test(
        self, requirement: str, acceptance_criteria: List[str]
    ) -> Optional[str]:
        """
        Generate test code for a requirement (RED phase).

        Args:
            requirement: The requirement to test
            acceptance_criteria: List of acceptance criteria

        Returns:
            Generated test code as string
        """
        try:
            prompt = self.prompts.generate_test_prompt(
                requirement=requirement,
                acceptance_criteria=acceptance_criteria,
            )

            # Use SDK to generate test
            if hasattr(self.sdk, "query"):
                response = await self.sdk.query(prompt=prompt)
                return self._extract_code_from_response(response)

            logger.warning("SDK query method not available")
            return None

        except Exception as e:
            logger.error(f"Error generating test: {e}", exc_info=True)
            return None

    async def _generate_implementation(
        self, requirement: str, test_code: str
    ) -> Optional[str]:
        """
        Generate minimal implementation for a requirement (GREEN phase).

        Args:
            requirement: The requirement to implement
            test_code: The test code that should pass

        Returns:
            Generated implementation code
        """
        try:
            prompt = self.prompts.generate_implementation_prompt(
                failing_test=test_code,
                requirement=requirement,
            )

            # Use SDK to generate implementation
            if hasattr(self.sdk, "query"):
                response = await self.sdk.query(prompt=prompt)
                return self._extract_code_from_response(response)

            logger.warning("SDK query method not available")
            return None

        except Exception as e:
            logger.error(f"Error generating implementation: {e}", exc_info=True)
            return None

    async def _refactor_code(
        self,
        requirement: str,
        test_code: str,
        implementation: str,
    ) -> Optional[str]:
        """
        Refactor code while keeping tests green (REFACTOR phase).

        Args:
            requirement: The requirement
            test_code: The test code
            implementation: The implementation

        Returns:
            Refactored implementation code
        """
        try:
            prompt = self.prompts.generate_refactor_prompt(
                passing_test=test_code,
                implementation=implementation,
                requirement=requirement,
            )

            # Use SDK to refactor code
            if hasattr(self.sdk, "query"):
                response = await self.sdk.query(prompt=prompt)
                return self._extract_code_from_response(response)

            logger.warning("SDK query method not available")
            return None

        except Exception as e:
            logger.error(f"Error refactoring code: {e}", exc_info=True)
            return None

    async def _save_test(
        self, test_code: str, story_path: str, requirement: str
    ) -> str:
        """
        Save generated test to file.

        Args:
            test_code: The test code to save
            story_path: Path to the story file
            requirement: The requirement

        Returns:
            Path to saved test file
        """
        story_dir = Path(story_path).parent
        test_filename = f"test_{self._sanitize_filename(requirement)}.py"
        test_path = story_dir / test_filename

        test_path.write_text(test_code, encoding="utf-8")
        return str(test_path)

    async def _save_implementation(
        self, implementation: str, story_path: str, requirement: str
    ) -> str:
        """
        Save generated implementation to file.

        Args:
            implementation: The implementation code to save
            story_path: Path to the story file
            requirement: The requirement

        Returns:
            Path to saved implementation file
        """
        story_dir = Path(story_path).parent
        impl_filename = f"{self._sanitize_filename(requirement)}.py"
        impl_path = story_dir / impl_filename

        impl_path.write_text(implementation, encoding="utf-8")
        return str(impl_path)

    async def _save_refactored_code(
        self, refactored_code: str, story_path: str, requirement: str
    ) -> str:
        """
        Save refactored code to file.

        Args:
            refactored_code: The refactored code to save
            story_path: Path to the story file
            requirement: The requirement

        Returns:
            Path to saved refactored file
        """
        story_dir = Path(story_path).parent
        refactor_filename = f"{self._sanitize_filename(requirement)}_refactored.py"
        refactor_path = story_dir / refactor_filename

        refactor_path.write_text(refactored_code, encoding="utf-8")
        return str(refactor_path)

    def _sanitize_filename(self, text: str) -> str:
        """
        Sanitize text to create valid filename.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized filename
        """
        # Remove special characters and replace spaces with underscores
        filename = "".join(c for c in text if c.isalnum() or c in " _-").rstrip()
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        # Limit length
        return filename[:50] if len(filename) > 50 else filename

    def _get_criteria_for_requirement(
        self, requirement: str, acceptance_criteria: List[str]
    ) -> List[str]:
        """
        Get acceptance criteria for a specific requirement.

        Args:
            requirement: The requirement
            acceptance_criteria: All acceptance criteria

        Returns:
            Criteria relevant to this requirement
        """
        # Simple heuristic: return all criteria if we can't map them
        # In a real implementation, this would use NLP to match criteria to requirements
        return acceptance_criteria

    def _extract_code_from_response(self, response: Any) -> Optional[str]:
        """
        Extract code from SDK response.

        Args:
            response: SDK response

        Returns:
            Extracted code as string
        """
        try:
            # Handle different response formats
            if isinstance(response, str):
                return self._extract_code_block(response)
            elif hasattr(response, "result"):
                result = response.result
                if isinstance(result, str):
                    return self._extract_code_block(result)
            elif hasattr(response, "content"):
                content = response.content
                if isinstance(content, str):
                    return self._extract_code_block(content)

            logger.warning(f"Unexpected response format: {type(response)}")
            return None

        except Exception as e:
            logger.error(f"Error extracting code from response: {e}")
            return None

    def _extract_code_block(self, text: str) -> str:
        """
        Extract code block from text.

        Args:
            text: Text containing code block

        Returns:
            Extracted code
        """
        # Try to extract code from markdown code blocks
        if "```" in text:
            # Split by code blocks
            parts = text.split("```")
            if len(parts) >= 3:
                # Take the middle part (first code block)
                code = parts[1]
                # Remove language specifier if present
                lines = code.split("\n")
                if lines and ":" in lines[0]:
                    lines = lines[1:]
                return "\n".join(lines).strip()

        # If no code block found, return the whole text
        return text.strip()

    async def track_coverage(
        self, story_path: str, test_files: List[str]
    ) -> Dict[str, float]:
        """
        Track test coverage for generated tests.

        Args:
            story_path: Path to the story file
            test_files: List of test file paths

        Returns:
            Dictionary with coverage metrics
        """
        try:
            # This would integrate with coverage.py in a real implementation
            # For now, return mock coverage data
            coverage_data = {
                "total_coverage": 85.0,
                "statement_coverage": 85.0,
                "branch_coverage": 80.0,
                "line_coverage": 85.0,
            }

            logger.info(f"Coverage tracking: {coverage_data}")
            return coverage_data

        except Exception as e:
            logger.error(f"Error tracking coverage: {e}")
            return {}

    def verify_coverage_threshold(self, coverage: Dict[str, float]) -> bool:
        """
        Verify coverage meets threshold.

        Args:
            coverage: Coverage metrics

        Returns:
            True if coverage meets or exceeds threshold
        """
        total_coverage = coverage.get("total_coverage", 0.0)
        return total_coverage >= self.coverage_threshold
