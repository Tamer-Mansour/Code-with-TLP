# Common Bit Tricks in Hardware Modeling

Experienced hardware engineers have a toolkit of idioms that replace branchy, slow general code with a handful of bitwise operations. Knowing these tricks makes your SystemC register models faster, more readable, and closer to what hardware actually does.

## 1. Test Whether a Value Is a Power of Two

A power of 2 has exactly one bit set. Subtracting 1 flips all the low bits:

```cpp
bool is_power_of_two(uint32_t n) {
    return n != 0 && (n & (n - 1)) == 0;
}
// 8 = 0b1000, 7 = 0b0111, 8 & 7 = 0 → true
// 6 = 0b0110, 5 = 0b0101, 6 & 5 = 4 → false
```

Used to validate alignment arguments at runtime without division.

## 2. Isolate the Lowest Set Bit

```cpp
uint32_t lowest = n & (-n);    // or equivalently n & (~n + 1)
// n = 0b1010'1100 → lowest = 0b0000'0100
```

This returns a value with only the lowest 1-bit set and all others cleared. Useful in interrupt-priority arbitration: the hardware finds the lowest-numbered pending interrupt by isolating the LSB of the pending mask.

## 3. Clear the Lowest Set Bit (Kernighan's Trick)

```cpp
n &= n - 1;   // e.g. 0b1010'1100 → 0b1010'1000
```

Each application removes exactly one set bit. Iterating until `n == 0` counts set bits (popcount) in O(popcount) time.

## 4. Byte Reversal (Endian Swap)

When a peripheral delivers a 32-bit word in big-endian order on a little-endian host:

```cpp
uint32_t bswap32(uint32_t x) {
    return ((x & 0xFF000000u) >> 24)
         | ((x & 0x00FF0000u) >>  8)
         | ((x & 0x0000FF00u) <<  8)
         | ((x & 0x000000FFu) << 24);
}
```

GCC provides `__builtin_bswap32(x)` which compiles to a single `BSWAP` instruction on x86 or `REV` on ARM.

## 5. Sign-Extend an Arbitrary-Width Field

After extracting an N-bit signed field from a register, sign-extend it to 32 bits:

```cpp
int32_t sign_extend(uint32_t value, int bits) {
    int shift = 32 - bits;
    return (int32_t)(value << shift) >> shift;
}
// sign_extend(0xFFE, 12) → -2
```

The double-shift trick works because C++ arithmetic right shift replicates the sign bit (on all major compilers, even though the standard calls it implementation-defined).

## 6. Swap Two Variables Without a Temporary

```cpp
a ^= b;
b ^= a;
a ^= b;
```

Classic, but avoid it in real code — it fails if `a` and `b` alias the same memory location. It also prevents compilers from optimising to a register swap. Know it for interview questions only.

## 7. Round Integer Division Up

```cpp
uint32_t div_round_up(uint32_t n, uint32_t d) {
    return (n + d - 1) / d;
}
```

When `d` is a power of 2, replace with the shift/mask form: `(n + d - 1) >> log2(d)`.

## 8. Saturating Increment / Decrement

Incrementing without overflow past a maximum:

```cpp
uint8_t sat_inc(uint8_t v) {
    return v + (v != 0xFF);   // add 1 only if not already at max
}
```

Some DSP hardware operations require saturation; modelling this correctly is essential in SystemC TLM peripherals such as audio codecs.

## 9. Conditional Negate Without Branching

```cpp
int32_t cond_negate(int32_t v, bool negate) {
    int32_t mask = -(int32_t)negate;  // 0 or 0xFFFFFFFF
    return (v ^ mask) - mask;
}
```

When `negate` is false, `mask = 0` and the expression returns `v`. When true, `mask = -1 = 0xFFFFFFFF`, and `(v ^ ~0) - (-1)` = `(~v) + 1` = `-v`.

## 10. Generating a Contiguous Bit Mask

```cpp
uint32_t make_mask(int width) {
    return (width == 32) ? 0xFFFFFFFFu : (1u << width) - 1u;
}
// make_mask(4) → 0xF, make_mask(8) → 0xFF
```

The special case for width = 32 is required because `1u << 32` is undefined behaviour in C/C++.

## Summary Table

| Trick | Expression | Use case |
|-------|-----------|----------|
| Power-of-2 test | `n && !(n & (n-1))` | Validate alignment |
| Lowest set bit | `n & (-n)` | Priority arbitration |
| Clear lowest bit | `n & (n-1)` | Popcount loop |
| Byte swap | shift/OR pattern | Endian conversion |
| Align mask | `(1u << w) - 1` | Field extraction |

**Interview answer:** "I know a suite of O(1) bit tricks — power-of-2 test `n & (n-1) == 0`, lowest-bit isolation `n & (-n)`, and the mask formula `(1 << w) - 1`. I choose the right one based on whether I'm testing, isolating, or clearing bits."
