# Bitwise Operators: AND, OR, XOR, NOT, Shifts

Bitwise operators work directly on the binary representation of integers. They are the backbone of systems programming — from setting hardware registers to writing compact, cache-friendly data structures. Understanding them at the bit level, not just the truth-table level, separates a systems programmer from a general-purpose developer.

## The Six Operators at a Glance

| Operator | Symbol | Effect |
|----------|--------|--------|
| AND | `&` | Bit is 1 only when both inputs are 1 |
| OR | `\|` | Bit is 1 when at least one input is 1 |
| XOR | `^` | Bit is 1 when inputs differ |
| NOT (complement) | `~` | Flips every bit |
| Left shift | `<<` | Shifts bits toward higher significance |
| Right shift | `>>` | Shifts bits toward lower significance |

## AND — Masking

AND is used to **isolate** specific bits. Every bit ANDed with 0 becomes 0; every bit ANDed with 1 keeps its value.

```cpp
uint8_t status = 0b10110101;
uint8_t lower_nibble = status & 0x0F;  // 0b00000101
```

Use AND to extract a field or test whether particular bits are set.

## OR — Setting Bits

OR forces specific bits to 1 without disturbing the rest.

```cpp
uint8_t config = 0b00001010;
config = config | 0b00100000;  // set bit 5 → 0b00101010
```

## XOR — Toggling and Differencing

XOR flips bits where the mask is 1. Applying the same XOR twice restores the original value — a property used in simple encryption and toggle idioms.

```cpp
uint8_t flags = 0b11001100;
flags = flags ^ 0b00001111;  // toggle lower nibble → 0b11000011
flags = flags ^ 0b00001111;  // toggle again → 0b11001100 (restored)
```

## NOT — Bitwise Complement

`~` flips every bit of its operand. On a 32-bit `unsigned int`, `~0u` produces `0xFFFFFFFF`. Watch the type: applying `~` to a small integer literal promotes it first.

```cpp
uint8_t mask = ~0b00001111u;  // 0b11110000 — upper nibble mask
```

> **Pitfall:** `~0` on a signed int gives `-1` in two's complement. Prefer `~0u` or cast explicitly when building masks.

## Left Shift — Multiply by Powers of Two

`x << n` shifts bits left by `n` positions, filling with zeros on the right. This multiplies `x` by `2^n` as long as no significant bit is lost.

```cpp
uint32_t one = 1u;
uint32_t bit5 = one << 5;  // 0x00000020 — bit 5 set
```

## Right Shift — Divide by Powers of Two

`x >> n` shifts right by `n` positions.

- For **unsigned** types, vacated high bits fill with 0 (logical shift).
- For **signed** types, behavior is implementation-defined in C++03 but in practice all modern compilers perform an arithmetic shift (sign-extend).

```cpp
uint32_t x = 0x80;
uint32_t halved = x >> 1;   // 0x40 — unsigned, always fills with 0
```

## Compound Assignment Forms

All six operators have compound assignment variants: `&=`, `|=`, `^=`, `<<=`, `>>=`. Prefer them for brevity and readability.

```cpp
uint32_t reg = read_hw_register();
reg |= (1u << 4);   // set bit 4
reg &= ~(1u << 3);  // clear bit 3
reg ^= (1u << 7);   // toggle bit 7
write_hw_register(reg);
```

## Precedence Warning

Bitwise operators have **lower** precedence than comparison operators. Always parenthesize:

```cpp
// Bug: reads as (x & (FLAG == 0)) because == binds tighter than &
if (x & FLAG == 0) { ... }

// Correct:
if ((x & FLAG) == 0) { ... }
```

## Worked Example: Extract a Field

Extract bits 4-6 (a 3-bit field) from a status byte:

```cpp
uint8_t status = 0b01101010;
uint8_t field = (status >> 4) & 0x07;  // shift field to bit 0, mask 3 bits
// result: 0b110 = 6
```

> **Interview answer:** "AND isolates bits, OR sets them, XOR toggles them, NOT complements, and shifts multiply or divide by powers of two. The key insight is that every pattern is mask-based: craft a mask with `1u << n` and combine with `&`, `|`, or `^`."
