# Exercise Prompt: Count Set Bits (Population Count)

## Problem Statement

Given T 32-bit unsigned integers, output the number of 1-bits in each integer (the population count / Hamming weight).

## Input Format

```
T
n1
n2
...
```

- Line 1: integer T (1 ≤ T ≤ 10000)
- Next T lines: one non-negative integer per line (0 ≤ n ≤ 4294967295)

## Output Format

T lines, each containing a single integer in [0, 32] — the number of set bits.

## Constraints

- 1 ≤ T ≤ 10000
- 0 ≤ n ≤ 4294967295 (fits in a 32-bit unsigned integer)

## Sample Input

```
5
0
1
255
4294967295
305419896
```

## Sample Output

```
0
1
8
32
13
```

## Explanation

- 0 = 0b0...0 → 0 set bits
- 1 = 0b1 → 1 set bit
- 255 = 0xFF = 0b11111111 → 8 set bits
- 4294967295 = 0xFFFFFFFF → all 32 bits set
- 305419896 = 0x12345678 → binary 0001 0010 0011 0100 0101 0110 0111 1000 → 13 set bits

## Hints

- Brian Kernighan's trick: `n &= (n - 1)` clears the lowest set bit each iteration.
- Python's built-in `bin(n).count('1')` also works correctly.

## Time and Memory Limits

- Time limit: 3000 ms
- Memory limit: 256 MB
