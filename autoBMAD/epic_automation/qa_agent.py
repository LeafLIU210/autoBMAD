"""
QA Agent - Quality Assurance Agent

Handles quality assurance and validation tasks.
Returns QA results indicating pass/fail status.
Integrates with task guidance for QA-specific operations.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Any
from enum import Enum
import re
import time

# Import SafeClaudeSDK wrapper
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

# Import Claude SDK types
try:
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
except ImportError:
    # For development without SDK installed
    query = None
    ClaudeAgentOptions = None
    ResultMessage = None

# Type annotations for QA tools
if TYPE_CHECKING:
    pass
else:
    try:
        from .qa_tools_integration import QAStatus  # type: ignore  # noqa: F401
        QA_TOOLS_AVAILABLE = True
    except ImportError:
        # Fallback classes for when qa_tools_integration is not available
        class QAStatus(Enum):
            """QA status enum with value attribute."""
            PASS = "PASS"
            FAIL = "FAIL"
            CONCERNS = "CONCERNS"
            WAIVED = "WAIVED"

        class QAAutomationWorkflow:
            """Fallback QA workflow when tools are not available."""
            def __init__(self, basedpyright_dir: str, fixtest_dir: str, timeout: int = 300, max_retries: int = 1):
                self.basedpyright_dir = basedpyright_dir
                self.fixtest_dir = fixtest_dir
                self.timeout = timeout
                self.max_retries = max_retries

            async def run_qa_checks(self, source_dir: str, test_dir: str) -> dict[str, Any]:
                """Fallback implementation when QA tools are not available."""
                return {
                    'overall_status': QAStatus.WAIVED.value,  # type: ignore
                    'basedpyright': {'errors': 0, 'warnings': 0},
                    'fixtest': {'tests_failed': 0, 'tests_errors': 0},
                    'message': 'QA tools not available'
                }

        # QA_TOOLS_AVAILABLE already set to False by default

logger = logging.getLogger(__name__)


class QAAgent:
    """
    Simplified Quality Assurance agent for story validation.

    This agent delegates all story parsing and review operations to Claude SDK,
    providing a simplified interface for QA phase execution.
    """

    name: str = "QA Agent"

    def __init__(self) -> None:
        """Initialize QA agent."""
        logger.info(f"{self.name} initialized")

    async def execute(
        self,
        story_content: str,  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
        story_path: str = "",
        task_guidance: str | None = None,  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
        use_qa_tools: bool = True,  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
        source_dir: str = "src",  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
        test_dir: str = "tests",  # noqa: ARG002  # pyright: ignore[reportUnusedParameter]
    ) -> dict[str, str | bool | list[str]]:
        """
        Execute simplified QA phase - delegate all parsing and review to Claude SDK.

        Args:
            story_content: Raw markdown content of the story (not used directly)
            story_path: Path to the story file

        Returns:
            Dictionary with QA results based on AI-driven review
        """
        logger.info(f"{self.name} executing simplified QA phase")

        try:
            # Execute AI-driven QA review (handles all parsing internally)
            logger.info(f"{self.name} Starting QA review for: {story_path}")
            qa_review_success = await self._execute_qa_review(story_path)

            # If SDK review failed or was cancelled, use fallback QA review
            if not qa_review_success:
                logger.warning(f"{self.name} AI-driven QA review failed, using fallback review")
                fallback_result = await self._perform_fallback_qa_review(story_path, source_dir, test_dir)
                return fallback_result

            logger.info(f"{self.name} QA review completed successfully")

            # Check story status
            status_ready = await self._check_story_status(story_path)

            if not status_ready:
                # Collect QA gate files
                gate_paths = await self._collect_qa_gate_paths()

                # If no gate files found, use fallback review
                if not gate_paths:
                    logger.warning(f"{self.name} No QA gate files found, using fallback review")
                    fallback_result = await self._perform_fallback_qa_review(story_path, source_dir, test_dir)
                    return fallback_result

                # Create dev prompt for fixing
                dev_prompt = f"*review-qa {' '.join(gate_paths)} 根据qa gate文件执行修复"

                logger.info(f"{self.name} QA found issues, needs fixing")
                return {
                    'passed': False,
                    'needs_fix': True,
                    'gate_paths': gate_paths,
                    'dev_prompt': dev_prompt
                }
            else:
                # Status is Ready for Done, story completed
                logger.info(f"{self.name} QA PASSED - Ready for Done")
                return {
                    'passed': True,
                    'completed': True,
                    'needs_fix': False
                }

        except asyncio.CancelledError:
            logger.warning(f"{self.name} QA execution was cancelled, using fallback review")
            # Use fallback review for cancelled executions
            fallback_result = await self._perform_fallback_qa_review(story_path, source_dir, test_dir)
            fallback_result['cancelled'] = True
            return fallback_result
        except Exception as e:
            logger.error(f"{self.name} execution failed: {e}, using fallback review")
            # Use fallback review for any exceptions
            fallback_result = await self._perform_fallback_qa_review(story_path, source_dir, test_dir)
            fallback_result['error'] = str(e)
            return fallback_result



    # ========== SIMPLIFIED: Removed _apply_qa_guidance (奥卡姆剃刀原则) ==========
    # Original method removed - AI-driven QA review replaces this complex logic
    # The new _execute_qa_review() method handles all guidance through Claude SDK

    # ========== SIMPLIFIED: Removed _run_qa_tools (奥卡姆剃刀原则) ==========
    # Original method removed - BasedPyright and Fixtest tools replaced by AI-driven QA review
    # The new _execute_qa_review() method uses Claude SDK for intelligent quality assessment

    # ========== SIMPLIFIED: Removed _calculate_qa_result (奥卡姆剃刀原则) ==========
    # Original method removed - Complex calculation replaced by AI-driven decision
    # The new _execute_qa_review() and _check_story_status() methods handle all decisions through AI

    async def generate_qa_report(self, qa_result: dict[str, object]) -> str:
        """
        Generate QA report from results.

        Args:
            qa_result: QA result dictionary

        Returns:
            Formatted QA report string
        """
        report_lines = [
            "=" * 60,
            "QA REPORT",
            "=" * 60,
            f"Status: {'PASS' if qa_result.get('passed', False) else 'FAIL'}",
            f"Score: {qa_result.get('score', 0)}/100",
            f"Completeness: {qa_result.get('completeness', 0.0):.0%}",
            ""
        ]

        if qa_result.get('failures'):
            report_lines.append("FAILURES:")
            failures = qa_result['failures']
            if isinstance(failures, list):
                for failure in failures:  # pyright: ignore[reportUnknownVariableType]
                    report_lines.append(f"  - {failure}")
            report_lines.append("")

        if qa_result.get('warnings'):
            report_lines.append("WARNINGS:")
            warnings = qa_result['warnings']
            if isinstance(warnings, list):
                for warning in warnings:  # pyright: ignore[reportUnknownVariableType]
                    report_lines.append(f"  - {warning}")
            report_lines.append("")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    # ========== SIMPLIFIED: Removed _run_test_suite (奥卡姆剃刀原则) ==========
    # Original method removed - Pytest execution replaced by AI-driven QA review
    # The new _execute_qa_review() method uses Claude SDK for comprehensive testing

    # ========== SIMPLIFIED: Removed _update_qa_status (奥卡姆剃刀原则) ==========
    # Original method removed - Status updates handled by Claude SDK in _execute_qa_review()
    # The new _check_story_status() method reads status, AI updates it

    # ========== NEW: AI-Driven QA Methods (奥卡姆剃刀原则 - 极简方案) ==========

    async def _execute_qa_review(self, story_path: str) -> bool:
        """
        Execute AI-driven QA review using safe SDK wrapper.

        Args:
            story_path: Path to the story file

        Returns:
            True if review completed successfully
        """
        if not story_path:
            logger.warning("No story path provided for QA review")
            return True

        try:
            logger.info(f"Executing AI-driven QA review for: {story_path}")

            # Build the prompt for Claude SDK
            prompt = (
                f'@.bmad-core\\agents\\qa.md *review {story_path} '
                '审查故事文档，更新故事文档status。'
                f'*gate {story_path} 创建qa gate文件到 @docs\\gates\\'
            )

            # Create ClaudeAgentOptions for SDK
            if ClaudeAgentOptions is None:
                logger.warning("Claude Agent SDK not available - QA review skipped")
                return True

            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd())
            )

            # Use SafeClaudeSDK with valid options
            sdk = SafeClaudeSDK(prompt, options, timeout=1200.0)
            return await sdk.execute()

        except Exception as e:
            logger.error(f"Failed to execute QA review: {e}")
            return False

    async def _perform_fallback_qa_review(self, story_path: str, source_dir: str = "src", test_dir: str = "tests") -> dict[str, Any]:
        """
        Perform fallback QA review when SDK review fails or is unavailable.
        
        Args:
            story_path: Path to the story file
            source_dir: Source code directory
            test_dir: Test directory
            
        Returns:
            Dictionary with QA results
        """
        logger.info(f"{self.name} Performing fallback QA review for: {story_path}")
        
        try:
            # Run basic QA checks
            checks = [
                self._check_code_quality_basics(story_path, source_dir),
                self._check_test_files_exist(story_path, test_dir),
                self._check_documentation_updated(story_path)
            ]
            
            # Execute all checks concurrently
            results = await asyncio.gather(*checks, return_exceptions=True)
            
            # Process results
            passed_checks = 0
            total_checks = len(results)
            failure_reasons = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failure_reasons.append(f"Check {i+1} failed with error: {result}")
                elif isinstance(result, dict) and result.get('passed', False):
                    passed_checks += 1
                else:
                    failure_reasons.append(f"Check {i+1} failed")
            
            # Determine overall result
            overall_passed = passed_checks == total_checks
            needs_fix = not overall_passed
            
            logger.info(f"{self.name} Fallback QA review completed: {passed_checks}/{total_checks} checks passed")
            
            return {
                'passed': overall_passed,
                'needs_fix': needs_fix,
                'gate_paths': [],
                'dev_prompt': f'*review-qa 根据基础QA检查结果执行修复: {", ".join(failure_reasons)}' if failure_reasons else '',
                'fallback_review': True,
                'checks_passed': passed_checks,
                'total_checks': total_checks
            }
            
        except Exception as e:
            logger.error(f"{self.name} Fallback QA review failed: {e}")
            return {
                'passed': False,
                'needs_fix': True,
                'gate_paths': [],
                'dev_prompt': f'*review-qa 基础QA检查失败: {str(e)}',
                'fallback_review': True,
                'error': str(e)
            }

    async def _check_code_quality_basics(self, story_path: str, source_dir: str = "src") -> dict[str, Any]:
        """
        Check basic code quality indicators.
        
        Args:
            story_path: Path to the story file
            source_dir: Source code directory
            
        Returns:
            Dictionary with check results
        """
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                return {'passed': False, 'reason': f'Source directory {source_dir} does not exist'}
            
            # Check for Python files
            python_files = list(source_path.rglob("*.py"))
            if not python_files:
                return {'passed': False, 'reason': 'No Python files found in source directory'}
            
            # Basic checks on Python files
            issues = []
            total_files = len(python_files)
            files_with_docstrings = 0
            files_with_type_hints = 0
            
            for py_file in python_files:
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Check for docstrings
                    if '"""' in content or "'''" in content:
                        files_with_docstrings += 1
                    
                    # Check for type hints (basic)
                    if '-> ' in content or ': ' in content:
                        files_with_type_hints += 1
                        
                    # Check for very long lines (basic quality check)
                    long_lines = [line for line in content.split('\n') if len(line) > 120]
                    if long_lines:
                        issues.append(f"{py_file.name} has {len(long_lines)} long lines")
                        
                except Exception as e:
                    issues.append(f"Could not read {py_file.name}: {e}")
            
            # Calculate quality score
            docstring_ratio = files_with_docstrings / total_files if total_files > 0 else 0
            type_hint_ratio = files_with_type_hints / total_files if total_files > 0 else 0
            
            # Basic quality threshold: at least 50% of files should have docstrings
            passed = docstring_ratio >= 0.5 and len(issues) < total_files * 0.3
            
            return {
                'passed': passed,
                'total_files': total_files,
                'files_with_docstrings': files_with_docstrings,
                'files_with_type_hints': files_with_type_hints,
                'docstring_ratio': docstring_ratio,
                'type_hint_ratio': type_hint_ratio,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Code quality check failed: {e}")
            return {'passed': False, 'reason': f'Code quality check error: {e}'}

    async def _check_test_files_exist(self, story_path: str, test_dir: str = "tests") -> dict[str, Any]:
        """
        Check if test files exist and are properly structured.
        
        Args:
            story_path: Path to the story file
            test_dir: Test directory
            
        Returns:
            Dictionary with check results
        """
        try:
            test_path = Path(test_dir)
            if not test_path.exists():
                return {'passed': False, 'reason': f'Test directory {test_dir} does not exist'}
            
            # Look for test files
            test_files = list(test_path.rglob("test_*.py")) + list(test_path.rglob("*_test.py"))
            
            if not test_files:
                return {'passed': False, 'reason': 'No test files found', 'test_count': 0}
            
            # Basic check: ensure test files have test functions
            valid_test_files = 0
            total_test_functions = 0
            
            for test_file in test_files:
                try:
                    content = test_file.read_text(encoding='utf-8')
                    # Count test functions (basic pattern matching)
                    test_functions = re.findall(r'^def test_', content, re.MULTILINE)
                    if test_functions:
                        valid_test_files += 1
                        total_test_functions += len(test_functions)
                except Exception as e:
                    logger.debug(f"Could not read test file {test_file}: {e}")
            
            passed = valid_test_files > 0 and total_test_functions > 0
            
            return {
                'passed': passed,
                'test_files_found': len(test_files),
                'valid_test_files': valid_test_files,
                'total_test_functions': total_test_functions,
                'test_count': total_test_functions
            }
            
        except Exception as e:
            logger.error(f"Test files check failed: {e}")
            return {'passed': False, 'reason': f'Test files check error: {e}', 'test_count': 0}

    async def _check_documentation_updated(self, story_path: str) -> dict[str, Any]:
        """
        Check if documentation has been updated recently.
        
        Args:
            story_path: Path to the story file
            
        Returns:
            Dictionary with check results
        """
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                return {'passed': False, 'reason': 'Story file does not exist'}
            
            # Check if story file has been modified recently (within last 7 days)
            story_mtime = story_file.stat().st_mtime
            current_time = time.time()
            time_diff_days = (current_time - story_mtime) / (24 * 3600)
            
            # Check for documentation content
            content = story_file.read_text(encoding='utf-8')
            
            # Basic documentation checks
            has_implementation = '## Implementation' in content or '# Implementation' in content
            has_status = '**Status**:' in content or '## Status' in content
            has_acceptance = '## Acceptance Criteria' in content or '# Acceptance Criteria' in content
            
            # Consider documentation updated if it has key sections and was modified recently
            documentation_score = sum([has_implementation, has_status, has_acceptance])
            recently_updated = time_diff_days < 7
            
            passed = documentation_score >= 2 and recently_updated
            
            return {
                'passed': passed,
                'last_updated': time_diff_days,
                'documentation_score': documentation_score,
                'has_implementation': has_implementation,
                'has_status': has_status,
                'has_acceptance': has_acceptance,
                'recently_updated': recently_updated
            }
            
        except Exception as e:
            logger.error(f"Documentation check failed: {e}")
            return {'passed': False, 'reason': f'Documentation check error: {e}'}

    async def _check_story_status(self, story_path: str) -> bool:
        """
        Check if story status is Ready for Done.

        Args:
            story_path: Path to the story file

        Returns:
            True if status is Ready for Done
        """
        if not story_path:
            return False

        try:
            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"Story file not found: {story_path}")
                return False

            # Read story content
            with open(story_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for Ready for Done status
            status_pattern = r'\*\*Status\*\*:\s*(Ready for Done|Ready_for_Done)'
            if re.search(status_pattern, content):
                logger.info(f"Story status is Ready for Done: {story_path}")
                return True

            # Also check for alternative patterns
            status_section = re.search(r'## Status\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if status_section:
                status_text = status_section.group(1).strip()
                if 'Ready for Done' in status_text:
                    logger.info(f"Story status is Ready for Done (section): {story_path}")
                    return True

            logger.info(f"Story status not Ready for Done: {story_path}")
            return False

        except Exception as e:
            logger.error(f"Failed to check story status: {e}")
            return False

    async def _collect_qa_gate_paths(self) -> list[str]:
        """
        Collect all QA gate file paths from docs/qa/gates/.

        Returns:
            List of gate file paths
        """
        try:
            gates_dir = Path("docs/qa/gates")
            # 自动创建目录（如果不存在）
            gates_dir.mkdir(parents=True, exist_ok=True)

            # Find all markdown files in gates directory
            gate_files = list(gates_dir.glob("*.md"))
            gate_paths = [str(f) for f in gate_files]

            logger.info(f"Collected {len(gate_paths)} QA gate files from {gates_dir}")
            return gate_paths

        except Exception as e:
            logger.error(f"Failed to collect QA gate paths: {e}")
            return []
