# Unsigned vs Signed Integer Representation

When you declare an integer in C or Rust, you are telling the compiler how to interpret a fixed-width pattern of bits. The same 32 bits can represent very different values depending on whether the type is signed or unsigned. Getting this distinction wrong is a source of subtle, hard-to-debug bugs.

## Unsigned Integers

An n-bit unsigned integer represents values from **0 to 2ⁿ − 1**. Every bit contributes a non-negative power of 2, and there is no concept of negative numbers.

```c
uint8_t  u8  = 255;   // 0xFF  —  range [0, 255]
uint16_t u16 = 65535; // 0xFFFF — range [0, 65535]
uint32_t u32 = 4294967295U;
```

Unsigned arithmetic wraps around modulo 2ⁿ. Subtracting past zero wraps to the maximum value — this is defined behavior in C for unsigned types.

```c
uint8_t x = 0;
x -= 1;  // x is now 255 — well-defined wrap-around
```

## Signed Integers

An n-bit signed integer must encode both positive and negative values. The most common encoding is **two's complement** (covered in the next lesson), but three encodings exist:

| Encoding         | Positive range         | Negative range         | Zero representations |
|------------------|------------------------|------------------------|----------------------|
| Sign-magnitude   | 0 to 2ⁿ⁻¹ − 1         | −(2ⁿ⁻¹ − 1) to −1    | Two (+0 and −0)      |
| One's complement | 0 to 2ⁿ⁻¹ − 1         | −(2ⁿ⁻¹ − 1) to −1    | Two (+0 and −0)      |
| Two's complement | 0 to 2ⁿ⁻¹ − 1         | −2ⁿ⁻¹ to −1           | One                  |

Modern hardware universally uses **two's complement** because addition and subtraction work without special-casing the sign bit.

```c
int8_t  s8  = -1;   // 0xFF in memory — same bits as uint8_t 255!
int16_t s16 = -128; // 0xFF80
int32_t s32 = -2147483648; // 0x80000000 — most negative 32-bit value
```

## The Sign Bit

In two's complement, the **most-significant bit (MSB)** acts as the sign bit: 0 means non-negative, 1 means negative. For an 8-bit value, this splits the range at 128:

```
Bits 0111 1111 = +127 (signed)  /  127 (unsigned)
Bits 1000 0000 = -128 (signed)  /  128 (unsigned)
Bits 1111 1111 =   -1 (signed)  /  255 (unsigned)
```

## Common Pitfalls

**Mixing signed and unsigned in comparisons.** In C, when you compare a signed and an unsigned value, the signed value is implicitly converted to unsigned. This can flip the result:

```c
int   a = -1;
unsigned int b = 1;
if (a < b) {           // You expect true …
    printf("a < b");   // … but this never prints!
}
// -1 is reinterpreted as 0xFFFFFFFF (4294967295), which > 1
```

**Overflow behavior.** Signed integer overflow is *undefined behavior* in C/C++. The compiler is allowed to assume it never happens and optimize accordingly. Unsigned overflow is defined (wraps around).

```c
int x = INT_MAX;
x++;        // Undefined behavior in C — never rely on this
uint32_t y = UINT32_MAX;
y++;        // y == 0 — defined wrap-around
```

**strlen and negative indices.** `strlen` returns `size_t`, which is unsigned. Comparing it with a signed int can silently wrap.

```c
int len = strlen(s) - 1;  // Fine if strlen > 0
// BUT if the string is empty, strlen(s) == 0
// and strlen(s) - 1 wraps to SIZE_MAX (a huge number)
```

## RISC-V Context

RISC-V provides separate instructions for signed and unsigned operations where the interpretation matters:

- `LBU` / `LB` — load byte, **u**nsigned (zero-extended) vs signed (sign-extended)
- `BLTU` / `BLT` — branch less-than, unsigned vs signed comparison
- `DIVU` / `DIV` — unsigned vs signed division

The ISA makes the distinction explicit so hardware needs only one bit-pattern representation in registers.

> **Interview answer:** Unsigned integers represent values from 0 to 2ⁿ−1 using all bits as magnitude; signed integers (in two's complement) use the MSB as a sign bit, giving range −2ⁿ⁻¹ to 2ⁿ⁻¹−1. Mixing them in comparisons is a classic bug because C promotes signed to unsigned implicitly.
