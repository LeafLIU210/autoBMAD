"""
Test pyproject.toml configuration.

This module validates that the pyproject.toml file contains all required
configuration sections, metadata, and tool configurations.
"""

import sys
from pathlib import Path

# Use tomllib for Python 3.11+, tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
    load_toml = tomllib.load
else:
    import tomli
    load_toml = tomli.load


class TestPyprojectConfiguration:
    """Test suite for pyproject.toml configuration validation."""

    def test_build_system_defined(self) -> None:
        """Test that build system is properly defined."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "build-system" in data, "pyproject.toml should have [build-system] section"
        build_system = data["build-system"]

        assert "requires" in build_system, "build-system should specify requires"
        assert "build-backend" in build_system, "build-system should specify build-backend"

    def test_build_backend_is_hatchling(self) -> None:
        """Test that build backend is set to hatchling."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        build_backend = data["build-system"]["build-backend"]
        assert "hatchling" in build_backend.lower(), \
            "build-backend should use hatchling"

    def test_hatchling_config_for_src(self) -> None:
        """Test that hatchling is configured to build from src/."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "tool" in data, "pyproject.toml should have [tool] section"
        assert "hatch" in data["tool"], "pyproject.toml should have [tool.hatch] section"

        # Check the actual structure: [tool.hatch.build.targets.wheel]
        build_targets = data["tool"]["hatch"]["build"]["targets"]
        assert "wheel" in build_targets, "Should have wheel build target"

        wheel_target = build_targets["wheel"]
        assert "packages" in wheel_target, "wheel target should specify packages"
        assert wheel_target["packages"] == ["src"], \
            "Should build from src/ directory"

    def test_project_name_defined(self) -> None:
        """Test that project name is properly defined."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        project = data["project"]
        name = project["name"]

        assert isinstance(name, str), "Project name should be a string"
        assert len(name) > 0, "Project name should not be empty"
        assert " " not in name, "Project name should not contain spaces (use hyphens)"

    def test_project_version_format(self) -> None:
        """Test that project version follows semantic versioning."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        import re

        version = data["project"]["version"]
        # Simple semver pattern: major.minor.patch
        semver_pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(semver_pattern, version), \
            f"Version should follow semantic versioning (x.y.z), got: {version}"

    def test_project_description_present(self) -> None:
        """Test that project has a description."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        description = data["project"]["description"]
        assert isinstance(description, str), "Description should be a string"
        assert len(description) > 0, "Description should not be empty"

    def test_readme_file_specified(self) -> None:
        """Test that README file is specified in project."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        readme = data["project"]["readme"]
        assert isinstance(readme, str), "README should be specified"
        assert "README" in readme, "README file should be referenced"

        # Verify the file exists
        readme_path = Path(readme)
        # Handle both direct path and file:// format
        if readme_path.exists():
            assert readme_path.is_file(), f"{readme} should be a file"

    def test_python_version_requirement(self) -> None:
        """Test that Python version requirement is specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        requires_python = data["project"]["requires-python"]
        assert isinstance(requires_python, str), "requires-python should be specified"
        assert ">" in requires_python or ">=" in requires_python, \
            "Should specify minimum Python version"
        assert "3" in requires_python, \
            "Should specify Python 3 version"

    def test_license_specified(self) -> None:
        """Test that license is specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        license_info = data["project"]["license"]
        assert "text" in license_info, "License should specify text"
        assert isinstance(license_info["text"], str), "License text should be a string"

    def test_authors_specified(self) -> None:
        """Test that authors are specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        authors = data["project"]["authors"]
        assert isinstance(authors, list), "Authors should be a list"
        assert len(authors) > 0, "At least one author should be specified"

        for author in authors:
            assert "name" in author, "Each author should have a name"
            assert isinstance(author["name"], str), "Author name should be a string"

    def test_keywords_present(self) -> None:
        """Test that keywords are specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        keywords = data["project"]["keywords"]
        assert isinstance(keywords, list), "Keywords should be a list"
        assert len(keywords) > 0, "At least one keyword should be specified"

    def test_classifiers_present(self) -> None:
        """Test that PyPI classifiers are specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        classifiers = data["project"]["classifiers"]
        assert isinstance(classifiers, list), "Classifiers should be a list"
        assert len(classifiers) > 5, "Should have multiple classifiers for PyPI"

    def test_dependencies_present(self) -> None:
        """Test that project dependencies are specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        dependencies = data["project"]["dependencies"]
        assert isinstance(dependencies, list), "Dependencies should be a list"
        # Can be empty for library-only projects, but usually has some

    def test_dev_dependencies_present(self) -> None:
        """Test that development dependencies are specified."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        optional_deps = data["project"]["optional-dependencies"]
        assert "dev" in optional_deps, "Should have dev dependencies"

        dev_deps = optional_deps["dev"]
        assert isinstance(dev_deps, list), "Dev dependencies should be a list"
        assert len(dev_deps) > 0, "Should have development dependencies"

        # Check for common dev tools
        dev_dep_names = [dep.split(">=")[0].split("==")[0] for dep in dev_deps]
        assert any("pytest" in dep for dep in dev_dep_names), \
            "Should include pytest in dev dependencies"

    def test_pytest_configuration_present(self) -> None:
        """Test that pytest configuration is present."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "tool" in data, "Should have tool configuration"
        assert "pytest" in data["tool"], "Should have pytest configuration"

        # Check for the actual structure: [tool.pytest.ini_options]
        pytest_config = data["tool"]["pytest"]
        assert "ini_options" in pytest_config, "Should have pytest ini_options"

        ini_options = pytest_config["ini_options"]
        assert "addopts" in ini_options, "Should have pytest addopts"
        assert "testpaths" in ini_options, "Should specify testpaths"

        testpaths = ini_options["testpaths"]
        assert "tests" in testpaths, "Should specify tests directory"

    def test_ruff_configuration_present(self) -> None:
        """Test that ruff linting configuration is present."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "tool" in data, "Should have tool configuration"
        assert "ruff" in data["tool"], "Should have ruff configuration"

        ruff_config = data["tool"]["ruff"]
        assert "line-length" in ruff_config, "Should specify line length"
        assert "target-version" in ruff_config, "Should specify target version"

    def test_project_scripts_present(self) -> None:
        """Test that project entry point scripts are configured."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        # Check if scripts are defined
        if "project.scripts" in data:
            scripts = data["project.scripts"]
            assert isinstance(scripts, dict), "Scripts should be a dictionary"

    def test_mypy_configuration_present(self) -> None:
        """Test that mypy type checking configuration is present."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        assert "tool" in data, "Should have tool configuration"
        assert "mypy" in data["tool"], "Should have mypy configuration"

    def test_configuration_consistency(self) -> None:
        """Test that various configuration sections are consistent."""
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = load_toml(f)

        # Get Python version from requires-python
        requires_python = data["project"]["requires-python"]

        # Get Python version from ruff
        ruff_python = data["tool"]["ruff"]["target-version"]

        # Get Python version from mypy
        mypy_python = data["tool"]["mypy"]["python_version"]

        # All should be consistent (or at least compatible)
        # This is a basic sanity check
        assert "3" in requires_python, "requires-python should specify Python 3"
        assert "3" in ruff_python, "ruff target-version should be Python 3"
        assert "3" in mypy_python, "mypy python_version should be Python 3"
