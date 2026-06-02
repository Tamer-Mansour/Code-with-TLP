# Prompt: cpp-alloc-tracker-simulation

## Problem Statement

You are implementing the core bookkeeping logic of a memory leak detector. Your program receives a sequence of memory events and must identify bugs and leaks.

## Input Format

- First line: a single integer `N` — the number of events (1 <= N <= 1000).
- Next `N` lines: each line is one of:
  - `ALLOC <id> <size>` — allocate a block. `id` is a positive integer (1 <= id <= 10^6), `size` is a positive integer representing bytes (1 <= size <= 10^9).
  - `FREE <id>` — free the block with the given `id`.

Constraints:
- `id` values are unique per allocation (the same `id` will not be re-allocated while it is live).
- A `FREE` on an `id` that has never been allocated, or that has already been freed, is an error.
- Multiple `ALLOC`s with the same `id` will not occur while the same `id` is still live (but an `id` may be reused after it has been freed).

## Output Format

For each event, if the event is an error, print immediately:
```
ERROR: double-free or invalid-free of id <id>
```

After all events are processed:
- For each leaked block (allocated but never freed), print one line per block in **ascending order of id**:
```
LEAK: id <id> size <size>
```
- Then print a summary line:
```
Summary: <leak_count> leak(s), <error_count> error(s)
```

If there are no leaks, print no LEAK lines. If there are no errors, the error count is 0.

## Sample Input 1

```
5
ALLOC 1 64
ALLOC 2 128
FREE 1
FREE 3
FREE 2
```

## Sample Output 1

```
ERROR: double-free or invalid-free of id 3
Summary: 0 leak(s), 1 error(s)
```

## Sample Input 2

```
4
ALLOC 10 256
ALLOC 20 512
FREE 10
ALLOC 30 1024
```

## Sample Output 2

```
LEAK: id 20 size 512
LEAK: id 30 size 1024
Summary: 2 leak(s), 0 error(s)
```

## Sample Input 3

```
6
ALLOC 5 100
FREE 5
FREE 5
ALLOC 3 200
ALLOC 7 300
FREE 7
```

## Sample Output 3

```
ERROR: double-free or invalid-free of id 5
LEAK: id 3 size 200
Summary: 1 leak(s), 1 error(s)
```

## Notes

- Output error lines **as they occur** (in the order the bad FREE events appear).
- Output LEAK lines **after all events** are processed, sorted by id ascending.
- The summary line is always the last line of output.
