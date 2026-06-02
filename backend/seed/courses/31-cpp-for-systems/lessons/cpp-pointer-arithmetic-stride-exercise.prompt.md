# Exercise Prompt: Compute Pointer Offsets and Array Strides

## Problem Statement

Simulate pointer arithmetic. Given a base memory address and an element size (in bytes), apply a sequence of pointer-addition/subtraction operations and print the resulting address after each step.

When a pointer of element size `S` is advanced by `N` elements, the address changes by `N × S` bytes. This exercise makes that arithmetic concrete.

## Input Format

```
base_address element_size
op_count
op_1
op_2
...
op_count
```

- Line 1: two space-separated integers:
  - `base_address` — starting address (0 ≤ base_address ≤ 10^9)
  - `element_size` — bytes per element; one of {1, 2, 4, 8}
- Line 2: integer `op_count` (1 ≤ op_count ≤ 20)
- Next `op_count` lines: one integer each — the number of elements to add (may be negative)

## Output Format

Print exactly `op_count` lines. Line `i` contains the address after applying the first `i` operations cumulatively.

All output values are guaranteed to be non-negative integers.

## Constraints

- 0 ≤ base_address ≤ 10^9
- element_size ∈ {1, 2, 4, 8}
- 1 ≤ op_count ≤ 20
- -100 ≤ each operation ≤ 100
- All intermediate and final addresses ≥ 0

## Sample Input 1

```
1000 4
3
1
2
-1
```

## Sample Output 1

```
1004
1012
1008
```

**Explanation:** Starting at 1000 with element size 4:
- +1 element → 1000 + 4 = 1004
- +2 elements → 1004 + 8 = 1012
- -1 element → 1012 - 4 = 1008

## Sample Input 2

```
2048 8
4
3
-1
0
2
```

## Sample Output 2

```
2072
2064
2064
2080
```

**Explanation:** Starting at 2048 with element size 8:
- +3 → 2048 + 24 = 2072
- -1 → 2072 - 8 = 2064
- +0 → 2064 + 0 = 2064
- +2 → 2064 + 16 = 2080

## Sample Input 3

```
0 1
5
10
5
-3
100
-50
```

## Sample Output 3

```
10
15
12
112
62
```

**Explanation:** Element size 1 means each step adds exactly N bytes (like `char*`).
