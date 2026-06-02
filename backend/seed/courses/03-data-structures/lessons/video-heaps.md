# Video: Heaps & Priority Queues

This video explains the binary min-heap and max-heap as array-based complete binary trees, walks through the heapify, push, and pop operations, and shows how Python's `heapq` module wraps these primitives.

**Key takeaways:**
- A heap stores its complete binary tree in a flat array: children of index `i` are at `2i+1` and `2i+2`; the parent of `i` is at `(i-1)//2`.
- `heapq.heappush` and `heapq.heappop` both run in O(log n) by "bubbling" the element up or down the tree.
- The "min-heap of size k" pattern (push each element, pop when size exceeds k) solves top-k and streaming-median problems in O(n log k) time.

**Approximate timestamps:**
- 0:00 — Heap property, complete binary tree, and array encoding
- 10:00 — Sift-up (heappush) and sift-down (heappop) step by step
- 22:00 — Building a heap in O(n) with heapify
- 30:00 — Python `heapq` module: push, pop, pushpop, nlargest, nsmallest
- 38:00 — Priority queue applications: Dijkstra's, k-th largest, merge k sorted lists
