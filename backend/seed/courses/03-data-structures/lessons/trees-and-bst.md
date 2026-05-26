# Trees & Binary Search Trees

A **tree** is a hierarchical data structure of nodes where each node has a value and zero or more children. Trees are **acyclic** — there is exactly one path between any two nodes — and always have exactly one **root** (the topmost node, with no parent).

## Terminology

| Term        | Definition                                                               |
|-------------|--------------------------------------------------------------------------|
| Root        | The topmost node (no parent). There is exactly one root per tree.        |
| Leaf        | A node with no children.                                                 |
| Height      | Length of the longest root-to-leaf path (edges, not nodes).             |
| Depth       | Distance (edge count) from the root to a given node.                    |
| Level        | All nodes at the same depth form one level.                              |
| Subtree     | A node plus all its descendants.                                         |
| Degree      | Number of children of a node.                                            |
| Binary tree | Every node has at most two children (left, right).                       |
| Full BT     | Every node has 0 or 2 children (never 1).                               |
| Complete BT | All levels filled except possibly the last, filled left-to-right.       |
| Perfect BT  | All leaves at the same level; exactly 2^(h+1)−1 nodes at height h.     |

```
         10          ← root (depth 0, level 0)
        /  \
       5    15       ← depth 1
      / \     \
     2   7    20     ← depth 2 — leaves: 2, 7, 20
```

Height = 2. Node 5 has degree 2. Node 15 has degree 1.

## Binary Tree Node

```python
class TreeNode:
    def __init__(self, val: int):
        self.val = val
        self.left = None
        self.right = None
```

A perfect binary tree of height h has `2^(h+1) − 1` total nodes, and the bottom level alone holds `2^h` nodes — more than all other levels combined. This geometric doubling explains why O(log n) height is so powerful.

## Tree Traversals

All four classic traversals visit every node exactly once — O(n) time. Space is O(h) for the recursion stack (h = height). For a balanced tree h = O(log n); for a skewed tree h = O(n).

### In-order: Left → Root → Right

```python
def inorder(node, result):
    if node:
        inorder(node.left, result)
        result.append(node.val)
        inorder(node.right, result)
```

**Key property:** in-order traversal of a BST yields values in ascending sorted order.

### Pre-order: Root → Left → Right

```python
def preorder(node, result):
    if node:
        result.append(node.val)
        preorder(node.left, result)
        preorder(node.right, result)
```

**Use case:** serialize a tree (pre-order uniquely reconstructs the tree structure when combined with in-order).

### Post-order: Left → Right → Root

```python
def postorder(node, result):
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.val)
```

**Use case:** evaluate expression trees (leaf = operand, internal = operator); delete a tree bottom-up.

### Level-order (BFS): level by level

```python
from collections import deque

def level_order(root) -> list:
    if not root:
        return []
    result = []
    q = deque([root])
    while q:
        level_size = len(q)
        level = []
        for _ in range(level_size):
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        result.append(level)
    return result
```

**Use case:** shortest path from root (each level is one step deeper), serialization, finding the width of a tree.

## Binary Search Tree (BST)

A BST enforces the **BST invariant** on every node `n`:
- Every value in `n`'s **left** subtree is **strictly less than** `n.val`.
- Every value in `n`'s **right** subtree is **strictly greater than** `n.val`.

This invariant means **in-order traversal of any valid BST produces a sorted sequence** — the BST is essentially a sorted dictionary with O(h) operations.

### Search — O(h)

```python
def search(node: TreeNode, target: int) -> TreeNode:
    if node is None or node.val == target:
        return node
    if target < node.val:
        return search(node.left, target)
    return search(node.right, target)
```

Each comparison eliminates half the remaining tree (if balanced). The path from root to the answer has at most h edges.

### Insertion — O(h)

```python
def insert(node: TreeNode, val: int) -> TreeNode:
    if node is None:
        return TreeNode(val)
    if val < node.val:
        node.left = insert(node.left, val)
    elif val > node.val:
        node.right = insert(node.right, val)
    # equal values: ignore duplicates (common convention)
    return node
```

### Deletion — O(h) — Three Cases

Case 1: target is a leaf — just remove it.
Case 2: target has one child — replace with that child.
Case 3: target has two children — replace value with **in-order successor** (leftmost node of the right subtree), then delete the successor.

