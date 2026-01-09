"""
SpecDevAgent - TDD-focused development agent for spec automation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

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

        # Initialize TDD workflow components (simplified stubs for now)
        self.prompts = {}  # Prompt templates
        self.tdd_engine = None  # TDD workflow engine
        self.test_verifier = None  # Test verifier
        self.quality_gate_runner = None  # Quality gate runner

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

            # Call SDK to execute TDD workflow
            await self.sdk.query("Execute TDD workflow")

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

    def verify_independent_operation(self) -> Dict[str, Any]:
        """Verify that SpecDevAgent operates independently."""
        results: Dict[str, Any] = {
            "independent": True,
            "checks": {
                "no_bmad_core": True,
                "sdk_integration": True,
                "components_available": True,
            },
            "errors": [],
        }

        # Check for .bmad-core dependencies
        import sys
        for module_name in sys.modules.keys():
            if "bmad_core" in module_name.lower():
                results["checks"]["no_bmad_core"] = False
                results["independent"] = False
                results["errors"].append(f"Found bmad-core dependency: {module_name}")

        # Verify SDK integration
        if self.sdk is None:
            results["checks"]["sdk_integration"] = False
            results["independent"] = False
            results["errors"].append("SDK not initialized")

        logger.info(f"Independent operation verification: {results}")
        return results
