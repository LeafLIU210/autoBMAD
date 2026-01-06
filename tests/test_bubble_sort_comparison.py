"""Comparison protocol tests for bubble sort module.

This test file verifies that bubble sort works correctly with complex custom objects
that implement various comparison protocols and magic methods.
"""


class TestBubbleSortComparisonProtocol:
    """Comparison protocol test cases for bubble sort."""

    def test_custom_object_with_lt(self):
        """Test sorting with custom object implementing __lt__."""
        from src.bubble_sort import bubble_sort

        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __lt__(self, other):
                return self.age < other.age

            def __eq__(self, other):
                return self.age == other.age

            def __repr__(self):
                return f"Person({self.name}, {self.age})"

        people = [
            Person("Alice", 30),
            Person("Bob", 25),
            Person("Charlie", 35),
            Person("Diana", 25),
        ]

        result = bubble_sort(people)

        # Should be sorted by age
        assert result[0].age == 25
        assert result[1].age == 25
        assert result[2].age == 30
        assert result[3].age == 35

    def test_complex_custom_comparison(self):
        """Test sorting with complex custom comparison logic."""
        from src.bubble_sort import bubble_sort

        class Product:
            def __init__(self, name, price, rating):
                self.name = name
                self.price = price
                self.rating = rating

            def __lt__(self, other):
                # Sort by rating first, then by price
                if self.rating == other.rating:
                    return self.price < other.price
                return self.rating > other.rating  # Higher rating first

            def __eq__(self, other):
                return (
                    self.rating == other.rating
                    and self.price == other.price
                )

            def __repr__(self):
                return f"Product({self.name}, ${self.price}, {self.rating})"

        products = [
            Product("A", 100, 5),
            Product("B", 50, 3),
            Product("C", 200, 5),
            Product("D", 75, 3),
            Product("E", 150, 4),
        ]

        result = bubble_sort(products)

        # Should be sorted by rating (desc), then by price (asc)
        assert result[0].name == "A"  # rating 5, price 100
        assert result[1].name == "C"  # rating 5, price 200
        assert result[2].name == "E"  # rating 4
        assert result[3].name == "B"  # rating 3, price 50
        assert result[4].name == "D"  # rating 3, price 75

    def test_lexicographic_comparison(self):
        """Test sorting with lexicographic (dictionary order) comparison."""
        from src.bubble_sort import bubble_sort

        class Word:
            def __init__(self, text):
                self.text = text

            def __lt__(self, other):
                return self.text.lower() < other.text.lower()

            def __eq__(self, other):
                return self.text.lower() == other.text.lower()

            def __repr__(self):
                return f"Word({self.text})"

        words = [
            Word("Apple"),
            Word("banana"),
            Word("Cherry"),
            Word("date"),
            Word("apple"),
        ]

        result = bubble_sort(words)

        # Should be sorted alphabetically (case-insensitive)
        assert result[0].text == "Apple"
        assert result[1].text == "apple"
        assert result[2].text == "banana"
        assert result[3].text == "Cherry"
        assert result[4].text == "date"

    def test_reverse_order_comparison(self):
        """Test sorting with reverse order comparison."""
        from src.bubble_sort import bubble_sort

        class Priority:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                # Reverse order: higher value is "less"
                return self.value > other.value

            def __eq__(self, other):
                return self.value == other.value

            def __repr__(self):
                return f"Priority({self.value})"

        priorities = [
            Priority(1),  # Low priority
            Priority(5),  # High priority
            Priority(3),  # Medium priority
            Priority(4),  # High priority
        ]

        result = bubble_sort(priorities)

        # Should be sorted in reverse (highest priority first)
        assert result[0].value == 5
        assert result[1].value == 4
        assert result[2].value == 3
        assert result[3].value == 1

    def test_multi_attribute_comparison(self):
        """Test sorting with multiple attributes."""
        from src.bubble_sort import bubble_sort

        class Student:
            def __init__(self, name, grade, age):
                self.name = name
                self.grade = grade
                self.age = age

            def __lt__(self, other):
                # Sort by grade (desc), then by age (asc)
                if self.grade == other.grade:
                    return self.age < other.age
                return self.grade > other.grade

            def __eq__(self, other):
                return self.grade == other.grade and self.age == other.age

            def __repr__(self):
                return f"Student({self.name}, {self.grade}, {self.age})"

        students = [
            Student("Alice", 85, 20),
            Student("Bob", 92, 19),
            Student("Charlie", 85, 21),
            Student("Diana", 92, 20),
        ]

        result = bubble_sort(students)

        # Should be sorted by grade (desc), then by age (asc)
        assert result[0].name == "Bob"  # grade 92, age 19
        assert result[1].name == "Diana"  # grade 92, age 20
        assert result[2].name == "Alice"  # grade 85, age 20
        assert result[3].name == "Charlie"  # grade 85, age 21

    def test_date_comparison(self):
        """Test sorting with date/time objects."""
        from datetime import datetime, timedelta
        from src.bubble_sort import bubble_sort

        base = datetime(2024, 1, 1)
        dates = [
            base + timedelta(days=5),
            base,
            base + timedelta(days=3),
            base + timedelta(days=7),
            base + timedelta(days=1),
        ]

        result = bubble_sort(dates)

        # Should be sorted chronologically
        assert result[0] == base
        assert result[1] == base + timedelta(days=1)
        assert result[2] == base + timedelta(days=3)
        assert result[3] == base + timedelta(days=5)
        assert result[4] == base + timedelta(days=7)

    def test_tuple_comparison(self):
        """Test sorting with tuples (natural tuple comparison)."""
        from src.bubble_sort import bubble_sort

        tuples = [
            (3, "c"),
            (1, "a"),
            (2, "b"),
            (1, "d"),
            (3, "a"),
        ]

        result = bubble_sort(tuples)

        # Tuples compare element-wise
        expected = [
            (1, "a"),
            (1, "d"),
            (2, "b"),
            (3, "a"),
            (3, "c"),
        ]

        assert result == expected

    def test_nested_list_comparison(self):
        """Test sorting with nested lists."""
        from src.bubble_sort import bubble_sort

        nested = [
            [3, 5],
            [1, 2],
            [2, 8],
            [1, 1],
            [3, 3],
        ]

        result = bubble_sort(nested)

        # Lists compare element-wise
        expected = [
            [1, 1],
            [1, 2],
            [2, 8],
            [3, 3],
            [3, 5],
        ]

        assert result == expected

    def test_string_length_comparison(self):
        """Test sorting by string length."""
        from src.bubble_sort import bubble_sort

        class StringLength:
            def __init__(self, text):
                self.text = text

            def __lt__(self, other):
                return len(self.text) < len(other.text)

            def __eq__(self, other):
                return len(self.text) == len(other.text)

            def __repr__(self):
                return f"StringLength({self.text})"

        strings = [
            StringLength("hello"),
            StringLength("a"),
            StringLength("world"),
            StringLength("hi"),
        ]

        result = bubble_sort(strings)

        # Should be sorted by length
        assert len(result[0].text) == 1
        assert len(result[1].text) == 2
        assert len(result[2].text) == 5
        assert len(result[3].text) == 5

    def test_unicode_comparison(self):
        """Test sorting with Unicode characters."""
        from src.bubble_sort import bubble_sort

        class UnicodeString:
            def __init__(self, text):
                self.text = text

            def __lt__(self, other):
                return self.text < other.text

            def __eq__(self, other):
                return self.text == other.text

            def __repr__(self):
                return f"UnicodeString({self.text})"

        unicode_strings = [
            UnicodeString("α"),
            UnicodeString("β"),
            UnicodeString("a"),
            UnicodeString("ñ"),
            UnicodeString("ç"),
        ]

        result = bubble_sort(unicode_strings)

        # Should be sorted according to Unicode code points
        # (actual order depends on Unicode values)
        assert result[0].text == "a"  # 'a' has lowest code point
        assert len(result) == 5

    def test_mixed_comparable_types(self):
        """Test sorting with mixed but comparable types."""
        from src.bubble_sort import bubble_sort

        # All comparable as floats
        mixed = [3, 1.5, 2, 4.2, 1]

        result = bubble_sort(mixed)
        expected = [1, 1.5, 2, 3, 4.2]

        assert result == expected

    def test_custom_eq_without_gt(self):
        """Test object with custom comparison that might not support all operators."""
        from src.bubble_sort import bubble_sort

        class Item:
            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value < other.value

            def __eq__(self, other):
                return self.value == other.value

            def __le__(self, other):
                return self.value <= other.value

            def __gt__(self, other):
                return self.value > other.value

            def __ge__(self, other):
                return self.value >= other.value

            def __ne__(self, other):
                return self.value != other.value

            def __repr__(self):
                return f"Item({self.value})"

        items = [Item(3), Item(1), Item(2), Item(1)]

        # Should work with proper comparison methods
        result = bubble_sort(items)

        # Result should have same values
        values = [item.value for item in result]
        assert values == [1, 1, 2, 3]

    def test_complex_number_comparison(self):
        """Test sorting with complex numbers using magnitude."""
        from src.bubble_sort import bubble_sort

        class ComplexWrapper:
            """Wrapper for complex numbers to enable sorting."""
            def __init__(self, complex_num):
                self.complex_num = complex_num

            def __lt__(self, other):
                # Sort by magnitude (absolute value)
                return abs(self.complex_num) < abs(other.complex_num)

            def __eq__(self, other):
                return abs(self.complex_num) == abs(other.complex_num)

            def __repr__(self):
                return f"ComplexWrapper({self.complex_num})"

        complex_nums = [
            ComplexWrapper(3 + 2j),
            ComplexWrapper(1 + 1j),
            ComplexWrapper(2 + 3j),
            ComplexWrapper(1 + 2j),
        ]

        result = bubble_sort(complex_nums)

        # Check they are sorted by magnitude
        magnitudes = [abs(c.complex_num) for c in result]
        assert magnitudes == sorted(magnitudes)
