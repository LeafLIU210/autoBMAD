"""
Tests for QA Tools Integration Module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'bmad-workflow'))

from qa_tools_integration import BasedPyrightResult, FixtestResult

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

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
