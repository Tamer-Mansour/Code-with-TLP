# Quiz: Heaps, Priority Queues & Sorting

**Q1. In a zero-indexed binary min-heap stored as an array, what is the index of the parent of the node at index i?**
- [ ] i // 2
- [x] (i - 1) // 2
- [ ] 2 * i + 1
- [ ] i - 1

**Q2. Which statement about heaps and priority queues is correct?**
- [ ] A heap is the same thing as a priority queue
- [ ] A priority queue is a concrete data structure using arrays
- [x] A priority queue is an Abstract Data Type (ADT); a binary heap is one concrete implementation of it
- [ ] A binary heap is a Binary Search Tree where both children are less than the parent

**Q3. What is the time complexity of building a heap from n unsorted elements using the "heapify from the bottom" approach?**
- [ ] O(n log n) — same as inserting n elements one at a time
- [x] O(n) — most nodes sift down only a short distance
- [ ] O(n²) — each element compared with all others
- [ ] O(log n) — only the root needs sifting

**Q4. You want to find the 3rd largest element in a stream of 1 million numbers using O(1) extra space on average. The best approach is:**
- [ ] Sort all numbers and index from the end — O(n log n)
- [ ] Use a max-heap and pop three times — O(n)
- [x] Maintain a min-heap of size 3; when the heap exceeds 3, pop the minimum — O(n log 3) = O(n)
- [ ] Scan the array three times — O(3n) = O(n) but simpler

**Q5. Merge sort guarantees O(n log n) in all cases. Quicksort's worst-case complexity is:**
- [ ] O(n log n) — same as merge sort
- [ ] O(n) — linear scan
- [x] O(n²) — occurs when the pivot is always the minimum or maximum element
- [ ] O(n^1.5) — average of O(n log n) and O(n²)

**Q6. Which sorting algorithm is stable AND O(n log n) guaranteed in all cases?**
- [ ] Quicksort
- [ ] Heapsort
- [x] Merge sort
- [ ] Counting sort (only works for bounded integers)

**Q7. You are sorting 1 million 32-bit integers. Which statement about the theoretical lower bound is correct?**
- [ ] No comparison-based sort can beat O(n) for any input
- [x] Any comparison-based sort requires Ω(n log n) comparisons in the worst case — this is an information-theoretic lower bound
- [ ] Counting sort beats this lower bound because it is comparison-based
- [ ] The lower bound applies only to stable sorts

**Q8. Heapsort and merge sort both have O(n log n) worst-case complexity. Why is quicksort often faster in practice?**
- [ ] Quicksort has a better worst case
- [ ] Quicksort uses less total work per element
- [x] Quicksort has better cache locality — it accesses contiguous memory regions — and lower constant factors compared to merge sort's auxiliary array allocations and heapsort's jumping access pattern
- [ ] Quicksort is stable, which avoids redundant comparisons
