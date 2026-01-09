"""
Prompt System for TDD-focused development.

This module provides TDD-specific prompts for:
- Test generation from acceptance criteria (RED phase)
- Implementation prompts for minimal code (GREEN phase)
- Refactoring prompts for code improvement (REFACTOR phase)
- Error handling prompts for debugging
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PromptSystem:
    """
    TDD-focused prompt generation system.

    Provides structured prompts for each phase of the TDD cycle:
    1. RED: Write failing test based on requirement
    2. GREEN: Write minimal code to pass test
    3. REFACTOR: Improve code while keeping tests green
    """

    def __init__(self) -> None:
        """Initialize the PromptSystem."""
        logger.info("PromptSystem initialized")

    def generate_test_prompt(
        self,
        requirement: str,
        acceptance_criteria: List[str],
        context: str = "",
    ) -> str:
        """
        Generate a test-first prompt (RED phase).

        Args:
            requirement: The requirement to test
            acceptance_criteria: List of acceptance criteria
            context: Additional context information

        Returns:
            Formatted prompt for test generation
        """
        prompt = f"""You are an expert TDD practitioner. Write failing tests FIRST (RED phase).

Requirement:
{requirement}

Acceptance Criteria:
"""

        for i, criteria in enumerate(acceptance_criteria, 1):
            prompt += f"{i}. {criteria}\n"

        if context:
            prompt += f"\nContext:\n{context}\n"

        prompt += """
Instructions:
1. Write comprehensive unit tests that FAIL initially
2. Tests should be specific and cover all acceptance criteria
3. Use pytest with descriptive test names
4. Include setup, execution, and assertion phases
5. Focus on behavior, not implementation
6. Write tests before writing any implementation code

Provide ONLY the test code, nothing else.
"""

        return prompt

    def generate_implementation_prompt(
        self,
        failing_test: str,
        requirement: str,
        context: str = "",
    ) -> str:
        """
        Generate minimal implementation prompt (GREEN phase).

        Args:
            failing_test: The failing test that needs to pass
            requirement: The requirement being implemented
            context: Additional context

        Returns:
            Formatted prompt for minimal implementation
        """
        prompt = f"""You are an expert TDD practitioner. Write MINIMAL code to pass the failing test (GREEN phase).

Requirement:
{requirement}

Failing Test:
```python
{failing_test}
```

Context:
{context}

Instructions:
1. Write the MINIMAL code needed to make the test pass
2. Do NOT over-engineer or add extra features
3. Focus on making the test green, not perfection
4. Follow the simplest solution that works
5. No refactoring yet - that's the next phase
6. Ensure the code is clean and readable

Provide ONLY the implementation code, nothing else.
"""

        return prompt

    def generate_refactor_prompt(
        self,
        passing_test: str,
        implementation: str,
        requirement: str,
        context: str = "",
    ) -> str:
        """
        Generate refactoring prompt (REFACTOR phase).

        Args:
            passing_test: The test that's currently passing
            implementation: Current implementation code
            requirement: The requirement
            context: Additional context

        Returns:
            Formatted prompt for refactoring
        """
        prompt = f"""You are an expert TDD practitioner. Refactor the code while keeping tests green (REFACTOR phase).

Requirement:
{requirement}

Passing Test:
```python
{passing_test}
```

Current Implementation:
```python
{implementation}
```

Context:
{context}

Instructions:
1. Improve the code structure WITHOUT changing behavior
2. Keep ALL tests green - they must continue to pass
3. Apply SOLID principles and clean code practices
4. Remove duplication, improve naming, enhance readability
5. Ensure maintainability and extensibility
6. Aim for >80% test coverage

Provide ONLY the refactored implementation code, nothing else.
"""

        return prompt

    def generate_error_debug_prompt(
        self,
        error_message: str,
        failing_test: str,
        current_implementation: str,
    ) -> str:
        """
        Generate error handling and debugging prompt.

        Args:
            error_message: The error message
            failing_test: The failing test
            current_implementation: Current implementation

        Returns:
            Formatted prompt for debugging
        """
        prompt = f"""You are an expert TDD practitioner. Debug and fix the failing test.

Error Message:
{error_message}

Failing Test:
```python
{failing_test}
```

Current Implementation:
```python
{current_implementation}
```

Instructions:
1. Analyze the error message carefully
2. Identify the root cause of the failure
3. Provide a minimal fix that makes the test pass
4. Explain the issue and the solution
5. Ensure the fix doesn't break other tests

Provide the corrected implementation code with a brief explanation.
"""

        return prompt

    def generate_requirement_to_test_prompt(
        self,
        requirement: str,
        acceptance_criteria: List[str],
    ) -> str:
        """
        Generate prompt to map requirements to test cases.

        Args:
            requirement: Single requirement
            acceptance_criteria: List of acceptance criteria

        Returns:
            Prompt for requirement-to-test mapping
        """
        prompt = f"""Map the following requirement to specific test cases.

