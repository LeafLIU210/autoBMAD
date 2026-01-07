"""
Data generators for benchmarking.

Provides various input distributions for testing algorithm performance.
"""

import random
from typing import List, Optional
from enum import Enum


class Distribution(Enum):
    """Types of data distributions for benchmarking."""

    SORTED = "sorted"
    REVERSE = "reverse"
    RANDOM = "random"
    PARTIALLY_SORTED = "partially_sorted"


class DataGenerator:
    """Generate test data with various distributions."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional random seed.

        Args:
            seed: Random seed for reproducible results.
        """
        self.seed = seed
        self._rng = random.Random(seed)

    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility.

        Args:
            seed: Random seed value.
        """
        self.seed = seed
        self._rng = random.Random(seed)

    def generate_sorted(self, size: int) -> List[int]:
        """Generate sorted data.

        Args:
            size: Number of elements.

        Returns:
            Sorted list from 0 to size-1.
        """
        return list(range(size))

    def generate_reverse_sorted(self, size: int) -> List[int]:
        """Generate reverse-sorted data.

        Args:
            size: Number of elements.

        Returns:
            Reverse sorted list from size-1 to 0.
        """
        return list(range(size - 1, -1, -1))

    def generate_random(self, size: int) -> List[int]:
        """Generate random data.

        Args:
            size: Number of elements.

        Returns:
            Shuffled list of unique integers.
        """
        data = list(range(size))
        self._rng.shuffle(data)
        return data

    def generate_partially_sorted(
        self,
        size: int,
        sorted_percentage: float = 0.9
    ) -> List[int]:
        """Generate partially sorted data.

        Creates a list that is mostly sorted with some elements swapped.

        Args:
            size: Number of elements.
            sorted_percentage: Percentage of list that remains sorted (0.0-1.0).

        Returns:
            Partially sorted list.
        """
        data = list(range(size))
        num_swaps = int(size * (1 - sorted_percentage) / 2)

        for _ in range(num_swaps):
            i = self._rng.randint(0, size - 1)
            j = self._rng.randint(0, size - 1)
            data[i], data[j] = data[j], data[i]

        return data

    def generate(
        self,
        size: int,
        distribution: Distribution,
        **kwargs
    ) -> List[int]:
        """Generate data with specified distribution.

        Args:
            size: Number of elements.
            distribution: Type of distribution.
            **kwargs: Additional arguments for specific distributions.

        Returns:
            Generated data list.
        """
        generators = {
            Distribution.SORTED: self.generate_sorted,
            Distribution.REVERSE: self.generate_reverse_sorted,
            Distribution.RANDOM: self.generate_random,
            Distribution.PARTIALLY_SORTED: self.generate_partially_sorted,
        }

        generator = generators.get(distribution)
        if generator is None:
            raise ValueError(f"Unknown distribution: {distribution}")

        if distribution == Distribution.PARTIALLY_SORTED:
            sorted_percentage = kwargs.get("sorted_percentage", 0.9)
            return generator(size, sorted_percentage=sorted_percentage)

        return generator(size)

    @staticmethod
    def get_all_distributions() -> List[Distribution]:
        """Get all available distributions.

        Returns:
            List of all Distribution enum values.
        """
        return list(Distribution)
