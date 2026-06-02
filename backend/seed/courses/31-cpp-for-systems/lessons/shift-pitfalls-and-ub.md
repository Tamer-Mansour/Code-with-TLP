# Shift Pitfalls: Signedness and Undefined Behavior

Shift operators look simple but carry several traps that routinely produce undefined behavior (UB), security bugs, and subtle portability failures. This lesson catalogs each pitfall with the exact standard rule behind it.

## Pitfall 1: Shifting by a Negative Amount

```cpp
int n = -1;
uint32_t x = 1u << n;   // UB: shift count is negative
```

The C++ standard (and C11) say: if the shift count is negative or greater than or equal to the width of the promoted type, the behavior is **undefined**. Both violations fall in this single rule.

## Pitfall 2: Shifting by More Than the Type Width

```cpp
uint32_t x = 1u << 32;  // UB: 32 >= width of uint32_t (32 bits)
uint64_t y = 1ULL << 64; // UB: 64 >= width of uint64_t
```

A common appearance: building a mask in a loop where the count can reach the width.

```cpp
// Danger: if n == 32, this is UB
uint32_t make_mask(int n) {
    return (1u << n) - 1;   // wrong when n == 32
}

// Safe version:
uint32_t make_mask_safe(int n) {
    if (n >= 32) return 0xFFFFFFFFu;
    return (1u << n) - 1;
}
```

## Pitfall 3: Left-Shifting Into or Past the Sign Bit (Signed Types)

For **signed** types, left-shifting a 1-bit into the sign bit is UB in C++14 and earlier:

```cpp
int x = 1 << 31;   // UB on 32-bit int: shifts into sign bit
```

C++20 tightened the rules: left shifts on signed integers now have defined behavior (two's complement is mandated), but only if the mathematical result fits in the type. Shifting into the sign bit remains UB before C++20.

**Fix:** use unsigned types for bitmask arithmetic.

```cpp
uint32_t x = 1u << 31;   // OK: unsigned, result is 2147483648
```

## Pitfall 4: Right-Shifting Signed Negative Values

For signed types, right shift is implementation-defined (not UB, but non-portable):

```cpp
int x = -8;
int y = x >> 1;   // implementation-defined: -4 (arithmetic) or some other value
```

In practice every mainstream compiler performs an **arithmetic right shift** (sign-extend), which gives `-4`. But this is not guaranteed by the standard before C++20. For portable code, avoid right-shifting negative signed integers.

```cpp
// Portable signed right-shift (arithmetic):
int arithmetic_shift_right(int x, int n) {
    // Relies on implementation-defined behavior; document the assumption
    return x >> n;
}

// Guaranteed portable: cast to unsigned, shift, cast back (only for two's complement systems)
int safe_shr(int x, int n) {
    return static_cast<int>(static_cast<unsigned>(x) >> n);
}
```

## Pitfall 5: Integer Promotion on Small Types

When you apply a shift to a `char` or `short`, it is promoted to `int` first:

```cpp
uint8_t x = 0xFF;
uint8_t y = x << 1;   // x promoted to int first; result is 510, then truncated to uint8_t
// y = 0xFE, not necessarily what you intended
```

Be explicit about widths when shifting small types:

```cpp
uint16_t x = 0x00FFu;
uint16_t y = static_cast<uint16_t>(x << 4);  // shift then truncate intentionally
```

## Pitfall 6: Using `1` Instead of `1u` or `1ULL`

```cpp
uint64_t mask = 1 << 40;    // Bug: 1 is int (32 bits); shift by 40 is UB
uint64_t mask = 1ULL << 40; // Correct
```

The literal `1` is of type `int`. Shifting it beyond 31 is UB regardless of what the result is assigned to. Always suffix the literal with `u` or `ULL` to match the intended width.

## Summary: Safe Shift Checklist

| Rule | Check |
|------|-------|
| Shift count non-negative | `assert(n >= 0)` |
| Shift count < type width | `assert(n < 32)` for `uint32_t` |
| Use unsigned for masks | `1u << n`, not `1 << n` |
| Match literal suffix to register width | `1ULL << n` for 64-bit |
| Right-shift signed negatives carefully | Cast to unsigned or document assumption |

## Quick Compiler Flags

Enable warnings that catch many of these issues:

```bash
g++ -Wall -Wextra -Wshift-count-overflow -Wshift-count-negative -Wsign-conversion
```

Sanitizers catch the rest at runtime:

```bash
g++ -fsanitize=undefined ./program
```

> **Interview answer:** "Two categories: undefined behavior from a negative or oversized shift count, and UB from left-shifting into the sign bit of a signed type (pre-C++20). The fix is always to use unsigned types for bitmask work and to ensure the shift count is in `[0, width-1]`. Always suffix bitmask literals with `u` or `ULL` to match the register width."