```python
def find_min(node: TreeNode) -> TreeNode:
    while node.left:
        node = node.left
    return node

def delete(node: TreeNode, val: int) -> TreeNode:
    if node is None:
        return None
    if val < node.val:
        node.left = delete(node.left, val)
    elif val > node.val:
        node.right = delete(node.right, val)
    else:
        # Found the node to delete
        if node.left is None:           # Case 1 or 2: no left child
            return node.right
        if node.right is None:          # Case 2: no right child
            return node.left
        # Case 3: two children
        successor = find_min(node.right)
        node.val = successor.val
        node.right = delete(node.right, successor.val)
    return node
```

## BST Complexity

| Operation | Average (balanced, h≈log n) | Worst (skewed, h=n) |
|-----------|-----------------------------|---------------------|
| Search    | O(log n)                    | O(n)                |
| Insert    | O(log n)                    | O(n)                |
| Delete    | O(log n)                    | O(n)                |
| Min/Max   | O(log n)                    | O(n)                |
| In-order  | O(n)                        | O(n)                |

**When does a BST become skewed?** Inserting already-sorted values: `insert(1); insert(2); insert(3); ...` produces a right-leaning chain of height n — identical in structure to a linked list. Every operation degrades to O(n).

## Height and Balance

The height of a binary tree determines the cost of all BST operations. For a tree with n nodes:
- Perfect/complete tree: h = ⌊log₂ n⌋ ≈ O(log n).
- Skewed (worst case): h = n − 1 ≈ O(n).

The **balance factor** of a node = (height of right subtree) − (height of left subtree). A node is **balanced** if its balance factor is in {−1, 0, 1}.

## AVL Trees — Balanced BST Introduction

An **AVL tree** (Adelson-Velsky & Landis, 1962) is a self-balancing BST that maintains the invariant: every node's balance factor is in {−1, 0, 1}. After any insert or delete, if a violation is detected, the tree restores balance with **rotations**.

### The Four Rotation Cases

**Right Rotation (LL Case):** Triggered when a node's left subtree is too tall and the imbalance is in the left-left direction.

```
     z                   y
    / \                 / \
   y   T4    →         x   z
  / \                 /\   /\
 x   T3              T1 T2 T3 T4
/ \
T1 T2
```

```python
def rotate_right(z):
    y = z.left
    T3 = y.right
    y.right = z
    z.left = T3
    # Update heights
    z.height = 1 + max(height(z.left), height(z.right))
    y.height = 1 + max(height(y.left), height(y.right))
    return y   # new subtree root
```

**Left Rotation (RR Case):** Mirror image of right rotation.

**Left-Right Rotation (LR Case):** Left-rotate the left child, then right-rotate the node.

**Right-Left Rotation (RL Case):** Right-rotate the right child, then left-rotate the node.

### AVL Guarantees

An AVL tree with n nodes always has height h ≤ 1.44 × log₂(n+2). This guarantees:

| Operation | AVL Tree | Unbalanced BST |
|-----------|----------|----------------|
| Search    | O(log n) | O(n) worst     |
| Insert    | O(log n) | O(n) worst     |
| Delete    | O(log n) | O(n) worst     |

The constant overhead of maintaining heights and performing rotations is worth it when the input key sequence is adversarial (e.g., sorted data).

### Red-Black Trees — the Alternative

A **Red-Black tree** uses one-bit colour flags (red/black) and a relaxed balancing condition. Its height ≤ 2 × log₂(n+1). It permits at most **one rotation per insert** (vs. O(log n) rotations for AVL). Red-Black trees are therefore preferred for write-heavy workloads and are the basis for:
- Java `TreeMap` / `TreeSet`
- C++ `std::map` / `std::set`
- Linux Kernel process scheduling (CFS)

### Python's Sorted Structures

Python's standard library does not include a balanced BST, but `sortedcontainers.SortedList` provides O(log n) operations. For interview/competitive purposes, you can implement a balanced BST or use the `heapq` module when you only need the minimum/maximum.

## Worked Example: Building and Traversing a BST

```python
# Insert [5, 3, 7, 1, 4, 6, 8] into a BST and print sorted output

class TreeNode:
    def __init__(self, val):
        self.val = val; self.left = self.right = None

def insert(root, val):
    if root is None: return TreeNode(val)
    if val < root.val: root.left = insert(root.left, val)
    elif val > root.val: root.right = insert(root.right, val)
    return root

def inorder(node, out):
    if node:
        inorder(node.left, out)
        out.append(node.val)
        inorder(node.right, out)

root = None
for v in [5, 3, 7, 1, 4, 6, 8]:
    root = insert(root, v)

result = []
inorder(root, result)
print(result)  # [1, 3, 4, 5, 6, 7, 8]
```

The resulting BST:
```
       5
      / \
     3   7
    / \ / \
   1  4 6  8
```
Height = 2. Every path from root to leaf has length 2 — this is perfectly balanced.
