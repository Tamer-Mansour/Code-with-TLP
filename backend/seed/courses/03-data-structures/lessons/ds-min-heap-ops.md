# Exercise: Min-Heap Operations (Manual Implementation)

Practice building a min-heap from scratch — without using Python's `heapq` module. You will implement the sift-up and sift-down operations that underpin every heap.

## What You'll Practice

- Storing a complete binary tree in a flat array
- Sift-up after insertion (restoring the heap property upward)
- Sift-down after extraction (restoring the heap property downward)
- Simulating a sequence of INSERT and EXTRACT_MIN operations

## Instructions

Read operations from standard input line by line until EOF:

- `INSERT x` — insert integer `x` into the min-heap
- `EXTRACT_MIN` — remove and print the smallest element; print `EMPTY` if the heap is empty

**Constraint:** you must implement the heap manually using a Python list. Do not import or use `heapq`.

## Key Concepts

### Array Representation

For a node at index `i` (0-indexed):
- Left child: `2*i + 1`
- Right child: `2*i + 2`
- Parent: `(i - 1) // 2`

### Sift-Up (after INSERT)

1. Append the new value at the end of the array.
2. While the new value is less than its parent, swap them and move up.

### Sift-Down (after EXTRACT_MIN)

1. Save the root (minimum).
2. Move the last element to index 0 and remove the last slot.
3. While the current node is greater than its smallest child, swap with the smallest child and move down.

## Example

```
Input:
INSERT 5
INSERT 3
INSERT 8
EXTRACT_MIN
INSERT 1
EXTRACT_MIN
EXTRACT_MIN

Output:
3
1
5
```

After inserting 5, 3, 8 the heap array is `[3, 5, 8]` (3 sifted to root). EXTRACT_MIN removes 3. After INSERT 1, the heap becomes `[1, 5, 8]`. EXTRACT_MIN removes 1. EXTRACT_MIN removes 5.
