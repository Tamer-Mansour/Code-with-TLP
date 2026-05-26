# Searching and Sorting

Searching and sorting are two of the most fundamental operations in computing. Nearly every application—from a contact book to a search engine—relies on efficient searching and sorting. This lesson walks through the major algorithms step by step, with full traces and complexity analysis.

## Searching

The goal: given a collection of items and a target value, find the item's position (or determine it is absent).

### Linear Search

**Idea:** Check each element one by one from left to right until the target is found or the list ends.

```
ALGORITHM LinearSearch(list, target):
    FOR i FROM 0 TO len(list) - 1:
        IF list[i] == target:
            RETURN i          # found at index i
    RETURN -1                  # not found
```

**Full trace: Find 7 in `[3, 1, 4, 1, 5, 9, 7, 6]`**

| i | list[i] | == 7? |
|---|---------|-------|
| 0 | 3 | No |
| 1 | 1 | No |
| 2 | 4 | No |
| 3 | 1 | No |
| 4 | 5 | No |
| 5 | 9 | No |
| 6 | 7 | **Yes → return 6** |

**Complexity:**
- Best case: target at index 0 → O(1)
- Worst case: target at end or absent → O(n)
- Works on **unsorted** data

**When to use linear search:** small lists, unsorted data, or when you only search once (sorting first would cost more than just scanning).

### Binary Search

**Idea:** Only works on a **sorted** list. Compare the target to the middle element. If equal, done. If the target is smaller, search the left half; if larger, search the right half. Repeat.

Each comparison eliminates *half* the remaining elements.

```
ALGORITHM BinarySearch(sorted_list, target):
    low ← 0
    high ← len(sorted_list) - 1
    WHILE low <= high:
        mid ← (low + high) // 2
        IF sorted_list[mid] == target:
            RETURN mid
        ELSE IF sorted_list[mid] < target:
            low ← mid + 1        # target is in right half
        ELSE:
            high ← mid - 1       # target is in left half
    RETURN -1   # not found
```

**Full trace: Find 7 in `[1, 2, 4, 5, 7, 9, 12]` (indices 0–6)**

| Step | low | high | mid | list[mid] | Decision |
|------|-----|------|-----|-----------|----------|
| 1 | 0 | 6 | 3 | 5 | 7 > 5 → low = 4 |
| 2 | 4 | 6 | 5 | 9 | 7 < 9 → high = 4 |
| 3 | 4 | 4 | 4 | 7 | **Found! Return 4** |

Only 3 comparisons to search 7 elements.

**For 1,000,000 elements:** log₂(1,000,000) ≈ 20 comparisons at most.

**Complexity:**
- Best case: O(1) (target is at the middle on first try)
- Worst case: O(log n)

**Key requirement:** the list must be **sorted**. If you need to search the same data many times, sort once and use binary search repeatedly.

## Sorting

The goal: rearrange a list so that elements are in a specified order (usually ascending).

### Bubble Sort

**Idea:** Make repeated passes through the list, swapping adjacent elements that are out of order. After each pass, the largest unsorted element has "bubbled" to its final position at the right end.

```
ALGORITHM BubbleSort(list):
    n ← len(list)
    FOR i FROM 0 TO n - 2:
        FOR j FROM 0 TO n - 2 - i:
            IF list[j] > list[j+1]:
                SWAP list[j] and list[j+1]
```

**Full trace: Sort `[5, 3, 8, 1, 4]`**

```
Initial:   [5, 3, 8, 1, 4]

Pass 1 (i=0): compare j=0,1,2,3
  j=0: 5>3 → swap → [3, 5, 8, 1, 4]
  j=1: 5<8 → no swap
  j=2: 8>1 → swap → [3, 5, 1, 8, 4]
  j=3: 8>4 → swap → [3, 5, 1, 4, 8]   ← 8 is in final position

Pass 2 (i=1): compare j=0,1,2
  j=0: 3<5 → no swap
  j=1: 5>1 → swap → [3, 1, 5, 4, 8]
  j=2: 5>4 → swap → [3, 1, 4, 5, 8]   ← 5 is in final position

Pass 3 (i=2): compare j=0,1
  j=0: 3>1 → swap → [1, 3, 4, 5, 8]
  j=1: 3<4 → no swap                   ← 4 is in final position

Pass 4 (i=3): compare j=0
  j=0: 1<3 → no swap                   ← 3 and 1 are in final position

Result: [1, 3, 4, 5, 8] ✓
```

**Complexity:** O(n²) worst and average case, O(n) best case (already sorted, with optimisation).

Bubble sort is simple to understand but rarely used in practice because O(n²) is too slow for large inputs.

### Selection Sort

**Idea:** Find the smallest element in the unsorted portion and swap it to the front, then repeat for the remaining unsorted portion.

```
ALGORITHM SelectionSort(list):
    n ← len(list)
    FOR i FROM 0 TO n - 2:
        min_idx ← i
        FOR j FROM i+1 TO n - 1:
            IF list[j] < list[min_idx]:
                min_idx ← j
        SWAP list[i] and list[min_idx]
```

**Trace: Sort `[5, 3, 8, 1, 4]`**

