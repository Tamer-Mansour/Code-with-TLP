# Arrays & Memory Layout

An **array** is the most fundamental data structure in computing: a contiguous block of memory where every element sits at a fixed offset from the base address. Understanding how arrays use memory is the foundation for analysing the performance of almost every algorithm you will ever write.

## How Memory Works

When you declare an array of 4-byte integers, the runtime reserves `n × 4` bytes in a single, unbroken chunk. Element `i` lives at address `base + i × element_size`. The CPU never has to "follow a pointer" to find an element — it calculates the address with a single multiply-and-add instruction.

```
Index:   0    1    2    3    4
         ┌────┬────┬────┬────┬────┐
Memory:  │ 12 │  5 │ 99 │  3 │ 47 │
         └────┴────┴────┴────┴────┘
         base+0  +4   +8  +12  +16
```

Modern CPUs load data in **cache lines** (typically 64 bytes, holding 16 × 4-byte ints). When you access `arr[0]`, the hardware automatically pre-fetches `arr[1]` through `arr[15]` into the L1 cache. Iterating an array in order therefore exploits **spatial locality** — you pay a cache-miss cost once, then get 15 "free" reads. This is why array traversal is dramatically faster in practice than the O(n) asymptotic analysis alone predicts.

## Indexing and Bounds Checking

Random access is **O(1)**: given any index `i`, the CPU computes `base + i * element_size` in a single clock cycle. This is the superpower of arrays compared to linked structures which require O(n) pointer traversal to reach element `i`.

Bounds checking behaviour differs by language:
- **Python** lists wrap negative indices (`a[-1]` is the last element; `a[-2]` is second-to-last). An out-of-range index raises `IndexError`.
- **C/C++** have no built-in bounds checking — out-of-bounds access is undefined behaviour (silent data corruption or segmentation fault).
- **Java** throws `ArrayIndexOutOfBoundsException` at runtime.

A common bug: accessing `arr[n]` (length = n, valid indices 0..n-1). Always use strict `< len(arr)` comparisons in loops.

## Static vs. Dynamic Arrays

A **static array** (C-style `int arr[100]`) has a fixed capacity decided at compile or allocation time. Its memory footprint is exactly `capacity × element_size` bytes — no wasted space, no overhead. But once allocated, it cannot grow.

A **dynamic array** (Python `list`, C++ `std::vector`, Java `ArrayList`) grows automatically when full. When the internal buffer fills up, the runtime:

1. Allocates a new block of size `current_capacity × growth_factor` (commonly 1.5× or 2×).
2. Copies all `n` existing elements to the new block — **O(n)** work.
3. Frees the old block.
4. Continues inserting into the new, larger buffer.

```python
# Demonstrating Python list resizing
import sys

a = []
prev_size = sys.getsizeof(a)
for i in range(20):
    a.append(i)
    cur_size = sys.getsizeof(a)
    if cur_size != prev_size:
        print(f"len={len(a):2d}  allocated bytes: {prev_size} → {cur_size}")
        prev_size = cur_size
# Output shows resizing at sizes 1, 5, 9, 17 (CPython growth: 0,4,8,16,25,35,...)
```

The growth sequence in CPython is: 0, 4, 8, 16, 25, 35, 46, 58, 72, 88, … — each resize roughly 1.125× the previous capacity (smaller arrays grow faster proportionally).

## Amortised Analysis in Depth

Why is `append` O(1) amortised even though resizes cost O(n)?

Use the **accounting argument**: charge each `append` a cost of 3 tokens instead of 1.
- 1 token pays for the append itself.
- 2 tokens go into a "savings account" attached to the new element.

