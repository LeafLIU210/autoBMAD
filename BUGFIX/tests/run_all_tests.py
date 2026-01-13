#!/usr/bin/env python3
"""
Test Runner

Run all BUGFIX test suites.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

# Import all test modules
from test_cancel_scope import TestCancelScopeFixes
from test_sdk_sessions import TestSDKSessionManager
from test_timeout_handling import TestTimeoutHandling
from test_resource_cleanup import TestResourceCleanup
from test_integration import TestIntegrationScenarios
from test_performance import TestPerformanceBenchmarks


class TestRunner:
    """Test Runner"""

    def __init__(self):
        self.results = []
        self.start_time = None

    def run_test_class(self, test_class, test_name):
        """Run a test class"""
        print(f"\n{'='*60}")
        print(f"Running test: {test_name}")
        print(f"{'='*60}")

        test_instance = test_class()
        methods = [m for m in dir(test_instance) if m.startswith('test_')]

        passed = 0
        failed = 0
        errors = []

        for method_name in methods:
            try:
                print(f"\n  Test: {method_name}...", end=" ")
                method = getattr(test_instance, method_name)
                method()
                print("PASS")
                passed += 1
            except Exception as e:
                print("FAIL")
                failed += 1
                errors.append({
                    "test": method_name,
                    "error": str(e),
                    "traceback": str(sys.exc_info()[2])
                })

        result = {
            "name": test_name,
            "total": len(methods),
            "passed": passed,
            "failed": failed,
            "errors": errors
        }

        self.results.append(result)

        print(f"\n{test_name} Results:")
        print(f"  Total: {result['total']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Failed: {result['failed']}")

        if result['failed'] > 0:
            print(f"\n  Failed tests:")
            for error in errors:
                print(f"    - {error['test']}: {error['error']}")

        return result['failed'] == 0

    def run_all_tests(self):
        """Run all tests"""
        self.start_time = time.time()

        print("\n" + "="*60)
        print("BUGFIX_20260107 Test Suite")
        print("="*60)
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Define test classes and names
        test_suites = [
            (TestCancelScopeFixes, "Cancel Scope Fix Tests"),
            (TestSDKSessionManager, "SDK Session Management Tests"),
            (TestTimeoutHandling, "Timeout Handling Tests"),
            (TestResourceCleanup, "Resource Cleanup Tests"),
            (TestIntegrationScenarios, "Integration Tests"),
            (TestPerformanceBenchmarks, "Performance Tests")
        ]

        all_passed = True

        # Run each test suite
        for test_class, test_name in test_suites:
            if not self.run_test_class(test_class, test_name):
                all_passed = False

        # Print summary
        self.print_summary()

        return all_passed

    def print_summary(self):
        """Print test summary"""
        total_time = time.time() - self.start_time

        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)

        total_tests = sum(r['total'] for r in self.results)
        total_passed = sum(r['passed'] for r in self.results)
        total_failed = sum(r['failed'] for r in self.results)

        print(f"\nTotal runtime: {total_time:.3f}s")
        print(f"Total tests: {total_tests}")
        print(f"Total passed: {total_passed}")
        print(f"Total failed: {total_failed}")
        print(f"Success rate: {total_passed/total_tests*100:.1f}%")

        if total_failed == 0:
            print("\nSUCCESS: All tests passed!")
        else:
            print(f"\nWARNING: {total_failed} tests failed")

        print("\nTest suite details:")
        for result in self.results:
            status = "PASS" if result['failed'] == 0 else "FAIL"
            print(f"  {status} {result['name']}: {result['passed']}/{result['total']}")

        # Save results to file
        self.save_results()

    def save_results(self):
        """Save test results"""
        results_file = Path(__file__).parent / "test_results.json"

        import json

        results_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_time": time.time() - self.start_time,
            "summary": {
                "total": sum(r['total'] for r in self.results),
                "passed": sum(r['passed'] for r in self.results),
                "failed": sum(r['failed'] for r in self.results),
            },
            "results": self.results
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()

    sys.exit(0 if success else 1)
