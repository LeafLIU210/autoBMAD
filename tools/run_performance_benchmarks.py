#!/usr/bin/env python3
"""CLI tool for running performance benchmarks.

Generates JSON and HTML reports with benchmark results and provides
CI integration support with pass/fail thresholds.

Task 6: Create benchmark runner and reporting
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Default benchmark paths
BENCHMARK_DIR = Path(__file__).parent.parent / "tests" / "benchmarks"
REPORT_DIR = Path(__file__).parent.parent / ".benchmarks"


def run_pytest_benchmarks(
    benchmark_dir: Path,
    verbose: bool = False,
    markers: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """Run pytest-benchmark tests.

    Args:
        benchmark_dir: Directory containing benchmark tests
        verbose: Enable verbose output
        markers: Optional pytest markers to filter by

    Returns:
        CompletedProcess with return code and output
    """
    cmd = [
        sys.executable, "-m", "pytest",
        str(benchmark_dir),
        "-v",
        "--tb=short",
        "--no-header",
    ]

    if verbose:
        cmd.append("-vv")

    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


def parse_benchmark_results(output: str) -> dict[str, Any]:
    """Parse pytest output to extract benchmark results.

    Args:
        output: Raw pytest output

    Returns:
        Dictionary with parsed results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
        },
    }

    for line in output.split("\n"):
        # Parse test results
        if "::" in line and ("PASSED" in line or "FAILED" in line):
            parts = line.split()
            test_name = parts[0] if parts else "unknown"
            status = "passed" if "PASSED" in line else "failed"

            results["tests"][test_name] = {
                "status": status,
            }
            results["summary"]["total"] += 1
            results["summary"][status] += 1

    return results


def generate_json_report(results: dict[str, Any], output_path: Path) -> None:
    """Generate JSON report file.

    Args:
        results: Benchmark results dictionary
        output_path: Path to write JSON report
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def generate_html_report(results: dict[str, Any], output_path: Path) -> None:
    """Generate HTML report file.

    Args:
        results: Benchmark results dictionary
        output_path: Path to write HTML report
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Benchmark Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .test-list {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .status-passed {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-failed {{
            color: #f44336;
            font-weight: bold;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .ci-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .ci-pass {{
            background: #4CAF50;
            color: white;
        }}
        .ci-fail {{
            background: #f44336;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>Performance Benchmark Report</h1>
    <div class="timestamp">Generated: {results['timestamp']}</div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-value">{results['summary']['total']}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #4CAF50;">{results['summary']['passed']}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #f44336;">{results['summary']['failed']}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #ff9800;">{results['summary']['errors']}</div>
            <div class="metric-label">Errors</div>
        </div>
        <br>
        <span class="ci-badge {'ci-pass' if results['summary']['failed'] == 0 else 'ci-fail'}">
            {'✓ CI Pass' if results['summary']['failed'] == 0 else '✗ CI Fail'}
        </span>
    </div>

    <div class="test-list">
        <h2>Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {generate_test_rows(results['tests'])}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_test_rows(tests: dict[str, Any]) -> str:
    """Generate HTML table rows for test results.

    Args:
        tests: Dictionary of test results

    Returns:
        HTML string for table rows
    """
    rows = []
    for test_name, test_data in tests.items():
        status_class = f"status-{test_data['status']}"
        status_icon = "✓" if test_data['status'] == "passed" else "✗"
        rows.append(
            f"<tr><td>{test_name}</td>"
            f"<td class='{status_class}'>{status_icon} {test_data['status'].upper()}</td></tr>"
        )
    return "\n".join(rows) if rows else "<tr><td colspan='2'>No tests found</td></tr>"


def check_ci_thresholds(results: dict[str, Any]) -> bool:
    """Check if results meet CI thresholds.

    Args:
        results: Benchmark results

    Returns:
        True if all thresholds pass
    """
    # All tests must pass
    return results["summary"]["failed"] == 0 and results["summary"]["errors"] == 0


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Run performance benchmarks and generate reports"
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=BENCHMARK_DIR,
        help="Directory containing benchmark tests",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPORT_DIR,
        help="Directory to write reports",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Generate JSON report",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Enable CI mode (fail on threshold violations)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--marker",
        "-m",
        action="append",
        dest="markers",
        help="Only run tests with given marker",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Performance Benchmark Runner")
    print("=" * 60)

    # Run benchmarks
    print("\nRunning benchmarks...")
    result = run_pytest_benchmarks(
        args.benchmark_dir,
        verbose=args.verbose,
        markers=args.markers,
    )

    # Parse results
    results = parse_benchmark_results(result.stdout + "\n" + result.stderr)

    # Print summary
    print("\n" + "=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    print(f"Total: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Errors: {results['summary']['errors']}")

    # Generate reports
    if args.json or args.html:
        print("\nGenerating reports...")

    if args.json:
        json_path = args.output_dir / "benchmark_report.json"
        generate_json_report(results, json_path)
        print(f"JSON report: {json_path}")

    if args.html:
        html_path = args.output_dir / "benchmark_report.html"
        generate_html_report(results, html_path)
        print(f"HTML report: {html_path}")

    # CI check
    if args.ci:
        print("\n" + "=" * 60)
        if check_ci_thresholds(results):
            print("✓ CI Thresholds: PASSED")
            return 0
        else:
            print("✗ CI Thresholds: FAILED")
            return 1

    # Return appropriate exit code
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
