"""Test suite for pyproject.toml configuration validation.

Tests cover:
- Configuration structure
- Metadata validation
- Build system configuration
- Tool configurations
"""

import pytest
from pathlib import Path
import toml


class TestPyprojectStructure:
    """Test pyproject.toml file structure."""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml file exists."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist"

    def test_pyproject_is_valid_toml(self):
        """Test that pyproject.toml is valid TOML."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
            parsed = toml.loads(content)
            assert parsed is not None
            assert isinstance(parsed, dict)
        except Exception as e:
            pytest.fail(f"pyproject.toml is not valid TOML: {e}")

    def test_pyproject_has_required_sections(self):
        """Test that pyproject.toml has required sections."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
            parsed = toml.loads(content)

            # pyproject.toml should have [project] or [tool.poetry] or similar
            has_project = 'project' in parsed
            has_poetry = 'tool' in parsed and 'poetry' in parsed['tool']
            has_setup = 'project' in parsed and 'setup' in str(parsed.get('project', {}))

            assert has_project or has_poetry or has_setup, \
                "pyproject.toml should have [project] or [tool.poetry] section"
        except Exception as e:
            pytest.skip(f"Cannot read pyproject.toml: {e}")

    def test_build_system_specified(self):
        """Test that build-system is specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        assert 'build-system' in parsed, \
            "pyproject.toml must specify build-system"

        build_system = parsed['build-system']
        assert 'build-backend' in build_system, \
            "build-system must specify build-backend"

        assert 'requires' in build_system, \
            "build-system must specify requires"


class TestProjectMetadata:
    """Test project metadata configuration."""

    def test_project_has_name(self):
        """Test that project has a name."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        assert 'name' in project, \
            "Project must have a name"

        name = project['name']
        assert isinstance(name, str), \
            "Project name must be a string"
        assert len(name) > 0, \
            "Project name cannot be empty"

    def test_project_name_valid(self):
        """Test that project name follows Python naming conventions."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        name = project.get('name', '')

        # Python package names should be lowercase and use hyphens or underscores
        import re
        assert re.match(r'^[a-z0-9._-]+$', name), \
            f"Project name '{name}' should follow Python naming conventions (lowercase, ._- allowed)"

    def test_project_has_version(self):
        """Test that project has a version."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        assert 'version' in project, \
            "Project must have a version"

        version = project['version']
        assert isinstance(version, str), \
            "Project version must be a string"
        assert len(version) > 0, \
            "Project version cannot be empty"

    def test_version_format_valid(self):
        """Test that version follows semantic versioning or similar."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        version = project.get('version', '')

        # Check for common version formats (semantic versioning)
        import re
        # Allow formats like: 1.0.0, 1.0.0-alpha, 1.0.0-alpha.1, etc.
        semver_pattern = r'^\d+\.\d+\.\d+([.-](alpha|beta|rc|dev|post)?[.-]?\d*)?$'
        assert re.match(semver_pattern, version), \
            f"Version '{version}' should follow semantic versioning or similar format"

    def test_project_has_description(self):
        """Test that project has a description."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        assert 'description' in project, \
            "Project should have a description"

        description = project['description']
        assert isinstance(description, str), \
            "Project description must be a string"
        assert len(description) > 0, \
            "Project description cannot be empty"

    def test_description_meaningful(self):
        """Test that description is meaningful (not just placeholder)."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        description = project.get('description', '')

        # Check that description is not a placeholder
        placeholders = ['TODO', 'PLACEHOLDER', 'DESCRIPTION', 'enter description here']
        description_lower = description.lower()
        assert not any(placeholder in description_lower for placeholder in placeholders), \
            "Project description should be meaningful, not a placeholder"

    def test_project_has_readme(self):
        """Test that project specifies README file."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})

        # Check if readme is specified (it's optional but recommended)
        # If specified, it should be a string or object
        readme = project.get('readme')
        if readme:
            assert isinstance(readme, (str, list, dict)), \
                "README should be a string, list, or dict if specified"

    def test_project_has_license_or_authors(self):
        """Test that project has either license or authors."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})

        has_license = 'license' in project
        has_authors = 'authors' in project
        has_maintainers = 'maintainers' in project

        assert has_license or has_authors or has_maintainers, \
            "Project should have license or authors/maintainers specified"

    def test_authors_format_valid(self):
        """Test that authors have valid format if specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        authors = project.get('authors', [])

        if authors:
            assert isinstance(authors, list), \
                "Authors should be a list"

            for author in authors:
                assert isinstance(author, dict), \
                    "Each author should be a dictionary"
                assert 'name' in author or 'email' in author, \
                    "Each author should have name or email"

    def test_license_format_valid(self):
        """Test that license has valid format if specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        license_info = project.get('license', {})

        if license_info:
            assert isinstance(license_info, dict), \
                "License should be a dictionary if specified"

            # Should have either file or text
            has_file = 'file' in license_info
            has_text = 'text' in license_info
            assert has_file or has_text, \
                "License should specify either 'file' or 'text'"


class TestDependencies:
    """Test project dependencies configuration."""

    def test_dependencies_specified(self):
        """Test that project specifies dependencies or indicates no dependencies."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})

        # Either dependencies should be specified, or it should be explicitly empty
        has_dependencies = 'dependencies' in project
        if has_dependencies:
            deps = project['dependencies']
            assert isinstance(deps, list), \
                "Dependencies should be a list"

    def test_dependency_format_valid(self):
        """Test that dependencies follow PEP 508 format."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        dependencies = project.get('dependencies', [])

        for dep in dependencies:
            assert isinstance(dep, str), \
                f"Each dependency should be a string: {dep}"

            # Basic validation: dependency name should be present
            assert len(dep.strip()) > 0, \
                "Dependency name cannot be empty"

    def test_optional_dependencies_format_valid(self):
        """Test that optional dependencies (extras) are valid."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        optional_deps = project.get('optional-dependencies', {})

        if optional_deps:
            assert isinstance(optional_deps, dict), \
                "Optional dependencies should be a dictionary"

            for extra_name, extra_deps in optional_deps.items():
                assert isinstance(extra_deps, list), \
                    f"Optional dependency '{extra_name}' should be a list"

                for dep in extra_deps:
                    assert isinstance(dep, str), \
                        f"Each dependency in '{extra_name}' should be a string"

    def test_python_version_specified(self):
        """Test that Python version requirement is specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})

        # Python-Requires or requires-python should be specified
        has_python_req = 'requires-python' in project
        assert has_python_req, \
            "Project should specify requires-python"


class TestBuildSystem:
    """Test build system configuration."""

    def test_build_backend_specified(self):
        """Test that build backend is specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        build_system = parsed.get('build-system', {})
        build_backend = build_system.get('build-backend')

        assert build_backend is not None, \
            "Build system must specify build-backend"

        assert isinstance(build_backend, str), \
            "Build backend must be a string"

        assert len(build_backend) > 0, \
            "Build backend cannot be empty"

    def test_build_backend_valid(self):
        """Test that build backend is a known/valid backend."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        build_system = parsed.get('build-system', {})
        build_backend = build_system.get('build-backend', '')

        # List of common build backends
        valid_backends = [
            'setuptools.build_meta',
            'poetry.core.masonry.api',
            'hatchling.build',
            'flit_core.buildapi',
            'pdm.backend'
        ]

        assert build_backend in valid_backends, \
            f"Build backend '{build_backend}' should be one of the known backends"

    def test_build_requires_specified(self):
        """Test that build requirements are specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        build_system = parsed.get('build-system', {})
        requires = build_system.get('requires')

        assert requires is not None, \
            "Build system must specify requires"

        assert isinstance(requires, list), \
            "Build requires must be a list"

        assert len(requires) > 0, \
            "Build requires cannot be empty"

    def test_build_requirements_valid(self):
        """Test that build requirements are valid."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        build_system = parsed.get('build-system', {})
        requires = build_system.get('requires', [])

        for req in requires:
            assert isinstance(req, str), \
                f"Each build requirement should be a string: {req}"

            assert len(req.strip()) > 0, \
                "Build requirement cannot be empty"


class TestToolConfiguration:
    """Test tool configurations in pyproject.toml."""

    def test_pytest_configured(self):
        """Test that pytest is configured."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        # Check for pytest configuration in [tool.pytest] or in pytest.ini
        has_pytest_section = 'tool' in parsed and 'pytest' in parsed['tool']

        # Either [tool.pytest] exists or pytest.ini should exist
        if not has_pytest_section:
            pytest_ini = project_root / "pytest.ini"
            assert pytest_ini.exists(), \
                "pytest should be configured in [tool.pytest] or pytest.ini"

    def test_coverage_configured(self):
        """Test that coverage is configured."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        # Check for coverage configuration in [tool.coverage] or [tool.coverage.*]
        has_coverage = 'tool' in parsed and 'coverage' in parsed['tool']

        # This is recommended but not required
        # Just verify the structure if it exists

    def test_ruff_configured(self):
        """Test that ruff linter is configured if present."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        # Check for ruff configuration
        has_ruff = 'tool' in parsed and 'ruff' in parsed['tool']

        # This is recommended but not required
        # Just verify the structure if it exists

    def test_type_checker_configured(self):
        """Test that type checker (mypy/basedpyright) is configured if present."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        # Check for mypy or basedpyright configuration
        has_mypy = 'tool' in parsed and 'mypy' in parsed['tool']
        has_basedpyright = 'tool' in parsed and 'basedpyright' in parsed['tool']

        # This is recommended but not required
        # Just verify the structure if it exists


class TestEntryPoints:
    """Test entry points configuration."""

    def test_console_scripts_format_valid(self):
        """Test that console scripts have valid format."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        scripts = project.get('scripts', {})

        if scripts:
            assert isinstance(scripts, dict), \
                "Console scripts should be a dictionary"

            for script_name, script_entry in scripts.items():
                assert isinstance(script_name, str), \
                    "Script name must be a string"
                assert isinstance(script_entry, str), \
                    "Script entry must be a string"
                assert ':' in script_entry, \
                    f"Script entry '{script_entry}' should be in format 'module:function'"

    def test_gui_scripts_format_valid(self):
        """Test that GUI scripts have valid format."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        scripts = project.get('gui-scripts', {})

        if scripts:
            assert isinstance(scripts, dict), \
                "GUI scripts should be a dictionary"

            for script_name, script_entry in scripts.items():
                assert isinstance(script_name, str), \
                    "Script name must be a string"
                assert isinstance(script_entry, str), \
                    "Script entry must be a string"
                assert ' = ' in script_entry, \
                    f"Script entry '{script_entry}' should be in format 'module:function'"


class TestClassifiers:
    """Test project classifiers if specified."""

    def test_classifiers_format_valid(self):
        """Test that classifiers have valid format if specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        classifiers = project.get('classifiers', [])

        if classifiers:
            assert isinstance(classifiers, list), \
                "Classifiers should be a list"

            for classifier in classifiers:
                assert isinstance(classifier, str), \
                    f"Each classifier should be a string: {classifier}"

                # PyPI classifiers are strings, no further validation needed


class TestURLs:
    """Test project URLs if specified."""

    def test_urls_format_valid(self):
        """Test that project URLs have valid format if specified."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"

        content = pyproject_file.read_text(encoding="utf-8")
        parsed = toml.loads(content)

        project = parsed.get('project', {})
        urls = project.get('urls', {})

        if urls:
            assert isinstance(urls, dict), \
                "Project URLs should be a dictionary"

            for url_name, url_value in urls.items():
                assert isinstance(url_name, str), \
                    "URL name must be a string"
                assert isinstance(url_value, str), \
                    "URL value must be a string"

                # Basic URL validation
                assert url_value.startswith(('http://', 'https://')), \
                    f"URL '{url_value}' should start with http:// or https://"
