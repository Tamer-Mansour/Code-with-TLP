# Two's Complement and Signed Integers

Hardware registers that hold signed values — ADC outputs, temperature sensors, offset fields — use two's complement encoding universally. Misreading a two's complement number as unsigned is a classic firmware bug.

## Why Not Sign-Magnitude?

An early alternative was to dedicate the MSB as a sign flag and keep the magnitude in the remaining bits. That scheme creates two zeros (`+0` and `-0`) and requires separate adder circuits for addition and subtraction. Two's complement eliminates both problems: addition hardware is identical for signed and unsigned, and zero has a unique representation.

## The Two's Complement Rule

For an N-bit value the MSB carries weight **-2^(N-1)** instead of +2^(N-1). All other bits keep their normal positive weights.

```
8-bit example: 0b1111_1110

Weight: -128  64  32  16  8  4  2  1
Bit:       1   1   1   1  1  1  1  0

Value = -128 + 64 + 32 + 16 + 8 + 4 + 2 + 0 = -2
```

## Converting Positive to Negative (and Back)

**Recipe:** invert all bits, then add 1.

```cpp
int8_t pos =  5;   // 0b0000_0101
               //  invert → 0b1111_1010
               //  +1     → 0b1111_1011  = -5
int8_t neg = -5;   // 0b1111_1011
               //  invert → 0b0000_0100
               //  +1     → 0b0000_0101  = 5  ✓
```

This is self-inverse — applying it twice returns the original value.

## Range of N-bit Two's Complement

| Bits | Min | Max |
|------|-----|-----|
| 8 | -128 | +127 |
| 16 | -32 768 | +32 767 |
| 32 | -2 147 483 648 | +2 147 483 647 |

Notice: there is one more negative value than positive. `-128` (0b1000_0000 for 8 bits) has no positive counterpart, so `abs(INT8_MIN)` overflows — a common bug.

## Sign Extension

When widening a signed value from N bits to M bits (M > N), replicate the MSB into every new high bit.

```cpp
int8_t  small = -5;           // 0b1111_1011
int16_t big   = (int16_t)small; // 0b1111_1111_1111_1011  = -5 ✓
```

In C/C++ an implicit cast from a signed narrow type to a wider signed type performs sign extension automatically. Unsigned widening zero-extends instead.

> **Pitfall:** casting `uint8_t` to `int32_t` zero-extends first (value 0xFB becomes 251, not -5). If a register field is documented as signed, you must cast to the signed narrow type first.

## Detecting Overflow

Two's complement overflow occurs when the result of an operation cannot be represented.

```cpp
int8_t a = 120, b = 10;
int8_t c = a + b;   // 130 overflows! wraps to -126
```

Detection rule: overflow happens when both operands have the same sign and the result has the opposite sign. Hardware processors set an overflow flag (V flag in ARM, OF in x86) for exactly this condition.

## Worked Example — ADC Two's Complement Output

A 12-bit ADC with a signed two's complement output reads back `0xFFE` from a register.

```
0xFFE = 0b1111_1111_1110  (12 bits)

Sign bit (bit 11) = 1 → negative number
Invert: 0b0000_0000_0001
Add 1:  0b0000_0000_0010 = 2

So 0xFFE represents -2 (LSB units)
```

In C++, extracting and sign-extending this field:

```cpp
uint32_t raw = read_register();          // e.g. 0x00000FFE
int32_t  adc = (int32_t)(raw & 0xFFF);  // isolate 12 bits → 4094
// Sign extend from bit 11
if (adc & 0x800) adc |= ~0xFFF;         // fill high bits with 1s
// adc is now -2
```

## Key Points

- Two's complement is the universal signed integer encoding in modern hardware.
- Converting negative: **invert + 1** (works in both directions).
- Sign extension replicates the MSB; unsigned widening zero-extends.
- `INT_MIN` has no positive counterpart — never negate it.

**Interview answer:** "Two's complement assigns weight -2^(N-1) to the MSB. To negate, I invert all bits and add 1. This lets hardware reuse the same adder for both signed and unsigned arithmetic."
