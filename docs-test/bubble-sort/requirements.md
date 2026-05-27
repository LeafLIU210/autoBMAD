# Bubble Sort Library — Stakeholder Requirements

**Document Type**: Requirements Specification  
**Version**: 1.0.0  
**Status**: Approved  
**Audience**: Pipeline agents — Analyst, PM, PO

---

## 1. Stakeholder Analysis

### 1.1 Primary Stakeholders

| Stakeholder          | Role                    | Key Interest                                    |
|----------------------|-------------------------|-------------------------------------------------|
| CS Students          | End User                | Learn how Bubble Sort works with visual output  |
| Educators            | End User + Content Creator | Embed algorithm in course materials          |
| Software Developers  | End User                | Use as a reference or test fixture              |
| Library Maintainer   | Internal Team           | Stable API, low maintenance burden              |
| Open Source Community | External Contributor   | Clear contribution guide, clean codebase        |

### 1.2 Stakeholder Needs Summary

**CS Students need:**
- A simple, runnable example they can import and experiment with
- Visual step-by-step output to understand the algorithm's behavior
- Clear error messages when they pass invalid inputs

**Educators need:**
- A stable API that does not change between academic semesters
- Ability to demonstrate best-case vs. worst-case with the same code
- Metrics (comparisons, swaps) to support complexity analysis exercises

**Software Developers need:**
- A predictable, typed public API
- Zero mandatory dependencies (pure Python standard library)
- A CLI tool for quick scripting and shell-level usage

---

## 2. Functional Requirements

### FR-01: Core Sort Function

**Priority**: P0 — Must Have  
**Description**: The library MUST expose a `sort()` function that accepts a list of comparable
elements and returns the sorted list along with metrics.

**Acceptance Criteria**:
- `sort([3, 1, 2])` returns `([1, 2, 3], SortMetrics(...))`
- Input list of length 0 or 1 is handled without error
- Raises `TypeError` when elements are not mutually comparable
- Returns identical object as input when `copy=False` (default)
- Returns a new list when `copy=True`

---

### FR-02: Optimized Sort Variant

**Priority**: P0 — Must Have  
**Description**: The library MUST provide an early-termination variant that detects a sorted
list in O(n) time.

**Acceptance Criteria**:
- `sort([1, 2, 3], optimized=True)` completes in a single pass (1 comparison per element pair)
- `SortMetrics.early_terminated` is `True` when sort exits early
- `SortMetrics.passes` reflects the actual number of passes executed

---

### FR-03: Step Visualization

**Priority**: P1 — Should Have  
**Description**: The library SHOULD support an optional visualization mode that prints each
comparison step to stdout.

**Acceptance Criteria**:
- `sort([3, 1, 2], visualize=True)` prints step-by-step output to stdout
- Output format: `Step N: [state] compare [i]=val vs [j]=val → SWAP|NO-SWAP`
- Each pass boundary is marked: `Pass N complete → [state]`
- No visualization output when `visualize=False` (default)

---

### FR-04: Reverse Sort Support

**Priority**: P1 — Should Have  
**Description**: The library SHOULD support sorting in descending order.

**Acceptance Criteria**:
- `sort([1, 3, 2], reverse=True)` returns `([3, 2, 1], SortMetrics(...))`
- Works with both standard and optimized variants

---

### FR-05: Custom Key Function

**Priority**: P1 — Should Have  
**Description**: The library SHOULD accept a `key` callable, mirroring the built-in `sorted()`.

**Acceptance Criteria**:
- `sort(['banana', 'apple', 'fig'], key=len)` sorts by string length
- `key` function is applied once per element, not on every comparison (Schwartzian transform)
- Raises `TypeError` if `key` is not callable

---

### FR-06: CLI Tool

**Priority**: P1 — Should Have  
**Description**: The package SHOULD install a `bubblepy` CLI entry point.

