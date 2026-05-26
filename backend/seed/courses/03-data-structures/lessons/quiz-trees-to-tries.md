# Quiz: Trees, Heaps, Graphs & Tries

**Q1. In-order traversal of a valid BST produces values in which order?**
- [ ] Random order
- [ ] Reverse sorted order
- [x] Ascending (sorted) order
- [ ] Insertion order

**Q2. What is the worst-case height of an unbalanced BST with n nodes, and when does it occur?**
- [ ] O(log n) — always guaranteed
- [ ] O(sqrt n) — when keys are inserted in blocks
- [x] O(n) — when keys are inserted in sorted (or reverse-sorted) order
- [ ] O(n log n) — depends on the number of rotations

**Q3. In a binary min-heap stored as a 0-indexed array, what is the index of the left child of the node at index i?**
- [ ] 2*i
- [x] 2*i + 1
- [ ] 2*i + 2
- [ ] (i - 1) // 2

**Q4. What is the time complexity of building a heap from an unsorted array of n elements using heapify (sift-down from bottom up)?**
- [ ] O(n log n) — same as inserting one by one
- [ ] O(log n)
- [x] O(n) — geometric series argument shows most nodes sift down very little
- [ ] O(n²)

**Q5. BFS uses which data structure to track nodes to visit next?**
- [ ] Stack — to go deeper first
- [x] Queue — to process nodes in order of discovery distance
- [ ] Priority queue — to visit cheapest nodes first
- [ ] Set — to avoid revisiting nodes

**Q6. An adjacency matrix uses O(V²) space. For a graph with V=10 000 vertices and E=50 000 edges (sparse), how much space does the adjacency list save compared to the matrix?**
- [ ] None — both use the same space for any graph
- [ ] About 2×
- [x] About 2 000× — matrix uses ~10^8 entries vs. ~60 000 for the list
- [ ] About 10× — only edges are different

**Q7. A trie's `starts_with(prefix)` query runs in time proportional to:**
- [ ] The total number of words in the trie
- [x] The length of the prefix — O(L) regardless of dictionary size
- [ ] The total characters across all inserted words
- [ ] O(1) always

**Q8. In Union-Find with path compression AND union by rank, each find/union operation is:**
- [ ] O(log n)
- [ ] O(sqrt n)
- [x] O(α(n)) — the inverse Ackermann function, effectively constant for all practical n
- [ ] O(n)
