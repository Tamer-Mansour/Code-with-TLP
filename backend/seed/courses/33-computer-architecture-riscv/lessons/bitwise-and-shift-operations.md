# Bitwise and Shift Operations

Beyond arithmetic, every ALU implements a set of **bitwise** and **shift** operations. These work directly on the individual bits of operands and are essential for masking, packing/unpacking fields, and efficient arithmetic tricks.

## Bitwise Operations

Bitwise operations apply a Boolean function to every corresponding pair of bits independently. They complete in a single gate delay — the fastest operations an ALU performs.

| Operation | Symbol | Bit rule | Example (4-bit) |
|-----------|--------|----------|-----------------|
| AND | `&` | 1 only if both 1 | `1010 & 1100 = 1000` |
| OR | `\|` | 1 if either is 1 | `1010 \| 1100 = 1110` |
| XOR | `^` | 1 if bits differ | `1010 ^ 1100 = 0110` |
| NOT | `~` | Flip every bit | `~1010 = 0101` |

### Common Use Cases

- **AND for masking**: extract specific bits by ANDing with a mask.
- **OR for setting bits**: set a specific bit by ORing with a mask.
- **XOR for toggling**: flip a specific bit by XORing with a mask.
- **XOR for comparison**: `A ^ B == 0` if and only if `A == B` — fast equality check.

```c
uint32_t x = 0b10110100;

// Extract bits [5:4]
uint32_t field = (x >> 4) & 0x3;    // 0x3 = 0b11 is a 2-bit mask

// Set bit 1
x |= (1 << 1);

// Clear bit 2
x &= ~(1 << 2);

// Toggle bit 7
x ^= (1 << 7);
```

## Shift Operations

Shifts move bits left or right by a specified number of positions. There are three variants:

### Logical Shift Left (SLL / `<<`)

All bits shift left; vacated positions on the right are filled with **zeros**. Bits shifted off the left end are lost.

```
0001_1010 << 2 = 0110_1000
```

Left-shifting by N is equivalent to multiplying by 2^N (for unsigned and signed values with no overflow).

### Logical Shift Right (SRL / unsigned `>>`)

All bits shift right; vacated positions on the left are filled with **zeros**.

```
0110_1000 >> 2 = 0001_1010
```

Logical right shift by N is equivalent to unsigned integer division by 2^N.

### Arithmetic Shift Right (SRA / signed `>>`)

All bits shift right; vacated positions on the left are filled with the **sign bit** (the MSB). This preserves the sign of a two's complement number.

```
1110_1000 >> 2 (arithmetic) = 1111_1010   (sign bit replicated)
0110_1000 >> 2 (arithmetic) = 0001_1010   (sign bit = 0, same as logical)
```

Arithmetic right shift by N is equivalent to signed integer division by 2^N (rounding toward negative infinity).

### Comparison Table

| Type | Vacated bits filled with | Use case |
|------|--------------------------|----------|
| SLL | 0 | Multiply by power of 2 |
| SRL | 0 | Unsigned divide by power of 2 |
| SRA | Sign bit (MSB copy) | Signed divide by power of 2 |

## RISC-V Shift Instructions

RISC-V provides all three shift types as both immediate and register-form instructions:

```asm
sll  t0, t1, t2     # t0 = t1 << t2   (logical left)
srl  t0, t1, t2     # t0 = t1 >> t2   (logical right)
sra  t0, t1, t2     # t0 = t1 >> t2   (arithmetic right)
slli t0, t1, 4      # t0 = t1 << 4    (immediate)
srli t0, t1, 4      # t0 = t1 >> 4
srai t0, t1, 4      # t0 = t1 >> 4   (arithmetic)
```

The shift amount is taken from the lower 5 bits of the register (or the 5-bit immediate) — shifting a 32-bit value by more than 31 is meaningless.

## Hardware Implementation

- **Barrel shifter**: the standard hardware for implementing shifts in one clock cycle. It uses a tree of multiplexers — each layer either shifts by a power of 2 or passes through unchanged.
  - 5 layers of muxes handle shifts of 0-31 bits for a 32-bit operand.
  - Delay: O(log N) mux levels.

```
Layer 0: shift by 0 or 1
Layer 1: shift by 0 or 2
Layer 2: shift by 0 or 4
Layer 3: shift by 0 or 8
Layer 4: shift by 0 or 16
```

## Common Pitfalls

- **Shift amount masking**: shifting by a value >= the word size (e.g., shifting a 32-bit int by 32) is **undefined behavior in C**. The hardware silently masks the shift amount to 5 bits.
- **Arithmetic vs. logical right shift**: using `>>` in C on a `signed int` is implementation-defined (usually arithmetic), but on an `unsigned int` it is always logical. Always cast explicitly.
- **Left shift overflow**: `1 << 31` in signed 32-bit arithmetic is UB in C — use `1u << 31` or `(uint32_t)1 << 31`.

> **Interview answer:** The ALU supports logical (zero-fill) and arithmetic (sign-fill) shifts via a barrel shifter — a tree of multiplexers that shifts by any amount in O(log N) gate delays; arithmetic right shift preserves the sign bit, making it equivalent to signed division by a power of two.
