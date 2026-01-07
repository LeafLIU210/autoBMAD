"""
Export functionality for benchmark results.

Supports CSV, JSON, and plain text export formats.
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from .benchmark_runner import BenchmarkResult


class BaseExporter(ABC):
    """Base class for result exporters."""

    def __init__(self, output_dir: str = "reports"):
        """Initialize exporter with output directory.

        Args:
            output_dir: Directory for output files.
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_filename(self, prefix: str, extension: str) -> str:
        """Generate timestamped filename.

        Args:
            prefix: Filename prefix.
            extension: File extension.

        Returns:
            Timestamped filename.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"

    @abstractmethod
    def export(
        self,
        results: List[BenchmarkResult],
        filename: Optional[str] = None
    ) -> str:
        """Export results to file.

        Args:
            results: List of benchmark results.
            filename: Optional custom filename.

        Returns:
            Path to exported file.
        """
        pass


class CSVExporter(BaseExporter):
    """Export benchmark results to CSV format."""

    def export(
        self,
        results: List[BenchmarkResult],
        filename: Optional[str] = None
    ) -> str:
        """Export results to CSV file.

        Args:
            results: List of benchmark results.
            filename: Optional custom filename.

        Returns:
            Path to exported CSV file.
        """
        if filename is None:
            filename = self._generate_filename("benchmark_results", "csv")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "algorithm",
                "input_size",
                "distribution",
                "num_runs",
                "mean_time_sec",
                "median_time_sec",
                "std_dev_time_sec",
                "min_time_sec",
                "max_time_sec",
                "p95_time_sec",
                "mean_comparisons",
                "mean_swaps",
                "timestamp"
            ])

            # Data rows
            for result in results:
                time_stats = result.get_time_stats()
                comp_stats = result.get_comparisons_stats()
                swap_stats = result.get_swaps_stats()

                writer.writerow([
                    result.algorithm_name,
                    result.input_size,
                    result.distribution,
                    result.num_runs,
                    f"{time_stats.mean:.9f}",
                    f"{time_stats.median:.9f}",
                    f"{time_stats.std_dev:.9f}",
                    f"{time_stats.min_value:.9f}",
                    f"{time_stats.max_value:.9f}",
                    f"{time_stats.p95:.9f}",
                    f"{comp_stats.mean:.0f}",
                    f"{swap_stats.mean:.0f}",
                    result.timestamp
                ])

        return filepath


class JSONExporter(BaseExporter):
    """Export benchmark results to JSON format."""

    def export(
        self,
        results: List[BenchmarkResult],
        filename: Optional[str] = None
    ) -> str:
        """Export results to JSON file.

        Args:
            results: List of benchmark results.
            filename: Optional custom filename.

        Returns:
            Path to exported JSON file.
        """
        if filename is None:
            filename = self._generate_filename("benchmark_results", "json")

        filepath = os.path.join(self.output_dir, filename)

        data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_results": len(results)
            },
            "results": [result.to_dict() for result in results]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return filepath


class TextExporter(BaseExporter):
    """Export benchmark results to plain text format."""

    def export(
        self,
        results: List[BenchmarkResult],
        filename: Optional[str] = None
    ) -> str:
        """Export results to plain text file.

        Args:
            results: List of benchmark results.
            filename: Optional custom filename.

        Returns:
            Path to exported text file.
        """
        if filename is None:
            filename = self._generate_filename("benchmark_results", "txt")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE BENCHMARK RESULTS\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            for result in results:
                time_stats = result.get_time_stats()
                comp_stats = result.get_comparisons_stats()
                swap_stats = result.get_swaps_stats()

                f.write("-" * 60 + "\n")
                f.write(f"Algorithm: {result.algorithm_name}\n")
                f.write(f"Input Size: {result.input_size}\n")
                f.write(f"Distribution: {result.distribution}\n")
                f.write(f"Number of Runs: {result.num_runs}\n")
                f.write("\n")

                f.write("Execution Time Statistics:\n")
                f.write(f"  Mean:    {time_stats.mean * 1000:.4f} ms\n")
                f.write(f"  Median:  {time_stats.median * 1000:.4f} ms\n")
                f.write(f"  Std Dev: {time_stats.std_dev * 1000:.4f} ms\n")
                f.write(f"  Min:     {time_stats.min_value * 1000:.4f} ms\n")
                f.write(f"  Max:     {time_stats.max_value * 1000:.4f} ms\n")
                f.write(f"  P95:     {time_stats.p95 * 1000:.4f} ms\n")
                ci = time_stats.confidence_interval_95
                f.write(f"  95% CI:  [{ci[0] * 1000:.4f}, {ci[1] * 1000:.4f}] ms\n")
                f.write("\n")

                f.write("Operation Counts (per run avg):\n")
                f.write(f"  Comparisons: {comp_stats.mean:.0f}\n")
                f.write(f"  Swaps:       {swap_stats.mean:.0f}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"Total benchmarks: {len(results)}\n")
            f.write("=" * 80 + "\n")

        return filepath


def export_comparison_report(
    comparison: Dict[str, Any],
    output_dir: str = "reports",
    filename: Optional[str] = None
) -> str:
    """Export algorithm comparison report.

    Args:
        comparison: Comparison data from BenchmarkRunner.compare_with_builtin.
        output_dir: Output directory.
        filename: Optional custom filename.

    Returns:
        Path to exported file.
    """
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_report_{timestamp}.txt"

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("ALGORITHM COMPARISON REPORT\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Comparing: {comparison['algorithm']}\n")
        f.write(f"Against:   {comparison['builtin']}\n\n")

        f.write("-" * 60 + "\n")
        f.write(f"{'Size':>10} | {'Custom (ms)':>12} | {'Built-in (ms)':>14} | {'Speedup':>10}\n")
        f.write("-" * 60 + "\n")

        for comp in comparison["comparisons"]:
            custom_ms = comp["custom_time"] * 1000
            builtin_ms = comp["builtin_time"] * 1000
            speedup = comp["speedup_factor"]

            f.write(f"{comp['size']:>10} | {custom_ms:>12.4f} | {builtin_ms:>14.4f} | {speedup:>10.1f}x\n")

        f.write("-" * 60 + "\n\n")

        f.write("Note: Python's built-in sorted() uses Timsort, a hybrid sorting\n")
        f.write("algorithm derived from merge sort and insertion sort. It is\n")
        f.write("optimized in C and achieves O(n log n) time complexity, making\n")
        f.write("it significantly faster than bubble sort's O(n²) for large inputs.\n")
        f.write("\nEducational Value: Bubble sort is valuable for learning sorting\n")
        f.write("concepts due to its simplicity and intuitive swapping mechanism.\n")

    return filepath
