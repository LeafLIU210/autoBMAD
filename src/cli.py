"""Command-line interface for the bubble sort algorithm."""

import argparse
import json
import sys
from typing import List, Optional, Tuple, TextIO

from .bubble_sort import bubble_sort


def bubble_sort_detailed(arr: List) -> Tuple[List, int, int]:
    """
    Sort a list using bubble sort and return statistics.

    Args:
        arr: A list of comparable elements to sort

    Returns:
        Tuple of (sorted_list, comparisons_count, swaps_count)
    """
    if arr is None:
        raise TypeError("Input cannot be None")

    result = list(arr)
    comparisons = 0
    swaps = 0

    if len(result) <= 1:
        return result, comparisons, swaps

    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swaps += 1
                swapped = True
        if not swapped:
            break

    return result, comparisons, swaps


def bubble_sort_steps(arr: List) -> Tuple[List, List[Tuple[int, List]]]:
    """
    Sort a list using bubble sort and return each pass.

    Args:
        arr: A list of comparable elements to sort

    Returns:
        Tuple of (sorted_list, list of (pass_number, state_after_pass))
    """
    if arr is None:
        raise TypeError("Input cannot be None")

    result = list(arr)
    steps = []

    if len(result) <= 1:
        return result, steps

    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        steps.append((i + 1, list(result)))
        if not swapped:
            break

    return result, steps


def parse_input_value(value: str) -> float:
    """
    Parse a single input value to a number.

    Args:
        value: String representation of a number

    Returns:
        Parsed float value

    Raises:
        ValueError: If the value cannot be parsed as a number
    """
    value = value.strip()
    if not value:
        raise ValueError("Empty value")
    try:
        # Try integer first
        if '.' not in value:
            return int(value)
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number '{value}'")


def parse_array_string(input_str: str) -> List[float]:
    """
    Parse a string containing numbers into a list.

    Supports:
    - Space-separated: "5 3 1 4 2"
    - Comma-separated: "5,3,1,4,2"
    - JSON array: "[5, 3, 1, 4, 2]"

    Args:
        input_str: String containing numbers

    Returns:
        List of parsed numbers

    Raises:
        ValueError: If parsing fails
    """
    input_str = input_str.strip()

    if not input_str:
        raise ValueError("No input provided")

    # Try JSON format first (both array and object)
    if input_str.startswith('[') or input_str.startswith('{'):
        try:
            result = json.loads(input_str)
            if not isinstance(result, list):
                raise ValueError("Invalid JSON format: expected array")
            # Validate all elements are numbers
            for i, item in enumerate(result):
                if not isinstance(item, (int, float)):
                    raise ValueError(f"Invalid number at position {i + 1}")
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    # Try comma-separated
    if ',' in input_str:
        parts = input_str.split(',')
    else:
        # Space-separated
        parts = input_str.split()

    if not parts:
        raise ValueError("No input provided")

    result = []
    for i, part in enumerate(parts):
        try:
            result.append(parse_input_value(part))
        except ValueError:
            raise ValueError(f"Invalid number '{part.strip()}' at position {i + 1}")

    return result


