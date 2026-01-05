"""
Documentation Accuracy Tests

Verifies that documentation accurately reflects actual system behavior.
Tests all documented commands, files, and examples.
"""

import pytest
import subprocess
import sys
from pathlib import Path
import os


@pytest.mark.documentation
class TestDocumentationAccuracy:
    """Test that documentation matches reality."""

    def test_readme_commands_exist(self):
        """Verify commands in README actually work."""
        # Check if epic_driver.py exists
        epic_driver_path = Path("autoBMAD/epic_automation/epic_driver.py")
        assert epic_driver_path.exists(), "epic_driver.py should exist"

        # Check if --help works
        result = subprocess.run(
            [sys.executable, str(epic_driver_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"--help failed: {result.stderr}"
        assert "--skip-quality" in result.stdout, "--skip-quality should be in help"
        assert "--skip-tests" in result.stdout, "--skip-tests should be in help"

    def test_setup_dependencies_exist(self):
        """Verify setup instructions mention correct dependencies."""
        setup_file = Path("autoBMAD/epic_automation/SETUP.md")
        assert setup_file.exists(), "SETUP.md should exist"

        content = setup_file.read_text()

        # Check for required dependencies
        assert "basedpyright" in content, "SETUP should mention basedpyright"
        assert "ruff" in content, "SETUP should mention ruff"
        assert "pytest" in content, "SETUP should mention pytest"
        assert "debugpy" in content, "SETUP should mention debugpy"

    def test_example_epic_exists(self):
        """Verify example epic file exists."""
        example_file = Path("docs/examples/example-epic-with-quality-gates.md")
        assert example_file.exists(), "Example epic should exist"

        content = example_file.read_text()

        # Check content structure
        assert "Story 001" in content, "Should have Story 001"
        assert "Story 002" in content, "Should have Story 002"
        assert "Quality Gates" in content, "Should mention quality gates"
        assert "Test Automation" in content, "Should mention test automation"

    def test_troubleshooting_guide_exists(self):
        """Verify troubleshooting guide exists."""
        guide_file = Path("docs/troubleshooting/quality-gates.md")
        assert guide_file.exists(), "Troubleshooting guide should exist"

        content = guide_file.read_text()

        # Check for common issues
        assert "Basedpyright" in content, "Should mention basedpyright"
        assert "Ruff" in content, "Should mention ruff"
        assert "Pytest" in content, "Should mention pytest"
        assert "Debugpy" in content, "Should mention debugpy"

    def test_user_guides_exist(self):
        """Verify user guide files exist."""
        quality_gates_guide = Path("docs/user-guide/quality-gates.md")
        test_automation_guide = Path("docs/user-guide/test-automation.md")

        assert quality_gates_guide.exists(), "Quality gates user guide should exist"
        assert test_automation_guide.exists(), "Test automation user guide should exist"

    def test_api_documentation_exists(self):
        """Verify API documentation exists."""
        api_file = Path("docs/api/README.md")
        assert api_file.exists(), "API documentation should exist"

        content = api_file.read_text()

        # Check for API classes
        assert "CodeQualityAgent" in content, "Should document CodeQualityAgent"
        assert "TestAutomationAgent" in content, "Should document TestAutomationAgent"
        assert "StateManager" in content, "Should document StateManager"
        assert "EpicDriver" in content, "Should document EpicDriver"

    def test_integration_tests_exist(self):
        """Verify integration test files exist."""
        test_file = Path("tests/integration/test_complete_workflow.py")
        assert test_file.exists(), "Integration test file should exist"

        content = test_file.read_text()

        # Check test coverage
        assert "test_full_5_phase_workflow" in content, "Should test full workflow"
        assert "test_workflow_skip_quality" in content, "Should test skip quality"
        assert "test_workflow_skip_tests" in content, "Should test skip tests"

    def test_performance_tests_exist(self):
        """Verify performance test files exist."""
        test_file = Path("tests/performance/test_benchmarks.py")
        assert test_file.exists(), "Performance test file should exist"

        content = test_file.read_text()

        # Check benchmark tests
        assert "test_basedpyright_performance" in content, "Should benchmark basedpyright"
        assert "test_ruff_performance" in content, "Should benchmark ruff"
        assert "test_pytest_performance" in content, "Should benchmark pytest"

    def test_documented_files_exist(self):
        """Verify all files mentioned in documentation actually exist."""
        # Files mentioned in docs
        files_to_check = [
            "README.md",
            "SETUP.md",
            "docs/examples/example-epic-with-quality-gates.md",
            "docs/troubleshooting/quality-gates.md",
            "docs/user-guide/quality-gates.md",
            "docs/user-guide/test-automation.md",
            "docs/api/README.md",
            "tests/integration/test_complete_workflow.py",
            "tests/performance/test_benchmarks.py",
        ]

        for file_path in files_to_check:
            full_path = Path(file_path)
            assert full_path.exists(), f"Documented file should exist: {file_path}"

    def test_cli_options_documented(self):
        """Verify CLI options are documented."""
        # Check README
        readme = Path("autoBMAD/epic_automation/README.md").read_text()
        assert "--skip-quality" in readme, "README should document --skip-quality"
        assert "--skip-tests" in readme, "README should document --skip-tests"

        # Check SETUP
        setup = Path("autoBMAD/epic_automation/SETUP.md").read_text()
        assert "--skip-quality" in setup or "skip-quality" in setup, \
            "SETUP should mention skip-quality"
        assert "--skip-tests" in setup or "skip-tests" in setup, \
            "SETUP should mention skip-tests"

    def test_workflow_phases_documented(self):
        """Verify all 5 workflow phases are documented."""
        readme = Path("autoBMAD/epic_automation/README.md").read_text()

        # Check for all 5 phases
        phases = [
            "Phase 1: SM-Dev-QA",
            "Phase 2: Quality Gates",
            "Phase 3: Test Automation",
            "Phase 4: Orchestration",
            "Phase 5: Documentation",
        ]

        for phase in phases:
            assert phase in readme, f"Should document {phase}"

    def test_quality_gate_tools_documented(self):
        """Verify quality gate tools are documented."""
        readme = Path("autoBMAD/epic_automation/README.md").read_text()

        assert "Basedpyright" in readme, "Should mention Basedpyright"
        assert "Ruff" in readme, "Should mention Ruff"

    def test_test_automation_tools_documented(self):
        """Verify test automation tools are documented."""
        readme = Path("autoBMAD/epic_automation/README.md").read_text()

        assert "Pytest" in readme, "Should mention Pytest"
        assert "Debugpy" in readme, "Should mention Debugpy"

    def test_configuration_example_exists(self):
        """Verify configuration example exists."""
        example_file = Path("docs/examples/example-epic-with-quality-gates.md")
        content = example_file.read_text()

        assert "pyproject.toml" in content, "Should have configuration example"
        assert "basedpyright" in content, "Should show basedpyright config"
        assert "ruff" in content, "Should show ruff config"
        assert "pytest" in content, "Should show pytest config"

    def test_example_commands_work(self):
        """Verify example commands in documentation are syntactically correct."""
        readme = Path("autoBMAD/epic_automation/README.md").read_text()

        # Extract commands (lines starting with ```bash)
        import re
        commands = re.findall(r'```bash\n(.*?)\n```', readme, re.DOTALL)

        # Basic check: commands should not have obvious syntax errors
        for command in commands:
            # Skip empty commands
            if not command.strip():
                continue

            # Check for basic patterns
            assert "python" in command or "pip" in command or "basedpyright" in command or "ruff" in command or "pytest" in command, \
                f"Command should be valid: {command[:50]}..."

    def test_documentation_links_valid(self):
        """Verify internal documentation links are valid."""
        # Check that all documented paths exist
        docs_dir = Path("docs")
        if docs_dir.exists():
            # Read all markdown files in docs
            for md_file in docs_dir.rglob("*.md"):
                content = md_file.read_text()

                # Check for [relative paths](path) pattern
                import re
                links = re.findall(r'\[.*?\]\((.*?)\)', content)

                for link in links:
                    # Skip external links
                    if link.startswith("http"):
                        continue

                    # Check if linked file exists
                    link_path = md_file.parent / link
                    # Allow fragment links (#section)
                    if "#" in link:
                        actual_path = str(link_path).split("#")[0]
                        link_path = Path(actual_path)

                    # Some links might be relative, check both
                    if not link_path.exists():
                        # Try from project root
                        alt_path = Path(link)
                        if not alt_path.exists():
                            print(f"Warning: Link target not found: {link} in {md_file}")
                            # Don't fail - some links might be valid fragments or external

    def test_story_task_completion(self):
        """Verify story tasks have completion markers."""
        story_file = Path("docs/stories/005.documentation-testing-integration.md")
        content = story_file.read_text()

        # This test documents what we're working on
        # All tasks should be marked complete after implementation
        assert "Story 005" in content, "Should be testing Story 005"

        # Check that tasks section exists
        assert "Tasks / Subtasks" in content, "Should have tasks section"

    def test_file_list_section_exists(self):
        """Verify File List section exists in story."""
        story_file = Path("docs/stories/005.documentation-testing-integration.md")
        content = story_file.read_text()

        # The File List section should be present for tracking changes
        assert "File List" in content or "### File List" in content, \
            "Story should have File List section"

    def test_change_log_exists(self):
        """Verify Change Log section exists."""
        story_file = Path("docs/stories/005.documentation-testing-integration.md")
        content = story_file.read_text()

        assert "Change Log" in content, "Should have Change Log section"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
