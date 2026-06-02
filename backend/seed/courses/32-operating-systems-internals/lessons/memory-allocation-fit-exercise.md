# Exercise: Simulate First-Fit Allocation and Report Fragmentation

In this exercise you will implement a simplified memory allocator that uses the **First-Fit** strategy. Given a sequence of allocation and deallocation operations on a contiguous memory region, your program must track the state of the free list, perform each operation, and report the final fragmentation statistics.

## What You Will Implement

- A free-list manager that starts with one large free block spanning the entire memory.
- **Allocation (`ALLOC id size`):** Find the first free block large enough, allocate `size` bytes from it, record the allocation under the given id, and split the remainder back into the free list. If no block is large enough, print `FAIL id`.
- **Deallocation (`FREE id`):** Return the block to the free list. Perform **immediate coalescing** — if the freed block is adjacent to an existing free block, merge them.
- **Final report:** After all operations, print the number of free blocks and total free bytes.

## Why This Matters

Implementing First-Fit with coalescing teaches:

- How allocators track both used and free memory simultaneously.
- Why coalescing is essential — without it, repeated alloc/free cycles fragment the free list even when plenty of memory is available.
- How to reason about external fragmentation: many small free blocks vs. one large one.

## Getting Started

Read the problem specification carefully — pay attention to the ordering of the free list (address order) and the coalescing rules. Start with a list containing a single free block, then process operations one by one.

The starter code provides the I/O skeleton. You need to fill in the `first_fit_alloc`, `free_block`, and `coalesce` logic.

```python
import sys

def solve():
    data = sys.stdin.read().split('\n')
    # TODO: parse and simulate
    pass

solve()
```

Open the exercise panel to see the full problem statement, constraints, and sample cases.
