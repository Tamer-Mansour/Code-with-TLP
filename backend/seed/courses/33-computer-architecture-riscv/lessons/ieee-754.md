# IEEE 754 Floating-Point Format

IEEE 754 is the standard that defines how floating-point numbers are stored in bits. Every language and CPU you will encounter — from Python's `float` to RISC-V's FPU — follows this standard. Understanding the layout explains why `0.1 + 0.2 ≠ 0.3` and how to diagnose precision loss in production systems.

## The Three Fields

A floating-point number has three fields: **sign**, **exponent**, and **fraction** (also called the significand or mantissa).

```
value = (−1)^sign  ×  1.fraction  ×  2^(exponent − bias)
```

The `1.` in front of the fraction is implicit — it is not stored (the **hidden bit** trick), giving one free bit of precision.

### Single Precision (float, 32 bits)

```
 31  30       23  22                    0
 ┌─┬──────────┬──────────────────────────┐
 │S│ Exponent │       Fraction           │
 │1│   8 bits │         23 bits          │
 └─┴──────────┴──────────────────────────┘
Bias = 127
```

### Double Precision (double, 64 bits)

```
 63  62           52  51                 0
 ┌─┬──────────────┬───────────────────────┐
 │S│   Exponent   │       Fraction        │
 │1│    11 bits   │        52 bits        │
 └─┴──────────────┴───────────────────────┘
Bias = 1023
```

## Worked Example: Encoding 6.75

1. Convert to binary: 6 = `110`, 0.75 = `0.11` → `110.11`
2. Normalize: `1.1011 × 2²`
3. Exponent stored = 2 + 127 = 129 = `10000001`
4. Fraction = `1011 0000 0000 0000 0000 000` (23 bits, pad with zeros)

```
Sign: 0
Exponent: 10000001
Fraction: 10110000000000000000000

Hex: 0x40D80000
```

## Special Values

The standard reserves certain exponent patterns for special cases:

| Exponent bits | Fraction bits | Meaning              |
|---------------|---------------|----------------------|
| All 0s        | All 0s        | ±Zero                |
| All 0s        | Non-zero      | Subnormal number     |
| All 1s        | All 0s        | ±Infinity            |
| All 1s        | Non-zero      | NaN (Not a Number)   |

```python
import math, struct

print(math.isinf(1.0 / 0.0))   # True — but raises ZeroDivisionError in Python
print(math.isnan(float('nan'))) # True
print(float('inf') > 1e308)     # True
```

## Subnormal Numbers

When the exponent is all zeros, the hidden bit is 0 instead of 1. This allows gradual underflow — very small numbers near zero are represented with reduced precision rather than snapping directly to zero. The formula becomes:

```
value = (−1)^sign × 0.fraction × 2^(1 − bias)
```

Subnormal arithmetic is correct but often much slower on hardware.

## Precision and Rounding

Single precision has ~7 significant decimal digits; double has ~15-16. Values that cannot be represented exactly are rounded to the nearest representable number:

```python
>>> 0.1 + 0.2
0.30000000000000004   # rounding error accumulates

>>> f"{0.1:.20f}"
'0.10000000000000000555'  # 0.1 is not exact in binary
```

**Rule of thumb:** never compare floats with `==`. Use a tolerance:

```c
bool approx_equal(double a, double b, double eps) {
    return fabs(a - b) < eps;
}
```

## Common Pitfalls

- **Catastrophic cancellation** — subtracting two nearly-equal floats loses significant digits. Example: `(1.0000001 - 1.0)` in single precision gives 0 instead of ~1e-7.
- **Associativity does not hold** — `(a + b) + c ≠ a + (b + c)` in general. This matters for parallel reduction in ML.
- **Integer range** — single precision can represent all integers exactly only up to 2²⁴ = 16,777,216. Beyond that, some integers are not representable.

## RISC-V FPU

RISC-V defines the **F extension** (single-precision) and **D extension** (double-precision), each with 32 dedicated floating-point registers (f0–f31). Instructions like `FADD.S`, `FMUL.D`, and `FCVT.S.W` follow the IEEE 754 standard with configurable rounding modes stored in the `fcsr` control register.

```asm
fadd.s  fa0, fa1, fa2   # fa0 = fa1 + fa2  (single-precision)
fmul.d  fa0, fa1, fa2   # fa0 = fa1 * fa2  (double-precision)
```

> **Interview answer:** IEEE 754 stores a float as sign (1 bit), biased exponent, and a fractional mantissa with an implicit leading 1. Single precision has 8-bit exponent (bias 127) and 23-bit fraction giving ~7 decimal digits of precision; double has 11-bit exponent (bias 1023) and 52-bit fraction giving ~15 digits. Special exponent patterns encode ±0, ±∞, NaN, and subnormals.
