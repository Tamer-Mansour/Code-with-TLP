# Integer Promotion and Implicit Conversions

C++ inherited a set of arithmetic conversion rules from C that were designed in the 1970s for PDP-11 hardware. They are still with us today and they cause more subtle bugs than almost any other language feature.

## Integer Promotions

Before any arithmetic operation, operands smaller than `int` are **promoted**. The rule:

> If `int` can represent all values of the original type, the value is converted to `int`; otherwise to `unsigned int`.

On virtually every modern platform, `int` is 32 bits, so `char`, `signed char`, `unsigned char`, `short`, and `unsigned short` all promote to `int`.

```cpp
uint8_t a = 200;
uint8_t b = 100;
uint8_t result = a + b;  // a and b promote to int first!
                          // int(200) + int(100) = int(300)
                          // then truncated back to uint8_t: 44
```

This promotion is why the following prints a negative number:

```cpp
uint8_t x = 0xFF;
int y = ~x;       // ~(int)0xFF = ~0x000000FF = 0xFFFFFF00 = -256, NOT 0
```

## Usual Arithmetic Conversions

When an operator has two operands of different types, C++ applies the **usual arithmetic conversions** — a hierarchy from lowest to highest rank:

1. `bool` < `char` < `short` < `int` < `long` < `long long`
2. Unsigned variants rank alongside their signed peers.
3. If either operand is `unsigned long long`, the other is converted to `unsigned long long`.
4. If types have the same rank but differ in signedness, the **signed type is converted to unsigned**.

```cpp
int   s = -1;
unsigned int u = 1;
// Both have rank int. Signed → unsigned. -1 becomes UINT_MAX.
if (s < u)    puts("negative");  // never prints
if (s + u > 0) puts("positive"); // s + u = UINT_MAX, which IS > 0 (unsigned)
```

## Floating-Point Conversions

Integer-to-float conversion is exact for small integers but loses precision for large ones:

```cpp
int64_t big = 9007199254740993LL;  // 2^53 + 1
double  d   = big;                  // double has 53-bit mantissa
int64_t back = (int64_t)d;         // 9007199254740992 — off by 1!
```

Rule of thumb: `double` can exactly represent integers up to 2^53 (about 9 quadrillion). Beyond that, rounding occurs.

## Narrowing Conversions

Converting to a smaller type **truncates** — silently in C-style casts, and as a compile error in `{}` initialization:

```cpp
int wide = 300;
uint8_t narrow = wide;     // silently truncates: 44 (300 % 256)
uint8_t safe   = {wide};   // compile error: narrowing conversion
```

Always use `{}` initialization in modern C++ to catch narrowing at compile time.

## A Subtle Promotion Bug in Real Code

```cpp
// Supposed to detect if high byte is set
uint16_t val = 0x8000;
if (val >> 15 == 1) {          // shift promotes val to int first
    puts("high bit set");       // int(0x8000) >> 15 = 1 — works here
}

// But this is more dangerous:
uint16_t flags = 0xFFFF;
int shifted = flags >> 1;      // int(0xFFFF) >> 1 = 0x7FFF — OK
// However:
int16_t signed_flags = 0xFFFF; // -1 as signed
int bad = signed_flags >> 1;   // implementation-defined! (arithmetic vs logical shift)
```

Right-shifting a negative signed integer is **implementation-defined** — on most platforms it does arithmetic shift (sign extends), but you cannot rely on that.

## Conversion Rules Summary

| From | To | Result |
|------|----|--------|
| small int type | `int` | promoted, value preserved |
| `int` | `unsigned int` | reinterpreted (bit pattern same) |
| larger int | smaller int | truncated (low bits kept) |
| `int64_t` | `double` | rounded if > 2^53 |
| `double` | `int` | truncated toward zero; UB if out of range |

## Practical Advice

- Perform explicit casts when you intend a narrowing conversion.
- Use `-Wconversion` to catch implicit narrowing in GCC/Clang.
- Avoid mixing signed and unsigned in arithmetic expressions.
- Use `static_cast<uint8_t>(...)` rather than C-style `(uint8_t)(...)` to make the intent visible in code review.

**Interview answer:** "Operands smaller than int are promoted to int before arithmetic. When signed and unsigned types of the same rank are mixed, the signed value is converted to unsigned — turning -1 into UINT_MAX. Use explicit casts and enable -Wconversion to surface these issues at compile time."
