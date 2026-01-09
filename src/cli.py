"""Command-Line Interface for Bubble Sort Algorithm."""

import argparse
import json
import sys
from pathlib import Path

from src.bubblesort import bubble_sort


def parse_array_input(array_str: str) -> list[int | float]:
    if not array_str or not array_str.strip():
        raise ValueError("Empty input")
    array_str = array_str.strip()
    if array_str.startswith("[") and array_str.endswith("]"):
        array_str = array_str[1:-1]
    if "," in array_str:
        elements = array_str.split(",")
    else:
        elements = array_str.split()
    result = []
    for elem in elements:
        elem = elem.strip()
        if not elem:
            continue
        try:
            if "." in elem or "e" in elem.lower():
                result.append(float(elem))
            else:
                result.append(int(elem))
        except ValueError:
            raise ValueError(f"Invalid number: {elem}")
    return result


def read_from_file(file_path: str) -> list[int | float]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        content = path.read_text(encoding='utf-8-sig').strip()
        if not content:
            raise ValueError("File is empty")
        return parse_array_input(content)
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"Error reading file: {e}")


def get_sorting_steps(data: list[int | float]) -> list[list[int | float]]:
    steps = [data.copy()]
    result = data.copy()
    n = len(result)
    for i in range(n - 1):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
                steps.append(result.copy())
        if not swapped:
            break
    return steps


def format_output(
    data: list[int | float],
    sorted_data: list[int | float],
    format_type: str = "default",
    show_stats: bool = False,
) -> str:
    if format_type == "json":
        output = {"input": data, "sorted": sorted_data}
        if show_stats:
            steps = get_sorting_steps(data)
            output["statistics"] = {
                "comparisons": len(steps) * len(data) if len(steps) > 1 else 0,
                "swaps": len(steps) - 1 if len(steps) > 1 else 0,
                "steps": len(steps),
            }
        return json.dumps(output, indent=2)
    elif format_type == "steps":
        steps = get_sorting_steps(data)
        output_lines = ["Sorting Steps:"]
        for i, step in enumerate(steps):
            output_lines.append(f"Step {i}: {step}")
        return "\n".join(output_lines)
    elif format_type == "detailed":
        output_lines = [f"Input: {data}", f"Sorted: {sorted_data}"]
        if show_stats:
            steps = get_sorting_steps(data)
            output_lines.append(
                f"Comparisons: {len(steps) * len(data) if len(steps) > 1 else 0}"
            )
            output_lines.append(f"Swaps: {len(steps) - 1 if len(steps) > 1 else 0}")
        return "\n".join(output_lines)
    else:
        return str(sorted_data)


def get_input_data(args: argparse.Namespace) -> list[int | float]:
    # Check for array input first
    if args.array is not None:
        return parse_array_input(args.array)
    # Then check for file input
    elif args.file:
        return read_from_file(args.file)
    # Then check stdin (but not in interactive mode)
    elif hasattr(args, "interactive") and args.interactive:
        raise ValueError("No input provided")
    elif not sys.stdin.isatty():
        content = sys.stdin.read().strip()
        if not content:
            raise ValueError("No input received from stdin")
        return parse_array_input(content)
    # No input provided
    else:
        raise ValueError("No input provided")


def validate_data(data: list[int | float]) -> None:
    if not data:
        raise ValueError("No data to sort")
    for elem in data:
        if not isinstance(elem, (int, float)):
            raise ValueError(f"Non-numeric value found: {elem}")
    if len(data) > 10000:
        raise ValueError("List too long (max 10000 elements)")


def interactive_mode():
    print("Bubble Sort Interactive Mode")
    print("Enter numbers separated by spaces or commas (or quit to exit)")
    print("-" * 50)
    while True:
        try:
            user_input = input("\nEnter array: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not user_input:
                continue
            data = parse_array_input(user_input)
            validate_data(data)
            sorted_data = bubble_sort(data)
            print(f"Sorted: {sorted_data}")
        except (ValueError, EOFError, KeyboardInterrupt) as e:
            if isinstance(e, (EOFError, KeyboardInterrupt)):
                print("\nGoodbye!")
                break
            print(f"Error: {e}")


def batch_mode():
    print("Bubble Sort Batch Mode")
    print("Enter file paths (one per line, or quit to exit)")
    print("-" * 50)
    while True:
        try:
            file_path = input("File path: ").strip()
            if file_path.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not file_path:
                continue
            data = read_from_file(file_path)
            validate_data(data)
            sorted_data = bubble_sort(data)
            print(f"File: {file_path}")
            print(f"Input: {data}")
            print(f"Sorted: {sorted_data}")
            print()
        except (ValueError, FileNotFoundError, EOFError, KeyboardInterrupt) as e:
            if isinstance(e, (EOFError, KeyboardInterrupt)):
                print("\nGoodbye!")
                break
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Bubble Sort Algorithm CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s [1, 3, 2, 5, 4]
  %(prog)s 1,3,2,5,4
  %(prog)s --file input.txt
  cat input.txt | %(prog)s
  %(prog)s --format detailed [5, 3, 8, 1]
  %(prog)s --format steps [3, 1, 2]
  %(prog)s --format json [5, 3, 8, 1]""",
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "array", nargs="?", help='Array to sort (e.g., "[1, 3, 2]" or "1, 3, 2")'
    )
    input_group.add_argument("-f", "--file", help="Read array from file")
    input_group.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )
    input_group.add_argument(
        "--batch",
        action="store_true",
        help="Run in batch mode (process multiple files)",
    )

    parser.add_argument(
        "--format",
        choices=["default", "detailed", "steps", "json"],
        default="default",
        help="Output format (default: default)",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Include statistics in output"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return
    if args.batch:
        batch_mode()
        return

    try:
        data = get_input_data(args)
        validate_data(data)
        sorted_data = bubble_sort(data)
        output = format_output(
            data, sorted_data, format_type=args.format, show_stats=args.stats
        )
        print(output)
    except (ValueError, FileNotFoundError) as e:
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
