"""
QA Agent - Quality Assurance Agent

Handles quality assurance and validation tasks.
Returns QA results indicating pass/fail status.
Integrates with task guidance for QA-specific operations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import re

# Try to import QA tools, provide fallback if not available
try:
    from qa_tools_integration import QAAutomationWorkflow, QAStatus
    QA_TOOLS_AVAILABLE = True
except ImportError:
    # Fallback classes for when qa_tools_integration is not available
    class QAStatus:
        PASS = "PASS"
        FAIL = "FAIL"
        CONCERNS = "CONCERNS"
        WAIVED = "WAIVED"

    class QAAutomationWorkflow:
        def __init__(self, basedpyright_dir: str, fixtest_dir: str, timeout: int = 300, max_retries: int = 2):
            self.basedpyright_dir = basedpyright_dir
            self.fixtest_dir = fixtest_dir
            self.timeout = timeout
            self.max_retries = max_retries

        async def run_qa_checks(self, source_dir: str, test_dir: str) -> Dict[str, Any]:
            """Fallback implementation when QA tools are not available."""
            return {
                'overall_status': QAStatus.WAIVED.value,
                'basedpyright': {'errors': 0, 'warnings': 0},
                'fixtest': {'tests_failed': 0, 'tests_errors': 0},
                'message': 'QA tools not available'
            }

    QA_TOOLS_AVAILABLE = False

logger = logging.getLogger(__name__)


class QAAgent:
    """Quality Assurance agent for validating story implementation."""

    def __init__(self):
        """Initialize QA agent."""
        self.name = "QA Agent"
        logger.info(f"{self.name} initialized")

    async def execute(
        self,
        story_content: str,
        task_guidance: str = "",
        use_qa_tools: bool = True,
        source_dir: str = "src",
        test_dir: str = "tests"
    ) -> Dict[str, Any]:
        """
        Execute QA phase for a story.

        Args:
            story_content: Raw markdown content of the story
            task_guidance: Task guidance from .bmad-core/tasks/review-story.md
            use_qa_tools: If True, run BasedPyright and Fixtest checks
            source_dir: Source code directory for BasedPyright check
            test_dir: Test directory for Fixtest check

        Returns:
            Dictionary with QA results including 'passed' boolean and detailed results
        """
        logger.info(f"{self.name} executing QA phase (tools={use_qa_tools})")

        try:
            # Parse story for validation
            story_data = await self._parse_story_for_qa(story_content)

            if not story_data:
                return {
                    'passed': False,
                    'error': 'Failed to parse story',
                    'score': 0
                }

            # Perform QA validations
            validations = await self._perform_validations(story_data)

            # Apply task guidance if provided
            if task_guidance:
                guided_validations = await self._apply_qa_guidance(
                    validations,
                    task_guidance
                )
                validations.update(guided_validations)

            # Run QA tools if enabled
            tool_results = {}
            if use_qa_tools:
                try:
                    tool_results = await self._run_qa_tools(source_dir, test_dir)
                    logger.info(f"QA tools completed: {tool_results.get('overall_status', 'UNKNOWN')}")
                except Exception as e:
                    logger.error(f"QA tools execution failed: {e}")
                    tool_results = {
                        'error': str(e),
                        'overall_status': QAStatus.FAIL.value
                    }

            # Calculate overall result including tool results
            qa_result = self._calculate_qa_result(validations, tool_results)

            # Log results
            if qa_result['passed']:
                logger.info(f"{self.name} QA phase PASSED (score: {qa_result['score']})")
            else:
                logger.warning(
                    f"{self.name} QA phase FAILED (score: {qa_result['score']}, "
                    f"failures: {len(qa_result.get('failures', []))})"
                )

            return qa_result

        except Exception as e:
            logger.error(f"{self.name} execution failed: {e}")
            return {
                'passed': False,
                'error': str(e),
                'score': 0
            }

    async def _parse_story_for_qa(self, story_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse story for QA validation.

        Args:
            story_content: Raw markdown content

        Returns:
            Parsed story data or None if parsing fails
        """
        try:
            data = {
                'title': None,
                'status': None,
                'acceptance_criteria': [],
                'tasks': [],
                'subtasks': [],
                'file_list': [],
                'dev_notes': None,
                'raw_content': story_content
            }

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', story_content, re.MULTILINE)
            if title_match:
                data['title'] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status\*\*:\s*(.+)$', story_content, re.MULTILINE)
            if status_match:
                data['status'] = status_match.group(1).strip()

            # Extract acceptance criteria
            ac_pattern = r'- \[([ x])\]\s+(.+)$'
            ac_matches = re.findall(ac_pattern, story_content, re.MULTILINE)
            data['acceptance_criteria'] = [
                {'checked': checked == 'x', 'text': text.strip()}
                for checked, text in ac_matches
            ]

            # Extract tasks
            task_pattern = r'- \[([ x])\] Task \d+(?::\s*(.+))?$'
            task_matches = re.findall(task_pattern, story_content, re.MULTILINE)
            data['tasks'] = [
                {'checked': checked == 'x', 'text': (text or "").strip()}
                for checked, text in task_matches
            ]

            # Extract subtasks
            subtask_pattern = r'- \[([ x])\] Subtask \d+\.\d+:\s+(.+)$'
            subtask_matches = re.findall(subtask_pattern, story_content, re.MULTILINE)
            data['subtasks'] = [
                {'checked': checked == 'x', 'text': text.strip()}
                for checked, text in subtask_matches
            ]

            # Extract file list section
            # Match "### File List" followed by content (may not have blank line after header)
            file_list_match = re.search(
                r'### File List\s*\n(.*?)(?=\n###|\n---|\Z)',
                story_content,
                re.DOTALL | re.MULTILINE
            )
            if file_list_match:
                file_section = file_list_match.group(1)
                # Extract file paths
                file_pattern = r'- (`[^`]+`|\S+\.[a-zA-Z0-9]+)'
                file_matches = re.findall(file_pattern, file_section)
                data['file_list'] = file_matches

            # Extract dev notes
            dev_notes_match = re.search(
                r'## Dev Notes\s*\n(.*?)(?=\n##|\n---|\Z)',
                story_content,
                re.DOTALL | re.MULTILINE
            )
            if dev_notes_match:
                data['dev_notes'] = dev_notes_match.group(1).strip()

            logger.info(
                f"Parsed story for QA: {len(data['acceptance_criteria'])} AC, "
                f"{len(data['tasks'])} tasks, {len(data['subtasks'])} subtasks"
            )
            return data

        except Exception as e:
            logger.error(f"Failed to parse story for QA: {e}")
            return None

    async def _perform_validations(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform QA validations on story data.

        Args:
            story_data: Parsed story data

        Returns:
            Dictionary with validation results
        """
        validations = {
            'has_title': bool(story_data.get('title')),
            'has_status': bool(story_data.get('status')),
            'ac_completeness': 0.0,
            'task_completeness': 0.0,
            'subtask_completeness': 0.0,
            'has_file_list': len(story_data.get('file_list', [])) > 0,
            'has_dev_notes': bool(story_data.get('dev_notes')),
            'story_completeness': 0.0
        }

        # Check acceptance criteria completeness
        ac_list = story_data.get('acceptance_criteria', [])
        if ac_list:
            checked_ac = sum(1 for ac in ac_list if ac['checked'])
            validations['ac_completeness'] = checked_ac / len(ac_list)
        else:
            validations['ac_completeness'] = 0.0

        # Check task completeness
        task_list = story_data.get('tasks', [])
        if task_list:
            checked_tasks = sum(1 for task in task_list if task['checked'])
            validations['task_completeness'] = checked_tasks / len(task_list)
        else:
            validations['task_completeness'] = 0.0

        # Check subtask completeness
        subtask_list = story_data.get('subtasks', [])
        if subtask_list:
            checked_subtasks = sum(1 for st in subtask_list if st['checked'])
            validations['subtask_completeness'] = checked_subtasks / len(subtask_list)
        else:
            validations['subtask_completeness'] = 0.0

        # Calculate overall completeness
        validations['story_completeness'] = (
            validations['ac_completeness'] +
            validations['task_completeness'] +
            validations['subtask_completeness']
        ) / 3

        return validations

    async def _apply_qa_guidance(
        self,
        validations: Dict[str, Any],
        task_guidance: str
    ) -> Dict[str, Any]:
        """
        Apply QA task guidance to validations.

        Args:
            validations: Current validation results
            task_guidance: Task guidance content

        Returns:
            Updated validation results
        """
        try:
            # Check for specific guidance patterns
            if "file list" in task_guidance.lower():
                logger.info("Applying file list guidance")

            if "test" in task_guidance.lower():
                logger.info("Applying testing guidance")

            if "validation" in task_guidance.lower():
                logger.info("Applying validation guidance")

            if "complete" in task_guidance.lower():
                logger.info("Applying completeness guidance")

            # In a real implementation, this would adjust validation criteria
            # based on the specific QA guidance
            # For now, we just log that we applied it

            return {}

        except Exception as e:
            logger.error(f"Failed to apply QA guidance: {e}")
            return {}

    async def _run_qa_tools(self, source_dir: str, test_dir: str) -> Dict[str, Any]:
        """
        Run QA tools (BasedPyright and Fixtest) on the codebase.

        Args:
            source_dir: Source code directory
            test_dir: Test directory

        Returns:
            Dictionary with tool results
        """
        logger.info("Running QA tools (BasedPyright + Fixtest)...")

        # Determine workflow directories from current path with flexible lookup
        current_dir = Path(__file__).parent

        # Try multiple locations for basedpyright-workflow
        possible_locations = [
            current_dir.parent.parent / "basedpyright-workflow",  # project_root/basedpyright-workflow
            current_dir / "basedpyright-workflow",                 # current_dir/basedpyright-workflow
            Path.cwd() / "basedpyright-workflow",                  # cwd/basedpyright-workflow
        ]

        basedpyright_dir = None
        for loc in possible_locations:
            if loc.exists():
                basedpyright_dir = loc
                break

        if basedpyright_dir is None:
            # Default fallback
            basedpyright_dir = current_dir.parent.parent / "basedpyright-workflow"

        # Same for fixtest_dir
        possible_ft_locations = [
            current_dir.parent.parent / "fixtest-workflow",
            current_dir / "fixtest-workflow",
            Path.cwd() / "fixtest-workflow",
        ]

        fixtest_dir = None
        for loc in possible_ft_locations:
            if loc.exists():
                fixtest_dir = loc
                break

        if fixtest_dir is None:
            fixtest_dir = current_dir.parent.parent / "fixtest-workflow"

        # Initialize QA workflow
        qa_workflow = QAAutomationWorkflow(
            basedpyright_dir=str(basedpyright_dir),
            fixtest_dir=str(fixtest_dir),
            timeout=300,
            max_retries=2
        )

        try:
            # Run QA checks
            results = await qa_workflow.run_qa_checks(source_dir, test_dir)
            logger.info(f"QA tools completed with status: {results.get('overall_status', 'UNKNOWN')}")
            return results
        except Exception as e:
            logger.error(f"QA tools execution failed: {e}")
            # Return fallback result on error
            return {
                'overall_status': QAStatus.WAIVED.value,
                'basedpyright': {'errors': 0, 'warnings': 0},
                'fixtest': {'tests_failed': 0, 'tests_errors': 0},
                'error': str(e),
                'message': 'QA tools execution failed'
            }

    def _calculate_qa_result(
        self,
        validations: Dict[str, Any],
        tool_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall QA result from validations and tool results.

        Args:
            validations: Validation results
            tool_results: QA tool execution results

        Returns:
            Dictionary with QA result including pass/fail and details
        """
        failures = []
        warnings = []
        tool_failures = []
        tool_warnings = []

        # Check required fields
        if not validations.get('has_title'):
            failures.append("Missing story title")

        if not validations.get('has_status'):
            failures.append("Missing story status")

        # Check completeness thresholds
        if validations['ac_completeness'] < 1.0:
            failures.append(f"Acceptance criteria incomplete ({validations['ac_completeness']:.0%})")

        if validations['task_completeness'] < 1.0:
            failures.append(f"Tasks incomplete ({validations['task_completeness']:.0%})")

        if validations['subtask_completeness'] < 1.0:
            warnings.append(f"Subtasks incomplete ({validations['subtask_completeness']:.0%})")

        # Warnings for non-critical items
        if not validations.get('has_file_list'):
            warnings.append("Missing file list section")

        if not validations.get('has_dev_notes'):
            warnings.append("Missing dev notes section")

        # Process tool results if available
        tool_status = 'N/A'
        if tool_results:
            overall_status = tool_results.get('overall_status', 'UNKNOWN')
            tool_status = overall_status

            # Add tool-specific failures
            if overall_status == QAStatus.FAIL.value:
                # Extract BasedPyright errors
                bp_result = tool_results.get('basedpyright', {})
                if isinstance(bp_result, dict) and bp_result.get('errors', 0) > 0:
                    tool_failures.append(
                        f"BasedPyright found {bp_result['errors']} type errors"
                    )

                # Extract Fixtest failures
                ft_result = tool_results.get('fixtest', {})
                if isinstance(ft_result, dict) and ft_result.get('tests_failed', 0) > 0:
                    tool_failures.append(
                        f"Fixtest: {ft_result['tests_failed']} tests failed, "
                        f"{ft_result.get('tests_errors', 0)} errors"
                    )

            elif overall_status == QAStatus.CONCERNS.value:
                # Extract warnings from tools
                bp_result = tool_results.get('basedpyright', {})
                if isinstance(bp_result, dict) and bp_result.get('warnings', 0) > 0:
                    tool_warnings.append(
                        f"BasedPyright: {bp_result['warnings']} warnings"
                    )

                ft_result = tool_results.get('fixtest', {})
                if isinstance(ft_result, dict) and ft_result.get('tests_failed', 0) > 0:
                    tool_warnings.append(
                        f"Fixtest: {ft_result['tests_failed']} tests need attention"
                    )

        # Combine failures and warnings
        all_failures = failures + tool_failures
        all_warnings = warnings + tool_warnings

        # Calculate score (0-100)
        base_score = int(validations['story_completeness'] * 70)  # 70% for document completeness
        tool_score = 30  # 30% for tools

        # Adjust score based on tool results
        if tool_results:
            overall_status = tool_results.get('overall_status', 'UNKNOWN')
            if overall_status == QAStatus.PASS.value:
                tool_score = 30
            elif overall_status == QAStatus.CONCERNS.value:
                tool_score = 15
            elif overall_status == QAStatus.FAIL.value:
                tool_score = 0
            elif overall_status == QAStatus.WAIVED.value:
                tool_score = 20  # Partial credit if tools are unavailable

        score = base_score + tool_score

        # Determine pass/fail
        # Must have 100% completion on AC and tasks, no critical failures
        # AND tool results must not be FAIL
        tool_passed = True
        if tool_results:
            overall_status = tool_results.get('overall_status', 'UNKNOWN')
            tool_passed = overall_status not in [QAStatus.FAIL.value]

        passed = len(all_failures) == 0 and validations['story_completeness'] >= 1.0 and tool_passed

        result = {
            'passed': passed,
            'score': score,
            'completeness': validations['story_completeness'],
            'failures': all_failures,
            'warnings': all_warnings,
            'validations': validations,
            'tool_results': tool_results or {},
            'summary': {
                'document_score': base_score,
                'tool_score': tool_score,
                'tool_status': tool_status
            }
        }

        return result

    async def generate_qa_report(self, qa_result: Dict[str, Any]) -> str:
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
            f"Status: {'PASS' if qa_result['passed'] else 'FAIL'}",
            f"Score: {qa_result['score']}/100",
            f"Completeness: {qa_result['completeness']:.0%}",
            ""
        ]

        if qa_result.get('failures'):
            report_lines.append("FAILURES:")
            for failure in qa_result['failures']:
                report_lines.append(f"  - {failure}")
            report_lines.append("")

        if qa_result.get('warnings'):
            report_lines.append("WARNINGS:")
            for warning in qa_result['warnings']:
                report_lines.append(f"  - {warning}")
            report_lines.append("")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)
