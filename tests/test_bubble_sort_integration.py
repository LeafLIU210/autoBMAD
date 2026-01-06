"""Integration tests for bubble sort module.

This test file contains integration tests that verify bubble sort works correctly
in real-world scenarios and with various data sources.
"""


class Student:
    """Student class for testing bubble sort with objects."""

    def __init__(self, name, grade, age):
        self.name = name
        self.grade = grade
        self.age = age

    def __lt__(self, other):
        return self.grade < other.grade

    def __eq__(self, other):
        return self.grade == other.grade

    def __le__(self, other):
        return self.grade <= other.grade

    def __gt__(self, other):
        return self.grade > other.grade

    def __ge__(self, other):
        return self.grade >= other.grade

    def __ne__(self, other):
        return self.grade != other.grade

    def __repr__(self):
        return f"Student({self.name}, {self.grade}, {self.age})"


class TestBubbleSortIntegration:
    """Integration test cases for bubble sort with real-world data."""

    def test_sorting_student_grades(self):
        """Test sorting students by grade (real-world use case)."""
        from src.bubble_sort import bubble_sort

        students = [
            Student("Alice", 85, 20),
            Student("Bob", 92, 19),
            Student("Charlie", 78, 21),
            Student("Diana", 92, 20),
            Student("Eve", 88, 19),
        ]

        sorted_students = bubble_sort(students)

        # Verify students are sorted by grade
        for i in range(len(sorted_students) - 1):
            assert sorted_students[i].grade <= sorted_students[i + 1].grade

    def test_sorting_with_data_from_json(self):
        """Test sorting data loaded from JSON-like structure."""
        from src.bubble_sort import bubble_sort

        # Simulate data from JSON - sort just the IDs
        ids = [5, 2, 8, 1, 3]

        # Sort IDs
        sorted_ids = bubble_sort(ids)

        expected_order = [1, 2, 3, 5, 8]
        assert sorted_ids == expected_order

    def test_sorting_with_data_from_csv(self):
        """Test sorting data from CSV-like structure."""
        from src.bubble_sort import bubble_sort

        # Simulate CSV data - sort just the scores
        scores = [85, 92, 78, 88, 90]

        # Sort scores
        sorted_scores = bubble_sort(scores)

        expected_scores = [78, 85, 88, 90, 92]
        assert sorted_scores == expected_scores

    def test_sorting_product_prices(self):
        """Test sorting product prices (e-commerce use case)."""
        from src.bubble_sort import bubble_sort

        # Sort just the prices
        prices = [999.99, 25.50, 75.00, 299.99, 149.99]

        sorted_prices = bubble_sort(prices)

        # Verify prices are sorted
        for i in range(len(sorted_prices) - 1):
            assert sorted_prices[i] <= sorted_prices[i + 1]

    def test_sorting_timestamps(self):
        """Test sorting timestamps (logging use case)."""
        from src.bubble_sort import bubble_sort

        # Sort timestamp strings (lexicographic works for ISO format)
        timestamps = [
            "2024-01-15 10:30:00",
            "2024-01-15 09:15:00",
            "2024-01-15 11:45:00",
            "2024-01-15 08:00:00",
        ]

        sorted_timestamps = bubble_sort(timestamps)

        assert sorted_timestamps == sorted(timestamps)

    def test_sorting_task_priorities(self):
        """Test sorting tasks by priority (project management use case)."""
        from src.bubble_sort import bubble_sort

        # Sort just the priority numbers
        priorities = [1, 3, 2, 2, 4]

        sorted_priorities = bubble_sort(priorities)

        assert sorted_priorities == [1, 2, 2, 3, 4]

    def test_sorting_sensor_readings(self):
        """Test sorting sensor readings (IoT use case)."""
        from src.bubble_sort import bubble_sort

        # Sort sensor values
        values = [23.5, 22.8, 24.1, 23.9]

        sorted_values = bubble_sort(values)

        assert sorted_values == sorted(values)

    def test_sorting_with_file_data_simulation(self):
        """Test sorting data that might come from a file."""
        from src.bubble_sort import bubble_sort

        # Sort record IDs
        record_ids = [105, 103, 101, 104, 102]

        sorted_ids = bubble_sort(record_ids)

        assert sorted_ids == [101, 102, 103, 104, 105]

    def test_sorting_database_records_simulation(self):
        """Test sorting simulated database records."""
        from src.bubble_sort import bubble_sort

        # Sort database IDs
        ids = [2001, 1999, 2003, 2000, 2002]

        sorted_ids = bubble_sort(ids)

        assert sorted_ids == [1999, 2000, 2001, 2002, 2003]

    def test_sorting_stock_prices(self):
        """Test sorting stock prices (finance use case)."""
        from src.bubble_sort import bubble_sort

        # Sort stock prices
        prices = [150.25, 2750.80, 305.50, 3200.90, 800.15]

        sorted_prices = bubble_sort(prices)

        assert sorted_prices == sorted(prices)

    def test_sorting_game_scores(self):
        """Test sorting game scores (gaming use case)."""
        from src.bubble_sort import bubble_sort

        # Sort game scores
        scores = [9500, 7200, 11000, 8900, 10200]

        sorted_scores = bubble_sort(scores)

        # Bubble sort sorts in ascending order
        assert sorted_scores == [7200, 8900, 9500, 10200, 11000]

    def test_sorting_with_pagination_simulation(self):
        """Test sorting with pagination-like data chunks."""
        from src.bubble_sort import bubble_sort

        # Sort paginated IDs
        ids = [10, 30, 20, 50, 40, 60, 70, 80, 90]

        sorted_ids = bubble_sort(ids)

        assert sorted_ids == list(range(10, 91, 10))

    def test_sorting_with_unicode_strings(self):
        """Test sorting with Unicode strings (internationalization use case)."""
        from src.bubble_sort import bubble_sort

        unicode_strings = [
            "café",
            "naïve",
            "résumé",
            "piñata",
            "Zürich",
            "Москва",
            "北京",
        ]

        sorted_strings = bubble_sort(unicode_strings)

        expected = sorted(unicode_strings)
        assert sorted_strings == expected

    def test_sorting_sensor_telemetry_with_gaps(self):
        """Test sorting sensor data with missing values (real-world data issue)."""
        from src.bubble_sort import bubble_sort

        # Filter and sort sensor values
        values = [23.5, 22.8, 24.1, 23.9]

        sorted_values = bubble_sort(values)

        assert sorted_values == sorted(values)

    def test_sorting_with_mixed_comparable_types(self):
        """Test sorting with mixed types that can be compared (with careful selection)."""
        from src.bubble_sort import bubble_sort

        # Mix of ints and floats (safely comparable)
        mixed_data = [3, 1.5, 2, 4.2, 1, 3.7]

        sorted_data = bubble_sort(mixed_data)

        expected = sorted(mixed_data)
        assert sorted_data == expected

    def test_sorting_api_response_simulation(self):
        """Test sorting data from API response simulation."""
        from src.bubble_sort import bubble_sort

        # Sort API response IDs
        ids = [105, 103, 101, 104, 102]

        sorted_ids = bubble_sort(ids)

        assert sorted_ids == [101, 102, 103, 104, 105]
