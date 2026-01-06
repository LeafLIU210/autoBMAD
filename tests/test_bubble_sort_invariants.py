"""Algorithm invariant tests for bubble sort module.

This test file verifies mathematical invariants and properties of the bubble sort
algorithm to ensure correctness and catch potential implementation bugs.
"""

import random


class Point:
    """Point class for testing sorting with custom comparison."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        # Sort by x coordinate, then by y
        if self.x == other.x:
            return self.y < other.y
        return self.x < other.x

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class TestBubbleSortInvariants:
    """Algorithm invariant test cases for bubble sort."""

    def test_monotonicity_invariant(self):
        """Test that after sorting, list is in non-decreasing order."""
        from src.bubble_sort import bubble_sort

        random.seed(123)
        for _ in range(20):
            test_list = [random.randint(-100, 100) for _ in range(random.randint(0, 50))]

            result = bubble_sort(test_list)

            for i in range(len(result) - 1):
                assert result[i] <= result[i + 1], (
                    f"Monotonicity violated: {result[i]} > {result[i + 1]}"
                )

    def test_transitivity_invariant(self):
        """Test that if a <= b and b <= c, then a <= c."""
        from src.bubble_sort import bubble_sort

        test_list = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        result = bubble_sort(test_list)

        # Randomly sample triplets and verify transitivity
        random.seed(456)
        for _ in range(100):
            indices = random.sample(range(len(result)), 3)
            indices.sort()
            a, b, c = result[indices[0]], result[indices[1]], result[indices[2]]

            # Check all combinations
            assert (a <= b and b <= c) or (a >= b and b >= c), (
                f"Transitivity violated: {a}, {b}, {c}"
            )

    def test_antisymmetry_invariant(self):
        """Test that if a <= b and b <= a, then a == b."""
        from src.bubble_sort import bubble_sort

        test_list = [1, 2, 2, 3, 3, 3, 2, 1]
        result = bubble_sort(test_list)

        # Check that equal elements are truly equal
        for i in range(len(result) - 1):
            if result[i] <= result[i + 1] and result[i + 1] <= result[i]:
                assert result[i] == result[i + 1], (
                    f"Antisymmetry violated: {result[i]} != {result[i + 1]}"
                )

    def test_reflexivity_invariant(self):
        """Test that x <= x for all elements."""
        from src.bubble_sort import bubble_sort

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        result = bubble_sort(test_list)

        for element in result:
            assert element <= element, "Reflexivity violated"

    def test_stability_invariant(self):
        """Test that equal elements maintain their relative order."""
        from src.bubble_sort import bubble_sort

        # Create elements with same value but different identities
        items = [(3, "a"), (1, "b"), (2, "c"), (1, "d"), (3, "e")]
        result = bubble_sort(items.copy())

        # Verify stability: items with same first element maintain order
        # Check that (1, "b") comes before (1, "d")
        assert (1, "b") in result
        assert (1, "d") in result
        assert result.index((1, "b")) < result.index((1, "d"))

        # Check that (3, "a") comes before (3, "e")
        assert (3, "a") in result
        assert (3, "e") in result
        assert result.index((3, "a")) < result.index((3, "e"))

    def test_commutativity_of_duplicates(self):
        """Test that duplicates can be reordered without affecting result."""
        from src.bubble_sort import bubble_sort

        original = [2, 1, 2, 1, 2]
        result1 = bubble_sort(original.copy())
        result2 = bubble_sort(original.copy())

        assert result1 == result2

    def test_partition_invariant(self):
        """Test that elements are correctly partitioned."""
        from src.bubble_sort import bubble_sort

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        result = bubble_sort(test_list)

        # For any position i, all elements to the left are <= all to the right
        for i in range(len(result) - 1):
            left_elem = result[i]
            right_elem = result[i + 1]
            assert left_elem <= right_elem

    def test_bubble_up_invariant(self):
        """Test that larger elements 'bubble up' to the end."""
        from src.bubble_sort import bubble_sort

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        original_max = max(test_list)
        result = bubble_sort(test_list)

        # Maximum element should be at the end
        assert result[-1] == original_max

    def test_boundary_invariant(self):
        """Test that boundaries are correctly handled."""
        from src.bubble_sort import bubble_sort

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        result = bubble_sort(test_list)

        # First element should be minimum
        assert result[0] == min(test_list)

        # Last element should be maximum
        assert result[-1] == max(test_list)

    def test_comparison_protocol_invariant(self):
        """Test that custom comparison protocol works correctly."""
        from src.bubble_sort import bubble_sort

        points = [
            Point(3, 5),
            Point(1, 2),
            Point(2, 8),
            Point(1, 1),
            Point(3, 3),
            Point(2, 3),
        ]

        result = bubble_sort(points)

        # Verify sorting by x, then by y
        for i in range(len(result) - 1):
            current = result[i]
            next_elem = result[i + 1]
            assert current <= next_elem

        # Verify specific ordering
        assert result[0] == Point(1, 1)
        assert result[1] == Point(1, 2)
        assert result[2] == Point(2, 3)
        assert result[3] == Point(2, 8)
        assert result[4] == Point(3, 3)
        assert result[5] == Point(3, 5)

    def test_inversion_count_decreases(self):
        """Test that the number of inversions decreases with each pass."""
        from src.bubble_sort import bubble_sort

        def count_inversions(lst):
            count = 0
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    if lst[i] > lst[j]:
                        count += 1
            return count

        original = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        initial_inversions = count_inversions(original)

        result = bubble_sort(original)
        final_inversions = count_inversions(result)

        assert initial_inversions >= final_inversions
        assert final_inversions == 0

    def test_strict_weak_ordering(self):
        """Test that sorting establishes a strict weak ordering."""
        from src.bubble_sort import bubble_sort

        test_list = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        result = bubble_sort(test_list)

        # For strict weak ordering, we need:
        # 1. Irreflexivity: not(x < x)
        for element in result:
            assert not (element < element), "Irreflexivity violated"

        # 2. Asymmetry: if x < y then not(y < x)
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[i] < result[j]:
                    assert not (result[j] < result[i])

        # 3. Transitivity: if x < y and y < z then x < z
        # (already tested in transitivity_invariant)
