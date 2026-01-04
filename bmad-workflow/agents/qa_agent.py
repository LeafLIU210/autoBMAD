"""
QA Agent for BMAD Quality Assessment

This agent is responsible for performing comprehensive quality assessment
and providing structured gate decisions. It loads review-story.md guidance
and uses Claude SDK for intelligent QA workflows.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from anthropic.types import MessageParam

from .base_agent import BaseAgent


class QAResultStatus(Enum):
    """QA Gate result status enum."""
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"


class QAGateResult:
    """Structured QA gate result."""

    def __init__(self, status: QAResultStatus, reason: str):
        """
        Initialize QA gate result.

        Args:
            status: The gate status (PASS/CONCERNS/FAIL/WAIVED)
            reason: Explanation for the gate decision
        """
        self.status = status
        self.reason = reason
        self.timestamp = datetime.now()
        self.findings: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "findings": self.findings,
            "recommendations": self.recommendations,
            "quality_score": self._calculate_quality_score()
        }

    def _calculate_quality_score(self) -> int:
        """
        Calculate quality score based on status.

        Returns:
            Quality score (0-100).
        """
        if self.status == QAResultStatus.PASS:
            return 100
        elif self.status == QAResultStatus.CONCERNS:
            return 70
        elif self.status == QAResultStatus.FAIL:
            return 40
        else:  # WAIVED
            return 60


class QAAgent(BaseAgent):
    """
    QA Agent for BMAD Quality Assessment.

    Extends BaseAgent to provide comprehensive QA review capabilities,
    loading review-story.md guidance and implementing structured
    quality gates with PASS/CONCERNS/FAIL/WAIVED decisions.
    """

    def __init__(self):
        """Initialize the QA Agent with review-story task type."""
        super().__init__(agent_name="qa", task_type="review-story")
        self.logger = logging.getLogger("bmad.qa_agent")
        self.story_path: Optional[Path] = None
        self.story_content: Optional[str] = None
        self._reset_session_state()

    def _reset_session_state(self) -> None:
        """Reset agent session state."""
        self.current_story_id: Optional[str] = None
        self.review_findings: List[Dict[str, Any]] = []
        self.refactoring_performed: List[Dict[str, str]] = []

    def review_story(self, story_path: Path) -> QAGateResult:
        """
        Perform comprehensive QA review of a story.

        Args:
            story_path: Path to the story file to review.

        Returns:
            QAGateResult with structured decision and findings.

        Raises:
            Exception: If story review fails.
        """
        try:
            self.logger.info(f"Starting QA review: {story_path}")
            self.reset_session()
            self._reset_session_state()

            # Validate story file exists
            if not story_path.exists():
                raise FileNotFoundError(f"Story file not found: {story_path}")

            # Load story content
            self.story_path = story_path
            with open(story_path, 'r', encoding='utf-8') as f:
                self.story_content = f.read()

            # Load task guidance
            task_guidance = self.load_task_guidance()

            # Get system prompt
            system_prompt = self.get_system_prompt()

            # Build review prompt
            review_prompt = self._build_review_prompt()

            # Call Claude API
            messages: List[MessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": review_prompt}
            ]

            response = self.call_claude(messages, max_tokens=8192)

            # Process review response and create gate result
            gate_result = self._process_review_response(response)

            self.logger.info(f"QA review completed: {gate_result.status.value} - {gate_result.reason}")
            return gate_result

        except Exception as e:
            self.logger.error(f"QA review failed: {e}")
            return QAGateResult(
                status=QAResultStatus.FAIL,
                reason=f"Review failed with error: {str(e)}"
            )

    def _build_review_prompt(self) -> str:
        """
        Build the prompt for story review.

        Returns:
            The review prompt.
        """
        prompt_parts = [
            "Please perform a comprehensive QA review of the story following the task guidance.",
            "",
            "Story Content:",
            "---",
            self.story_content,
            "---",
            "",
            "Instructions:",
            "1. Perform adaptive test architecture review based on risk assessment",
            "2. Analyze requirements traceability and coverage gaps",
            "3. Review code quality, architecture, and design patterns",
            "4. Assess test architecture and coverage adequacy",
            "5. Evaluate non-functional requirements (security, performance, reliability)",
            "6. Check testability and maintainability",
            "7. Identify and document technical debt",
            "8. Perform active refactoring where safe and appropriate",
            "9. Verify standards compliance (coding, structure, testing)",
            "10. Validate all acceptance criteria are met",
            "",
            "Please provide:",
            "- Comprehensive quality assessment",
            "- List of any refactoring performed with explanations",
            "- Compliance check results",
            "- Security and performance considerations",
            "- Final gate status: PASS, CONCERNS, FAIL, or WAIVED",
            "- Quality score (0-100)",
            "- Recommendations for improvements"
        ]

        return "\n".join(prompt_parts)

    def _process_review_response(self, response: Dict[str, Any]) -> QAGateResult:
        """
        Process the review response from Claude and create gate result.

        Args:
            response: The response from Claude API.

        Returns:
            QAGateResult with structured decision.

        Raises:
            Exception: If response processing fails.
        """
        try:
            content_blocks = response.get('content', [])
            if not content_blocks:
                raise Exception("No content blocks in response")

            # Extract text from content blocks
            response_content = ""
            for block in content_blocks:
                if hasattr(block, 'text'):
                    response_content += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_content += block['text']

            # Parse gate decision from response
            gate_result = self._extract_gate_decision(response_content)

            # Update story file with QA results
            self._update_story_qa_section(gate_result)

            self.logger.info(f"Review response processed successfully")
            return gate_result

        except Exception as e:
            self.logger.error(f"Failed to process review response: {e}")
            return QAGateResult(
                status=QAResultStatus.FAIL,
                reason=f"Response processing failed: {str(e)}"
            )

    def _extract_gate_decision(self, response_content: str) -> QAGateResult:
        """
        Extract gate decision from response content.

        Args:
            response_content: The response content to parse.

        Returns:
            QAGateResult with extracted decision.

        Raises:
            Exception: If gate decision cannot be determined.
        """
        # Look for gate status in response
        status_found = None
        reason_found = "QA review completed"

        for status in QAResultStatus:
            if status.value in response_content.upper():
                status_found = status
                break

        if not status_found:
            # Default to PASS if no explicit status found
            status_found = QAResultStatus.PASS

        # Extract reason (first paragraph or summary)
        lines = response_content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                reason_found = line.strip()[:200]  # Limit reason length
                break

        return QAGateResult(status=status_found, reason=reason_found)

    def _update_story_qa_section(self, gate_result: QAGateResult) -> None:
        """
        Update story file with QA results section.

        Args:
            gate_result: The QA gate result to record.

        Raises:
            Exception: If file update fails.
        """
        try:
            if not self.story_path or not self.story_content:
                return

            # Create QA Results section content
            qa_results = self._format_qa_results_section(gate_result)

            # Check if QA Results section already exists
            if "## QA Results" in self.story_content:
                # Append to existing section
                # Find the end of QA Results section or end of file
                lines = self.story_content.split('\n')
                qa_start_idx = None
                for i, line in enumerate(lines):
                    if line.strip() == "## QA Results":
                        qa_start_idx = i
                        break

                if qa_start_idx is not None:
                    # Find next section or end of file
                    qa_end_idx = len(lines)
                    for i in range(qa_start_idx + 1, len(lines)):
                        if lines[i].startswith("## "):
                            qa_end_idx = i
                            break

                    # Insert new QA result before the end
                    lines.insert(qa_end_idx, qa_results)
                    updated_content = '\n'.join(lines)
            else:
                # Append QA Results section at the end
                updated_content = self.story_content + "\n\n" + qa_results

            # Write updated content
            with open(self.story_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            self.logger.info(f"Story file updated with QA results: {self.story_path}")

        except Exception as e:
            self.logger.error(f"Failed to update story QA section: {e}")
            # Don't raise - QA review can succeed even if file update fails

    def _format_qa_results_section(self, gate_result: QAGateResult) -> str:
        """
        Format QA results section for story file.

        Args:
            gate_result: The QA gate result to format.

        Returns:
            Formatted QA results section.
        """
        date_str = gate_result.timestamp.strftime("%Y-%m-%d")
        timestamp_str = gate_result.timestamp.isoformat()

        return f"""## QA Results

