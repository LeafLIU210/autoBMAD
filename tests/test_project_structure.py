"""
Test suite for project infrastructure and setup validation.
Tests all acceptance criteria from Story 1.1: Project Setup and Infrastructure.
"""
import os
import sys
from pathlib import Path
import pytest


class TestProjectStructure:
    """Test project structure and package organization."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self, tmp_path):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"

    def test_main_package_has_init_file(self):
        """Verify main package directory has __init__.py file."""
        init_file = self.src_dir / "__init__.py"
        assert init_file.exists(), "src/__init__.py must exist for proper package structure"
        assert init_file.is_file(), "src/__init__.py must be a file"

    def test_tests_package_has_init_file(self):
        """Verify tests directory has __init__.py file."""
        init_file = self.tests_dir / "__init__.py"
        assert init_file.exists(), "tests/__init__.py must exist for proper package structure"
        assert init_file.is_file(), "tests/__init__.py must be a file"

    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml exists with proper configuration."""
        pyproject_file = self.project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist"
        assert pyproject_file.is_file(), "pyproject.toml must be a file"

        # Verify it contains expected sections
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')
        assert "[build-system]" in content, "pyproject.toml must have build-system section"
        assert "[project]" in content, "pyproject.toml must have project section"

    def test_pyproject_has_project_metadata(self):
        """Verify pyproject.toml has proper project metadata."""
        pyproject_file = self.project_root / "pyproject.toml"
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')

        # Check for essential metadata
        assert "name =" in content, "Project name must be defined"
        assert "version =" in content, "Project version must be defined"
        assert "description =" in content, "Project description must be defined"
        assert "requires-python =" in content, "Python version requirement must be defined"

    def test_pyproject_has_dependencies(self):
        """Verify pyproject.toml has dependencies configured."""
        pyproject_file = self.project_root / "pyproject.toml"
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')

        # Check for dependencies section
        assert "dependencies" in content, "Dependencies must be defined"

    def test_pyproject_has_test_configuration(self):
        """Verify pyproject.toml has pytest configuration."""
        pyproject_file = self.project_root / "pyproject.toml"
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')

        # Check for pytest configuration
        assert "[tool.pytest.ini_options]" in content or "[tool.pytest" in content, \
            "Pytest configuration must be present"

    def test_readme_exists(self):
        """Verify README.md exists."""
        readme_file = self.project_root / "README.md"
        assert readme_file.exists(), "README.md must exist"
        assert readme_file.is_file(), "README.md must be a file"

    def test_readme_has_installation_instructions(self):
        """Verify README.md contains installation instructions."""
        readme_file = self.project_root / "README.md"
        try:
            content = readme_file.read_text(encoding='utf-8').lower()
        except UnicodeDecodeError:
            content = readme_file.read_text(encoding='utf-8', errors='ignore').lower()

        # Check for installation-related keywords
        installation_keywords = ["install", "pip", "setup", "requirements"]
        found_keywords = [kw for kw in installation_keywords if kw in content]

        assert len(found_keywords) >= 2, \
            f"README.md must contain installation instructions (found: {found_keywords})"

    def test_readme_has_usage_instructions(self):
        """Verify README.md contains usage instructions."""
        readme_file = self.project_root / "README.md"
        try:
            content = readme_file.read_text(encoding='utf-8').lower()
        except UnicodeDecodeError:
            content = readme_file.read_text(encoding='utf-8', errors='ignore').lower()

        # Check for usage-related keywords
        usage_keywords = ["usage", "use", "example", "getting started", "quick start"]
        found_keywords = [kw for kw in usage_keywords if kw in content]

        assert len(found_keywords) >= 1, \
            f"README.md must contain usage instructions (found: {found_keywords})"

    def test_gitignore_exists(self):
        """Verify .gitignore exists."""
        gitignore_file = self.project_root / ".gitignore"
        assert gitignore_file.exists(), ".gitignore must exist"
        assert gitignore_file.is_file(), ".gitignore must be a file"

    def test_gitignore_has_python_patterns(self):
        """Verify .gitignore contains Python-specific patterns."""
        gitignore_file = self.project_root / ".gitignore"
        try:
            content = gitignore_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = gitignore_file.read_text(encoding='utf-8', errors='ignore')

        # Check for essential Python patterns
        python_patterns = ["__pycache__", "*.pyc", "*.pyo"]
        found_patterns = [p for p in python_patterns if p in content]

        assert len(found_patterns) >= 2, \
            f".gitignore must contain Python patterns (found: {found_patterns})"

    def test_git_repository_initialized(self):
        """Verify git repository is initialized."""
        git_dir = self.project_root / ".git"
        assert git_dir.exists(), ".git directory must exist"
        assert git_dir.is_dir(), ".git must be a directory"

    def test_github_workflows_exist(self):
        """Verify .github/workflows directory exists."""
        workflows_dir = self.project_root / ".github" / "workflows"
        assert workflows_dir.exists(), ".github/workflows/ directory must exist"
        assert workflows_dir.is_dir(), ".github/workflows/ must be a directory"

    def test_ci_cd_workflow_exists(self):
        """Verify CI/CD workflow file exists."""
        workflows_dir = self.project_root / ".github" / "workflows"
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        assert len(workflow_files) >= 1, "At least one CI/CD workflow file must exist"

    def test_package_is_installable(self):
        """Verify package can be installed (basic check)."""
        pyproject_file = self.project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist for package installation"

        # Verify build system is configured
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')
        assert "[build-system]" in content, "Build system must be configured"
        assert "requires" in content, "Build requirements must be specified"

    def test_directory_structure_follows_python_best_practices(self):
        """Verify directory structure follows Python packaging best practices."""
        # Check for standard directories
        expected_dirs = ["src", "tests", "docs"]
        for dir_name in expected_dirs:
            dir_path = self.project_root / dir_name
            assert dir_path.exists(), f"{dir_name}/ directory must exist"
            assert dir_path.is_dir(), f"{dir_name}/ must be a directory"

    def test_tests_have_proper_structure(self):
        """Verify tests directory has proper structure."""
        # Check for unit and integration test directories
        unit_tests_dir = self.tests_dir / "unit"
        integration_tests_dir = self.tests_dir / "integration"

        assert unit_tests_dir.exists(), "tests/unit/ directory must exist"
        assert integration_tests_dir.exists(), "tests/integration/ directory must exist"

    def test_pyproject_has_test_dependencies(self):
        """Verify pyproject.toml has test dependencies."""
        pyproject_file = self.project_root / "pyproject.toml"
        try:
            content = pyproject_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = pyproject_file.read_text(encoding='utf-8', errors='ignore')

        # Check for pytest in dependencies
        assert "pytest" in content.lower(), "pytest must be in dependencies"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