When a resize from capacity `c` to `2c` occurs, you need `c` tokens to copy `c` elements. At that point you have exactly `c` elements in the "savings" (they each deposited 2 tokens, but you already spent 1 on insertion, so... let's be precise):

With a **doubling** strategy: every time you insert into the second half of a full array, you've already paid for your own future move. More formally, if the current array has `n` elements and was last resized at size `n/2`, then `n/2` insertions happened since the last resize, each paying 2 extra tokens = `n` total tokens available — exactly enough to copy `n` elements. Therefore amortised cost per insertion is O(1).

| Operation       | Best   | Average  | Worst  | Amortised |
|-----------------|--------|----------|--------|-----------|
| Access `arr[i]` | O(1)   | O(1)     | O(1)   | O(1)      |
| Append (end)    | O(1)   | O(1)     | O(n)*  | O(1)      |
| Insert (front)  | O(n)   | O(n)     | O(n)   | O(n)      |
| Insert (middle) | O(n)   | O(n)     | O(n)   | O(n)      |
| Delete (end)    | O(1)   | O(1)     | O(1)   | O(1)      |
| Delete (middle) | O(n)   | O(n)     | O(n)   | O(n)      |
| Search (unsorted)| O(1)  | O(n)     | O(n)   | O(n)      |
| Search (sorted) | O(1)   | O(log n) | O(log n)| O(log n) |

*Only on resize; amortised is O(1).

## Python List Internals

Python `list` objects are dynamic arrays of **object pointers**. Each slot holds an 8-byte reference to a Python object heap-allocated elsewhere — not the object data itself. This means:

- `list.append` is O(1) amortised — just store a pointer.
- Accessing `a[i]` requires one pointer dereference to reach the object (slightly more work than a C `int[]`).
- `a[0]` and `a[999]` take the same time — the pointer is at a known offset.

```python
# All these operations are O(1)
a = [10, 20, 30]
x = a[1]          # read: O(1)
a[1] = 99         # write: O(1)
a.append(40)      # amortised O(1)
a.pop()           # O(1)
n = len(a)        # O(1) — length is stored as a field

# These are O(n)
a.insert(0, 5)    # inserts at front — shifts all elements right
a.pop(0)          # removes from front — shifts all elements left
```

## Memory Layout: Contiguous vs. Pointer-Based

Consider storing 1 000 000 integers:

| Storage method             | Bytes used (approx) | Random access |
|----------------------------|---------------------|---------------|
| `array.array('i', ...)`    | ~4 MB               | O(1), 1 deref |
| Python `list` of ints      | ~35 MB              | O(1), 2 derefs|
| Linked list of nodes       | ~56 MB              | O(n)          |

Python's `array` module stores raw C integers without boxing — 4× more memory-efficient than a `list` for numeric data. NumPy arrays (out of scope for this course) go further by providing SIMD vectorization.

## Common Array Bugs

1. **Off-by-one:** Using `i <= len(arr)` instead of `i < len(arr)`.
2. **Mutation during iteration:** Deleting elements while iterating shifts indices.
3. **Shallow copy:** `b = a` makes `b` an alias; `b = a[:]` or `b = a.copy()` make a true copy.
4. **Forgot `% n` in rotation:** Always reduce `k` modulo `n` before rotating.

```python
# Bug: mutation during iteration
a = [1, 2, 3, 4]
for i in range(len(a)):
    if a[i] % 2 == 0:
        a.pop(i)   # IndexError — length changed!

# Fix: iterate over a copy or build a new list
a = [x for x in a if x % 2 != 0]
```

## When to Use Arrays

Use a list (array) when:
- You need **O(1) random access** by index.
- Elements are accessed **sequentially** (excellent cache behaviour).
- The size is roughly known up front and inserts/deletes happen primarily at the end.

Prefer other structures when:
- **Frequent middle insertions/deletions** — consider a doubly-linked list or `collections.deque`.
- **Fast membership testing** with no ordering needs — use a `set` (hash table).
- **Sorted order with frequent updates** — use a sorted container or BST.
- **Fixed-size numeric data** with arithmetic — use `array.array` or NumPy.
