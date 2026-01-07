"""
Performance metrics and statistical analysis module.

Provides comprehensive statistical calculations for benchmark results.
"""

import math
from typing import List, Dict, Any, NamedTuple
from dataclasses import dataclass


@dataclass
class StatisticalSummary:
    """Statistical summary of performance measurements."""

    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    p25: float
    p75: float
    p95: float
    p99: float
    sample_size: int
    confidence_interval_95: tuple


class PerformanceMetrics:
    """Calculate statistical metrics for performance data."""

    @staticmethod
    def calculate_mean(values: List[float]) -> float:
        """Calculate arithmetic mean of values.

        Args:
            values: List of numeric values.

        Returns:
            Mean value, or 0.0 if empty list.
        """
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def calculate_median(values: List[float]) -> float:
        """Calculate median of values.

        Args:
            values: List of numeric values.

        Returns:
            Median value, or 0.0 if empty list.
        """
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        return sorted_values[mid]

    @staticmethod
    def calculate_std_dev(values: List[float]) -> float:
        """Calculate sample standard deviation.

        Args:
            values: List of numeric values.

        Returns:
            Standard deviation, or 0.0 if less than 2 values.
        """
        if len(values) < 2:
            return 0.0
        mean = PerformanceMetrics.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value.

        Args:
            values: List of numeric values.
            percentile: Percentile to calculate (0-100).

        Returns:
            Percentile value, or 0.0 if empty list.
        """
        if not values:
            return 0.0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_values[int(k)]
        return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)

    @staticmethod
    def calculate_confidence_interval(
        values: List[float],
        confidence: float = 0.95
    ) -> tuple:
        """Calculate confidence interval for the mean.

        Uses t-distribution approximation for small samples.

        Args:
            values: List of numeric values.
            confidence: Confidence level (default 0.95 for 95%).

        Returns:
            Tuple of (lower_bound, upper_bound).
        """
        if len(values) < 2:
            mean = PerformanceMetrics.calculate_mean(values)
            return (mean, mean)

        mean = PerformanceMetrics.calculate_mean(values)
        std_dev = PerformanceMetrics.calculate_std_dev(values)
        n = len(values)

        # Approximate t-value for 95% CI
        # Using 1.96 as approximation (z-score for large samples)
        t_value = 1.96 if n > 30 else 2.0

        margin = t_value * (std_dev / math.sqrt(n))
        return (mean - margin, mean + margin)

    @classmethod
    def calculate_summary(cls, values: List[float]) -> StatisticalSummary:
        """Calculate comprehensive statistical summary.

        Args:
            values: List of numeric values.

        Returns:
            StatisticalSummary with all metrics.
        """
        if not values:
            return StatisticalSummary(
                mean=0.0,
                median=0.0,
                std_dev=0.0,
                min_value=0.0,
                max_value=0.0,
                p25=0.0,
                p75=0.0,
                p95=0.0,
                p99=0.0,
                sample_size=0,
                confidence_interval_95=(0.0, 0.0)
            )

        return StatisticalSummary(
            mean=cls.calculate_mean(values),
            median=cls.calculate_median(values),
            std_dev=cls.calculate_std_dev(values),
            min_value=min(values),
            max_value=max(values),
            p25=cls.calculate_percentile(values, 25),
            p75=cls.calculate_percentile(values, 75),
            p95=cls.calculate_percentile(values, 95),
            p99=cls.calculate_percentile(values, 99),
            sample_size=len(values),
            confidence_interval_95=cls.calculate_confidence_interval(values)
        )
