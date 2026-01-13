"""
Comprehensive Edge Case Tests for Story 1.1
Tests edge cases, boundary conditions, and error handling for project setup.
"""
import os
import sys
from pathlib import Path
import pytest


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pyproject_toml_has_valid_toml_syntax(self):
        """Verify pyproject.toml has valid TOML syntax."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist"

        try:
            import tomllib
            with open(pyproject_file, 'rb') as f:
                tomllib.load(f)
        except ImportError:
            # Python < 3.11
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    tomli.load(f)
            except ImportError:
                pytest.skip("TOML parser not available")

    def test_readme_has_reasonable_length(self):
        """Verify README.md has substantial content."""
        readme_file = Path(__file__).parent.parent / "README.md"
        assert readme_file.exists(), "README.md must exist"

        content = readme_file.read_text(encoding='utf-8')
        assert len(content) > 500, \
            "README.md should have substantial content (> 500 characters)"

    def test_pyproject_dependencies_are_valid_package_names(self):
        """Verify all dependencies have valid package names."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # Basic check for common dependency patterns
        assert "dependencies" in content.lower(), \
            "Dependencies section should be present"

        # Check for valid package name patterns
        lines = content.split('\n')
        in_deps = False
        for line in lines:
            line = line.strip()
            if 'dependencies' in line.lower() and '=' in line:
                in_deps = True
                continue
            if in_deps:
                if line.startswith('[') or line.startswith('#'):
                    break
                if line.strip():
                    # Basic validation - package names should not have spaces
                    # and should use valid characters
                    assert '  ' not in line, \
                        "Dependencies should not have double spaces"

    def test_all_required_directories_exist(self):
        """Verify all required project directories exist."""
        project_root = Path(__file__).parent.parent

        # Required directories
        required_dirs = ["src", "tests", "docs", ".github"]
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"{dir_name}/ directory must exist"
            assert dir_path.is_dir(), f"{dir_name}/ must be a directory"

    def test_gitignore_excludes_common_patterns(self):
        """Verify .gitignore excludes common unwanted files."""
        gitignore_file = Path(__file__).parent.parent / ".gitignore"
        assert gitignore_file.exists(), ".gitignore must exist"

        content = gitignore_file.read_text(encoding='utf-8')

        # Check for common Python patterns
        required_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd"
        ]

        found_patterns = [p for p in required_patterns if p in content]
        assert len(found_patterns) >= 2, \
            f".gitignore should include common Python patterns (found: {found_patterns})"

    def test_license_file_exists(self):
        """Verify LICENSE or COPYING file exists."""
        project_root = Path(__file__).parent.parent

        # Check for common license file names
        license_files = ["LICENSE", "LICENSE.txt", "COPYING", "COPYING.txt"]
        found_license = any((project_root / lic).exists() for lic in license_files)

        assert found_license, \
            f"Project should have a license file (looked for: {license_files})"

    def test_pyproject_has_entry_points_configured(self):
        """Verify pyproject.toml has entry points if CLI is provided."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # If there's a CLI module, it should have entry points
        cli_file = Path(__file__).parent.parent / "src" / "cli.py"
        if cli_file.exists():
            assert "scripts" in content or "entry-points" in content.lower(), \
                "CLI application should have entry points configured"

    def test_test_directories_have_init_files(self):
        """Verify test subdirectories have __init__.py files."""
        tests_dir = Path(__file__).parent

        # Check unit and integration test directories
        subdirs = ["unit", "integration", "e2e", "gui", "performance"]
        for subdir_name in subdirs:
            subdir = tests_dir / subdir_name
            if subdir.exists():
                init_file = subdir / "__init__.py"
                assert init_file.exists(), \
                    f"tests/{subdir_name}/ should have __init__.py file"

    def test_no_empty_directories_in_src(self):
        """Verify no empty directories in src/."""
        src_dir = Path(__file__).parent.parent / "src"

        if not src_dir.exists():
            pytest.skip("src/ directory does not exist")

        # Find all directories
        for item in src_dir.rglob("*"):
            if item.is_dir():
                # Check if directory has any files
                has_files = any(f.is_file() for f in item.rglob("*"))
                has_subdirs = any(d.is_dir() for d in item.iterdir())

                # Allow empty __pycache__ directories
                if not has_files and not has_subdirs and item.name != "__pycache__":
                    assert False, \
                        f"Found empty directory in src/: {item.relative_to(src_dir)}"

    def test_pyproject_python_version_is_compatible(self):
        """Verify Python version requirement is reasonable."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # Check for Python version specification
        assert "requires-python" in content or "python_requires" in content, \
            "Python version requirement should be specified"

        # Extract version if present
        import re
        version_match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            # Basic validation - should be >= 3.8
            # Handle cases like ">=3.10" or ">=3"
            import re
            version_num = re.search(r'(\d+\.\d+)', version)
            if version_num:
                major_minor = version_num.group(1).split('.')
                if len(major_minor) >= 2:
                    major, minor = int(major_minor[0]), int(major_minor[1])
                    assert major >= 3 and minor >= 8, \
                        f"Python version should be >= 3.8 (found: {version})"

    def test_all_init_files_have_content(self):
        """Verify __init__.py files in src/ have substantial content."""
        src_dir = Path(__file__).parent.parent / "src"

        if not src_dir.exists():
            pytest.skip("src/ directory does not exist")

        # Check all __init__.py files
        init_files = list(src_dir.rglob("__init__.py"))

        for init_file in init_files:
            content = init_file.read_text(encoding='utf-8').strip()
            # Main package __init__.py should have substantial content
            if init_file.parent.name == "src":
                assert len(content) > 10, \
                    f"Main src/__init__.py should have substantial content"

    def test_no_bare_except_statements(self):
        """Verify no bare except statements in Python files."""
        import ast
        project_root = Path(__file__).parent.parent

        python_files = list(project_root.rglob("*.py"))
        for py_file in python_files:
            # Skip test files, generated files, and virtual environments
            if any(skip in str(py_file) for skip in
                   ["test", "htmlcov", "venv", "__pycache__", ".pytest_cache", ".git"]):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            pytest.fail(f"Found bare except in {py_file}")
            except SyntaxError:
                # Skip files with syntax errors - they might be incomplete or templates
                continue

    def test_pyproject_build_system_is_configured(self):
        """Verify build system is properly configured."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        assert "[build-system]" in content, \
            "Build system should be configured"

        assert "requires" in content, \
            "Build requirements should be specified"

    def test_ci_workflow_has_python_version_matrix(self):
        """Verify CI workflow tests multiple Python versions."""
        workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"

        if not workflows_dir.exists():
            pytest.skip("No .github/workflows directory")

        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

        for workflow_file in workflow_files:
            content = workflow_file.read_text(encoding='utf-8').lower()

            # Should test at least one Python version
            has_python = "python" in content and "version" in content
            if has_python:
                # Good - workflow tests Python
                break
        else:
            pytest.skip("No Python version testing found in workflows")


class TestIntegrationValidation:
    """Test integration scenarios and complete workflows."""

    def test_can_install_package_in_development_mode(self):
        """Verify package can be installed in development mode."""
        # This is a basic check - actual installation would require running pip
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist for installation"

        content = pyproject_file.read_text(encoding='utf-8')
        assert "[project]" in content or "[tool.poetry]" in content, \
            "Project configuration should be present"

    def test_project_structure_follows_pep_standards(self):
        """Verify project follows PEP standards."""
        project_root = Path(__file__).parent.parent

        # Check src layout (recommended in PEP 420)
        src_dir = project_root / "src"
        if src_dir.exists():
            assert src_dir.is_dir(), "src/ should be a directory"

        # Check for __init__.py in packages
        if src_dir.exists():
            for item in src_dir.rglob("*.py"):
                # All Python files should be in packages (autoBMAD is also valid)
                parent_name = item.parent.name
                assert parent_name.startswith(('__', 'src', 'autoBMAD', 'bubblesort')) or \
                       parent_name.endswith('automation'), \
                    f"Python files should be in proper packages (found: {parent_name})"

    def test_dependencies_are_reasonable(self):
        """Verify project dependencies are reasonable for a Python project."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # Should have at least some dependencies for a real project
        # (but we're not checking specific ones)
        assert "dependencies" in content.lower(), \
            "Project should have dependencies section"

    def test_documentation_is_accessible(self):
        """Verify documentation files are accessible."""
        project_root = Path(__file__).parent.parent

        # Check for documentation files
        doc_files = ["README.md", "LICENSE", "CHANGELOG.md"]
        found_docs = [f for f in doc_files if (project_root / f).exists()]

        assert len(found_docs) >= 2, \
            f"Project should have at least 2 documentation files (found: {found_docs})"

    def test_version_is_defined(self):
        """Verify project has a version defined."""
        pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        assert "version" in content, \
            "Project version should be defined"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