```
i=0: find min in [5,3,8,1,4] → min=1 at idx 3 → swap list[0] and list[3]
     → [1, 3, 8, 5, 4]

i=1: find min in [3,8,5,4] → min=3 at idx 1 → no swap needed
     → [1, 3, 8, 5, 4]

i=2: find min in [8,5,4] → min=4 at idx 4 → swap list[2] and list[4]
     → [1, 3, 4, 5, 8]

i=3: find min in [5,8] → min=5 at idx 3 → no swap
     → [1, 3, 4, 5, 8] ✓
```

**Complexity:** Always O(n²)—the number of comparisons is n(n-1)/2 regardless of input order.

Selection sort makes fewer *swaps* than bubble sort (at most n), which is useful when swapping is expensive.

### Merge Sort (Divide and Conquer)

**Idea:** Split the list in half, recursively sort each half, then merge the two sorted halves into one sorted list.

```
ALGORITHM MergeSort(list):
    IF len(list) <= 1:
        RETURN list
    mid ← len(list) // 2
    left  ← MergeSort(list[0 .. mid])
    right ← MergeSort(list[mid .. end])
    RETURN Merge(left, right)

ALGORITHM Merge(left, right):
    result ← []
    i ← 0, j ← 0
    WHILE i < len(left) AND j < len(right):
        IF left[i] <= right[j]:
            APPEND left[i] to result; i ← i + 1
        ELSE:
            APPEND right[j] to result; j ← j + 1
    APPEND remaining elements of left[i:] and right[j:]
    RETURN result
```

**Trace: Sort `[38, 27, 43, 3]`**

```
MergeSort([38, 27, 43, 3])
├── MergeSort([38, 27])
│   ├── MergeSort([38]) → [38]
│   ├── MergeSort([27]) → [27]
│   └── Merge([38], [27]) → [27, 38]
├── MergeSort([43, 3])
│   ├── MergeSort([43]) → [43]
│   ├── MergeSort([3])  → [3]
│   └── Merge([43], [3]) → [3, 43]
└── Merge([27, 38], [3, 43]):
    Compare 27 vs 3  → take 3   → [3]
    Compare 27 vs 43 → take 27  → [3, 27]
    Compare 38 vs 43 → take 38  → [3, 27, 38]
    Remaining: [43]  → take 43  → [3, 27, 38, 43] ✓
```

**Complexity:** O(n log n) always—the list splits log₂(n) times, and merging takes O(n) at each level.

Merge sort is the basis of Python's built-in `sorted()` function (Timsort, a hybrid merge/insertion sort).

### Quick Sort (Brief Overview)

**Idea:** Choose a "pivot" element, partition the list so all elements smaller than the pivot come before it and all larger elements come after, then recursively sort each partition.

- Average case: O(n log n)
- Worst case: O(n²) (if the pivot is always the smallest or largest element — rare with good pivot selection)
- In practice: often the fastest in-memory sort due to excellent cache behaviour

Python's `list.sort()` and `sorted()` use **Timsort**, a hybrid of merge sort and insertion sort, engineered for real-world data patterns.

## Comparing Algorithms

| Algorithm | Best case | Average | Worst case | Space | Stable? | Notes |
|-----------|-----------|---------|------------|-------|---------|-------|
| Linear search | O(1) | O(n) | O(n) | O(1) | — | Works on unsorted data |
| Binary search | O(1) | O(log n) | O(log n) | O(1) | — | Requires sorted data |
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Simple; rarely practical |
| Selection sort | O(n²) | O(n²) | O(n²) | O(1) | No | Minimal swaps |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Predictable; used in Python |
| Quick sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No | Fast in practice; most languages' default |

**Stable sort**: maintains the relative order of equal elements. Important when sorting objects with multiple fields (sort by last name, preserve first-name order for ties).

## Why Complexity Matters: A Numbers Game

With n = 1,000,000 items and assuming 10⁹ operations/second:

| Algorithm | Operations | Time |
|-----------|-----------|------|
| O(log n) binary search | ~20 | Instant |
| O(n) linear search | 1,000,000 | 1 ms |
| O(n log n) merge sort | 20,000,000 | 20 ms |
| O(n²) bubble sort | 1,000,000,000,000 (10¹²) | **~17 minutes** |

Choosing O(n²) over O(n log n) turns a 20-millisecond sort into a 17-minute one. At 10⁸ items, it would take months.

## Common Misconceptions

**"Bubble sort is called that because it's fast like bubbles rising."**
The name refers to how the largest values "bubble up" to the end of the array on each pass. It is one of the slowest practical sorting algorithms.

**"Binary search works on any list."**
Binary search **requires a sorted list**. On an unsorted list, binary search gives wrong answers. Always sort first (or use a data structure that maintains order, like a balanced BST or heap).

**"Merge sort always uses extra memory, so it's worse than in-place sorts."**
Merge sort uses O(n) extra memory, but its guaranteed O(n log n) worst case makes it preferable to quicksort in situations where worst-case performance matters (e.g., sorting user data in a database). Python's Timsort is merge sort-based.

## Key Takeaways

- **Linear search** is simple and works on unsorted data but is O(n). **Binary search** is O(log n) but requires sorted data.
- **Bubble sort** and **selection sort** are O(n²)—simple to implement but too slow for large datasets.
- **Merge sort** uses divide-and-conquer to achieve O(n log n) in all cases; it is stable and predictable.
- **Quick sort** is often fastest in practice but has O(n²) worst case; real implementations use randomised pivots to avoid it.
- Choosing the right algorithm can make the difference between milliseconds and hours for large datasets.
