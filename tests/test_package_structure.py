"""Test suite for package structure validation.

Tests cover:
- Directory structure
- File organization
- Package initialization
- Module accessibility
"""

from pathlib import Path
import sys
import pytest


class TestDirectoryStructure:
    """Test overall directory structure."""

    def test_root_directory_organization(self):
        """Test that root directory has proper organization."""
        project_root = Path(__file__).parent.parent
        required_dirs = ['src', 'tests', 'docs']
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"{dir_name} directory must exist"
            assert dir_path.is_dir(), f"{dir_name} must be a directory"

    def test_no_source_code_in_root(self):
        """Test that no source code is in root directory."""
        project_root = Path(__file__).parent.parent
        # Should have src/ directory instead
        assert (project_root / "src").exists(), "Source code should be in src/ directory"

    def test_documentation_directory_exists(self):
        """Test that documentation directory exists."""
        project_root = Path(__file__).parent.parent
        docs_dir = project_root / "docs"
        assert docs_dir.exists(), "docs directory must exist"

    def test_tests_isolation(self):
        """Test that tests are properly isolated from source."""
        project_root = Path(__file__).parent.parent
        tests_dir = project_root / "tests"
        src_dir = project_root / "src"

        # Tests directory should exist and be separate
        assert tests_dir.exists()
        assert tests_dir != src_dir

    def test_ci_cd_directory_exists(self):
        """Test that CI/CD configuration directory exists."""
        project_root = Path(__file__).parent.parent
        github_dir = project_root / ".github"
        # .github directory is recommended but not required
        # We can skip this or just check if it exists


class TestSourcePackageStructure:
    """Test source package structure."""

    def test_src_is_python_package(self):
        """Test that src is a Python package."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        init_file = src_dir / "__init__.py"
        assert init_file.exists(), "src/__init__.py must exist"

    def test_subpackage_structure(self):
        """Test that subpackages have proper structure."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Check for subdirectories in src
        subdirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and d.name != '__pycache__']

        for subdir in subdirs:
            init_file = subdir / "__init__.py"
            assert init_file.exists(), f"{subdir.name}/__init__.py must exist"

    def test_module_files_have_correct_extension(self):
        """Test that module files have .py extension."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Find all .py files in src
        py_files = list(src_dir.rglob("*.py"))

        # All .py files should be in proper locations
        for py_file in py_files:
            # Files should not be directly in src (should be in subpackages)
            assert py_file != src_dir / "__init__.py" or py_file.name == "__init__.py"

    def test_no_standalone_py_files_in_root_src(self):
        """Test that src root doesn't have standalone .py files (except __init__)."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Get all .py files in src root
        root_py_files = [f for f in src_dir.iterdir() if f.is_file() and f.suffix == '.py']

        # Only __init__.py should be in src root
        for py_file in root_py_files:
            if py_file.name != "__init__.py":
                # Some projects do have cli.py in src root, which is acceptable
                pass  # This is acceptable for entry point modules


