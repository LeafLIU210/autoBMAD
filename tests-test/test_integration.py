"""Integration tests for the bubble sort package."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Test package imports


class TestPackageStructure:
    """Test suite for package structure validation."""

    def test_package_can_be_imported(self):
        """Test that the package can be imported successfully."""
        import src.bubblesort

        assert hasattr(src.bubblesort, "bubble_sort")

    def test_bubble_sort_function_imported(self):
        """Test that bubble_sort is properly exported."""
        from src.bubblesort import bubble_sort

        assert callable(bubble_sort)

    def test_package_init_exports_correctly(self):
        """Test that __init__.py exports the correct API."""
        import src.bubblesort

        assert "bubble_sort" in src.bubblesort.__all__
        assert src.bubblesort.__all__ == ["bubble_sort"]

    def test_src_init_exists(self):
        """Test that src/__init__.py exists."""
        src_init = Path("src/__init__.py")
        assert src_init.exists()

    def test_bubblesort_init_exists(self):
        """Test that src/bubblesort/__init__.py exists."""
        package_init = Path("src/bubblesort/__init__.py")
        assert package_init.exists()

    def test_cli_module_exists(self):
        """Test that src/cli.py exists."""
        cli_module = Path("src/cli.py")
        assert cli_module.exists()

    def test_main_cli_entry_point(self):
        """Test that CLI can be invoked."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "Bubble Sort CLI" in result.stdout


class TestPyprojectConfiguration:
    """Test suite for pyproject.toml validation."""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists."""
        pyproject = Path("pyproject.toml")
        assert pyproject.exists()

    def test_pyproject_is_valid_toml(self):
        """Test that pyproject.toml is valid TOML."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        assert "project" in data
        assert "build-system" in data

    def test_project_metadata_present(self):
        """Test that project metadata is present."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        project = data["project"]
        assert "name" in project
        assert "version" in project
        assert "description" in project

    def test_test_dependencies_present(self):
        """Test that test dependencies are configured."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        project = data["project"]
        assert "optional-dependencies" in project
        assert "dev" in project["optional-dependencies"]
        dev_deps = project["optional-dependencies"]["dev"]
        # Check for pytest and pytest-cov in the dependency list
        assert any("pytest" in dep for dep in dev_deps)
        assert any("pytest-cov" in dep for dep in dev_deps)

    def test_pytest_configuration_present(self):
        """Test that pytest is configured."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        assert "tool" in data and "pytest" in data["tool"]

    def test_ruff_configuration_present(self):
        """Test that ruff linter is configured."""
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        assert "tool" in data and "ruff" in data["tool"]


class TestProjectFiles:
    """Test suite for required project files."""

    def test_readme_exists(self):
        """Test that README.md exists."""
        readme = Path("README.md")
        assert readme.exists()

    def test_license_exists(self):
        """Test that LICENSE exists."""
        license_file = Path("LICENSE")
        assert license_file.exists()

    def test_gitignore_exists(self):
        """Test that .gitignore exists."""
        gitignore = Path(".gitignore")
        assert gitignore.exists()

    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs = Path("docs")
        assert docs.exists()
        assert docs.is_dir()

    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        tests = Path("tests")
        assert tests.exists()
        assert tests.is_dir()


class TestFullWorkflowIntegration:
    """Integration tests for full CLI workflow."""

    def test_cli_sort_simple_array(self):
        """Test CLI sorting a simple array."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3,1,2"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "[1, 2, 3]" in result.stdout

    def test_cli_json_output(self):
        """Test CLI with JSON output format."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3,1,2", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert '"input"' in result.stdout
        assert '"sorted"' in result.stdout

    def test_cli_sorted_array_unchanged(self):
        """Test CLI with already sorted array."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "1,2,3"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "[1, 2, 3]" in result.stdout

    def test_cli_reverse_sorted(self):
        """Test CLI with reverse sorted array."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "5,4,3,2,1"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "[1, 2, 3, 4, 5]" in result.stdout

    def test_cli_with_file_input(self):
        """Test CLI with file input."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("5,3,1,4,2")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert result.returncode == 0
            assert "[1, 2, 3, 4, 5]" in result.stdout
        finally:
            os.unlink(temp_path)

    def test_cli_error_empty_input(self):
        """Test CLI error handling for empty input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode != 0
        assert "No input provided" in result.stderr

    def test_cli_error_invalid_number(self):
        """Test CLI error handling for invalid input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "1,abc,3"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode != 0
        assert "Invalid number" in result.stderr


class TestDevelopmentDependencies:
    """Test suite for development dependencies."""

    def test_ruff_available(self):
        """Test that ruff linter is available."""
        result = subprocess.run(
            ["python", "-m", "ruff", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0

    def test_black_available(self):
        """Test that black formatter is available."""
        try:
            result = subprocess.run(
                ["python", "-m", "black", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Black may not be available, skip this test
            pytest.skip("Black formatter not available")

    def test_pytest_available(self):
        """Test that pytest is available."""
        result = subprocess.run(
            ["python", "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0


class TestCodeQuality:
    """Test suite for code quality checks."""

    def test_ruff_lint_passes(self):
        """Test that ruff linting passes."""
        result = subprocess.run(
            ["python", "-m", "ruff", "check", "src"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Ruff linting failed: {result.stdout}"

    def test_black_format_check_passes(self):
        """Test that black format check passes."""
        result = subprocess.run(
            ["python", "-m", "black", "--check", "src"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Black formatting failed: {result.stdout}"
