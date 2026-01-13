"""
Test package structure and organization.

This module validates that the project follows proper Python packaging standards
and that all required files and directories are present.
"""

import os
import sys
from pathlib import Path
from typing import List

# Use tomllib for Python 3.11+, tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
    load_toml = tomllib.load
else:
    import tomli
    load_toml = tomli.load


class TestPackageStructure:
    """Test suite for validating package structure."""

    def test_src_directory_exists(self) -> None:
        """Test that src/ directory exists."""
        src_path = Path(__file__).parent.parent / "src"
        assert src_path.exists(), "src/ directory should exist"
        assert src_path.is_dir(), "src/ should be a directory"

    def test_tests_directory_exists(self) -> None:
        """Test that tests/ directory exists."""
        tests_path = Path(__file__).parent.parent / "tests"
        assert tests_path.exists(), "tests/ directory should exist"
        assert tests_path.is_dir(), "tests/ should be a directory"

    def test_docs_directory_exists(self) -> None:
        """Test that docs/ directory exists."""
        docs_path = Path(__file__).parent.parent / "docs"
        assert docs_path.exists(), "docs/ directory should exist"
        assert docs_path.is_dir(), "docs/ should be a directory"

    def test_src_init_file_exists(self) -> None:
        """Test that src/__init__.py exists."""
        init_path = Path(__file__).parent.parent / "src" / "__init__.py"
        assert init_path.exists(), "src/__init__.py should exist"
        assert init_path.is_file(), "src/__init__.py should be a file"

    def test_bubblesort_package_exists(self) -> None:
        """Test that src/bubblesort/ package directory exists."""
        package_path = Path(__file__).parent.parent / "src" / "bubblesort"
        assert package_path.exists(), "src/bubblesort/ package should exist"
        assert package_path.is_dir(), "src/bubblesort/ should be a directory"

    def test_bubblesort_init_file_exists(self) -> None:
        """Test that src/bubblesort/__init__.py exists."""
        init_path = Path(__file__).parent.parent / "src" / "bubblesort" / "__init__.py"
        assert init_path.exists(), "src/bubblesort/__init__.py should exist"
        assert init_path.is_file(), "src/bubblesort/__init__.py should be a file"

    def test_bubblesort_module_exists(self) -> None:
        """Test that src/bubblesort/bubble_sort.py module exists."""
        module_path = Path(__file__).parent.parent / "src" / "bubblesort" / "bubble_sort.py"
        assert module_path.exists(), "src/bubblesort/bubble_sort.py should exist"
        assert module_path.is_file(), "src/bubblesort/bubble_sort.py should be a file"

    def test_pyproject_toml_exists(self) -> None:
        """Test that pyproject.toml exists in project root."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml should exist"
        assert pyproject_path.is_file(), "pyproject.toml should be a file"

    def test_readme_exists(self) -> None:
        """Test that README.md exists in project root."""
        readme_path = Path(__file__).parent.parent / "README.md"
        assert readme_path.exists(), "README.md should exist"
        assert readme_path.is_file(), "README.md should be a file"

    def test_gitignore_exists(self) -> None:
        """Test that .gitignore exists in project root."""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should exist"
        assert gitignore_path.is_file(), ".gitignore should be a file"

    def test_git_repository_initialized(self) -> None:
        """Test that git repository is initialized."""
        git_dir = Path(__file__).parent.parent / ".git"
        assert git_dir.exists(), ".git directory should exist (git repository initialized)"
        assert git_dir.is_dir(), ".git should be a directory"

    def test_all_package_inits_are_files(self) -> None:
        """Test that all __init__.py files are proper files, not directories."""
        init_files = [
            Path(__file__).parent.parent / "src" / "__init__.py",
            Path(__file__).parent.parent / "src" / "bubblesort" / "__init__.py",
        ]

        for init_file in init_files:
            assert init_file.exists(), f"{init_file} should exist"
            assert init_file.is_file(), f"{init_file} should be a file, not a directory"
            assert init_file.stat().st_size > 0, f"{init_file} should not be empty"

    def test_pyproject_toml_is_valid_toml(self) -> None:
        """Test that pyproject.toml contains valid TOML structure."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "build-system" in data, "pyproject.toml should have [build-system] section"
        assert "project" in data, "pyproject.toml should have [project] section"
        assert "name" in data["project"], "project should have name"
        assert "version" in data["project"], "project should have version"
        assert "description" in data["project"], "project should have description"

    def test_pyproject_has_required_project_fields(self) -> None:
        """Test that pyproject.toml has all required project metadata."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        project = data["project"]

        # Check required fields
        required_fields = [
            "name",
            "version",
            "description",
            "readme",
            "requires-python",
            "license",
            "authors",
        ]

        for field in required_fields:
            assert field in project, f"project.{field} should be present in pyproject.toml"

    def test_pyproject_has_dependencies(self) -> None:
        """Test that pyproject.toml has dependencies section."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "dependencies" in data["project"], "project should have dependencies"

    def test_pyproject_has_dev_dependencies(self) -> None:
        """Test that pyproject.toml has optional dev dependencies."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "optional-dependencies" in data["project"], "project should have optional-dependencies"
        assert "dev" in data["project"]["optional-dependencies"], "dev dependencies should be present"

    def test_readme_has_project_content(self) -> None:
        """Test that README.md contains meaningful content."""
        readme_path = Path(__file__).parent.parent / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that README has substantial content
        assert len(content) > 100, "README.md should contain meaningful content"
        # README can be for any project, just check it has content

    def test_gitignore_has_python_entries(self) -> None:
        """Test that .gitignore contains Python-specific entries."""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for common Python gitignore entries
        python_entries = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            ".coverage",
        ]

        for entry in python_entries:
            assert entry in content, f".gitignore should contain '{entry}'"

    def test_gitignore_has_build_artifacts(self) -> None:
        """Test that .gitignore excludes build artifacts."""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for build artifact entries
        build_entries = [
            "build/",
            "dist/",
            "*.egg-info/",
        ]

        for entry in build_entries:
            assert entry in content, f".gitignore should contain '{entry}'"