**Acceptance Criteria**:
- `bubblepy sort 3 1 2` outputs `1 2 3` (space-separated)
- `bubblepy sort --visualize 3 1 2` prints step-by-step output then final result
- `bubblepy sort --reverse 3 1 2` outputs `3 2 1`
- `bubblepy sort --copy 3 1 2` does not mutate; confirms `copy=True` mode in output
- `bubblepy --version` prints current package version
- Non-zero exit code on invalid input

---

### FR-07: SortMetrics Reporting

**Priority**: P2 — Nice to Have  
**Description**: The library SHOULD expose detailed per-sort metrics.

**Acceptance Criteria**:
- `metrics.comparisons` is the exact count of `>` operations performed
- `metrics.swaps` is the exact count of element position exchanges
- `metrics.passes` is the number of outer loop iterations
- `metrics.input_size` matches `len(input)`
- Metrics are immutable after sort completion

---

## 3. Non-Functional Requirements

### NFR-01: Performance

- Sort 10,000 integers in under 5 seconds on a standard laptop (2020+)
- No memory allocation beyond O(1) auxiliary space per sort call

### NFR-02: Compatibility

- Supports Python 3.11, 3.12, 3.13
- Zero mandatory runtime dependencies (no numpy, no external packages)
- Optional dev dependencies: pytest, coverage, ruff, mypy

### NFR-03: Quality

- 100% line coverage on `bubblepy/core.py`
- All public functions have Google-style docstrings
- Passes `ruff check` and `mypy --strict` without warnings

### NFR-04: API Stability

- Public API follows semantic versioning (semver)
- Breaking changes require a major version bump
- Deprecation warnings issued at least one minor version before removal

### NFR-05: Accessibility (CLI)

- Error messages written to stderr, results to stdout
- Exit code 0 on success, non-zero on any error
- `--help` available on all subcommands

---

## 4. Out of Scope

The following items are explicitly out of scope for v1.0:

- Parallel or multi-threaded sort variants
- GPU-accelerated sort
- Integration with NumPy arrays or pandas DataFrames
- Web or GUI interface
- Sorting algorithms other than Bubble Sort variants

---

## 5. Acceptance Test Matrix

| Test ID | Feature         | Input                    | Expected Output                          | Priority |
|---------|-----------------|--------------------------|------------------------------------------|----------|
| AT-01   | Basic sort      | `[5, 3, 8, 1, 9, 2]`    | `[1, 2, 3, 5, 8, 9]`                    | P0       |
| AT-02   | Empty list      | `[]`                     | `([], SortMetrics(0,0,0,False,0))`       | P0       |
| AT-03   | Single element  | `[42]`                   | `([42], SortMetrics(0,0,0,False,1))`     | P0       |
| AT-04   | Already sorted  | `[1, 2, 3]` optimized    | `early_terminated=True`, `passes=1`      | P0       |
| AT-05   | Reverse sorted  | `[3, 2, 1]`              | `[1, 2, 3]`, max swaps                   | P0       |
| AT-06   | Copy mode       | `copy=True`              | Original list unchanged                  | P0       |
| AT-07   | Descending      | `[1,3,2]` `reverse=True` | `[3, 2, 1]`                              | P1       |
| AT-08   | Key function    | `['bb','a','ccc']` `key=len` | `['a', 'bb', 'ccc']`               | P1       |
| AT-09   | Visualize       | `[3,1,2]` `visualize=True` | stdout contains "Step" lines           | P1       |
| AT-10   | CLI basic       | `bubblepy sort 3 1 2`    | stdout: `1 2 3`, exit 0                  | P1       |
| AT-11   | CLI invalid     | `bubblepy sort abc`      | stderr message, exit non-zero            | P1       |
| AT-12   | Metrics count   | `[2, 1]`                 | `comparisons=1`, `swaps=1`               | P2       |

---

## 6. Definition of Done

A feature is considered done when:
1. Implementation passes all related acceptance tests
2. Unit tests achieve 100% line coverage for the feature
3. Docstrings are complete and follow Google style
4. No ruff or mypy errors
5. CHANGELOG entry added
6. API reference updated if public interface changed
