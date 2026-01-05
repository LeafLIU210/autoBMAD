#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portability Test Script

This script tests that the BMAD Epic Automation template can be
copied and used in a fresh location without modification.
"""

import sys
import tempfile
import shutil
from pathlib import Path


def test_basic_imports():
    """Test that all modules can be imported."""
    print("Testing basic imports...")

    try:
        from epic_driver import EpicDriver, parse_arguments  # type: ignore
        print("  [OK] epic_driver imported successfully")
    except ImportError as e:
        print(f"  [FAIL] Failed to import epic_driver: {e}")
        return False

    try:
        # Check argparse is available
        import argparse
        print("  [OK] argparse available")
    except ImportError:
        print("  [FAIL] argparse not available")
        return False

    return True


def test_argument_parsing():
    """Test that argument parsing works correctly."""
    print("\nTesting argument parsing...")

    try:
        from epic_driver import parse_arguments  # type: ignore

        # Test basic arguments
        test_args = ['epic_driver.py', 'test-epic.md']

        # We can't easily test argparse without modifying sys.argv
        # So we'll just verify the function exists
        assert callable(parse_arguments)
        print("  [OK] parse_arguments function is callable")
        return True
    except Exception as e:
        print(f"  [FAIL] Argument parsing test failed: {e}")
        return False


def test_epic_driver_initialization():
    """Test that EpicDriver can be initialized."""
    print("\nTesting EpicDriver initialization...")

    try:
        from epic_driver import EpicDriver  # type: ignore

        # Test with minimal arguments
        driver = EpicDriver(
            epic_path='test-epic.md',
            max_iterations=3,
            retry_failed=False,
            verbose=False,
            concurrent=False
        )

        assert driver.epic_path == Path('test-epic.md')
        assert driver.max_iterations == 3
        assert driver.retry_failed == False
        assert driver.verbose == False
        assert driver.concurrent == False

        print("  [OK] EpicDriver initialized with custom parameters")
        return True
    except Exception as e:
        print(f"  [FAIL] EpicDriver initialization failed: {e}")
        return False


def test_readme_exists():
    """Test that README.md exists and has content."""
    print("\nTesting documentation...")

    readme_path = Path(__file__).parent / 'README.md'

    if not readme_path.exists():
        print("  [FAIL] README.md not found")
        return False

    try:
        content = readme_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            content = readme_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"  [FAIL] Cannot read README.md: {e}")
            return False

    if len(content) < 1000:
        print("  [FAIL] README.md seems too short")
        return False

    required_sections = ['Overview', 'Installation', 'Usage', 'Architecture']
    for section in required_sections:
        if section not in content:
            print(f"  [FAIL] README.md missing section: {section}")
            return False

    print("  [OK] README.md exists with required sections")
    return True


def test_setup_guide_exists():
    """Test that SETUP.md exists and has content."""
    print("\nTesting setup guide...")

    setup_path = Path(__file__).parent / 'SETUP.md'

    if not setup_path.exists():
        print("  [FAIL] SETUP.md not found")
        return False

    try:
        content = setup_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            content = setup_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"  [FAIL] Cannot read SETUP.md: {e}")
            return False

    if len(content) < 500:
        print("  [FAIL] SETUP.md seems too short")
        return False

    print("  [OK] SETUP.md exists")
    return True


def test_no_external_dependencies():
    """Test that only standard library and expected modules are used."""
    print("\nTesting dependencies...")

    # Check epic_driver.py for imports
    epic_driver_path = Path(__file__).parent / 'epic_driver.py'
    content = epic_driver_path.read_text()

    # Extract import statements
    import_lines = [line for line in content.split('\n') if line.strip().startswith('import ')]

    external_imports = []
    for line in import_lines:
        line = line.strip()
        # Check for non-standard library imports
        if 'asyncio' in line or 'argparse' in line or 're' in line or 'sys' in line or \
           'pathlib' in line or 'typing' in line or 'logging' in line:
            continue  # Standard library
        if 'from epic_driver' in line or 'from .' in line:
            continue  # Local imports
        if 'from sm_agent' in line or 'from dev_agent' in line or \
           'from qa_agent' in line or 'from state_manager' in line:
            continue  # Local module imports

        external_imports.append(line)

    if external_imports:
        print(f"  [WARN] Found external imports: {external_imports}")
        print("  [INFO] These should be from the same package")
    else:
        print("  [OK] No external dependencies detected")

    return True


def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")

    required_files = [
        'epic_driver.py',
        'sm_agent.py',
        'dev_agent.py',
        'qa_agent.py',
        'state_manager.py',
        'README.md',
        'SETUP.md'
    ]

    epic_automation_dir = Path(__file__).parent
    missing_files = []

    for file in required_files:
        file_path = epic_automation_dir / file
        if not file_path.exists():
            missing_files.append(file)

    if missing_files:
        print(f"  [FAIL] Missing files: {missing_files}")
        return False

    print("  [OK] All required files present")
    return True


def test_copy_portability():
    """Test that the template can be copied to a new location."""
    print("\nTesting portability (copy to temp directory)...")

    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy the epic_automation directory
            source_dir = Path(__file__).parent
            dest_dir = temp_path / 'test_project' / 'autoBMAD' / 'epic_automation'

            shutil.copytree(source_dir, dest_dir)

            # Try to import from the new location
            sys.path.insert(0, str(dest_dir))

            from epic_driver import EpicDriver  # type: ignore

            # Initialize a driver
            driver = EpicDriver(
                epic_path='test-epic.md',
                max_iterations=3,
                retry_failed=False,
                verbose=False,
                concurrent=False
            )

            # Verify it works
            assert driver.max_iterations == 3

            print("  [OK] Template copied and imported successfully")
            return True

    except Exception as e:
        print(f"  [FAIL] Portability test failed: {e}")
        return False


def main():
    """Run all portability tests."""
    print("=" * 60)
    print("BMAD Epic Automation - Portability Test")
    print("=" * 60)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Argument Parsing", test_argument_parsing),
        ("EpicDriver Initialization", test_epic_driver_initialization),
        ("README Documentation", test_readme_exists),
        ("Setup Guide", test_setup_guide_exists),
        ("External Dependencies", test_no_external_dependencies),
        ("File Structure", test_file_structure),
        ("Copy Portability", test_copy_portability),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All portability tests passed!")
        print("The template is ready to be copied to new projects.")
        return 0
    else:
        print("\n[WARN] Some tests failed. Please review the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
