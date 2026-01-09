"""
SpecDevAgent - TDD-focused development agent for spec automation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .prompts import PromptSystem
from .tdd_workflow import TDDWorkflowEngine
from .test_verifier import TestVerifier
from .quality_gates import QualityGateRunner
from .spec_state_manager import SpecStateManager
from .doc_parser import DocumentParser

logger = logging.getLogger(__name__)


class SpecDevAgent:
    """Test-driven development agent for spec automation."""

    def __init__(
        self,
        sdk: Any,
        state_manager: Optional[SpecStateManager] = None,
        doc_parser: Optional[DocumentParser] = None,
    ) -> None:
        """Initialize the SpecDevAgent."""
        self.sdk = sdk
        self.state_manager = state_manager or SpecStateManager(
            db_path=Path("spec_progress.db")
        )
        self.doc_parser = doc_parser or DocumentParser()

        # Initialize TDD workflow components
        self.prompts = PromptSystem()
        self.tdd_engine = TDDWorkflowEngine(sdk=sdk, prompts=self.prompts)
        self.test_verifier = TestVerifier()
        self.quality_gate_runner = QualityGateRunner()

        logger.info("SpecDevAgent initialized with TDD workflow capabilities")

    async def execute_tdd_cycle(self, story_path: str) -> bool:
        """Execute complete TDD cycle for a story."""
        try:
            story_path_obj = Path(story_path)

            if not story_path_obj.exists():
                logger.error(f"Story file not found: {story_path}")
                return False

            # Update initial state
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status="in_progress",
                phase="parsing",
            )

            # Parse story document
            logger.info(f"Parsing story document: {story_path}")
            story_data = self.doc_parser.parse_document(story_path_obj)

            # Extract requirements and acceptance criteria
            requirements = story_data.get("requirements", [])
            acceptance_criteria = story_data.get("acceptance_criteria", [])

            logger.info(
                f"Extracted {len(requirements)} requirements and "
                f"{len(acceptance_criteria)} acceptance criteria"
            )

            # Update state to TDD phase
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status="in_progress",
                phase="tdd_cycle",
            )

            # Execute TDD workflow
            logger.info("Starting TDD cycle execution")
            tdd_success = await self.tdd_engine.execute_workflow(
                story_path=story_path,
                requirements=requirements,
                acceptance_criteria=acceptance_criteria,
            )

            if not tdd_success:
                logger.error("TDD workflow failed")
                self.state_manager.update_story_status(
                    story_path=str(story_path),
                    status="failed",
                    phase="tdd_cycle",
                )
                return False

            # Update state to verification phase
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status="in_progress",
                phase="verification",
            )

            # Verify all tests pass
            logger.info("Verifying all tests pass")
            tests_pass = await self.test_verifier.verify_all_tests_pass(
                story_path=story_path
            )

            if not tests_pass:
                logger.error("Not all tests passed")
                self.state_manager.update_story_status(
                    story_path=str(story_path),
                    status="failed",
                    phase="verification",
                )
                return False

            # Update state to quality gates phase
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status="in_progress",
                phase="quality_gates",
            )

            # Run quality gates
            logger.info("Running quality gates (Ruff, BasedPyright, Pytest)")
            quality_success = await self.quality_gate_runner.run_all_gates(
                source_dir=story_path_obj.parent
            )

            if not quality_success:
                logger.error("Quality gates failed")
                self.state_manager.update_story_status(
                    story_path=str(story_path),
                    status="failed",
                    phase="quality_gates",
                )
                return False

            # All phases complete successfully
            logger.info("TDD cycle completed successfully")
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status="completed",
                phase="done",
            )

            return True

        except Exception as e:
            logger.error(f"Error executing TDD cycle: {e}", exc_info=True)
            try:
                self.state_manager.update_story_status(
                    story_path=str(story_path),
                    status="failed",
                    phase="error",
                )
            except Exception:
                pass
            return False

    async def execute_tdd_cycle_with_error_handling(
        self, story_path: str
    ) -> bool:
        """Execute TDD cycle with comprehensive error handling."""
        try:
            return await self.execute_tdd_cycle(story_path)
        except FileNotFoundError as e:
            logger.error(f"Story file not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in TDD cycle: {e}", exc_info=True)
            return False

    def verify_independent_operation(self) -> Dict[str, Any]:
        """Verify that SpecDevAgent operates independently."""
        checks: Dict[str, bool] = {
            "no_bmad_core": True,
            "sdk_integration": True,
            "components_available": True,
        }
        errors: list[str] = []
        independent = True

        # Check for .bmad-core dependencies
        import sys
        for module_name in sys.modules.keys():
            if "bmad_core" in module_name.lower():
                checks["no_bmad_core"] = False
                independent = False
                errors.append(f"Found bmad-core dependency: {module_name}")

        # Verify SDK integration
        if self.sdk is None:
            checks["sdk_integration"] = False
            independent = False
            errors.append("SDK not initialized")

        # Verify all components
        required_components = [
            "tdd_engine",
            "prompts",
            "test_verifier",
            "quality_gate_runner",
            "state_manager",
            "doc_parser",
        ]

        for component in required_components:
            if not hasattr(self, component):
                checks["components_available"] = False
                independent = False
                errors.append(f"Missing component: {component}")

        results: Dict[str, Any] = {
            "independent": independent,
            "checks": checks,
            "errors": errors,
        }
        logger.info(f"Independent operation verification: {results}")
        return results
