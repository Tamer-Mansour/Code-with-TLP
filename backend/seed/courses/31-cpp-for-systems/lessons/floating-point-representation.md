# Floating Point: IEEE 754 and Precision Surprises

Floating-point arithmetic looks like real-number math but isn't. IEEE 754, the standard behind every `float` and `double` in C++, is a fixed-precision binary format. Understanding its layout prevents subtle bugs in numeric code, signal processing, and financial calculations.

## IEEE 754 Layout

A 32-bit `float` splits its 32 bits as follows:

```
 31  30      23  22                    0
 [S] [EEEEEEEE] [MMMMMMMMMMMMMMMMMMMMMMM]
  1 bit sign   8 bit exponent   23 bit mantissa (significand)
```

Value = (-1)^S * 1.M * 2^(E - 127)   (for normal numbers)

A 64-bit `double` uses 1 sign bit, 11 exponent bits, and 52 mantissa bits, giving about 15-17 significant decimal digits.

| Type | Total bits | Mantissa bits | Decimal digits | Exponent range |
|------|-----------|--------------|----------------|----------------|
| `float` | 32 | 23 (+1 implicit) | ~7 | ±3.4×10^38 |
| `double` | 64 | 52 (+1 implicit) | ~15-17 | ±1.8×10^308 |
| `long double` | 80/128 | 63/112 | ~18-34 | platform-dependent |

## The Classic 0.1 + 0.2 Problem

```cpp
#include <cstdio>

int main() {
    double a = 0.1, b = 0.2;
    double c = a + b;

    printf("%.20f\n", c);          // 0.30000000000000004441
    printf("%s\n", c == 0.3 ? "equal" : "not equal"); // "not equal"

    // Correct comparison: use an epsilon
    double eps = 1e-9;
    if (c - 0.3 < eps && 0.3 - c < eps) {
        puts("approximately equal");
    }
}
```

`0.1` is not exactly representable in binary floating-point. The nearest representable value is `0.1000000000000000055511151231257827021181583404541015625`.

## Special Values

IEEE 754 reserves exponent patterns for special cases:

| Value | Bit pattern (sign bit = 0) | Behavior |
|-------|---------------------------|----------|
| `+0` / `-0` | All zeros / only sign=1 | Equal under `==` |
| `+Inf` | exp all 1s, mantissa 0 | Propagates through arithmetic |
| `-Inf` | sign=1, exp all 1s, mantissa 0 | Propagates through arithmetic |
| `NaN` | exp all 1s, mantissa ≠ 0 | **Never equal to anything, including itself** |

```cpp
#include <cmath>
#include <cstdio>

double x = 0.0 / 0.0;   // NaN
double y = 1.0 / 0.0;   // +Inf

printf("%d\n", x == x);  // 0 — NaN != NaN!
printf("%d\n", std::isnan(x));  // 1 — correct way to test
printf("%d\n", std::isinf(y));  // 1
```

The NaN-not-equal-to-itself rule is why you must use `std::isnan()` and never `if (x == NaN)`.

## Inspecting the Bit Pattern

In systems code it is sometimes necessary to read the exact bits of a float:

```cpp
#include <cstdint>
#include <cstring>

float f = 1.0f;
uint32_t bits;
std::memcpy(&bits, &f, sizeof(bits));  // safe type pun
printf("1.0f bits: 0x%08X\n", bits);  // 0x3F800000
// sign=0, exp=127 (bias), mantissa=0 → (-1)^0 * 1.0 * 2^(127-127) = 1.0
```

Never use pointer casts (`*(uint32_t*)&f`) — that is undefined behavior. Use `memcpy` or C++20 `std::bit_cast<uint32_t>(f)`.

## Catastrophic Cancellation

Subtracting two nearly equal numbers destroys significant digits:

```cpp
double a = 1.000000001;
double b = 1.000000000;
double diff = a - b;  // result: ~1e-9 but only ~1 significant digit!
```

This matters in numerical algorithms (e.g., computing derivatives, Gaussian elimination). The fix is to algebraically rearrange the expression to avoid subtraction of close values.

## Floating-Point in Systems Code

- **Do not use `float`/`double` for financial calculations** — use integer cents or a decimal library.
- **Avoid float comparisons with `==`** — use epsilon comparisons or ULP (units in the last place) comparisons.
- **Compiler flags matter**: `-ffast-math` allows the compiler to reorder operations in ways that change results; `-ffp-contract=off` disables fused multiply-add contraction. Know your flags.
- **FPU state is per-thread** — on x86 the MXCSR register controls rounding mode and exception masking; context switches can affect this.

**Interview answer:** "IEEE 754 floating-point represents numbers as sign × 1.mantissa × 2^exponent. Most decimal fractions like 0.1 are not exactly representable, so floating-point equality comparisons almost always need an epsilon. NaN is the one value that is not equal to itself — detect it with std::isnan()."