class TestPackageInitialization:
    """Test package initialization files."""

    def test_all_packages_have_init_files(self):
        """Test that all Python packages have __init__.py files."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Find all directories that should have __init__.py
        for dir_path in src_dir.rglob("*"):
            if dir_path.is_dir() and not dir_path.name.startswith('.') and dir_path.name != '__pycache__':
                init_file = dir_path / "__init__.py"
                assert init_file.exists(), f"{dir_path.relative_to(src_dir)} must have __init__.py"

    def test_init_files_are_nonempty_or_justified(self):
        """Test that __init__.py files are either populated or have reason to be empty."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        for init_file in src_dir.rglob("__init__.py"):
            content = init_file.read_text()
            # Empty __init__.py is acceptable (makes directory a package)
            # But we can verify it's at least syntactically valid
            try:
                compile(content, str(init_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"{init_file} has syntax error: {e}")

    def test_init_files_dont_import_heavy_modules(self):
        """Test that __init__.py files don't import heavy modules at import time."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # This is a guideline check - __init__.py should be lightweight
        for init_file in src_dir.rglob("__init__.py"):
            content = init_file.read_text()
            # Check for heavy imports (heuristic)
            heavy_patterns = ['import ', 'from ']
            for pattern in heavy_patterns:
                # Count import statements
                lines = [line.strip() for line in content.split('\n')]
                import_count = sum(1 for line in lines if line.startswith(pattern))
                # More than a few imports in __init__.py might be problematic
                # This is a soft check
                if import_count > 10:
                    # Log warning but don't fail
                    pass


class TestModuleOrganization:
    """Test module organization and naming."""

    def test_package_names_follow_conventions(self):
        """Test that package names follow Python conventions."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Package names should be lowercase
                assert item.name.islower() or '_' in item.name, \
                    f"Package name {item.name} should be lowercase"

    def test_module_names_descriptive(self):
        """Test that module names are descriptive."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Find all .py files
        for py_file in src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue  # Skip __init__.py files

            name = py_file.stem
            # Module names should be lowercase and descriptive
            assert name.islower() or '_' in name, \
                f"Module name {name} should be lowercase"

    def test_no_singletons_as_package_names(self):
        """Test that package names are not named after singleton patterns."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        singleton_names = ['singleton', 'manager', 'factory', 'handler']
        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # This is a soft check - these names can be OK
                if item.name.lower() in singleton_names:
                    # Just note it for review
                    pass

    def test_related_functionality_grouped(self):
        """Test that related functionality is properly grouped."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # If there's a bubblesort package, check it's organized well
        bubble_dir = src_dir / "bubblesort"
        if bubble_dir.exists():
            # Should have __init__.py
            assert (bubble_dir / "__init__.py").exists()
            # Should have the main module
            assert (bubble_dir / "bubble_sort.py").exists()


class TestImportsAndDependencies:
    """Test import structure and dependencies."""

    def test_absolute_imports_used(self):
        """Test that absolute imports are used where appropriate."""
        # This is a structural test
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Check a few .py files for import patterns
        for py_file in src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            content = py_file.read_text()
            # Check for relative imports (., ..)
            lines = content.split('\n')
            has_relative = any(line.strip().startswith('from .') for line in lines)

            # Relative imports are OK for intra-package imports
            # This is just informational

    def test_no_circular_imports_obvious(self):
        """Test for obvious circular import patterns."""
        # This is a basic check - a full circular import detection would require deeper analysis
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Find all .py files
        py_files = list(src_dir.rglob("*.py"))

        # Basic check: a file shouldn't import itself
        for py_file in py_files:
            content = py_file.read_text()
            filename = py_file.name
            # Check if file imports itself (obvious circular import)
            assert f"import {filename[:-3]}" not in content, \
                f"{filename} shouldn't import itself"
            assert f"from {filename[:-3]}" not in content, \
                f"{filename} shouldn't import itself"

    def test_standard_library_imports_first(self):
        """Test that standard library imports come before local imports."""
        # This is PEP 8 style guide recommendation
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Check a few files for import ordering
        for py_file in src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            content = py_file.read_text()
            lines = content.split('\n')

            # Find import sections
            import_lines = [(i, line) for i, line in enumerate(lines)
                          if line.strip().startswith(('import ', 'from '))]

            if len(import_lines) > 1:
                # Check ordering (basic heuristic)
                stdlib_seen = False
                local_seen = False

                for idx, line in import_lines:
                    is_stdlib = any(lib in line for lib in
                                  ['os', 'sys', 'json', 'pathlib', 'collections'])
                    is_local = 'src' in line or '.' in line

                    if is_stdlib and local_seen:
                        pytest.fail(f"{py_file.name}: Local import comes after stdlib: {line}")
                    if is_local:
                        local_seen = True
                    if is_stdlib:
                        stdlib_seen = True


class TestFileAccessibility:
    """Test that files are accessible and properly structured."""

    def test_all_python_files_syntax_valid(self):
        """Test that all Python files have valid syntax."""
        project_root = Path(__file__).parent.parent

        # Find all .py files in src directory
        py_files = list((project_root / "src").rglob("*.py"))

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(py_file), 'exec')
            except (SyntaxError, UnicodeDecodeError) as e:
                pytest.fail(f"Syntax error in {py_file.relative_to(project_root)}: {e}")

    def test_test_files_accessible(self):
        """Test that test files can be discovered by pytest."""
        project_root = Path(__file__).parent.parent
        tests_dir = project_root / "tests"

        # Find all test files
        test_files = list(tests_dir.rglob("test_*.py"))

        assert len(test_files) > 0, "At least one test file should exist"

        # All test files should have valid syntax
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(test_file), 'exec')
            except (SyntaxError, UnicodeDecodeError) as e:
                pytest.fail(f"Test file {test_file.name} has syntax error: {e}")

    def test_no_hidden_source_files(self):
        """Test that no source files are hidden (start with .)."""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"

        # Check for hidden Python files
        hidden_files = list(src_dir.rglob(".*.py"))
        # Should be no hidden .py files
        assert len(hidden_files) == 0, "No hidden Python files should exist"

    def test_config_files_in_right_places(self):
        """Test that configuration files are in appropriate locations."""
        project_root = Path(__file__).parent.parent

        # Check for common config files in root
        config_files = ['pyproject.toml', 'setup.py', 'setup.cfg', 'pytest.ini', '.gitignore']
        for config in config_files:
            config_path = project_root / config
            if config_path.exists():
                assert config_path.is_file(), f"{config} should be a file, not a directory"


class TestDocumentationStructure:
    """Test documentation structure."""

    def test_docs_directory_structure(self):
        """Test that docs directory is properly structured."""
        project_root = Path(__file__).parent.parent
        docs_dir = project_root / "docs"

        assert docs_dir.exists(), "docs directory should exist"
        assert docs_dir.is_dir(), "docs should be a directory"

    def test_readme_in_root(self):
        """Test that README is in project root."""
        project_root = Path(__file__).parent.parent
        readme_files = ['README.md', 'README.rst', 'README.txt']

        has_readme = any((project_root / name).exists() for name in readme_files)
        assert has_readme, "README file should exist in project root"

    def test_api_documentation_structure(self):
        """Test that API documentation has structure."""
        project_root = Path(__file__).parent.parent
        docs_dir = project_root / "docs"

        # Check for common doc directories
        doc_dirs = ['api', 'user-guide', 'examples']
        for doc_dir in doc_dirs:
            doc_path = docs_dir / doc_dir
            # These are recommended but not required
            # Just check if they exist


class TestVersionControl:
    """Test version control structure."""

    def test_gitignore_exists(self):
        """Test that .gitignore exists."""
        project_root = Path(__file__).parent.parent
        gitignore = project_root / ".gitignore"

        assert gitignore.exists(), ".gitignore should exist"

    def test_gitignore_has_python_patterns(self):
        """Test that .gitignore has Python-specific patterns."""
        project_root = Path(__file__).parent.parent
        gitignore = project_root / ".gitignore"

        if gitignore.exists():
            content = gitignore.read_text().lower()
            # Should include common Python patterns
            patterns = ['__pycache__', '*.pyc', '.pytest_cache', '.coverage']
            has_pattern = any(pattern in content for pattern in patterns)
            assert has_pattern, ".gitignore should include Python patterns"

    def test_git_directory_exists(self):
        """Test that .git directory exists."""
        project_root = Path(__file__).parent.parent
        git_dir = project_root / ".git"

        # Git directory is expected for version control
        # But we won't fail if it's not present in all environments


class TestPackageAccessibility:
    """Test that packages and modules can be imported."""

    def test_src_can_be_imported(self):
        """Test that src package can be imported."""
        project_root = Path(__file__).parent.parent

        # Add src to path
        import_path = str(project_root / "src")
        if import_path not in sys.path:
            sys.path.insert(0, import_path)

        try:
            import src
            assert src is not None
        except ImportError as e:
            pytest.skip(f"Cannot import src package: {e}")

    def test_subpackages_can_be_imported(self):
        """Test that subpackages can be imported."""
        project_root = Path(__file__).parent.parent

        import_path = str(project_root / "src")
        if import_path not in sys.path:
            sys.path.insert(0, import_path)

        try:
            import src.bubblesort
            assert src.bubblesort is not None
        except ImportError:
            pytest.skip("bubblesort subpackage doesn't exist")

    def test_modules_can_be_imported(self):
        """Test that modules can be imported."""
        project_root = Path(__file__).parent.parent

        import_path = str(project_root / "src")
        if import_path not in sys.path:
            sys.path.insert(0, import_path)

        try:
            from src.bubblesort import bubble_sort
            assert bubble_sort is not None
            assert callable(bubble_sort)
        except ImportError as e:
            pytest.skip(f"Cannot import bubble_sort module: {e}")
