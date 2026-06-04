# Sorting Algorithms

Sorting transforms an unordered sequence into an ordered one. It underpins binary search, merge-join operations, priority queues, and countless other algorithms. Understanding the trade-offs between sorting strategies — time complexity, space, stability, and practical constant factors — is essential for every software engineer.

## Comparison-Based Sorts: O(n²) Algorithms

All three of these algorithms are simple, in-place, and O(n²) in the average and worst cases. They are practical only for small inputs (n ≤ 1000).

### Bubble Sort

Repeatedly scan the array, swapping adjacent out-of-order pairs. The largest unsorted element "bubbles" to its correct position each pass.

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break   # already sorted — O(n) best case
```

Best case O(n) (already sorted with the `swapped` optimisation). Worst case O(n²). **Stable**: equal elements keep their relative order.

### Selection Sort

Find the minimum in the unsorted suffix, then swap it to the front. Performs exactly n−1 swaps — useful when writes are expensive.

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
```

Always O(n²) — no early-exit optimisation. **Not stable** by default (swapping can move equal elements).

### Insertion Sort

Maintain a sorted prefix; insert each new element into its correct position by shifting larger elements right.

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
```

O(n) best case (already sorted), O(n²) worst case. **Stable**. Excellent for nearly sorted data or as the base case in hybrid algorithms (TimSort uses insertion sort for runs ≤ 32 elements).

## Merge Sort — O(n log n) Guaranteed

Divide the array in half, recursively sort each half, then merge the two sorted halves. The merge step is the key insight: combining two sorted arrays takes O(n) time.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**Recurrence:** T(n) = 2T(n/2) + O(n). By the Master Theorem: T(n) = **O(n log n) in all cases** — best, average, and worst. This is a critical distinction from quicksort.

**Stable** (the `<=` in the merge step preserves order of equal elements). **Space:** O(n) auxiliary for the merged arrays.

## Quick Sort — O(n log n) Average, O(n²) Worst

Partition the array around a pivot element so that every element to its left is smaller and every element to its right is larger. Then recursively sort each partition.

```python
def quicksort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quicksort(arr, lo, pivot_idx - 1)
        quicksort(arr, pivot_idx + 1, hi)

def partition(arr, lo, hi):
    pivot = arr[hi]   # last element as pivot
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

**Average case O(n log n)** — with a random pivot, partitions are roughly equal on average. **Worst case O(n²)** — when the pivot is always the minimum or maximum (e.g., already-sorted input with first-element pivot). Choosing a random pivot or the median-of-three avoids this.

**In-place** (O(log n) stack space for recursion). **Not stable** in the standard implementation. In practice, quicksort outperforms merge sort due to better cache locality and lower constant factors, which is why Python's `list.sort()` (TimSort) and Java's `Arrays.sort()` for primitives use quicksort-derived approaches.

## Heap Sort — O(n log n), In-Place

Build a max-heap, then repeatedly extract the maximum to the end of the array.

```python
import heapq

def heapsort(arr):
    negated = [-x for x in arr]
    heapq.heapify(negated)           # O(n)
    return [-heapq.heappop(negated) for _ in range(len(negated))]  # n * O(log n)
```

O(n log n) in all cases. O(1) extra space (ignoring Python overhead). **Not stable**. Poor cache locality due to the jumping access pattern — typically slower than quicksort in practice despite the same asymptotic bound.

## Non-Comparison Sorts

Comparison-based sorting cannot do better than O(n log n) — the information-theoretic lower bound requires at least log₂(n!) ≈ n log n comparisons. Non-comparison sorts break this barrier by exploiting structure in the data.

### Counting Sort — O(n + k)

Count occurrences of each value (range [0..k−1]), then reconstruct the sorted array.

```python
def counting_sort(arr, k):
    count = [0] * k
    for x in arr:
        count[x] += 1
    result = []
    for val, freq in enumerate(count):
        result.extend([val] * freq)
    return result
```

O(n + k) time and space. Only works for integers in a known bounded range. Optimal when k = O(n).

### Radix Sort — O(d · (n + k))

Sort integers digit by digit from least significant to most significant, using a stable sort (counting sort) at each digit position.

O(d × (n + 10)) for base-10 d-digit integers. When d is constant (e.g., 32-bit integers → d = 10 in base 10), this is effectively O(n). **Stable**.

## Sorting Stability

A sort is **stable** if equal elements preserve their original relative order. Stability matters when sorting by multiple keys (e.g., sort by last name, then by first name).

| Algorithm      | Stable | In-Place | Best     | Average   | Worst    |
|---------------|--------|----------|----------|-----------|----------|
| Bubble Sort   | Yes    | Yes      | O(n)     | O(n²)    | O(n²)   |
| Selection Sort| No     | Yes      | O(n²)   | O(n²)    | O(n²)   |
| Insertion Sort| Yes    | Yes      | O(n)     | O(n²)    | O(n²)   |
| Merge Sort    | Yes    | No       | O(n log n) | O(n log n) | O(n log n) |
| Quick Sort    | No*    | Yes      | O(n log n) | O(n log n) | O(n²)  |
| Heap Sort     | No     | Yes      | O(n log n) | O(n log n) | O(n log n) |
| Counting Sort | Yes    | No       | O(n+k)   | O(n+k)   | O(n+k)  |

*Stable quicksort variants exist but have overhead.

## Key Insight: Quicksort Worst Case vs. Merge Sort

A common misconception is that quicksort and merge sort have identical complexity. They do not. Merge sort is O(n log n) in **all cases** — best, average, and worst. Quicksort is O(n log n) on average but **O(n²) in the worst case** (e.g., sorted input with a naive first-element pivot). Always specify which case you mean when citing quicksort's complexity.

## Further Reading

- *Problem Solving with Algorithms and Data Structures using Python* (Miller & Ranum) — https://runestone.academy/ns/books/published/pythonds/index.html — interactive sorting chapter with step-by-step visualisations.
- *Introduction to Algorithms* (MIT 6.006 OCW) — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ — rigorous proofs of comparison-based lower bounds and non-comparison sort analyses.