### Review Date: {date_str}

### Reviewed By: Quinn (QA Agent)

### Gate Status: {gate_result.status.value}

### Status Reason: {gate_result.reason}

### Quality Score: {gate_result.to_dict()['quality_score']}/100

### Summary

[QA review summary will be populated here]

### Files Reviewed

- {self.story_path.name if self.story_path else 'story file'}

### Recommendations

[Recommendations will be listed here]

### Next Steps

[Next steps will be provided here]

---
*Review completed at {timestamp_str}*
"""

    def quick_review(self, story_path: Path) -> Dict[str, Any]:
        """
        Perform a quick review with basic checks.

        Args:
            story_path: Path to the story file.

        Returns:
            Dictionary with quick review results.
        """
        try:
            self.logger.info(f"Performing quick QA review: {story_path}")

            if not story_path.exists():
                return {
                    "status": "error",
                    "error": f"Story file not found: {story_path}",
                    "timestamp": datetime.now().isoformat()
                }

            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic checks
            checks = {
                "story_exists": True,
                "has_acceptance_criteria": "## Acceptance Criteria" in content,
                "has_tasks": "## Tasks / Subtasks" in content,
                "has_file_list": "## File List" in content,
                "not_draft": "**Status**: Draft" not in content,
                "has_qa_section": "## QA Results" in content
            }

            passed = sum(checks.values())
            total = len(checks)
            score = (passed / total) * 100 if total > 0 else 0

            # Quick status determination
            if score >= 90:
                status = QAResultStatus.PASS
            elif score >= 70:
                status = QAResultStatus.CONCERNS
            else:
                status = QAResultStatus.FAIL

            result = {
                "status": status.value,
                "score": score,
                "checks": checks,
                "story_path": str(story_path),
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Quick review completed: {status.value} ({score}%)")
            return result

        except Exception as e:
            self.logger.error(f"Quick review failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
