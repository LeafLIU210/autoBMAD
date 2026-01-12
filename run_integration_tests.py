#!/usr/bin/env python
"""Run integration tests and generate coverage report"""

import subprocess
import sys

def run_tests():
    """Run integration tests with coverage"""
    cmd = [
        "pytest",
        "tests/integration",
        "--cov=autoBMAD/epic_automation",
        "--cov-report=html",
        "--cov-report=term",
        "--no-header",
        "-v"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Tests timed out after 10 minutes", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())