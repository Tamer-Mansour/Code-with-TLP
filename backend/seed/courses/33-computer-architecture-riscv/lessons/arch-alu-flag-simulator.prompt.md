# Exercise Prompt: Simulate ALU Add and Set Flags

## Problem Statement

Implement an 8-bit ALU adder simulator. For each pair of 8-bit two's complement integers, compute the addition result and determine the four status flags that a hardware ALU would produce.

## Input Format

- The first line contains a single integer **T** (1 ≤ T ≤ 100): the number of test cases.
- Each of the next **T** lines contains two integers **A** and **B**, separated by a space.
- A and B are signed integers in the range **-128 to 127** (they represent 8-bit two's complement values).

## Output Format

For each test case, output one line in exactly the following format:

```
RESULT=<r> Z=<z> C=<c> N=<n> V=<v>
```

Where:
- `<r>` is the 8-bit result interpreted as an **unsigned** integer (0 to 255).
- `<z>` is 1 if the result equals 0, else 0.
- `<c>` is 1 if the unsigned sum of the 8-bit representations exceeds 255 (carry-out), else 0.
- `<n>` is bit 7 (the MSB) of the result (1 if result ≥ 128 unsigned, i.e., negative in signed).
- `<v>` is 1 if a signed overflow occurred (both inputs have the same sign but the result has a different sign), else 0.

## Constraints

- 1 ≤ T ≤ 100
- -128 ≤ A, B ≤ 127
- No third-party libraries; standard input/output only.
- Time limit: 3000 ms | Memory limit: 256 MB

## Flag Rules (Precise)

1. Treat A and B as 8-bit unsigned values: `a8 = A & 0xFF`, `b8 = B & 0xFF`.
2. `result_full = a8 + b8`
3. `result = result_full & 0xFF`
4. **Z** = 1 if `result == 0`, else 0.
5. **C** = `(result_full >> 8) & 1` (carry-out of bit 7).
6. **N** = `(result >> 7) & 1` (MSB of result).
7. **V**: let `a_sign = (a8 >> 7) & 1`, `b_sign = (b8 >> 7) & 1`, `r_sign = N`. Then **V** = 1 if `a_sign == b_sign` and `r_sign != a_sign`, else 0.

## Sample Input

```
5
5 3
100 50
-1 1
127 1
-128 -1
```

## Sample Output

```
RESULT=8 Z=0 C=0 N=0 V=0
RESULT=150 Z=0 C=0 N=1 V=1
RESULT=0 Z=1 C=1 N=0 V=0
RESULT=128 Z=0 C=0 N=1 V=1
RESULT=127 Z=0 C=1 N=0 V=1
```

## Explanation of Sample Cases

| Case | A | B | a8 | b8 | sum | result | Z | C | N | V | Notes |
|------|---|---|----|----|-----|--------|---|---|---|---|-------|
| 1 | 5 | 3 | 5 | 3 | 8 | 8 | 0 | 0 | 0 | 0 | Normal add |
| 2 | 100 | 50 | 100 | 50 | 150 | 150 | 0 | 0 | 1 | 1 | Both positive, result looks negative (signed overflow) |
| 3 | -1 | 1 | 255 | 1 | 256 | 0 | 1 | 1 | 0 | 0 | -1+1=0, carry set |
| 4 | 127 | 1 | 127 | 1 | 128 | 128 | 0 | 0 | 1 | 1 | MAX_INT+1 signed overflow |
| 5 | -128 | -1 | 128 | 255 | 383 | 127 | 0 | 1 | 0 | 1 | MIN_INT-1 signed underflow |
