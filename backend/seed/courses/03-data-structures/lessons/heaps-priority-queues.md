# Heaps & Priority Queues

A **binary heap** is a complete binary tree stored in a flat array that satisfies the **heap property**: for a min-heap every parent is ≤ both its children, so the root always holds the minimum element. Heaps are the most efficient general-purpose priority queue.

## Why a Flat Array?

A complete binary tree (all levels full except possibly the last, which is filled left-to-right) maps perfectly to a zero-indexed array using simple arithmetic — no pointers needed:

```
Tree:
           1           ← index 0
         /   \
        3     5        ← indices 1, 2
       / \   /
      7   9 8          ← indices 3, 4, 5

Array:  [1, 3, 5, 7, 9, 8]
```

For node at index `i`:
- **Left child:** `2*i + 1`
- **Right child:** `2*i + 2`
- **Parent:** `(i - 1) // 2`

This representation stores a complete binary tree of n nodes in exactly n array slots with zero pointer overhead. Cache locality is excellent — parent and children are near each other in memory.

## Core Operations — Step-by-Step Walkthroughs

### heappush (Sift Up) — O(log n)

**Algorithm:**
1. Append the new value at the end of the array (maintaining completeness).
2. Sift up: repeatedly swap the new element with its parent while it is smaller than the parent.

```
State before push(2):  [1, 3, 5, 7, 9, 8]

1. Append:   [1, 3, 5, 7, 9, 8, 2]   ← index 6
2. Parent of 6 = (6-1)//2 = 2, value arr[2]=5. Is 2 < 5? Yes → swap.
             [1, 3, 2, 7, 9, 8, 5]
3. Parent of 2 = (2-1)//2 = 0, value arr[0]=1. Is 2 < 1? No → stop.

Final:       [1, 3, 2, 7, 9, 8, 5]
```

Each level of the tree has twice as many nodes as the one above, so the height is at most ⌊log₂ n⌋. Sift-up traverses at most one root-to-leaf path: O(log n).

### heappop (Sift Down) — O(log n)

**Algorithm:**
1. Save the root (the minimum).
2. Move the last element to the root position (maintaining completeness — last slot is removed).
3. Sift down: repeatedly swap the new root with the **smaller of its two children** while it is larger than that child.

```
State: [1, 3, 2, 7, 9, 8, 5]   pop() → returns 1

1. Move last to root: [5, 3, 2, 7, 9, 8]
2. Sift down from index 0 (value 5):
   Children: left=arr[1]=3, right=arr[2]=2. Smaller child = 2 at index 2.
   Is 5 > 2? Yes → swap(0, 2): [2, 3, 5, 7, 9, 8]
3. Sift down from index 2 (value 5):
   Children: left=arr[5]=8. Is 5 > 8? No → stop.

Final: [2, 3, 5, 7, 9, 8]   (2 is the new minimum)
```

### heapify — O(n) Not O(n log n)

Building a heap from an unsorted array by calling `heappush` n times is O(n log n). But there is a smarter approach: **sift down every non-leaf node, starting from the last internal node up to the root**.

```
The last internal node is at index (n//2 - 1).
All nodes at index n//2 and above are already leaves — they trivially satisfy the heap property.
```

**Why O(n)?** Nodes near the bottom (most of the tree) sift down a very short distance. Formally, the total work is `∑_{k=0}^{⌊log n⌋} ⌈n/2^(k+1)⌉ × k` which sums to O(n) by the geometric series identity.

```python
import heapq

arr = [5, 3, 8, 1, 9, 2, 7]
heapq.heapify(arr)          # O(n), in-place min-heap
print(arr)                  # [1, 3, 2, 5, 9, 8, 7]  (heap order)
print(arr[0])               # 1 — the minimum
```

## Python heapq Module

Python provides **only a min-heap** via `heapq`. The heap is stored as a regular Python `list`; `heapq` functions treat it as a heap.

```python
import heapq

# Min-heap
h = []
heapq.heappush(h, 4)
heapq.heappush(h, 1)
heapq.heappush(h, 7)
heapq.heappush(h, 2)
print(heapq.heappop(h))    # 1 — always the minimum
print(heapq.heappop(h))    # 2
print(h[0])                # peek at min without removing: 4

# Max-heap: negate all values
maxh = []
for v in [4, 1, 7, 2]:
    heapq.heappush(maxh, -v)
print(-heapq.heappop(maxh))   # 7 — largest value

# Heap with tuples (priority, value) — sorted by priority first
events = []
heapq.heappush(events, (3, "low"))
heapq.heappush(events, (1, "urgent"))
heapq.heappush(events, (2, "medium"))
while events:
    pri, task = heapq.heappop(events)
    print(f"  {pri}: {task}")
# 1: urgent, 2: medium, 3: low
```

