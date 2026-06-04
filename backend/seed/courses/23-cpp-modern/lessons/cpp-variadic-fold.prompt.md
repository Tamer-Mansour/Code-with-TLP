# Variadic Template Argument Pack Expander

Simulate fold expressions and pack operations on integer sequences.

## Operations

- `LEFT_FOLD op v1 v2 ... vN` — left fold: `(((v1 op v2) op v3) ...)`
- `RIGHT_FOLD op v1 v2 ... vN` — right fold: `(v1 op (v2 op (...vN)))`
- `SIZEOF_PACK v1 v2 ... vN` — print the count of values

**Operators:** `+`, `-`, `*`, `MAX` (returns the larger of two integers)

## Input Format

- Line 1: integer `N` (number of operations)
- Lines 2..N+1: one operation per line (values are space-separated integers after the operator)

## Output Format

One result per line.

## Example

**Input:**
```
6
LEFT_FOLD + 1 2 3 4
RIGHT_FOLD - 10 3 2 1
LEFT_FOLD * 2 3 4
LEFT_FOLD MAX 5 2 9 1 7
SIZEOF_PACK 10 20 30 40 50
RIGHT_FOLD + 1 2 3 4 5
```

**Output:**
```
10
8
24
9
5
15
```

**Explanation of RIGHT_FOLD - 10 3 2 1:**
`10 - (3 - (2 - 1)) = 10 - (3 - 1) = 10 - 2 = 8`

## Constraints

- `1 <= N <= 50`
- Each pack has at least 2 values
- All values are integers in the range `-1000` to `1000`
- Results fit in a 64-bit integer
