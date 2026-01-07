"""
Benchmark runner for performance testing.

Orchestrates benchmarks and collects performance metrics.
"""

import time
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .metrics import PerformanceMetrics, StatisticalSummary
from .data_generators import DataGenerator, Distribution


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    algorithm_name: str
    input_size: int
    distribution: str
    execution_times: List[float] = field(default_factory=list)
    comparisons: List[int] = field(default_factory=list)
    swaps: List[int] = field(default_factory=list)
    num_runs: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_time_stats(self) -> StatisticalSummary:
        """Get statistical summary of execution times."""
        return PerformanceMetrics.calculate_summary(self.execution_times)

    def get_comparisons_stats(self) -> StatisticalSummary:
        """Get statistical summary of comparison counts."""
        return PerformanceMetrics.calculate_summary(
            [float(c) for c in self.comparisons]
        )

    def get_swaps_stats(self) -> StatisticalSummary:
        """Get statistical summary of swap counts."""
        return PerformanceMetrics.calculate_summary(
            [float(s) for s in self.swaps]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of the result.
        """
        time_stats = self.get_time_stats()
        return {
            "algorithm_name": self.algorithm_name,
            "input_size": self.input_size,
            "distribution": self.distribution,
            "num_runs": self.num_runs,
            "timestamp": self.timestamp,
            "execution_time": {
                "mean": time_stats.mean,
                "median": time_stats.median,
                "std_dev": time_stats.std_dev,
                "min": time_stats.min_value,
                "max": time_stats.max_value,
                "p95": time_stats.p95,
                "confidence_interval_95": time_stats.confidence_interval_95,
            },
            "comparisons": {
                "mean": self.get_comparisons_stats().mean,
                "total": sum(self.comparisons) // max(1, len(self.comparisons)),
            },
            "swaps": {
                "mean": self.get_swaps_stats().mean,
                "total": sum(self.swaps) // max(1, len(self.swaps)),
            },
        }


class InstrumentedSort:
    """Wrapper to count comparisons and swaps during sorting."""

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    def reset(self):
        """Reset counters."""
        self.comparisons = 0
        self.swaps = 0

    def bubble_sort_instrumented(
        self,
        data: List[Any]
    ) -> List[Any]:
        """Bubble sort with instrumentation.

        Args:
            data: List to sort.

        Returns:
            Sorted list.
        """
        self.reset()
        result = list(data)
        n = len(result)

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.comparisons += 1
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
                    self.swaps += 1
                    swapped = True
            if not swapped:
                break

        return result


class BenchmarkRunner:
    """Orchestrate performance benchmarks."""

    DEFAULT_SIZES = [10, 100, 1000, 10000]
    DEFAULT_RUNS = 10

    def __init__(
        self,
        num_runs: int = DEFAULT_RUNS,
        seed: Optional[int] = None
    ):
        """Initialize benchmark runner.

        Args:
            num_runs: Number of runs per benchmark for statistical validity.
            seed: Random seed for reproducibility.
        """
        self.num_runs = num_runs
        self.data_generator = DataGenerator(seed)
        self.results: List[BenchmarkResult] = []
        self._instrumented_sort = InstrumentedSort()

    def benchmark_algorithm(
        self,
        algorithm: Callable[[List], List],
        name: str,
        sizes: Optional[List[int]] = None,
        distributions: Optional[List[Distribution]] = None,
        use_instrumentation: bool = True
    ) -> List[BenchmarkResult]:
        """Run comprehensive benchmark for an algorithm.

        Args:
            algorithm: Sorting function to benchmark.
            name: Name of the algorithm.
            sizes: List of input sizes to test.
            distributions: List of distributions to test.
            use_instrumentation: Whether to count comparisons/swaps.

        Returns:
            List of BenchmarkResult objects.
        """
        sizes = sizes or self.DEFAULT_SIZES
        distributions = distributions or DataGenerator.get_all_distributions()
        results = []

        for size in sizes:
            for distribution in distributions:
                result = self._run_benchmark(
                    algorithm=algorithm,
                    name=name,
                    size=size,
                    distribution=distribution,
                    use_instrumentation=use_instrumentation
                )
                results.append(result)
                self.results.append(result)

        return results

    def _run_benchmark(
        self,
        algorithm: Callable[[List], List],
        name: str,
        size: int,
        distribution: Distribution,
        use_instrumentation: bool
    ) -> BenchmarkResult:
        """Run benchmark for specific size and distribution.

        Args:
            algorithm: Sorting function.
            name: Algorithm name.
            size: Input size.
            distribution: Data distribution.
            use_instrumentation: Whether to count operations.

        Returns:
            BenchmarkResult with collected metrics.
        """
        result = BenchmarkResult(
            algorithm_name=name,
            input_size=size,
            distribution=distribution.value,
            num_runs=self.num_runs
        )

        for _ in range(self.num_runs):
            # Generate fresh data for each run
            data = self.data_generator.generate(size, distribution)

            if use_instrumentation and "bubble" in name.lower():
                # Use instrumented version for bubble sort
                start = time.perf_counter()
                self._instrumented_sort.bubble_sort_instrumented(data)
                elapsed = time.perf_counter() - start

                result.execution_times.append(elapsed)
                result.comparisons.append(self._instrumented_sort.comparisons)
                result.swaps.append(self._instrumented_sort.swaps)
            else:
                # Standard timing without instrumentation
                start = time.perf_counter()
                algorithm(data)
                elapsed = time.perf_counter() - start

                result.execution_times.append(elapsed)
                result.comparisons.append(0)
                result.swaps.append(0)

        return result

    def compare_with_builtin(
        self,
        algorithm: Callable[[List], List],
        name: str,
        sizes: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Compare algorithm performance with Python's built-in sort.

        Args:
            algorithm: Algorithm to compare.
            name: Algorithm name.
            sizes: Input sizes to test.

        Returns:
            Dictionary with comparison results.
        """
        sizes = sizes or self.DEFAULT_SIZES
        comparison = {
            "algorithm": name,
            "builtin": "Python sorted() (Timsort)",
            "comparisons": []
        }

        for size in sizes:
            # Benchmark custom algorithm
            data = self.data_generator.generate(size, Distribution.RANDOM)

            # Time custom algorithm
            times_custom = []
            for _ in range(self.num_runs):
                test_data = data.copy()
                start = time.perf_counter()
                algorithm(test_data)
                elapsed = time.perf_counter() - start
                times_custom.append(elapsed)

            # Time built-in sort
            times_builtin = []
            for _ in range(self.num_runs):
                test_data = data.copy()
                start = time.perf_counter()
                sorted(test_data)
                elapsed = time.perf_counter() - start
                times_builtin.append(elapsed)

            custom_mean = PerformanceMetrics.calculate_mean(times_custom)
            builtin_mean = PerformanceMetrics.calculate_mean(times_builtin)

            speedup = custom_mean / builtin_mean if builtin_mean > 0 else 0

            comparison["comparisons"].append({
                "size": size,
                "custom_time": custom_mean,
                "builtin_time": builtin_mean,
                "speedup_factor": speedup,
                "builtin_is_faster": builtin_mean < custom_mean
            })

        return comparison

    def get_all_results(self) -> List[BenchmarkResult]:
        """Get all collected benchmark results.

        Returns:
            List of all BenchmarkResult objects.
        """
        return self.results

    def clear_results(self) -> None:
        """Clear all collected results."""
        self.results = []
