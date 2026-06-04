# Two's Complement Overflow Detector

Given two signed integers **A** and **B** (in decimal) and their bit-width **N**, determine whether adding A and B produces a two's complement overflow.

Print `OVERFLOW` if the mathematical result cannot be represented in N-bit two's complement, otherwise print `OK` followed by the result.

## Input Format

```
Line 1: N  (bit width, 4 <= N <= 32)
Line 2: A  (signed integer)
Line 3: B  (signed integer)
```

**Constraints:** A and B are guaranteed to be valid N-bit two's complement values, i.e., `-(2^(N-1)) <= A, B <= 2^(N-1) - 1`.

## Output Format

- If `A + B` overflows N-bit two's complement: print `OVERFLOW`
- Otherwise: print `OK R` where R is the mathematical sum

## Examples

**Example 1**
```
Input:
8
100
50

Output:
OVERFLOW
```
Explanation: 100 + 50 = 150, which exceeds the 8-bit max of 127.

**Example 2**
```
Input:
8
100
27

Output:
OK 127
```
Explanation: 100 + 27 = 127, which is exactly representable (edge case).

**Example 3**
```
Input:
16
-10000
5000

Output:
OK -5000
```

## Hints

- The range of an N-bit two's complement integer is `[-(2^(N-1)), 2^(N-1) - 1]`.
- Compute the sum in full precision (Python integers have arbitrary precision).
- Check whether the sum falls outside the representable range.
