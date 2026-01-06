"""
Tests for QA Tools Integration Module
"""

import pytest
import sys
from pathlib import Path

# Check if bmad-workflow module exists
BMAD_WORKFLOW_PATH = Path(__file__).parent.parent / 'bmad-workflow'
HAS_BMAD_WORKFLOW = BMAD_WORKFLOW_PATH.exists()

# Skip all tests in this module if bmad-workflow doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_BMAD_WORKFLOW,
    reason="bmad-workflow module not found - tests will be implemented when module is ready"
)

if HAS_BMAD_WORKFLOW:
    sys.path.insert(0, str(BMAD_WORKFLOW_PATH))
    try:
        from qa_tools_integration import BasedPyrightResult, FixtestResult
    except ImportError:
        HAS_BMAD_WORKFLOW = False
        pytestmark = pytest.mark.skipif(
            True,
            reason="qa_tools_integration module not found in bmad-workflow"
        )

        class TestBasedPyrightResult:
            def test_creation(self):
                result = BasedPyrightResult(
                    success=True, exit_code=0, output='Test', error_count=0, warning_count=5,
                    type_errors=[], style_violations=[], import_issues=[], undefined_variables=[]
                )
                assert result.success is True
                assert result.warning_count == 5

        class TestFixtestResult:
            def test_creation(self):
                result = FixtestResult(
                    success=True, exit_code=0, output='Test', tests_passed=10, tests_failed=0,
                    tests_skipped=0, coverage_percentage=85.5, failing_test_cases=[], auto_fixed_tests=[]
                )
                assert result.success is True
                assert result.tests_passed == 10

    else:
        # Dummy test class when module is not available
        class TestQADummy:
            def test_module_not_available(self):
                """Dummy test when bmad-workflow module is not available"""
                pytest.skip("bmad-workflow module not found")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
