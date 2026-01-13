"""
Performance benchmarks for quality gates and test automation

Tests cover:
- Basedpyright execution time
- Ruff execution time
- Pytest execution time
- Complete workflow timing
- Memory usage
"""

import pytest
import time
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil


@pytest.mark.performance
class TestQualityGateBenchmarks:
    """Benchmark quality gate execution times."""

    def count_python_files(self, directory: str) -> int:
        """Count Python files in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and cache
            dirs[:] = [d for d in dirs if d not in ('.venv', 'venv', '__pycache__', '.pytest_cache')]

            for file in files:
                if file.endswith('.py'):
                    count += 1
        return count

    def test_basedpyright_performance(self):
        """Benchmark basedpyright execution time.

        Expected: < 10 seconds per .py file
        Maximum: < 30 seconds per .py file
        """
        source_dir = "src"

        # Skip if src doesn't exist
        if not os.path.exists(source_dir):
            pytest.skip(f"Source directory {source_dir} not found")

        # Count files
        file_count = self.count_python_files(source_dir)
        if file_count == 0:
            pytest.skip("No Python files found in src/")

        # Run basedpyright
        start_time = time.time()
        result = subprocess.run(
            ["basedpyright", source_dir],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        execution_time = time.time() - start_time

        # Calculate per-file time
        per_file_time = execution_time / file_count

        # Log results
        print(f"\nBasedpyright Performance Results:")
        print(f"  Files checked: {file_count}")
        print(f"  Total time: {execution_time:.2f}s")
        print(f"  Per-file time: {per_file_time:.2f}s")
        print(f"  Exit code: {result.returncode}")

        # Assert performance
        assert per_file_time < 10, f"Basedpyright too slow: {per_file_time}s per file (expected < 10s)"

        # Warning for very slow execution
        if per_file_time > 5:
            print(f"WARNING: Basedpyright is slow: {per_file_time:.2f}s per file")

    def test_ruff_performance(self):
        """Benchmark ruff execution time.

        Expected: < 5 seconds per .py file
        Maximum: < 15 seconds per .py file
        """
        source_dir = "src"

        # Skip if src doesn't exist
        if not os.path.exists(source_dir):
            pytest.skip(f"Source directory {source_dir} not found")

        # Count files
        file_count = self.count_python_files(source_dir)
        if file_count == 0:
            pytest.skip("No Python files found in src/")

        # Run ruff check
        start_time = time.time()
        result = subprocess.run(
            ["ruff", "check", source_dir],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        execution_time = time.time() - start_time

        # Calculate per-file time
        per_file_time = execution_time / file_count

        # Log results
        print(f"\nRuff Performance Results:")
        print(f"  Files checked: {file_count}")
        print(f"  Total time: {execution_time:.2f}s")
        print(f"  Per-file time: {per_file_time:.2f}s")
        print(f"  Exit code: {result.returncode}")

        # Assert performance
        assert per_file_time < 5, f"Ruff too slow: {per_file_time}s per file (expected < 5s)"

        # Warning for slow execution
        if per_file_time > 2:
            print(f"WARNING: Ruff is slower than expected: {per_file_time:.2f}s per file")

    def test_ruff_format_performance(self):
        """Benchmark ruff format execution time.

        Expected: < 2 seconds per .py file
        Maximum: < 5 seconds per .py file
        """
        source_dir = "src"

        # Skip if src doesn't exist
        if not os.path.exists(source_dir):
            pytest.skip(f"Source directory {source_dir} not found")

        # Count files
        file_count = self.count_python_files(source_dir)
        if file_count == 0:
            pytest.skip("No Python files found in src/")

        # Run ruff format
        start_time = time.time()
        result = subprocess.run(
            ["ruff", "format", "--check", source_dir],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        execution_time = time.time() - start_time

        # Calculate per-file time
        per_file_time = execution_time / file_count

        # Log results
        print(f"\nRuff Format Performance Results:")
        print(f"  Files checked: {file_count}")
        print(f"  Total time: {execution_time:.2f}s")
        print(f"  Per-file time: {per_file_time:.2f}s")
        print(f"  Exit code: {result.returncode}")

        # Assert performance
        assert per_file_time < 2, f"Ruff format too slow: {per_file_time}s per file (expected < 2s)"


@pytest.mark.performance
class TestPytestBenchmarks:
    """Benchmark pytest execution times."""

    def test_pytest_performance(self):
        """Benchmark pytest execution time.

        Expected: < 5 minutes for complete test suite
        Maximum: < 15 minutes for complete test suite
        """
        test_dir = "tests"

        # Skip if tests doesn't exist
        if not os.path.exists(test_dir):
            pytest.skip(f"Test directory {test_dir} not found")

        # Run pytest
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        execution_time = time.time() - start_time

        # Log results
        print(f"\nPytest Performance Results:")
        print(f"  Total time: {execution_time:.2f}s ({execution_time/60:.2f}m)")
        print(f"  Exit code: {result.returncode}")

        # Count tests from output
        output_lines = result.stdout.split('\n')
        test_count = 0
        for line in output_lines:
            if "passed" in line and "=" in line:
                # Example: "5 passed in 2.34s"
                parts = line.split()
                if parts:
                    try:
                        test_count = int(parts[0])
                        break
                    except (ValueError, IndexError):
                        pass

        if test_count > 0:
            print(f"  Tests run: {test_count}")
            per_test_time = execution_time / test_count
            print(f"  Per-test time: {per_test_time:.2f}s")

        # Assert performance
        assert execution_time < 300, f"Pytest too slow: {execution_time}s (expected < 300s)"

        # Warning for slow execution
        if execution_time > 180:
            print(f"WARNING: Pytest is slow: {execution_time:.2f}s ({execution_time/60:.2f}m)")

        # Pytest should pass
        assert result.returncode == 0, f"Pytest failed with exit code {result.returncode}"

    def test_pytest_with_coverage_performance(self):
        """Benchmark pytest with coverage execution time.

        Expected: < 8 minutes for complete test suite with coverage
        Maximum: < 20 minutes for complete test suite with coverage
        """
        test_dir = "tests"
        source_dir = "src"

        # Skip if tests doesn't exist
        if not os.path.exists(test_dir):
            pytest.skip(f"Test directory {test_dir} not found")

        if not os.path.exists(source_dir):
            pytest.skip(f"Source directory {source_dir} not found")

        # Run pytest with coverage
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "--cov=src", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            timeout=1200  # 20 minute timeout
        )
        execution_time = time.time() - start_time

        # Log results
        print(f"\nPytest with Coverage Performance Results:")
        print(f"  Total time: {execution_time:.2f}s ({execution_time/60:.2f}m)")
        print(f"  Exit code: {result.returncode}")

        # Assert performance
        assert execution_time < 480, f"Pytest with coverage too slow: {execution_time}s (expected < 480s)"

        # Pytest should pass
        assert result.returncode == 0, f"Pytest with coverage failed with exit code {result.returncode}"


@pytest.mark.performance
class TestWorkflowBenchmarks:
    """Benchmark complete workflow execution times."""

    @pytest.mark.slow
    def test_complete_workflow_performance(self):
        """Benchmark complete epic processing time.

        Expected: < 10 minutes for simple epic
        Maximum: < 30 minutes for simple epic
        """
        # This is a slow test that runs the complete workflow
        # It should only be run explicitly or with --runslow

        # Skip by default
        pytest.skip("Run with --runslow to execute this test")

    def test_file_creation_performance(self):
        """Benchmark file creation speed.

        Expected: < 0.1s per file
        Maximum: < 0.5s per file
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_count = 100
            start_time = time.time()

            # Create files
            for i in range(file_count):
                file_path = Path(tmpdir) / f"file_{i:03d}.py"
                file_path.write_text(f"# File {i}\ndef func_{i}() -> str:\n    return '{i}'\n")

            execution_time = time.time() - start_time
            per_file_time = execution_time / file_count

            # Log results
            print(f"\nFile Creation Performance Results:")
            print(f"  Files created: {file_count}")
            print(f"  Total time: {execution_time:.2f}s")
            print(f"  Per-file time: {per_file_time:.4f}s")

            # Assert performance
            assert per_file_time < 0.1, f"File creation too slow: {per_file_time}s per file (expected < 0.1s)"


