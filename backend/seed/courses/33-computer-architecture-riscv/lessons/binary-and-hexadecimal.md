# Binary, Octal, and Hexadecimal Number Systems

Computers store everything as sequences of bits — zeros and ones. To reason about machine code, memory addresses, and hardware registers, you need to read and write numbers in binary and hexadecimal fluently. This lesson builds that fluency from the ground up.

## Why Multiple Bases?

The decimal system uses base 10 because humans have ten fingers. Computers use **base 2 (binary)** because a transistor has two states: off (0) or on (1). **Base 16 (hexadecimal)** is a compact shorthand for binary: every four bits map exactly to one hex digit, making 32- and 64-bit values readable at a glance. **Base 8 (octal)** was popular in older systems and still appears in Unix file permissions.

## Binary (Base 2)

Each digit (bit) represents a power of 2, starting from 2⁰ on the right.

```
Binary: 1 0 1 1 0 1
Power:  2⁵ 2⁴ 2³ 2² 2¹ 2⁰
Value:  32 + 0 + 8 + 4 + 0 + 1 = 45
```

**Converting decimal to binary** — repeatedly divide by 2 and collect remainders:

```
45 ÷ 2 = 22 remainder 1   (LSB)
22 ÷ 2 = 11 remainder 0
11 ÷ 2 =  5 remainder 1
 5 ÷ 2 =  2 remainder 1
 2 ÷ 2 =  1 remainder 0
 1 ÷ 2 =  0 remainder 1   (MSB)
Read remainders bottom-up: 101101
```

## Hexadecimal (Base 16)

Hex uses digits 0–9 then A–F (A=10, B=11, … F=15). The prefix `0x` signals a hex literal in most languages.

| Hex | Decimal | Binary |
|-----|---------|--------|
| 0   | 0       | 0000   |
| 9   | 9       | 1001   |
| A   | 10      | 1010   |
| F   | 15      | 1111   |

**Binary ↔ Hex is trivial** — group bits in fours from the right:

```
Binary: 1010 1111 0011
Hex:      A    F    3   →  0xAF3
```

This is why RISC-V instructions and memory addresses are almost always written in hex: `0xDEADBEEF` is far easier to scan than 32 binary digits.

## Octal (Base 8)

Group bits in **threes**. Octal is mostly legacy, but you will encounter it in Unix permissions (`chmod 755`) where each digit encodes read/write/execute for owner, group, and others.

```
Binary: 111 101 101
Octal:   7   5   5   →  0755
```

## Worked Example

Convert `0x2A` to decimal and binary.

```
0x2A → 2×16¹ + A×16⁰
     = 2×16  + 10×1
     = 32 + 10
     = 42 (decimal)

0x2A → 0010 1010 (binary)
```

Verify: 32+8+2 = 42. ✓

## Common Pitfalls

- **MSB vs LSB confusion** — the most-significant bit is on the **left** in standard notation; LSB is on the right. Memory byte order (endianness) is a separate concern.
- **Forgetting the prefix** — `0x1A` ≠ `1A` (which is not a valid decimal literal). Always write `0x` for hex in code.
- **Off-by-one in grouping** — when grouping for hex, pad on the **left** with zeros: `10 1101` → `0010 1101` → `0x2D`, not `0x2 D`.

## Quick Reference

| Base | Prefix | Digits | Bits per digit |
|------|--------|--------|----------------|
| 2    | 0b     | 0-1    | 1              |
| 8    | 0o     | 0-7    | 3              |
| 16   | 0x     | 0-F    | 4              |

> **Interview answer:** Hex is used to represent binary data compactly because every hex digit maps exactly to four bits, making it easy to inspect registers and memory addresses without the verbosity of raw binary.
