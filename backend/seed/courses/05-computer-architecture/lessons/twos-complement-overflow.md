# Two's Complement Overflow Detection

Detecting integer overflow is one of the most practically important skills in low-level programming. Silent arithmetic overflow has caused spacecraft failures, security vulnerabilities, and subtle financial bugs. This lesson explains exactly when overflow occurs in two's complement arithmetic and how to detect it efficiently.

## Why Overflow Happens

An N-bit two's complement integer can represent values in the range `[-(2^(N-1)), 2^(N-1) - 1]`. For 8-bit numbers: -128 to +127. Any mathematical result that falls outside this window cannot be represented — the stored bit pattern wraps around and produces an incorrect value.

```
8-bit two's complement range: -128 to +127

  127 + 1  = 128  → cannot represent → wraps to -128  (OVERFLOW)
 -128 + (-1) = -129 → cannot represent → wraps to +127  (OVERFLOW)
  100 + 27 = 127  → representable                       (OK)
  100 + 28 = 128  → cannot represent                   (OVERFLOW)
```

## The Mathematical Test

Given N-bit values A and B, compute the true mathematical result `R = A + B`. If R falls outside `[-(2^(N-1)), 2^(N-1) - 1]`, overflow occurred.

```python
def has_overflow(A, B, N):
    min_val = -(2 ** (N - 1))
    max_val = 2 ** (N - 1) - 1
    R = A + B
    return R < min_val or R > max_val
```

## The Hardware Test (No Arbitrary Precision Needed)

In real hardware, you cannot compute the "true" result — the CPU only has N-bit registers. The hardware detects overflow by examining carry bits:

**Overflow occurs if and only if the carry INTO the sign bit differs from the carry OUT OF the sign bit.**

```
For 4-bit addition:
  A =  0111 (+7)
  B =  0001 (+1)
  R =  1000 (-8)  ← overflow! positive + positive = negative

  Carry into bit 3:  1   (from bit 2 sum)
  Carry out of bit 3: 0  (no carry out)
  Cin ≠ Cout → OVERFLOW

  A =  1001 (-7)
  B =  1110 (-2)
  R =  0111 (+7) + carry 1  ← overflow! negative + negative = positive

  Carry into bit 3:  1
  Carry out of bit 3: 1
  Cin = Cout → NO overflow (the carry-out is discarded for signed arithmetic)
```

## Sign-Based Shortcut

There is a simpler rule derived from the sign bits:

- **Positive overflow**: A > 0, B > 0, and R < 0 (positive + positive = negative)
- **Negative overflow**: A < 0, B < 0, and R > 0 (negative + negative = positive)
- **No overflow possible**: A and B have opposite signs (their sum is always representable)

```python
def has_overflow_sign(A, B, R):
    """R = A + B in full precision."""
    pos_overflow = (A > 0) and (B > 0) and (R < 0)
    neg_overflow = (A < 0) and (B < 0) and (R > 0)
    return pos_overflow or neg_overflow
```

## Worked Examples

```
N = 8 (range: -128 to +127)

  A = 100, B = 50:  100 + 50 = 150 > 127   → OVERFLOW
  A = -100, B = -50: -100 + (-50) = -150 < -128 → OVERFLOW
  A = 100, B = -50:  100 + (-50) = 50       → OK 50
  A = -64, B = -64:  -64 + (-64) = -128     → OK -128  (edge case: exactly representable)
  A = -64, B = -65:  -64 + (-65) = -129 < -128 → OVERFLOW
```

## Overflow vs. Wrap-Around

In C, **signed integer overflow is undefined behavior** — the compiler may assume it never happens and optimize aggressively. In contrast, **unsigned integer overflow is well-defined** and wraps around modulo 2^N. This distinction matters enormously in security-critical code.

```c
// WRONG: signed overflow is UB in C
int a = INT_MAX;
if (a + 1 > a) { ... }  // compiler may optimize away the check!

// CORRECT: check before the operation
if (a > INT_MAX - 1) { /* overflow */ }
```

## Further Reading

- **Nand2Tetris** (https://www.nand2tetris.org/) — Projects 2 and 3 build an ALU that handles overflow from first principles using only NAND gates.
- **MIT 6.004 Computation Structures** (https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/) — Lecture 3 covers two's complement arithmetic and overflow detection in detail.
