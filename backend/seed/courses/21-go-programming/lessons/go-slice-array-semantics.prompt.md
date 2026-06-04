# Slice vs Array Semantics

## Problem

A key concept in Go is that slices share a backing array until `append` forces a reallocation. Understanding when reallocation occurs is critical for writing correct, efficient Go code.

Simulate slice `append` behavior:

- You start with an empty slice of length 0 and a given capacity `C`.
- You are given `N` integers to append one at a time.
- After each append, determine whether a **reallocation** occurred.

**Reallocation rule:** When `len == cap` before an append, a new backing array is created with `new_cap = 2 * old_cap`. Then the element is appended to the new array.

For each appended value, output one line:
- `REALLOC <value> cap=<new_cap>` if a reallocation happened during this append
- `APPEND <value> cap=<current_cap>` if no reallocation was needed

## Input Format

```
C
N
v1 v2 v3 ... vN
```

- Line 1: starting capacity `C` (1 <= C <= 100)
- Line 2: number of values `N` (1 <= N <= 200)
- Line 3: N space-separated integers to append

## Output Format

N lines, one per append, in order.

## Example

**Input:**
```
4
8
1 2 3 4 5 6 7 8
```

**Output:**
```
APPEND 1 cap=4
APPEND 2 cap=4
APPEND 3 cap=4
APPEND 4 cap=4
REALLOC 5 cap=8
APPEND 6 cap=8
APPEND 7 cap=8
APPEND 8 cap=8
```

## Constraints

- 1 <= C <= 100
- 1 <= N <= 200
- Each value fits in a 32-bit integer
