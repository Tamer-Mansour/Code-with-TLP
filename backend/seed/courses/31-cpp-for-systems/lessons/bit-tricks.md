# Useful Bit Tricks: popcount, lowest set bit, power of two

Beyond the four fundamental patterns (set, clear, toggle, check), a small library of classical bit tricks appears regularly in systems code, competitive programming, and technical interviews. These are not clever hacks — they are well-understood, well-named idioms with measurable performance benefits.

## 1. Population Count (popcount)

**Counts the number of 1-bits in a word.** Used in checksums, Hamming distances, and hash functions.

### Compiler Built-in (Fastest)

```cpp
#include <bit>       // C++20
int n = std::popcount(0b10110101u);  // 5

// Pre-C++20 (GCC/Clang built-in):
int n = __builtin_popcount(x);       // unsigned int
int n = __builtin_popcountll(x);     // unsigned long long
```

### Classic Bit-Trick Loop (Kernighan's Method)

Each iteration clears the **lowest** set bit — so the loop runs exactly `popcount(x)` times:

```cpp
int popcount_kernighan(unsigned x) {
    int count = 0;
    while (x) {
        x &= (x - 1);   // clear lowest set bit
        ++count;
    }
    return count;
}
```

## 2. Isolate the Lowest Set Bit

```cpp
unsigned lsb = x & (-x);   // two's complement trick
```

`-x` in two's complement flips all bits then adds 1, which propagates a carry that sets exactly the position of the lowest 1-bit. ANDing with `x` isolates it.

```
x     = 0b10110100
-x    = 0b01001100
x & -x= 0b00000100   ← bit 2, the lowest set bit
```

**Applications:** iterating over set bits, finding alignment of a pointer, identifying the first pending interrupt bit.

```cpp
// Iterate over all set bits
unsigned flags = 0b10110010;
while (flags) {
    unsigned bit = flags & (-flags);          // isolate lowest bit
    int      pos = __builtin_ctz(flags);      // count trailing zeros
    process_flag(pos);
    flags &= flags - 1;                       // clear lowest bit
}
```

## 3. Clear the Lowest Set Bit

```cpp
x = x & (x - 1);
```

Subtracting 1 from `x` flips the lowest set bit to 0 and all trailing zeros to 1. AND with the original masks away those trailing ones along with the target bit.

## 4. Test Whether a Value Is a Power of Two

```cpp
bool is_power_of_two(unsigned x) {
    return x != 0 && (x & (x - 1)) == 0;
}
```

A power of two has exactly one bit set. `x - 1` turns that bit off and turns on all lower bits. ANDing gives 0 only if there was exactly one bit.

```
x = 8  = 0b00001000
x-1 = 7  = 0b00000111
x & (x-1)= 0b00000000  → zero → power of two
```

## 5. Round Up to Next Power of Two

```cpp
uint32_t next_pow2(uint32_t x) {
    if (x == 0) return 1;
    x--;
    x |= x >> 1;
    x |= x >> 2;
    x |= x >> 4;
    x |= x >> 8;
    x |= x >> 16;
    return x + 1;
}
```

Each OR-shift propagates the highest set bit downward to fill all lower positions. Adding 1 at the end steps to the next power.

In C++20: `std::bit_ceil(x)`.

## 6. Count Trailing Zeros (Find Lowest Set Bit Position)

```cpp
int pos = __builtin_ctz(x);   // GCC/Clang; undefined for x == 0
// C++20:
int pos = std::countr_zero(x);
```

Equivalent to `log2(x & -x)` — the index of the lowest set bit.

## 7. Bit Reversal

Reversing the bits of a byte appears in CRC calculations and bit-serial protocols:

```cpp
uint8_t reverse_bits(uint8_t b) {
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;  // swap nibbles
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2;  // swap pairs
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1;  // swap individual bits
    return b;
}
```

## Quick-Reference Table

| Trick | Expression |
|-------|-----------|
| Count set bits | `std::popcount(x)` / `__builtin_popcount(x)` |
| Isolate lowest set bit | `x & (-x)` |
| Clear lowest set bit | `x & (x - 1)` |
| Is power of two? | `x != 0 && (x & (x-1)) == 0` |
| Round up to power of two | `std::bit_ceil(x)` (C++20) |
| Count trailing zeros | `std::countr_zero(x)` / `__builtin_ctz(x)` |
| Count leading zeros | `std::countl_zero(x)` / `__builtin_clz(x)` |

> **Interview answer:** "The two most important bit tricks are `x & (x-1)` to clear the lowest set bit (and count set bits in a loop) and `x & (-x)` to isolate it. `(x & (x-1)) == 0` tests for powers of two. In modern C++ prefer `<bit>` header functions like `std::popcount` and `std::bit_ceil` because they are portable and the compiler maps them to hardware instructions."
