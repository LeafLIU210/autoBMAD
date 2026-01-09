"""
Quality Gates - Executes quality checks (Ruff, BasedPyright, Pytest).

This module integrates with the quality agents from epic_automation:
- RuffAgent for code linting and auto-fixing
- BasedpyrightAgent for type checking
- PytestAgent for test execution

Runs quality gates in sequence and ensures all pass before completion.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import quality agents - they are optional
_quality_agents_available = False
_QualityGatePipeline: type | None = None
_RuffAgent: type | None = None
_BasedpyrightAgent: type | None = None
_PytestAgent: type | None = None

try:
    from autoBMAD.epic_automation.quality_agents import (
        QualityGatePipeline,
        RuffAgent,
        BasedpyrightAgent,
        PytestAgent,
    )
    _quality_agents_available = True
    _QualityGatePipeline = QualityGatePipeline
    _RuffAgent = RuffAgent
    _BasedpyrightAgent = BasedpyrightAgent
    _PytestAgent = PytestAgent
except ImportError:
    logger.warning("Quality agents not available - quality gates will be skipped")


class QualityGateRunner:
    """
    Executes quality gates using quality agents.

    Quality gates include:
    1. Ruff - Code linting and formatting
    2. BasedPyright - Type checking
    3. Pytest - Test execution

    All gates must pass before completion.
    """

    def __init__(self) -> None:
        """Initialize QualityGateRunner."""
        self.pipeline: Any = None
        if _quality_agents_available and _QualityGatePipeline is not None:
            # Initialize quality gate pipeline
            self.pipeline = _QualityGatePipeline()
            logger.info("QualityGateRunner initialized with quality agents")
        else:
            logger.warning("QualityGateRunner initialized without quality agents")

    async def run_all_gates(self, source_dir: Path) -> bool:
        """
        Run all quality gates.

        Args:
            source_dir: Source directory for quality checks

        Returns:
            True if all quality gates pass
        """
        try:
            if not _quality_agents_available or self.pipeline is None:
                logger.warning("Quality agents not available, skipping quality gates")
                return True

            logger.info(f"Running quality gates for directory: {source_dir}")

            # Run complete quality gate pipeline
            results = await self.pipeline.execute_pipeline(
                source_dir=str(source_dir),
                test_dir=str(source_dir / "tests"),
                max_cycles=3,
            )

            # Check if all gates passed
            if results.get("success", False):
                logger.info("All quality gates passed successfully")
                return True
            else:
                logger.error(f"Quality gates failed: {results.get('errors', [])}")
                return False

        except Exception as e:
            logger.error(f"Error running quality gates: {e}", exc_info=True)
            return False

    async def run_ruff_gate(self, source_dir: Path) -> bool:
        """
        Run Ruff quality gate.

        Args:
            source_dir: Source directory

        Returns:
            True if Ruff gate passes
        """
        try:
            if not _quality_agents_available or _RuffAgent is None:
                logger.warning("Quality agents not available, skipping Ruff gate")
                return True

            ruff_agent = _RuffAgent()
            results = await ruff_agent.retry_cycle(source_dir=source_dir, max_cycles=3)

            success = results.get("successful_cycles", 0) > 0

            if success:
                logger.info("Ruff gate passed")
            else:
                logger.error("Ruff gate failed")

            return success

        except Exception as e:
            logger.error(f"Error running Ruff gate: {e}", exc_info=True)
            return False

    async def run_basedpyright_gate(self, source_dir: Path) -> bool:
        """
        Run BasedPyright quality gate.

        Args:
            source_dir: Source directory

        Returns:
            True if BasedPyright gate passes
        """
        try:
            if not _quality_agents_available or _BasedpyrightAgent is None:
                logger.warning("Quality agents not available, skipping BasedPyright gate")
                return True

            basedpyright_agent = _BasedpyrightAgent()
            results = await basedpyright_agent.retry_cycle(source_dir=source_dir, max_cycles=3)

            success = results.get("successful_cycles", 0) > 0

            if success:
                logger.info("BasedPyright gate passed")
            else:
                logger.error("BasedPyright gate failed")

            return success

        except Exception as e:
            logger.error(f"Error running BasedPyright gate: {e}", exc_info=True)
            return False

    async def run_pytest_gate(self, source_dir: Path) -> bool:
        """
        Run Pytest quality gate.

        Args:
            source_dir: Source directory

        Returns:
            True if Pytest gate passes
        """
        try:
            if not _quality_agents_available or _PytestAgent is None:
                logger.warning("Quality agents not available, skipping Pytest gate")
                return True

            pytest_agent = _PytestAgent()
            results = await pytest_agent.run_tests(
                test_dir=str(source_dir / "tests"),
                source_dir=str(source_dir),
            )

            success = results.get("success", False)

            if success:
                logger.info("Pytest gate passed")
            else:
                logger.error("Pytest gate failed")
                logger.error(f"Test errors: {results.get('errors', [])}")

            return success

        except Exception as e:
            logger.error(f"Error running Pytest gate: {e}", exc_info=True)
            return False

    async def get_quality_report(self, source_dir: Path) -> dict[str, Any]:
        """
        Get comprehensive quality report.

        Args:
            source_dir: Source directory

        Returns:
            Dictionary with quality gate results
        """
        try:
            if not _quality_agents_available or self.pipeline is None:
                return {
                    "available": False,
                    "message": "Quality agents not available",
                }

            # Run all gates and collect results
            results = await self.pipeline.execute_pipeline(
                source_dir=str(source_dir),
                test_dir=str(source_dir / "tests"),
                max_cycles=3,
            )

            # Format results
            report: dict[str, Any] = {
                "available": True,
                "overall_success": results.get("success", False),
                "ruff": results.get("ruff", {}),
                "basedpyright": results.get("basedpyright", {}),
                "pytest": results.get("pytest", {}),
                "errors": results.get("errors", []),
            }

            return report

        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {"error": str(e)}

    def verify_quality_agents_available(self) -> bool:
        """
        Verify quality agents are available.

        Returns:
            True if quality agents are available
        """
        return _quality_agents_available

    async def run_gates_with_retry(
        self, source_dir: Path, max_retries: int = 3
    ) -> bool:
        """
        Run quality gates with retry logic.

        Args:
            source_dir: Source directory
            max_retries: Maximum retry attempts

        Returns:
            True if gates pass after retries
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"Quality gate attempt {attempt}/{max_retries}")

            success = await self.run_all_gates(source_dir)

            if success:
                logger.info(f"Quality gates passed on attempt {attempt}")
                return True

            if attempt < max_retries:
                logger.warning(f"Quality gates failed on attempt {attempt}, retrying...")
                await asyncio.sleep(2)  # Wait before retry

        logger.error(f"Quality gates failed after {max_retries} attempts")
        return False
