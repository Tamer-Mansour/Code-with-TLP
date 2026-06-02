# Video: Binary Trees & Binary Search Trees

This video builds a binary search tree (BST) from scratch, implements all four traversals (in-order, pre-order, post-order, level-order), and explains insert, search, and delete operations with Big-O analysis.

**Key takeaways:**
- BST in-order traversal always produces a sorted sequence — this is the structural invariant that makes BSTs useful for range queries.
- Deletion is the trickiest BST operation: the two-children case requires finding the in-order successor (or predecessor) to maintain the BST property.
- A balanced BST guarantees O(log n) for all operations; a degenerate (sorted-insertion) BST degrades to O(n) — motivation for AVL trees and red-black trees.

**Approximate timestamps:**
- 0:00 — Tree terminology: root, leaf, height, depth, balance factor
- 8:00 — BST insert and search with worked examples
- 20:00 — In-order, pre-order, and post-order traversals (recursive + iterative)
- 32:00 — Level-order traversal (BFS on trees)
- 40:00 — BST delete: leaf, one-child, two-children cases
- 50:00 — AVL trees: rotations and height balancing overview
