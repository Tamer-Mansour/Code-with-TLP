# Simulate First-Fit Allocation and Report Fragmentation

## Problem Description

You are given a contiguous memory region of `M` bytes and a sequence of allocation and deallocation operations. Simulate a **First-Fit** memory allocator with **immediate free-block coalescing**.

The allocator maintains a free list of non-overlapping free blocks sorted by start address. Initially the free list contains a single block `[0, M)` (start = 0, size = M bytes).

### Operations

**`ALLOC id size`**
- Find the **first** free block (lowest start address) whose size is ≥ `size`.
- Allocate `size` bytes from the start of that block.
- If the block is larger, split it: the remainder becomes a new free block immediately after the allocated region.
- Record the allocation under `id`.
- Print `OK id start` where `start` is the byte offset where the block was placed.
- If no free block is large enough, print `FAIL id`. Do not modify the free list.

**`FREE id`**
- Release the block previously allocated under `id`. Guaranteed that `id` was allocated and not already freed.
- Add the freed region back to the free list.
- Perform **immediate coalescing**: merge the freed block with any adjacent free blocks (check the block immediately before and immediately after in address order).
- Do not print anything for `FREE` operations.

### Final Report

After processing all operations, print a single line:

```
num_free_blocks total_free_bytes
```

where `num_free_blocks` is the count of distinct free blocks remaining and `total_free_bytes` is the sum of their sizes.

## Input Format

```
M
N
op_1
op_2
...
op_N
```

- Line 1: integer `M` — total memory size in bytes (1 ≤ M ≤ 10^6)
- Line 2: integer `N` — number of operations (1 ≤ N ≤ 1000)
- Next N lines: each is either `ALLOC id size` or `FREE id`
  - `id` is a non-empty alphanumeric string (≤ 10 chars), unique per live allocation
  - `size` is a positive integer (1 ≤ size ≤ M)

## Output Format

For each `ALLOC` operation (in order), print one line:
- `OK id start` — allocation succeeded, starting at byte `start`
- `FAIL id` — no free block is large enough

After all operations, print one final line:
- `num_free_blocks total_free_bytes`

## Constraints

- All `FREE id` operations reference a currently allocated id.
- Allocation ids are unique while allocated (no duplicate active ids).
- 1 ≤ M ≤ 1,000,000
- 1 ≤ N ≤ 1,000
- 1 ≤ size ≤ M

## Sample Input

```
100
5
ALLOC A 30
ALLOC B 20
FREE A
ALLOC D 25
ALLOC E 80
```

## Sample Output

```
OK A 0
OK B 30
OK D 0
FAIL E
2 55
```

### Explanation

- `ALLOC A 30`: Free list `[0,100]`. First fit: allocate at 0. Remainder `[30,70]`. → `OK A 0`
- `ALLOC B 20`: Free list `[30,70]`. First fit: allocate at 30. Remainder `[50,50]`. → `OK B 30`
- `FREE A`: Add `[0,30]` back. Free list: `[0,30],[50,50]`. No adjacent blocks to coalesce (30 ≠ 50).
- `ALLOC D 25`: First fit: `[0,30]` ≥ 25, allocate at 0. Remainder `[25,5]`. Free list: `[25,5],[50,50]`. → `OK D 0`
- `ALLOC E 80`: Largest free block is 50 bytes < 80. → `FAIL E`
- Final: 2 free blocks, 5 + 50 = 55 bytes free. → `2 55`