Requirement:
{requirement}

Acceptance Criteria:
"""

        for i, criteria in enumerate(acceptance_criteria, 1):
            prompt += f"{i}. {criteria}\n"

        prompt += """
Instructions:
1. Create a detailed test plan mapping each acceptance criterion to specific test cases
2. Include positive and negative test scenarios
3. Consider edge cases and boundary conditions
4. Provide test descriptions, expected inputs, and expected outputs
5. Organize tests logically (unit, integration, edge cases)

Format:
For each test case:
- Test Name: [Descriptive name]
- Purpose: [What it's testing]
- Input: [Test input]
- Expected: [Expected output/behavior]
- Acceptance Criteria: [Which criteria it covers]
"""

        return prompt

    def generate_tdd_cycle_summary_prompt(
        self,
        requirements: List[str],
        acceptance_criteria: List[str],
        test_count: int,
        passed_tests: int,
        coverage_percent: float,
    ) -> str:
        """
        Generate summary prompt for TDD cycle completion.

        Args:
            requirements: List of requirements
            acceptance_criteria: List of acceptance criteria
            test_count: Total number of tests
            passed_tests: Number of passing tests
            coverage_percent: Test coverage percentage

        Returns:
            Prompt for TDD cycle summary
        """
        prompt = """Generate a comprehensive TDD cycle summary report.

Requirements Implemented:
"""

        for i, req in enumerate(requirements, 1):
            prompt += f"{i}. {req}\n"

        prompt += "\nAcceptance Criteria Coverage:\n"
        for i, ac in enumerate(acceptance_criteria, 1):
            prompt += f"{i}. {ac}\n"

        prompt += f"""
Test Results:
- Total Tests: {test_count}
- Passed Tests: {passed_tests}
- Failed Tests: {test_count - passed_tests}
- Coverage: {coverage_percent}%

Instructions:
1. Provide a summary of what was accomplished
2. Verify all acceptance criteria are met
3. Highlight any remaining work or issues
4. Confirm the TDD cycle is complete (RED → GREEN → REFACTOR)
5. Recommend next steps if any

Provide a concise summary report.
"""

        return prompt

    def get_red_green_refactor_sequence(
        self,
        requirement: str,
        acceptance_criteria: List[str],
        context: str = "",
    ) -> Dict[str, str]:
        """
        Get complete red-green-refactor prompt sequence.

        Args:
            requirement: The requirement to implement
            acceptance_criteria: List of acceptance criteria
            context: Additional context

        Returns:
            Dictionary with 'red', 'green', and 'refactor' prompts
        """
        return {
            "red": self.generate_test_prompt(
                requirement=requirement,
                acceptance_criteria=acceptance_criteria,
                context=context,
            ),
            "green": "",  # Filled after red phase
            "refactor": "",  # Filled after green phase
        }

    def complete_green_prompt(
        self,
        red_prompt: str,
        generated_test: str,
        requirement: str,
        context: str = "",
    ) -> str:
        """
        Complete the green phase prompt after test generation.

        Args:
            red_prompt: The original red prompt
            generated_test: The generated test code
            requirement: The requirement
            context: Additional context

        Returns:
            Green phase prompt
        """
        return self.generate_implementation_prompt(
            failing_test=generated_test,
            requirement=requirement,
            context=context,
        )

    def complete_refactor_prompt(
        self,
        green_prompt: str,
        generated_implementation: str,
        passing_test: str,
        requirement: str,
        context: str = "",
    ) -> str:
        """
        Complete the refactor phase prompt after implementation.

        Args:
            green_prompt: The original green prompt
            generated_implementation: The generated implementation
            passing_test: The passing test
            requirement: The requirement
            context: Additional context

        Returns:
            Refactor phase prompt
        """
        return self.generate_refactor_prompt(
            passing_test=passing_test,
            implementation=generated_implementation,
            requirement=requirement,
            context=context,
        )

    def generate_requirement_verification_prompt(
        self,
        requirement: str,
        source_code: str,
    ) -> str:
        """
        Generate a prompt for verifying if a requirement is implemented.

        Args:
            requirement: The requirement to verify
            source_code: Source code to analyze

        Returns:
            Formatted prompt for requirement verification
        """
        prompt = f"""You are a QA expert performing document-centric review.

Analyze the source code below to determine if the following requirement is implemented:

REQUIREMENT:
{requirement}

SOURCE CODE:
```
{source_code}
```

Instructions:
1. Trace each part of the requirement to the source code
2. Determine if the requirement is: Implemented / Partial / Missing / Unknown
3. Provide detailed findings for each component of the requirement
4. Focus on requirement traceability from document to code
5. Be specific about what is present and what is missing

Respond with ONLY one of these statuses at the beginning:
- "Implemented: " followed by explanation
- "Partial: " followed by explanation
- "Missing: " followed by explanation
- "Unknown: " followed by explanation
"""
        return prompt

    def generate_test_coverage_prompt(
        self,
        requirement: str,
        test_code: str,
    ) -> str:
        """
        Generate a prompt for assessing test coverage of a requirement.

        Args:
            requirement: The requirement to assess
            test_code: Test code to analyze

        Returns:
            Formatted prompt for test coverage assessment
        """
        prompt = f"""You are a QA expert assessing test coverage.

Analyze the test code below to determine test coverage for the requirement:

REQUIREMENT:
{requirement}

TEST CODE:
```
{test_code}
```

Instructions:
1. Identify all tests related to this requirement
2. Assess coverage as a percentage (0-100%)
3. Check if all acceptance criteria are tested
4. Identify any gaps in test coverage
5. Evaluate test quality and completeness

Respond with ONLY the coverage percentage (0-100%) followed by brief justification.
Example: "85% - Good coverage of main functionality but missing edge cases"
"""
        return prompt

    def generate_findings_prompt(
        self,
        requirement: str,
        acceptance_criteria: List[str],
        source_paths: List[str],
        test_paths: List[str],
    ) -> str:
        """
        Generate a prompt for detailed findings about requirement implementation.

        Args:
            requirement: The requirement
            acceptance_criteria: List of acceptance criteria
            source_paths: Source code file paths (as strings)
            test_paths: Test file paths (as strings)

        Returns:
            Formatted prompt for generating findings
        """
        paths_str = "\n".join([f"- {p}" for p in source_paths])
        tests_str = "\n".join([f"- {p}" for p in test_paths])
        
        prompt = f"""You are a QA expert generating detailed findings.

Generate detailed findings about the implementation of this requirement:

REQUIREMENT:
{requirement}

ACCEPTANCE CRITERIA:
"""
        for i, ac in enumerate(acceptance_criteria, 1):
            prompt += f"{i}. {ac}\n"

        prompt += f"""
SOURCE FILES:
{paths_str}

TEST FILES:
{tests_str}

Instructions:
1. Provide detailed findings about implementation quality
2. Identify specific gaps between requirement and implementation
3. Note any code quality issues
4. Highlight test coverage strengths and weaknesses
5. Provide actionable recommendations
6. Be specific and reference file locations when relevant

Format your response as a numbered list of findings, each on its own line.
Focus on actionable insights for developers.
"""
        return prompt

    def generate_gap_analysis_prompt(
        self,
        requirements: List[str],
        source_code: str,
    ) -> str:
        """
        Generate a prompt for gap analysis between requirements and implementation.

        Args:
            requirements: List of requirements
            source_code: Source code to analyze

        Returns:
            Formatted prompt for gap analysis
        """
        reqs_str = "\n".join([f"- {r}" for r in requirements])
        
        prompt = f"""You are a QA expert performing gap analysis.

Analyze the source code to identify gaps between requirements and implementation:

REQUIREMENTS:
{reqs_str}

SOURCE CODE:
```
{source_code}
```

Instructions:
1. Identify any missing implementations
2. Identify any extra implementations not in requirements
3. Trace each requirement to the code
4. Identify partial implementations
5. Provide a detailed gap analysis report

Respond with:
- Missing requirements (if any)
- Extra implementations (if any)
- Partial implementations (if any)
- Overall assessment
"""
        return prompt

    def generate_pass_fail_concerns_prompt(
        self,
        requirement: str,
        implementation_status: str,
        test_coverage: float,
        findings: List[str],
    ) -> str:
        """
        Generate a prompt for making PASS/FAIL/CONCERNS decision.

        Args:
            requirement: The requirement
            implementation_status: Status of implementation
            test_coverage: Test coverage percentage
            findings: List of findings

        Returns:
            Formatted prompt for decision making
        """
        findings_str = "\n".join([f"- {f}" for f in findings])
        
        prompt = f"""You are a QA expert making a PASS/FAIL/CONCERNS decision.

Make a decision based on the following information:

REQUIREMENT:
{requirement}

IMPLEMENTATION STATUS: {implementation_status}
TEST COVERAGE: {test_coverage:.1%}

FINDINGS:
{findings_str}

Decision Criteria:
- PASS: Requirement fully implemented with good test coverage (>70%)
- FAIL: Missing implementation OR very low test coverage (<30%)
- CONCERNS: Partial implementation OR moderate test coverage (30-70%)

Respond with ONLY one of: PASS / FAIL / CONCERNS
"""
        return prompt
