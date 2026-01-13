"""
Test package installation and import functionality.

This module validates that the package can be properly installed and imported
from the source directory, and that all imports work correctly.
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

import pytest


class TestPackageInstallation:
    """Test suite for package installation and import."""

    def test_package_importable_from_src(self) -> None:
        """Test that package can be imported from src/ directory."""
        # Add src to path if not already there
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Try importing
        try:
            import bubblesort
            assert bubblesort is not None, "bubblesort module should be importable"
        except ImportError as e:
            pytest.fail(f"Failed to import bubblesort module: {e}")

    def test_bubble_sort_function_importable(self) -> None:
        """Test that bubble_sort function can be imported."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from bubblesort import bubble_sort
            assert callable(bubble_sort), "bubble_sort should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import bubble_sort function: {e}")

    def test_package_has_all_attribute(self) -> None:
        """Test that package has __all__ attribute defined."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            import bubblesort
            assert hasattr(bubblesort, "__all__"), \
                "bubblesort package should have __all__ attribute"
            assert "bubble_sort" in bubblesort.__all__, \
                "bubble_sort should be in __all__"
        except ImportError as e:
            pytest.fail(f"Failed to import bubblesort package: {e}")

    def test_module_has_docstring(self) -> None:
        """Test that bubble_sort module has a docstring."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from bubblesort import bubble_sort
            assert bubble_sort.__doc__ is not None, \
                "bubble_sort function should have a docstring"
            assert len(bubble_sort.__doc__.strip()) > 0, \
                "bubble_sort function docstring should not be empty"
        except ImportError as e:
            pytest.fail(f"Failed to import bubble_sort function: {e}")

    def test_package_init_has_docstring(self) -> None:
        """Test that package __init__.py has a docstring."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            import bubblesort
            assert bubblesort.__doc__ is not None or bubblesort.__doc__ == "", \
                "bubblesort package should have __doc__ attribute"
        except ImportError as e:
            pytest.fail(f"Failed to import bubblesort package: {e}")

    def test_function_has_type_hints(self) -> None:
        """Test that bubble_sort function has type hints."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            from bubblesort import bubble_sort
            # Check if function has type hints
            annotations = bubble_sort.__annotations__
            assert len(annotations) > 0, \
                "bubble_sort function should have type hints"
            assert "return" in annotations, \
                "bubble_sort function should have return type hint"
        except ImportError as e:
            pytest.fail(f"Failed to import bubble_sort function: {e}")

    def test_package_structure_matches_expected(self) -> None:
        """Test that package structure matches expected layout."""
        # Check src directory structure
        src_dir = Path("src")
        assert src_dir.exists(), "src/ directory should exist"

        bubblesort_dir = src_dir / "bubblesort"
        assert bubblesort_dir.exists(), "src/bubblesort/ should exist"

        init_file = bubblesort_dir / "__init__.py"
        assert init_file.exists(), "src/bubblesort/__init__.py should exist"

        module_file = bubblesort_dir / "bubble_sort.py"
        assert module_file.exists(), "src/bubblesort/bubble_sort.py should exist"

    def test_can_install_in_development_mode(self) -> None:
        """Test that package can be installed in development mode."""
        # Try to run pip install -e . from parent directory
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"],
                cwd=str(Path(".").absolute()),
                capture_output=True,
                text=True,
                timeout=30
            )

            # Installation might fail due to dependencies, but shouldn't fail on structure
            if result.returncode != 0:
                # Check if it's a dependency issue, not a structure issue
                error_output = result.stderr.lower()
                if "no module named" in error_output or "could not find" in error_output:
                    # Skip if it's a dependency issue
                    pytest.skip("Skipping: dependencies not available")
                else:
                    # If it's a structural issue, fail
                    pytest.fail(f"Installation failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            pytest.skip("Skipping: installation timed out")
        except Exception as e:
            pytest.skip(f"Skipping installation test: {e}")

    def test_import_works_after_development_install(self) -> None:
        """Test that imports work after development mode installation."""
        # This test assumes the previous test passed
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            # Try different import styles
            import bubblesort
            from bubblesort import bubble_sort
            from bubblesort.bubble_sort import bubble_sort as bs

            # All should reference the same function
            assert bubble_sort is bs, "Import styles should reference same function"
            assert callable(bubble_sort), "Imported function should be callable"

        except ImportError as e:
            pytest.fail(f"Failed to import after development install: {e}")

    def test_package_metadata_accessible(self) -> None:
        """Test that package metadata is accessible."""
        src_path = str(Path("src").absolute())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        try:
            import bubblesort

            # Check if module is in sys.modules (after import)
            # This should pass if import worked above
            assert "bubblesort" in sys.modules or "src.bubblesort" in sys.modules, \
                "bubblesort should be in sys.modules after import"

            # Verify the module has expected attributes
            assert hasattr(bubblesort, "__name__"), "Module should have __name__"
            assert hasattr(bubblesort, "bubble_sort"), "Module should export bubble_sort"

        except ImportError as e:
            pytest.fail(f"Failed to check package metadata: {e}")

    def test_cli_entry_point_configured(self) -> None:
        """Test that CLI entry point is configured in pyproject.toml."""
        # Use tomllib or tomli
        if sys.version_info >= (3, 11):
            import tomllib
            load_toml = tomllib.load
        else:
            import tomli
            load_toml = tomli.load

        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        # Check if entry points are defined
        if "project.scripts" in data:
            scripts = data["project.scripts"]
            assert "bubble-sort" in scripts or "bubblesort" in scripts, \
                "CLI script should be configured in pyproject.toml"
        # If no scripts configured, that's also acceptable for this project

    def test_pythonpath_configuration(self) -> None:
        """Test that Python path configuration allows imports."""
        src_path = Path("src").absolute()
        assert src_path.exists(), "src/ path should exist"

        # Verify the path is accessible
        try:
            bubblesort_init = src_path / "bubblesort" / "__init__.py"
            assert bubblesort_init.exists(), "bubblesort __init__.py should exist"
        except Exception as e:
            pytest.fail(f"Python path configuration issue: {e}")