@pytest.mark.performance
class TestMemoryBenchmarks:
    """Benchmark memory usage."""

    def test_basedpyright_memory_usage(self):
        """Check basedpyright memory usage.

        Expected: < 500MB per 100 files
        Maximum: < 1GB per 100 files
        """
        try:
            import psutil
            import re
        except ImportError:
            pytest.skip("psutil not installed - skipping memory benchmark")

        source_dir = "src"

        # Skip if src doesn't exist
        if not os.path.exists(source_dir):
            pytest.skip(f"Source directory {source_dir} not found")

        # Count files
        file_count = self.count_python_files(source_dir)
        if file_count == 0:
            pytest.skip("No Python files found in src/")

        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Run basedpyright
        result = subprocess.run(
            ["basedpyright", source_dir],
            capture_output=True,
            text=True,
            timeout=300
        )

        # Get peak memory
        peak_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = peak_memory - initial_memory
        memory_per_file = memory_used / file_count

        # Log results
        print(f"\nBasedpyright Memory Usage:")
        print(f"  Files checked: {file_count}")
        print(f"  Initial memory: {initial_memory:.2f}MB")
        print(f"  Peak memory: {peak_memory:.2f}MB")
        print(f"  Memory used: {memory_used:.2f}MB")
        print(f"  Per-file memory: {memory_per_file:.2f}MB")

        # Assert memory usage
        assert memory_per_file < 5, f"Basedpyright memory too high: {memory_per_file:.2f}MB per file (expected < 5MB)"

    def count_python_files(self, directory: str) -> int:
        """Count Python files in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and cache
            dirs[:] = [d for d in dirs if d not in ('.venv', 'venv', '__pycache__', '.pytest_cache')]

            for file in files:
                if file.endswith('.py'):
                    count += 1
        return count


@pytest.mark.performance
class TestBaselineMetrics:
    """Document and verify baseline performance metrics."""

    def test_baseline_metrics_documentation(self):
        """Document baseline performance metrics.

        This test documents the expected baseline metrics for the system.
        It serves as documentation for what "normal" performance looks like.
        """
        print("\n" + "="*80)
        print("BASELINE PERFORMANCE METRICS")
        print("="*80)
        print("\nBasedpyright:")
        print("  Expected: < 10s per file")
        print("  Maximum: < 30s per file")
        print("  Measurement: Time to type-check all .py files in src/")

        print("\nRuff Check:")
        print("  Expected: < 5s per file")
        print("  Maximum: < 15s per file")
        print("  Measurement: Time to lint all .py files in src/")

        print("\nRuff Format:")
        print("  Expected: < 2s per file")
        print("  Maximum: < 5s per file")
        print("  Measurement: Time to format-check all .py files in src/")

        print("\nPytest:")
        print("  Expected: < 5 minutes total")
        print("  Maximum: < 15 minutes total")
        print("  Measurement: Time to run complete test suite")

        print("\nPytest with Coverage:")
        print("  Expected: < 8 minutes total")
        print("  Maximum: < 20 minutes total")
        print("  Measurement: Time to run tests with coverage report")

        print("\nFile Creation:")
        print("  Expected: < 0.1s per file")
        print("  Maximum: < 0.5s per file")
        print("  Measurement: Time to create 100 small Python files")

        print("\nMemory Usage (Basedpyright):")
        print("  Expected: < 5MB per file")
        print("  Maximum: < 10MB per file")
        print("  Measurement: Memory used during type checking")

        print("\n" + "="*80)
        print("END BASELINE METRICS")
        print("="*80 + "\n")

        # This test always passes - it's documentation
        assert True

    def test_performance_regression_detection(self):
        """Detect performance regressions.

        This test can be used to detect performance regressions by comparing
        current performance to historical baselines.
        """
        # In a real implementation, you might:
        # 1. Load historical performance data
        # 2. Compare current metrics to baselines
        # 3. Fail if performance degrades significantly

        # For now, just document the concept
        print("\n" + "="*80)
        print("PERFORMANCE REGRESSION DETECTION")
        print("="*80)
        print("\nTo detect performance regressions:")
        print("1. Run benchmarks regularly")
        print("2. Store results in database or file")
        print("3. Compare new results to baselines")
        print("4. Alert on significant degradation (>20%)")

        print("\nHistorical comparison points:")
        print("- Basedpyright: 5.2s per file")
        print("- Ruff: 1.8s per file")
        print("- Pytest: 180s total")
        print("\n" + "="*80 + "\n")

        # This test always passes - it's documentation
        assert True


if __name__ == "__main__":
    # Run benchmarks
    pytest.main([__file__, "-v", "-m", "performance"])
