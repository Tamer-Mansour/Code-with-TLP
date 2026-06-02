# Big-O Notation & Complexity Analysis

Every data-structure decision starts with a question: *how does this scale?* Big-O notation gives a language-independent, machine-independent answer by describing how an algorithm's resource usage grows as the input size n grows toward infinity.

## The Core Idea

We measure the **dominant term** and drop constants, because for large n they become irrelevant:

- `5n² + 3n + 100` → **O(n²)**
- `0.001n³` grows faster than `1 000 000 n²` once n > 10⁹ — asymptotic analysis captures this crossover.

Big-O is an **upper bound**: f(n) = O(g(n)) means there exist constants c > 0 and n₀ such that f(n) ≤ c·g(n) for all n ≥ n₀.

## Common Complexity Classes

| Class | Name | Example | 10⁶ operations at 10⁹ ops/s |
|-------|------|---------|------------------------------|
| O(1) | Constant | Array index, dict lookup | < 1 ns |
| O(log n) | Logarithmic | Binary search, BST search | ~20 ns |
| O(n) | Linear | Array scan, BFS/DFS | ~1 ms |
| O(n log n) | Linearithmic | Merge sort, heap sort | ~20 ms |
| O(n²) | Quadratic | Bubble sort, all pairs | ~17 min |
| O(2ⁿ) | Exponential | Brute-force subsets | Heat death of universe |

## Worked Examples

### Example 1 — Nested Loop

```python
def has_duplicate_pair(arr):
    n = len(arr)
    for i in range(n):         # runs n times
        for j in range(i+1, n): # runs up to n-1 times
            if arr[i] == arr[j]:
                return True
    return False
```

Inner loop runs n + (n-1) + ... + 1 = n(n-1)/2 times → **O(n²)**.

The O(n) version uses a hash set:

```python
def has_duplicate_fast(arr):
    seen = set()
    for x in arr:
        if x in seen:   # O(1) average
            return True
        seen.add(x)
    return False        # O(n) total
```

### Example 2 — Logarithmic

Binary search halves the search space at each step. After k steps, the remaining range is n/2ᵏ. When this reaches 1: k = log₂(n). So binary search is **O(log n)**.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Space Complexity

Space complexity counts **extra memory** the algorithm allocates (not counting the input itself).

```python
def reverse_copy(arr):
    return arr[::-1]   # O(n) space — creates a new list of n elements

def reverse_in_place(arr):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        arr[lo], arr[hi] = arr[hi], arr[lo]
        lo += 1; hi -= 1
    # O(1) space — only uses two pointer variables
```

## Best, Average, and Worst Cases

| Scenario | Meaning | Example (QuickSort) |
|----------|---------|---------------------|
| Best case Ω(n log n) | Ideal pivot splits evenly | Sorted input, median pivot |
| Average case Θ(n log n) | Random pivot expected | Random input |
| Worst case O(n²) | Pivot always min/max | Already-sorted + first-element pivot |

In interviews, **worst case** matters most. Average case matters for practical system design.

## Amortised Analysis

Some operations are occasionally expensive but cheap on average. The **aggregate method** computes total cost over n operations divided by n.

Python `list.append` is the canonical example: most appends cost O(1), but every time the buffer doubles, we copy all current elements — this happens at sizes 1, 2, 4, 8, 16, ... Total copy work for n appends ≤ 1 + 2 + 4 + ... + n = 2n. Amortised cost per append = 2n / n = **O(1)**.

## Quick Reference: Data-Structure Complexity

| Structure | Access | Search | Insert | Delete | Space |
|-----------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Dynamic Array (end) | O(1) | O(n) | O(1)* | O(1)* | O(n) |
| Linked List | O(n) | O(n) | O(1)† | O(1)† | O(n) |
| Hash Table | — | O(1)* | O(1)* | O(1)* | O(n) |
| BST (balanced) | — | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | — | O(n) | O(log n) | O(log n) | O(n) |

\* amortised / average case. † given a pointer to the position.

Internalise this table. Every data-structure choice in the rest of the course is a trade-off between the cells above.
