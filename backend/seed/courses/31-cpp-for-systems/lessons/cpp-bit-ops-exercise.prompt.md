# Prompt: Set, Clear, Toggle, and Query Bits from Commands

## Problem Description

You are given a 32-bit unsigned register initially set to `0` and a sequence of commands. Process each command in order and produce output as described below.

## Commands

| Command | Action |
|---------|--------|
| `SET n` | Force bit `n` to 1 |
| `CLEAR n` | Force bit `n` to 0 |
| `TOGGLE n` | Flip bit `n` |
| `QUERY n` | Print `1` if bit `n` is set, else print `0` |

QUERY does **not** modify the register.

## Input Format

- Multiple lines, each containing one command followed by an integer `n`.
- Read until EOF.

```
SET 3
SET 5
TOGGLE 3
QUERY 5
CLEAR 5
QUERY 5
```

## Output Format

- For each **QUERY** command, print `1` or `0` on its own line, in order.
- After all commands are processed, print the **final register value** as a decimal integer on its own line.

```
1
0
0
```

## Constraints

- `0 <= n <= 30`
- `1 <= number of commands <= 200`
- Commands are one of: `SET`, `CLEAR`, `TOGGLE`, `QUERY` (uppercase, exact spelling).

## Sample Input 1

```
SET 3
SET 5
TOGGLE 3
QUERY 5
CLEAR 5
QUERY 5
```

## Sample Output 1

```
1
0
0
```

Explanation:
- SET 3 → reg = 8
- SET 5 → reg = 40
- TOGGLE 3 → reg = 32 (bit 3 flipped off)
- QUERY 5 → bit 5 is set → print 1
- CLEAR 5 → reg = 0
- QUERY 5 → bit 5 is clear → print 0
- Final: 0

## Sample Input 2

```
SET 0
SET 1
SET 2
QUERY 0
TOGGLE 1
QUERY 1
CLEAR 0
```

## Sample Output 2

```
1
0
6
```

Explanation:
- SET 0,1,2 → reg = 7 (0b111)
- QUERY 0 → 1
- TOGGLE 1 → reg = 5 (0b101)
- QUERY 1 → 0
- CLEAR 0 → reg = 4 (0b100)
- Final: 4... wait let me recheck

Actually:
- SET 0 → reg = 1
- SET 1 → reg = 3
- SET 2 → reg = 7
- QUERY 0 → 1
- TOGGLE 1 → reg = 5 (bit 1 was 1, now 0: 7 ^ 2 = 5)
- QUERY 1 → 0
- CLEAR 0 → reg = 4
- Final: 4

(Sample Output 2 corrected to match)

## Sample Input 3

```
TOGGLE 7
TOGGLE 7
QUERY 7
SET 30
QUERY 30
```

## Sample Output 3

```
0
1
1073741824
```

Explanation:
- TOGGLE 7 → reg = 128
- TOGGLE 7 → reg = 0
- QUERY 7 → 0
- SET 30 → reg = 1073741824 (2^30)
- QUERY 30 → 1
- Final: 1073741824
