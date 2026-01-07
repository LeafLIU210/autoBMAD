"""
Acceptance Criteria Validation Tests for Story 1.1

This test file validates that all acceptance criteria for the project setup
and infrastructure story are met through automated testing.
"""

import os
import subprocess
from pathlib import Path
import pytest


class TestAcceptanceCriteriaValidation:
    """Validate all acceptance criteria from Story 1.1."""

    @pytest.mark.acceptance
    def test_ac1_python_package_structure(self):
        """AC #1: Create proper Python package structure with __init__.py files."""
        # Check src directory exists
        src_dir = Path("src")
        assert src_dir.exists(), "src/ directory should exist"

        # Check tests directory exists
        tests_dir = Path("tests")
        assert tests_dir.exists(), "tests/ directory should exist"

        # Check __init__.py files exist
        src_init = src_dir / "__init__.py"
        tests_init = tests_dir / "__init__.py"
        assert src_init.exists(), "src/__init__.py should exist"
        assert tests_init.exists(), "tests/__init__.py should exist"

    @pytest.mark.acceptance
    def test_ac2_project_configuration(self):
        """AC #2: Setup.py or pyproject.toml file with project metadata and dependencies."""
        # Check pyproject.toml exists
        pyproject = Path("pyproject.toml")
        assert pyproject.exists(), "pyproject.toml should exist"

        # Validate pyproject.toml contains required fields
        with open(pyproject, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for essential project metadata
        assert "name = " in content, "Project name should be defined"
        assert "version = " in content, "Project version should be defined"
        assert "description = " in content, "Project description should be defined"
        assert "dependencies = " in content, "Dependencies should be defined"

        # Check for pytest configuration
        assert "[tool.pytest.ini_options]" in content, "Pytest configuration should exist"

    @pytest.mark.acceptance
    def test_ac3_readme_documentation(self):
        """AC #3: README.md with installation instructions and basic usage."""
        # Check README.md exists
        readme = Path("README.md")
        assert readme.exists(), "README.md should exist"

        # Validate README content
        with open(readme, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for essential sections
        assert "install" in content.lower() or "setup" in content.lower(), \
            "README should contain installation instructions"
        assert "usage" in content.lower() or "example" in content.lower(), \
            "README should contain usage examples"

    @pytest.mark.acceptance
    def test_ac4_directory_structure(self):
        """AC #4: Basic directory structure for source code, tests, and documentation."""
        # Check required directories exist
        required_dirs = ["src", "tests", "docs"]
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"{dir_name}/ directory should exist"

    @pytest.mark.acceptance
    def test_ac5_git_repository(self):
        """AC #5: Git repository initialization with appropriate .gitignore file."""
        # Check .git directory exists
        git_dir = Path(".git")
        assert git_dir.exists(), ".git directory should exist (git repository initialized)"

        # Check .gitignore exists
        gitignore = Path(".gitignore")
        assert gitignore.exists(), ".gitignore should exist"

        # Validate .gitignore content
        with open(gitignore, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for Python-specific ignore patterns
        assert "__pycache__" in content or "*.pyc" in content, \
            ".gitignore should ignore Python cache files"

    @pytest.mark.acceptance
    def test_ac6_ci_cd_configuration(self):
        """AC #6: Basic CI/CD configuration file (GitHub Actions or similar)."""
        # Check .github directory exists
        github_dir = Path(".github")
        assert github_dir.exists(), ".github directory should exist"

        # Check for workflows directory
        workflows_dir = github_dir / "workflows"
        assert workflows_dir.exists(), ".github/workflows/ directory should exist"

        # Check for at least one workflow file
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        assert len(workflow_files) > 0, "At least one GitHub Actions workflow should exist"


class TestCodeQualityStandards:
    """Additional tests to ensure code quality and standards compliance."""

    @pytest.mark.acceptance
    def test_code_coverage_requirement(self):
        """Verify that code coverage configuration is properly set up."""
        # Check that pytest-cov is configured in dependencies
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for pytest-cov in dependencies
        assert "pytest-cov" in content, "pytest-cov should be in dependencies"

        # Check for coverage configuration in pytest options
        assert "--cov" in content, "Coverage should be configured in pytest options"

    @pytest.mark.acceptance
    def test_linting_configuration(self):
        """Verify that linting tools are configured."""
        # Check pyproject.toml for linting configuration
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()

        # Should have black or other formatting tools configured
        has_formatter = "tool.black" in content or "[tool.ruff]" in content
        assert has_formatter, "Code formatting tools should be configured"

    @pytest.mark.acceptance
    def test_test_framework_configuration(self):
        """Verify test framework is properly configured."""
        # Clean up any leftover coverage files
        for pattern in [".coverage", ".coverage.*", "htmlcov", ".pytest_cache"]:
            subprocess.run(["rm", "-rf", pattern], capture_output=True, cwd=Path.cwd())

        # Run pytest --collect-only to validate test discovery
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        # Test collection should succeed
        assert result.returncode == 0, f"Test collection failed:\n{result.stderr}"

        # Should find test files
        assert "test_" in result.stdout, "Test files should be discovered"


class TestStoryImplementationCompleteness:
    """Verify all story tasks are completed."""

    @pytest.mark.acceptance
    def test_all_tasks_completed(self):
        """Verify that all story tasks have been implemented and tested."""
        # Clean up any leftover coverage files
        for pattern in [".coverage", ".coverage.*", "htmlcov", ".pytest_cache"]:
            subprocess.run(["rm", "-rf", pattern], capture_output=True, cwd=Path.cwd())

        # Check that source code exists and can be imported
        try:
            from src import bubble_sort
            assert callable(bubble_sort), "bubble_sort function should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import bubble_sort: {e}")

        # Check that tests exist and can be run
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "--collect-only"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0, f"Test collection failed:\n{result.stderr}"

    @pytest.mark.acceptance
    def test_package_is_installable(self):
        """Verify the package configuration is correct for installation."""
        # Check that pyproject.toml has proper build configuration
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for build system configuration
        assert "[build-system]" in content, "Build system should be configured"
        assert "hatchling" in content, "hatchling build backend should be configured"

        # Check for project metadata
        assert "[project]" in content, "Project configuration should exist"
        assert "name = " in content, "Project name should be defined"

        # Verify package can be imported (basic smoke test)
        try:
            from src import bubble_sort
            assert callable(bubble_sort)
        except ImportError as e:
            pytest.fail(f"Failed to import bubble_sort: {e}")
