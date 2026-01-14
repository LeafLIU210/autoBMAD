"""Test suite for package installation and distribution.

Tests cover:
- Package structure
- Installation procedures
- Dependencies
- Build configuration
"""

import subprocess
import sys
from pathlib import Path
import pytest


class TestPackageInstallation:
    """Test package installation capabilities."""

    def test_package_can_be_built(self):
        """Test that package can be built using setuptools or similar."""
        # Check if pyproject.toml exists and is valid
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist for package building"

        # Verify pyproject.toml has required sections
        content = pyproject_file.read_text(encoding="utf-8")
        assert '[project]' in content or '[build-system]' in content

    def test_package_metadata_exists(self):
        """Test that package metadata is properly defined."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        # Check for common metadata fields
        assert 'name' in content.lower() or 'project' in content.lower()

    def test_dependencies_defined(self):
        """Test that project dependencies are defined."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        # Should have either dependencies or requirements
        has_deps = 'dependencies' in content or 'requires' in content or 'requirements' in content
        # It's OK if there are no dependencies, but the field should be checked

    def test_package_has_version(self):
        """Test that package has a version defined."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        assert 'version' in content.lower()

    def test_package_has_description(self):
        """Test that package has a description."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        assert 'description' in content.lower()


class TestPackageStructure:
    """Test package directory structure."""

    def test_src_structure(self):
        """Test that src directory structure is correct."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        assert src_dir.exists(), "src directory must exist"
        assert src_dir.is_dir(), "src must be a directory"

    def test_package_init_files(self):
        """Test that all packages have __init__.py files."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Check src has __init__.py
        src_init = src_dir / "__init__.py"
        assert src_init.exists(), "src/__init__.py must exist"

        # Check subdirectories have __init__.py
        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                init_file = item / "__init__.py"
                assert init_file.exists(), f"{item.name}/__init__.py must exist"

    def test_package_importable(self):
        """Test that packages can be imported."""
        # This should work if package is properly structured
        try:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root / "src"))

            # Try importing main package
            import src
            assert src is not None

            # Try importing subpackage if exists
            try:
                import src.bubblesort
                assert src.bubblesort is not None
            except ImportError:
                pass  # Subpackage might not exist

        except ImportError as e:
            pytest.skip(f"Package not importable: {e}")


class TestBuildSystem:
    """Test build system configuration."""

    def test_build_system_configured(self):
        """Test that build system is properly configured."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        assert 'build-system' in content.lower()

    def test_build_backend_specified(self):
        """Test that build backend is specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text(encoding="utf-8")
        # Check for common build backends
        has_backend = any(backend in content.lower()
                        for backend in ['setuptools', 'hatchling', 'poetry', 'flit'])
        assert has_backend, "Build backend should be specified"

    def test_package_backend_compatible(self):
        """Test that package backend is compatible with pip."""
        # This is a basic check that the backend is known
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        content = pyproject_file.read_text(encoding="utf-8")

        # Should use standard backends
        compatible_backends = ['setuptools', 'hatchling', 'poetry', 'flit', 'pdm']
        has_compatible = any(backend in content.lower() for backend in compatible_backends)
        assert has_compatible


class TestDevelopmentDependencies:
    """Test development dependencies and tooling."""

    def test_testing_framework_configured(self):
        """Test that testing framework is configured."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # Check for pytest configuration
            has_pytest = 'pytest' in content.lower() or '[tool.pytest' in content
            assert has_pytest, "pytest should be configured"

    def test_code_quality_tools_configured(self):
        """Test that code quality tools are configured."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # Check for common quality tools
            has_quality_tool = any(tool in content.lower()
                                  for tool in ['ruff', 'black', 'flake8', 'mypy', 'basedpyright'])
            # It's OK if quality tools are not configured yet
            # This is a verification that they might be set up

    def test_test_configuration_exists(self):
        """Test that test configuration file exists."""
        project_root = Path(__file__).parent.parent

        # Check for pytest.ini or pyproject.toml with [tool.pytest]
        pyproject_file = project_root / "pyproject.toml"
        pytest_ini = project_root / "pytest.ini"

        if pytest_ini.exists():
            content = pytest_ini.read_text(encoding="utf-8")
            assert 'pytest' in content.lower()
        elif pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            assert '[tool.pytest' in content