def read_from_file(filepath: str) -> List[float]:
    """
    Read array data from a file.

    Supports:
    - JSON files with array data
    - Text files with numbers (one per line or comma/space separated)

    Args:
        filepath: Path to the input file

    Returns:
        List of parsed numbers

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filepath}' not found")
    except IOError as e:
        raise IOError(f"Error reading file '{filepath}': {e}")

    if not content:
        raise ValueError("File is empty")

    return parse_array_string(content)


def read_from_stdin() -> List[float]:
    """
    Read array data from standard input.

    Returns:
        List of parsed numbers

    Raises:
        ValueError: If input is invalid
    """
    if sys.stdin.isatty():
        raise ValueError("No input provided via stdin")

    content = sys.stdin.read().strip()
    if not content:
        raise ValueError("No input provided")

    return parse_array_string(content)


def format_output_sorted(result: List) -> str:
    """Format output as sorted array only."""
    return str(result)


def format_output_detailed(original: List, result: List, comparisons: int, swaps: int) -> str:
    """Format output with detailed statistics."""
    lines = [
        f"Input: {original}",
        f"Output: {result}",
        f"Comparisons: {comparisons}",
        f"Swaps: {swaps}"
    ]
    return '\n'.join(lines)


def format_output_steps(original: List, result: List, steps: List[Tuple[int, List]]) -> str:
    """Format output showing each pass."""
    lines = [f"Input: {original}"]
    for pass_num, state in steps:
        lines.append(f"Pass {pass_num}: {state}")
    lines.append(f"Final: {result}")
    return '\n'.join(lines)


def run_interactive_mode(output_format: str = 'sorted') -> None:
    """
    Run the CLI in interactive mode.

    Args:
        output_format: Output format to use ('sorted', 'detailed', 'steps')
    """
    print("Bubble Sort - Interactive Mode")
    print("Enter numbers (comma or space separated), or 'quit' to exit.")
    print("-" * 50)

    while True:
        try:
            user_input = input("Enter array: ").strip()
        except EOFError:
            print("\nExiting...")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if user_input.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if not user_input:
            print("Error: No input provided")
            continue

        try:
            arr = parse_array_string(user_input)
            output = process_and_format(arr, output_format)
            print(output)
            print()
        except ValueError as e:
            print(f"Error: {e}")


def process_and_format(arr: List, output_format: str) -> str:
    """
    Process array and format output.

    Args:
        arr: Input array to sort
        output_format: Output format ('sorted', 'detailed', 'steps')

    Returns:
        Formatted output string
    """
    original = list(arr)

    if output_format == 'detailed':
        result, comparisons, swaps = bubble_sort_detailed(arr)
        return format_output_detailed(original, result, comparisons, swaps)
    elif output_format == 'steps':
        result, steps = bubble_sort_steps(arr)
        return format_output_steps(original, result, steps)
    else:  # 'sorted' is default
        result = bubble_sort(arr)
        return format_output_sorted(result)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='bubble-sort',
        description='Sort arrays using the bubble sort algorithm.',
        epilog='''
Examples:
  %(prog)s 5 3 1 4 2              Sort space-separated numbers
  %(prog)s 5,3,1,4,2              Sort comma-separated numbers
  %(prog)s --input-file data.txt  Sort numbers from a file
  %(prog)s --format detailed      Show sorting statistics
  %(prog)s --format steps         Show each pass of the algorithm
  %(prog)s --interactive          Run in interactive mode

Algorithm Information:
  Bubble sort is a simple sorting algorithm that repeatedly steps through
  the list, compares adjacent elements and swaps them if they are in the
  wrong order. The pass through the list is repeated until the list is sorted.

  Time Complexity: O(n^2) in worst and average case
  Space Complexity: O(n) - creates a new list
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'numbers',
        nargs='*',
        help='Numbers to sort (space or comma separated)'
    )

    parser.add_argument(
        '-i', '--input-file',
        metavar='FILE',
        help='Read input from a file (JSON or text format)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['sorted', 'detailed', 'steps'],
        default='sorted',
        help='Output format: sorted (default), detailed (with stats), steps (show passes)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Interactive mode
    if parsed_args.interactive:
        try:
            run_interactive_mode(parsed_args.format)
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Get input array
    arr = None

    # Priority: file > args > stdin
    if parsed_args.input_file:
        try:
            arr = read_from_file(parsed_args.input_file)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except IOError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif parsed_args.numbers:
        # Join all arguments and parse
        input_str = ' '.join(parsed_args.numbers)
        try:
            arr = parse_array_string(input_str)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        # Try reading from stdin (for piped input)
        if not sys.stdin.isatty():
            try:
                arr = read_from_stdin()
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
        else:
            # No input provided
            print("Error: No input provided", file=sys.stderr)
            print("Use --help for usage information", file=sys.stderr)
            return 1

    # Process and output
    try:
        output = process_and_format(arr, parsed_args.format)
        print(output)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
