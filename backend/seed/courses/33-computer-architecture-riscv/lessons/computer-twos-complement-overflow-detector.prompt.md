# Two's Complement Overflow Detector

## Problem Description

The RISC-V ALU performs 32-bit signed addition with the `ADD` instruction and sets **no overflow flag** (unlike MIPS). However, detecting signed overflow is essential for safe arithmetic.

Given two signed 32-bit integers `A` and `B` (each on a separate input line), compute their sum and print three values:

1. The **32-bit two's complement result** (as a signed decimal).
2. Whether **signed overflow** occurred (`YES` or `NO`). Overflow rule: overflow occurs if and only if A and B have the same sign and the result has a different sign.
3. Whether **unsigned carry-out** occurred (`YES` or `NO`). Carry-out rule: treat A and B as unsigned 32-bit values; carry-out is `YES` if their unsigned sum exceeds 2^32 − 1.

Process multiple pairs until EOF (end of input). Each pair is two consecutive lines.

## Input Format

Pairs of signed 32-bit integers, one integer per line:

```
A1
B1
A2
B2
...
```

- Each value is a signed decimal integer in the range [−2147483648, 2147483647].
- The total number of lines is always even.
- At most 100 pairs.

## Output Format

For each pair, one line in exactly this format:

```
result=<R> signed_overflow=<S> unsigned_carry=<U>
```

Where:
- `<R>` is the 32-bit two's complement sum, printed as a signed decimal (may be negative).
- `<S>` is `YES` if signed overflow occurred, `NO` otherwise.
- `<U>` is `YES` if unsigned carry-out occurred, `NO` otherwise.

## Sample Input

```
2147483647
1
-2147483648
-1
100
200
2000000000
2000000000
```

## Sample Output

```
result=-2147483648 signed_overflow=YES unsigned_carry=NO
result=2147483647 signed_overflow=YES unsigned_carry=YES
result=300 signed_overflow=NO unsigned_carry=NO
result=-294967296 signed_overflow=YES unsigned_carry=NO
```

## Explanation

**Pair 1:** 2147483647 + 1  
Both positive; mathematical result 2147483648 > INT32_MAX. 32-bit wrap: 2147483648 mod 2^32 = 2147483648; as signed = −2147483648. Both inputs positive, result negative → signed_overflow=YES. Unsigned: 2147483647 + 1 = 2147483648 ≤ 4294967295 → carry=NO.

**Pair 2:** −2147483648 + (−1)  
Both negative; mathematical result −2147483649 < INT32_MIN. 32-bit unsigned sum: 2147483648 + 4294967295 = 6442450943; truncated to 32 bits = 2147483647 (signed positive) → signed_overflow=YES. Unsigned sum 6442450943 > 4294967295 → carry=YES.

**Pair 3:** 100 + 200 = 300. Normal result, no overflow, no carry.

**Pair 4:** 2000000000 + 2000000000 = 4000000000. As signed 32-bit: 4000000000 − 4294967296 = −294967296. Both positive, result negative → signed_overflow=YES. Unsigned: 4000000000 ≤ 4294967295 (fits in 32 bits) → carry=NO.

## Constraints

- Each integer is in [−2147483648, 2147483647].
- 1 ≤ number of pairs ≤ 100.
- Use only the Python standard library.
- Time limit: 3000 ms
- Memory limit: 256 MB