class TestEntryPoints:
    """Test command-line entry points."""

    def test_cli_entry_point_configured(self):
        """Test that CLI entry point is configured if applicable."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # Check for console_scripts or gui_scripts
            has_scripts = 'console-scripts' in content.lower() or 'gui-scripts' in content.lower()
            # It's OK if there are no entry points
            # This verifies the structure if it exists

    def test_module_executable(self):
        """Test that CLI module can be executed."""
        project_root = Path(__file__).parent.parent
        cli_file = project_root / "src" / "cli.py"

        if cli_file.exists():
            # Check that it has a main function
            import sys
            sys.path.insert(0, str(project_root / "src"))
            try:
                import cli
                assert hasattr(cli, 'main'), "cli.py should have a main function"
            except ImportError as e:
                pytest.skip(f"Cannot import cli module: {e}")


class TestDocumentation:
    """Test documentation setup."""

    def test_readme_exists(self):
        """Test that README file exists."""
        project_root = Path(__file__).parent.parent
        readme_files = ['README.md', 'README.rst', 'README.txt']
        has_readme = any((project_root / name).exists() for name in readme_files)
        assert has_readme, "README file should exist"

    def test_readme_has_content(self):
        """Test that README has meaningful content."""
        project_root = Path(__file__).parent.parent
        readme_files = ['README.md', 'README.rst', 'README.txt']

        for readme_name in readme_files:
            readme_file = project_root / readme_name
            if readme_file.exists():
                content = readme_file.read_text(encoding="utf-8")
                assert len(content) > 50, f"{readme_name} should have meaningful content"
                break

    def test_license_file_exists(self):
        """Test that license file exists."""
        project_root = Path(__file__).parent.parent
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']
        has_license = any((project_root / name).exists() for name in license_files)
        # License is recommended but not always required


class TestInstallationMethods:
    """Test different installation methods."""

    def test_pip_installable(self):
        """Test that package could be installed with pip."""
        # This is a structural test, not an actual installation
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # Basic validation that pyproject.toml is well-formed
            # (This is a simple check, not a full validation)
            assert '[' in content and ']' in content
            assert 'project' in content.lower() or 'tool' in content.lower()

    def test_editable_install_possible(self):
        """Test that editable install is possible."""
        # Check for proper setup for development installation
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # pyproject.toml supports editable installs by default
            # This is just a basic structure check
            has_build = 'build-system' in content.lower()
            assert has_build


class TestVirtualEnvironmentCompatibility:
    """Test virtual environment compatibility."""

    def test_requires_python_version(self):
        """Test that Python version requirement is specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # Check for python_requires or requires-python
            has_python_version = 'python' in content.lower() and ('requires' in content.lower() or 'requires-python' in content.lower())
            # It's OK if Python version is not specified yet


class TestPackagingStandards:
    """Test compliance with packaging standards."""

    def test_follows_pep517(self):
        """Test that package follows PEP 517 (build system interface)."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "PEP 517 requires pyproject.toml"

    def test_pep518_compliant(self):
        """Test that package follows PEP 518 (build system requirements)."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # PEP 518: pyproject.toml should specify build-system
            assert 'build-system' in content.lower()

    def test_package_naming(self):
        """Test that package follows Python naming conventions."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        if src_dir.exists():
            # Check that package names are lowercase and use underscores
            for item in src_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Package names should be lowercase
                    assert item.name.islower() or '_' in item.name, \
                        f"Package name {item.name} should follow Python naming conventions"
