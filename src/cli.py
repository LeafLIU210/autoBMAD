"""Command Line Interface for bubble sort application."""

import argparse
import json
import sys

from src.bubblesort import bubble_sort


def parse_array_input(input_str: str) -> list[int | float]:
    """Parse a string input into a list of numbers.

    Args:
        input_str: String representation of an array (e.g., "1, 2, 3" or "[1, 2, 3]")

    Returns:
        List of parsed numbers

    Raises:
        ValueError: If input is empty or contains invalid numbers
    """
    if not input_str or not input_str.strip():
        raise ValueError("Empty input")

    # Remove brackets if present
    input_str = input_str.strip()
    if input_str.startswith("[") and input_str.endswith("]"):
        input_str = input_str[1:-1]

    # Split by comma or whitespace
    parts = input_str.replace(",", " ").split()

    # Filter out empty parts
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        raise ValueError("Empty input")

    result = []
    for part in parts:
        try:
            num = float(part)
            # Check if it's an integer
            if num.is_integer():
                result.append(int(num))
            else:
                result.append(num)
        except ValueError as err:
            raise ValueError(f"Invalid number: {part}") from err

    return result


def read_from_file(file_path: str) -> list[int | float]:
    """Read array data from a file.

    Args:
        file_path: Path to the file

    Returns:
        List of numbers from the file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or contains invalid data
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise ValueError("File is empty")

        return parse_array_input(content)
    except (OSError, UnicodeDecodeError) as err:
        raise ValueError(f"Error reading file: {err}") from err


def get_sorting_steps(data: list[int | float]) -> list[list[int | float]]:
    """Get all steps of the bubble sort algorithm.

    Args:
        data: List of numbers to sort

    Returns:
        List of lists showing each step of sorting
    """
    # Create a working copy
    steps = [data.copy()]
    working = data.copy()
    n = len(working)

    if n <= 1:
        return steps

    swapped = True
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if working[j] > working[j + 1]:
                working[j], working[j + 1] = working[j + 1], working[j]
                swapped = True
                steps.append(working.copy())

        if not swapped:
            break

    return steps


def format_output(
    original_data: list[int | float],
    sorted_data: list[int | float],
    format_type: str = "default",
    show_stats: bool = False,
) -> str:
    """Format the sorting output.

    Args:
        original_data: Original unsorted data
        sorted_data: Sorted data
        format_type: Output format ("default", "json", "steps", "detailed")
        show_stats: Whether to include statistics

    Returns:
        Formatted output string
    """
    if format_type == "json":
        output = {"input": original_data, "sorted": sorted_data}
        if show_stats:
            output["statistics"] = {
                "comparisons": len(original_data) ** 2,  # Approximation
                "swaps": sum(
                    1
                    for i in range(len(original_data))
                    for j in range(len(original_data) - 1)
                    if original_data[i] > original_data[j]
                ),
                "steps": len(get_sorting_steps(original_data)),
            }
        return json.dumps(output, indent=2)

    elif format_type == "steps":
        steps = get_sorting_steps(original_data)
        output_lines = ["Sorting Steps:"]
        for i, step in enumerate(steps):
            output_lines.append(f"Step {i}: {step}")
        return "\n".join(output_lines)

    elif format_type == "detailed":
        lines = [f"Input: {original_data}", f"Sorted: {sorted_data}"]
        if show_stats:
            lines.append(f"Comparisons: {len(original_data) ** 2}")
            lines.append(
                f"Swaps: {sum(1 for i in range(len(original_data)) for j in range(len(original_data) - 1) if original_data[i] > original_data[j])}"
            )
            lines.append(f"Steps: {len(get_sorting_steps(original_data))}")
        return "\n".join(lines)

    else:  # default
        return str(sorted_data)


def get_input_data(args: argparse.Namespace) -> list[int | float]:
    """Get input data from various sources.

    Args:
        args: Command line arguments namespace

    Returns:
        List of numbers

    Raises:
        ValueError: If no input provided
    """
    if args.array is not None:
        return parse_array_input(args.array)
    elif args.file is not None:
        return read_from_file(args.file)
    elif hasattr(args, "interactive") and args.interactive:
        # Interactive mode - will prompt user
        return []
    else:
        # Check stdin
        if sys.stdin.isatty():
            raise ValueError("No input provided")
        else:
            content = sys.stdin.read().strip()
            if not content:
                raise ValueError("No input received from stdin")
            return parse_array_input(content)


def validate_data(data: list[int | float]) -> None:
    """Validate input data.

    Args:
        data: List to validate

    Raises:
        ValueError: If data is invalid
    """
    if not data:
        raise ValueError("No data to sort")

    if len(data) > 10000:
        raise ValueError("List too long (max 10000 elements)")

    for item in data:
        if not isinstance(item, (int, float)):
            raise ValueError(f"Non-numeric value found: {item}")


def interactive_mode() -> None:
    """Run interactive mode for sorting."""
    print("Interactive Mode - Enter numbers to sort (or 'quit' to exit)")
    print("Example: 1, 2, 3 or [1, 2, 3]")

    while True:
        try:
            user_input = input("\nEnter numbers: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            try:
                data = parse_array_input(user_input)
                validate_data(data)
                sorted_data = bubble_sort(data)
                print(f"Sorted: {sorted_data}")
            except ValueError as e:
                print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def batch_mode() -> None:
    """Run batch mode for sorting from files."""
    print("Batch Mode - Enter file paths (or 'quit' to exit)")
    print(
        "Supported formats: .txt files with comma-separated or space-separated numbers"
    )

    while True:
        try:
            file_path = input("\nEnter file path: ").strip()

            if file_path.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not file_path:
                continue

            try:
                data = read_from_file(file_path)
                validate_data(data)
                sorted_data = bubble_sort(data)
                print(f"Sorted: {sorted_data}")
            except (ValueError, FileNotFoundError) as e:
                print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Bubble Sort CLI - Sort lists of numbers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("array", nargs="?", help='Array to sort (e.g., "1, 2, 3")')
    input_group.add_argument("-f", "--file", help="Read from file")
    input_group.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )
    input_group.add_argument(
        "--batch", action="store_true", help="Run in batch mode (process files)"
    )

    # Output options
    parser.add_argument(
        "--format",
        choices=["default", "json", "steps", "detailed"],
        default="default",
        help="Output format",
    )
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    try:
        if args.interactive:
            interactive_mode()
            return

        if args.batch:
            batch_mode()
            return

        # Get and validate data
        data = get_input_data(args)
        validate_data(data)

        # Sort data
        sorted_data = bubble_sort(data)

        # Format and output
        output = format_output(data, sorted_data, args.format, args.stats)
        print(output)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
