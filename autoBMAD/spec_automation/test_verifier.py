"""
Test Verifier - Verifies all generated tests pass.

This module:
1. Discovers all generated test files
2. Executes tests using pytest
3. Verifies all tests pass
4. Reports test results and coverage
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TestVerifier:
    """
    Verifies that all generated tests pass.

    Responsibilities:
    - Discover test files
    - Execute tests with pytest
    - Verify all tests pass
    - Collect coverage data
    - Report results
    """

    def __init__(self) -> None:
        """Initialize TestVerifier."""
        self.pytest_path = self._find_pytest_path()
        logger.info("TestVerifier initialized")

    async def verify_all_tests_pass(self, story_path: str) -> bool:
        """
        Verify all tests pass for a story.

        Args:
            story_path: Path to the story file

        Returns:
            True if all tests pass, False otherwise
        """
        try:
            story_dir = Path(story_path).parent

            # Discover test files
            logger.info("Discovering test files")
            test_files = self._discover_test_files(story_dir)

            if not test_files:
                logger.warning("No test files found")
                return False

            logger.info(f"Found {len(test_files)} test files")

            # Execute tests
            logger.info("Executing tests")
            results = await self._execute_tests(test_files, story_dir)

            # Verify all tests passed
            all_passed = self._verify_all_passed(results)

            if all_passed:
                logger.info("All tests passed successfully")
            else:
                logger.error("Some tests failed")

            return all_passed

        except Exception as e:
            logger.error(f"Error verifying tests: {e}", exc_info=True)
            return False

    def _discover_test_files(self, directory: Path) -> List[Path]:
        """
        Discover test files in directory.

        Args:
            directory: Directory to search

        Returns:
            List of test file paths
        """
        test_files = []

        # Look for test_*.py files
        for test_file in directory.glob("test_*.py"):
            test_files.append(test_file)

        # Look for tests directory
        tests_dir = directory / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.glob("test_*.py"):
                test_files.append(test_file)

        return test_files

    async def _execute_tests(
        self, test_files: List[Path], working_dir: Path
    ) -> Dict[str, Any]:
        """
        Execute test files using pytest.

        Args:
            test_files: List of test file paths
            working_dir: Working directory for test execution

        Returns:
            Dictionary with test execution results
        """
        try:
            # Build pytest command
            test_file_paths = [str(f) for f in test_files]
            cmd = [
                self.pytest_path,
                "-v",
                "--tb=short",
                "--cov-report=term-missing",
                "--cov-report=json:coverage.json",
            ] + test_file_paths

            logger.info(f"Running pytest: {' '.join(cmd)}")

            # Execute pytest
            process = await asyncio.create_subprocess_shell(
                " ".join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(working_dir),
            )

            stdout, stderr = await process.communicate()

            # Parse results
            results = {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8") if stdout else "",
                "stderr": stderr.decode("utf-8") if stderr else "",
                "test_files": test_file_paths,
            }

            # Try to parse coverage
            coverage_file = working_dir / "coverage.json"
            if coverage_file.exists():
                try:
                    import json

                    coverage_data = json.loads(coverage_file.read_text())
                    results["coverage"] = coverage_data
                except Exception as e:
                    logger.warning(f"Could not parse coverage file: {e}")

            return results

        except Exception as e:
            logger.error(f"Error executing tests: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _verify_all_passed(self, results: Dict[str, Any]) -> bool:
        """
        Verify all tests passed.

        Args:
            results: Test execution results

        Returns:
            True if all tests passed
        """
        # Check if pytest succeeded
        if not results.get("success", False):
            logger.error(f"Test execution failed: {results.get('stderr', '')}")
            return False

        # Check for failures in output
        output = results.get("stdout", "")
        if "FAILED" in output or "ERROR" in output:
            logger.error("Tests failed or had errors")
            return False

        # Check coverage if available
        coverage = results.get("coverage")
        if coverage:
            try:
                total_coverage = coverage.get("totals", {}).get("percent_covered", 0)
                if total_coverage < 80:
                    logger.warning(f"Coverage {total_coverage}% is below 80% threshold")
                    # Don't fail for low coverage in verification phase
                    # Quality gates will handle this
            except Exception as e:
                logger.warning(f"Could not check coverage: {e}")

        return True

    def _find_pytest_path(self) -> str:
        """
        Find pytest executable path.

        Returns:
            Path to pytest executable
        """
        # Try to find pytest in common locations
        import sys

        # Check if pytest is in PATH
        try:
            subprocess.run(
                ["pytest", "--version"],
                capture_output=True,
                check=True,
            )
            return "pytest"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Try virtual environment paths
        venv_paths = [
            Path(sys.prefix) / "Scripts" / "pytest.exe",  # Windows
            Path(sys.prefix) / "bin" / "pytest",  # Unix
            Path.cwd() / "venv" / "Scripts" / "pytest.exe",
            Path.cwd() / "venv" / "bin" / "pytest",
            Path.cwd() / ".venv" / "Scripts" / "pytest.exe",
            Path.cwd() / ".venv" / "bin" / "pytest",
        ]

        for venv_pytest in venv_paths:
            if venv_pytest.exists():
                return str(venv_pytest)

        # Default to pytest (will use PATH)
        return "pytest"

    async def get_test_summary(self, story_path: str) -> Dict[str, Any]:
        """
        Get summary of test execution.

        Args:
            story_path: Path to the story file

        Returns:
            Dictionary with test summary
        """
        try:
            story_dir = Path(story_path).parent
            test_files = self._discover_test_files(story_dir)

            results = await self._execute_tests(test_files, story_dir)

            summary = {
                "test_files": len(test_files),
                "passed": "PASSED" in results.get("stdout", ""),
                "success": results.get("success", False),
                "returncode": results.get("returncode", -1),
            }

            # Extract coverage if available
            if "coverage" in results:
                try:
                    coverage_totals = results["coverage"].get("totals", {})
                    summary["coverage"] = {
                        "percent": coverage_totals.get("percent_covered", 0),
                        "covered_lines": coverage_totals.get("covered_lines", 0),
                        "missing_lines": coverage_totals.get("missing_lines", 0),
                        "num_statements": coverage_totals.get("num_statements", 0),
                    }
                except Exception as e:
                    logger.warning(f"Could not extract coverage: {e}")

            return summary

        except Exception as e:
            logger.error(f"Error getting test summary: {e}")
            return {"error": str(e)}

    async def verify_test_coverage(self, story_path: str, min_coverage: float = 80.0) -> bool:
        """
        Verify test coverage meets minimum threshold.

        Args:
            story_path: Path to the story file
            min_coverage: Minimum coverage percentage required

        Returns:
            True if coverage meets threshold
        """
        try:
            summary = await self.get_test_summary(story_path)

            coverage = summary.get("coverage")
            if not coverage:
                logger.warning("No coverage data available")
                return False

            coverage_percent = coverage.get("percent", 0)

            if coverage_percent >= min_coverage:
                logger.info(f"Coverage {coverage_percent}% meets threshold {min_coverage}%")
                return True
            else:
                logger.error(f"Coverage {coverage_percent}% below threshold {min_coverage}%")
                return False

        except Exception as e:
            logger.error(f"Error verifying coverage: {e}")
            return False
