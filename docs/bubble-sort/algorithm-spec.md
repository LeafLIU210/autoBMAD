# Bubble Sort — Formal Algorithm Specification

**Document Type**: Algorithm Specification  
**Version**: 1.0.0  
**Status**: Approved  
**Audience**: Pipeline agents — Architect, PM, Analyst

---

## 1. Algorithm Description

Bubble Sort is a comparison-based sorting algorithm that repeatedly steps through the input
list, compares adjacent elements, and swaps them if they are in the wrong order. Each full
pass through the list "bubbles" the largest unsorted element to its correct position at the
end of the unsorted region.

---

## 2. Standard Bubble Sort

### 2.1 Pseudocode

```
procedure bubble_sort(A: list of sortable items)
    n ← length(A)
    for i from 0 to n - 1 do
        for j from 0 to n - i - 2 do
            if A[j] > A[j + 1] then
                swap(A[j], A[j + 1])
            end if
        end for
    end for
end procedure
```

### 2.2 Python Reference Implementation

```python
def bubble_sort(arr: list) -> None:
    """Sort a list in-place using standard Bubble Sort.

    Args:
        arr: The list to sort. Modified in-place.

    Time Complexity:
        Best:    O(n²) — no early exit
        Average: O(n²)
        Worst:   O(n²)

    Space Complexity: O(1) auxiliary
    """
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```

---

## 3. Optimized Bubble Sort (Early Termination)

### 3.1 Optimization Rationale

If a full pass through the list produces zero swaps, the list is already sorted.
Adding a `swapped` flag allows early termination, reducing best-case complexity to O(n).

### 3.2 Pseudocode

```
procedure optimized_bubble_sort(A: list of sortable items)
    n ← length(A)
    for i from 0 to n - 1 do
        swapped ← false
        for j from 0 to n - i - 2 do
            if A[j] > A[j + 1] then
                swap(A[j], A[j + 1])
                swapped ← true
            end if
        end for
        if swapped = false then
            break        // list is sorted; no further passes needed
        end if
    end for
end procedure
```

### 3.3 Python Reference Implementation

```python
def optimized_bubble_sort(arr: list) -> None:
    """Sort a list in-place using early-termination Bubble Sort.

    Args:
        arr: The list to sort. Modified in-place.

    Time Complexity:
        Best:    O(n)   — already sorted input
        Average: O(n²)
        Worst:   O(n²)

    Space Complexity: O(1) auxiliary
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
```

---

## 4. Complexity Analysis

| Metric            | Standard Bubble Sort | Optimized Bubble Sort |
|-------------------|---------------------|-----------------------|
| Best Time         | O(n²)               | O(n)                  |
| Average Time      | O(n²)               | O(n²)                 |
| Worst Time        | O(n²)               | O(n²)                 |
| Space (auxiliary) | O(1)                | O(1)                  |
| Stable            | Yes                 | Yes                   |
| In-place          | Yes                 | Yes                   |
| Adaptive          | No                  | Yes                   |

---

## 5. Stability Property

Bubble Sort is a **stable** sorting algorithm: elements with equal keys maintain their
relative order from the original input. This is guaranteed because the swap condition
is strictly `A[j] > A[j+1]` (not `>=`), so equal elements are never swapped.

---

## 6. Metrics Instrumentation

The production implementation must collect the following per-sort metrics:

| Metric             | Description                                             |
|--------------------|---------------------------------------------------------|
| `comparisons`      | Total number of element comparisons performed           |
| `swaps`            | Total number of element swaps performed                 |
| `passes`           | Number of outer loop iterations completed               |
| `early_terminated` | Boolean — whether the optimized variant exited early    |

### 6.1 Metrics Data Structure

```python
from dataclasses import dataclass

@dataclass
class SortMetrics:
    comparisons: int
    swaps: int
    passes: int
    early_terminated: bool
    input_size: int
```

---

## 7. Step Visualization Format

When `visualize=True`, each comparison step emits a line to stdout:

```
Step  1: [64, 34, 25, 12, 22]  compare [0]=64 vs [1]=34  → SWAP
Step  2: [34, 64, 25, 12, 22]  compare [1]=64 vs [2]=25  → SWAP
Step  3: [34, 25, 64, 12, 22]  compare [2]=64 vs [3]=12  → SWAP
...
Pass 1 complete → [34, 25, 12, 22, 64]
```

---

## 8. Public API Contract

```python
# bubblepy/core.py

def sort(
    data: list,
    *,
    copy: bool = False,
    optimized: bool = True,
    visualize: bool = False,
    key: Callable | None = None,
    reverse: bool = False,
) -> tuple[list, SortMetrics]:
    """Primary public sort entry point.

    Args:
        data:      Input list to sort.
        copy:      If True, return a sorted copy; original is not modified.
        optimized: If True, use early-termination variant.
        visualize: If True, print step-by-step comparison output to stdout.
        key:       Optional key function applied before comparisons (like sorted()).
        reverse:   If True, sort in descending order.

    Returns:
        Tuple of (sorted_list, SortMetrics).
        If copy=False, sorted_list is the same object as data (mutated in-place).
        If copy=True, sorted_list is a new list; data is unchanged.
    """
```

---

## 9. Known Limitations

1. **Not suitable for large datasets**: O(n²) average complexity makes Bubble Sort impractical
   beyond ~10,000 elements for performance-sensitive applications.
2. **No parallelism**: The sequential comparison model does not support parallel execution.
3. **Memory locality**: While O(1) extra space, cache behavior degrades on very large arrays
   due to sequential traversal pattern with repeated passes.

---

## 10. Educational Value

Bubble Sort remains valuable as a teaching tool because:
- The algorithm logic is simple enough to explain in one paragraph
- The swap visualization makes the sorting process visually intuitive
- It demonstrates why algorithm complexity matters (compare with O(n log n) sorts)
- Stability and in-place properties are easy to reason about
