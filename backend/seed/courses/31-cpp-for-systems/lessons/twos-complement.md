# Two's Complement and Negative Number Encoding

Two's complement is the universal encoding for signed integers on all modern hardware. Understanding it explains overflow behaviour, bitwise arithmetic on negative numbers, and why certain casts produce surprising results.

## What Is Two's Complement?

For an N-bit integer, the two's complement of a value `x` is `2^N - x`. In practice, you compute it by inverting all bits and adding 1:

```
 0000 0101  =  5
 1111 1010  (invert all bits = one's complement)
+0000 0001  (add 1)
---------
 1111 1011  = -5 in two's complement (8-bit)
```

The most significant bit (MSB) acts as a sign bit: `0` = non-negative, `1` = negative. This gives an 8-bit `int8_t` a range of -128 to +127.

## Why Two's Complement?

Two's complement was chosen because it makes addition and subtraction hardware identical for signed and unsigned integers. The ALU does not need to know the sign to add:

```
  0000 0101  (+5)
+ 1111 1011  (-5)
-----------
  0000 0000  (0, carry discarded)
```

One's complement (invert only) was the historical alternative, but it has two representations of zero (`+0` and `-0`) and requires an extra carry correction step.

## Range and Overflow

| Type | Bits | Min | Max |
|------|------|-----|-----|
| `int8_t` | 8 | -128 | 127 |
| `int16_t` | 16 | -32 768 | 32 767 |
| `int32_t` | 32 | -2 147 483 648 | 2 147 483 647 |
| `int64_t` | 64 | -9.2 × 10^18 | 9.2 × 10^18 |

Notice that the minimum magnitude is one larger than the maximum. This matters:

```cpp
#include <climits>
#include <cstdio>

int main() {
    int32_t x = INT32_MIN;   // -2147483648
    int32_t y = -x;          // undefined behaviour! no positive 2147483648 in int32_t
    printf("%d\n", y);       // result is implementation-defined
}
```

Signed overflow is **undefined behaviour** in C++. The compiler is allowed to assume it never happens and may optimise accordingly, producing subtle bugs.

## Inspecting the Bit Pattern

```cpp
#include <cstdint>
#include <cstring>
#include <cstdio>

void print_bits(int32_t v) {
    uint32_t raw;
    std::memcpy(&raw, &v, 4);   // safe type pun
    for (int i = 31; i >= 0; --i)
        putchar((raw >> i) & 1 ? '1' : '0');
    putchar('\n');
}

int main() {
    print_bits(5);    //  00000000000000000000000000000101
    print_bits(-5);   //  11111111111111111111111111111011
    print_bits(-1);   //  11111111111111111111111111111111
    print_bits(-128); //  11111111111111111111111110000000 (int32_t)
}
```

## Sign Extension

When you assign a narrower signed type to a wider one, the sign bit is replicated into all new high bits:

```cpp
int8_t  a = -1;       // 0xFF
int32_t b = a;        // 0xFFFFFFFF (-1), sign-extended correctly
uint32_t c = (uint32_t)a; // 0xFFFFFFFF (4294967295) — be careful!
```

This is why casting `int8_t -1` to `uint32_t` produces a large positive number, not 255.

## Practical Implication: Serializing Signed Integers

When writing a signed integer to a byte stream, the two's complement representation is already the bytes in memory. The only question is byte order (endianness). Read and write the raw bytes with `memcpy`:

```cpp
#include <cstdint>
#include <cstring>

void write_int32_be(uint8_t* buf, int32_t val) {
    // reinterpret as unsigned to avoid sign-related UB in bit shifts
    uint32_t u;
    std::memcpy(&u, &val, 4);
    buf[0] = (u >> 24) & 0xFF;
    buf[1] = (u >> 16) & 0xFF;
    buf[2] = (u >>  8) & 0xFF;
    buf[3] = (u      ) & 0xFF;
}

int32_t read_int32_be(const uint8_t* buf) {
    uint32_t u = ((uint32_t)buf[0] << 24) |
                 ((uint32_t)buf[1] << 16) |
                 ((uint32_t)buf[2] <<  8) |
                 ((uint32_t)buf[3]);
    int32_t val;
    std::memcpy(&val, &u, 4);
    return val;
}
```

## Common Pitfalls

- **Right-shifting negative values**: arithmetic right shift is implementation-defined for signed integers before C++20 (defined as arithmetic shift in C++20 for two's complement targets).
- **Comparing signed and unsigned**: mixing `int` and `unsigned int` in comparisons causes silent conversion, often turning negative values into large positives.
- **Assuming two's complement before C++20**: C++20 mandates two's complement for signed integers. Before that, other encodings were technically allowed (though non-existent in practice).

> **Interview answer:** Two's complement encodes negative numbers by inverting all bits and adding 1. It is used universally because signed and unsigned addition share the same hardware circuit. The MSB is the sign bit, and signed overflow is undefined behaviour in C++.
