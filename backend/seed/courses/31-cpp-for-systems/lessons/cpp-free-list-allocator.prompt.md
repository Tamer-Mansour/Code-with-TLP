# Memory Allocator: Free List Simulation

## Problem Description

Simulate a simple explicit free-list heap allocator with **first-fit** placement and **immediate coalescing**. This is the algorithm at the heart of `malloc`/`free` implementations like dlmalloc.

## Input Format

- **First line:** integer `H` — total heap size in bytes (1 ≤ H ≤ 10 000).
- **Subsequent lines:** one of:
  - `ALLOC id size` — allocate `size` contiguous bytes and assign handle `id`.
  - `FREE id` — free the block with handle `id`.

## Output Format

- `ALLOC id size` succeeds: print `id: [start, end)` where `start` is the 0-indexed first byte (inclusive) and `end = start + size` (exclusive). Use first-fit: choose the lowest-address free region that is large enough.
- `ALLOC id size` fails (no contiguous free block of sufficient size): print `id: FAILED`.
- `FREE id`: immediately coalesce adjacent free regions, then print `FREE id`.

## Constraints

- `id` is a 1–10 character uppercase alphanumeric string.
- `size` is a positive integer; at most one allocation with size > H will be attempted per test.
- At most 50 commands per test case.
- `FREE` is only called on ids that are currently allocated.
- No two live allocations have the same id.

## Sample Input 1

```
100
ALLOC A 30
ALLOC B 20
ALLOC C 40
FREE B
ALLOC D 15
ALLOC E 25
```

## Sample Output 1

```
A: [0, 30)
B: [30, 50)
C: [50, 90)
FREE B
D: [30, 45)
E: FAILED
```

**Explanation:** After freeing B, there is a 20-byte hole at [30, 50) and 10 bytes free at [90, 100). D (15 bytes) fits in the hole first-fit at [30, 45). E (25 bytes) cannot fit in either remaining fragment (5 bytes at [45, 50) and 10 bytes at [90, 100)).

## Sample Input 2

```
50
ALLOC X 10
ALLOC Y 10
ALLOC Z 10
FREE X
FREE Z
FREE Y
ALLOC BIG 45
```

## Sample Output 2

```
X: [0, 10)
Y: [10, 20)
Z: [20, 30)
FREE X
FREE Z
FREE Y
BIG: [0, 45)
```

**Explanation:** Freeing Y coalesces with the already-freed neighbors X and Z to produce one free region [0, 30). Together with the always-free [30, 50), the full heap is free. BIG (45 bytes) fits at [0, 45).

## Sample Input 3

```
20
ALLOC A 8
ALLOC B 8
FREE A
ALLOC C 10
ALLOC D 5
```

## Sample Output 3

```
A: [0, 8)
B: [8, 16)
FREE A
C: FAILED
D: [0, 5)
```

**Explanation:** After freeing A, the free regions are [0, 8) and [16, 20). C needs 10 bytes; neither fragment is large enough (8 and 4). D needs 5 bytes; the first-fit region [0, 8) fits.