### Useful heapq Utilities

```python
import heapq

data = [5, 3, 8, 1, 9, 2]

# k smallest / k largest — O(n log k)
print(heapq.nsmallest(3, data))   # [1, 2, 3]
print(heapq.nlargest(2, data))    # [9, 8]

# Merge k sorted iterables — O(n log k) where n = total elements
import heapq
a = [1, 4, 7]
b = [2, 5, 8]
c = [3, 6, 9]
print(list(heapq.merge(a, b, c)))  # [1,2,3,4,5,6,7,8,9]
```

## Priority Queue — Abstract Data Type

A **priority queue** is an ADT that always removes the highest-priority element. The binary heap is the canonical implementation.

```
ADT operations:
  insert(item, priority)     → O(log n)
  peek_min()                 → O(1)
  extract_min()              → O(log n)
  change_priority(item, new) → O(log n) with position map
```

The key insight: we can associate any object with a priority by using `(priority, object)` tuples, since Python compares tuples lexicographically.

## K-th Largest Element — O(n log k)

To find the k-th largest in a stream of n elements, maintain a min-heap of size k:

```python
import heapq

def kth_largest(nums: list, k: int) -> int:
    """O(n log k) time, O(k) space."""
    min_heap = []
    for x in nums:
        heapq.heappush(min_heap, x)
        if len(min_heap) > k:
            heapq.heappop(min_heap)   # discard values below the k-th largest
    return min_heap[0]   # root = k-th largest

print(kth_largest([3, 2, 1, 5, 6, 4], 2))   # 5
print(kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))  # 4
```

## Median Maintenance — Two Heaps

Maintain the running median of a stream of numbers using a **max-heap of the lower half** and a **min-heap of the upper half**:

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []   # max-heap (negate values): lower half
        self.hi = []   # min-heap: upper half

    def add_num(self, num: int) -> None:
        heapq.heappush(self.lo, -num)          # always push to lo first
        # Balance: lo's max must be <= hi's min
        if self.hi and (-self.lo[0]) > self.hi[0]:
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
        # Keep sizes equal or lo one larger
        if len(self.lo) > len(self.hi) + 1:
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
        elif len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2.0

mf = MedianFinder()
for x in [5, 15, 1, 3]:
    mf.add_num(x)
    print(mf.find_median())   # 5.0, 10.0, 5.0, 4.0
```

## Heapsort — O(n log n), O(1) Space

1. Build a max-heap from the array — O(n).
2. Repeatedly extract the maximum and place it at the last unsorted position — n × O(log n).

```python
def heapsort(arr: list) -> list:
    import heapq
    # Python only has min-heap; negate for max-heap simulation
    negated = [-x for x in arr]
    heapq.heapify(negated)
    return [-heapq.heappop(negated) for _ in range(len(negated))]

print(heapsort([5, 3, 8, 1, 9, 2]))   # [1, 2, 3, 5, 8, 9]
```

Heapsort is O(n log n) in all cases (no worst-case quadratic like quicksort). It uses O(1) extra space. However, it has poor cache behaviour compared to mergesort/quicksort due to the jumping access pattern during sift-down, so it is rarely used in practice.

## Complexity Summary

| Operation              | Binary Heap | Sorted Array | Unsorted Array | Balanced BST |
|------------------------|-------------|--------------|----------------|--------------|
| Find min/max           | O(1)        | O(1)         | O(n)           | O(log n)     |
| Insert                 | O(log n)    | O(n)         | O(1)           | O(log n)     |
| Extract min/max        | O(log n)    | O(1)†        | O(n)           | O(log n)     |
| Delete arbitrary       | O(log n)‡   | O(n)         | O(n)           | O(log n)     |
| Build from n items     | O(n)        | O(n log n)   | O(n)           | O(n log n)   |
| Peek min/max           | O(1)        | O(1)         | O(n)           | O(log n)     |

†Sorted array extract-min requires shifting all elements: O(n).  
‡Requires a position map for O(log n) arbitrary deletion; without it, O(n) to find the element.

## When to Use a Heap

Use a heap when:
- You need the **minimum or maximum repeatedly** (e.g., Dijkstra's algorithm, Huffman coding, task scheduling).
- You need **k-th largest/smallest** in a stream — maintain a heap of size k.
- You need a **streaming median** — the two-heap technique.
- You want **O(n log n) guaranteed** sorting with O(1) space (heapsort).

Prefer a sorted array when you need ordered iteration. Prefer a balanced BST when you need range queries or ordered traversal in addition to priority operations.
