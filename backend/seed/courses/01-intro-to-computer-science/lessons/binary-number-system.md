# The Binary Number System

Computers store and process everything—numbers, text, images, sound—as sequences of **0s and 1s**. Understanding *why* and *how* requires a solid grasp of the binary number system. This lesson takes you from first principles all the way through practical conversions.

## Why Binary?

A computer is built from billions of tiny switches called **transistors**. Each transistor is either **on** (conducting electricity) or **off** (not conducting). That gives us exactly two states, which map perfectly to the two digits of binary:

| Transistor state | Binary digit | Electrical meaning |
|-----------------|-------------|--------------------|
| Off | **0** | Low voltage (~0 V) |
| On | **1** | High voltage (~3.3 V or 5 V) |

Why not use base-10 (decimal) or base-3? Each would require transistors that can reliably hold 10 or 3 stable voltage levels. In practice, distinguishing 10 precise voltage levels reliably at billions of operations per second is enormously difficult—noise on the line would cause errors. Binary keeps hardware simple and robust: any voltage above a threshold is "1," anything below is "0."

## Place Value: How Bases Work

Every number system uses **place value**—the position of a digit determines how much it is worth.

### Base-10 (Decimal) Review

```
 3   4   2
 │   │   └─ 2 × 10⁰  =   2 × 1   =   2
 │   └───── 4 × 10¹  =   4 × 10  =  40
 └───────── 3 × 10²  =   3 × 100 = 300
                                    ───
                                    342
```

The base (10) is the multiplier between adjacent positions.

### Base-2 (Binary)

Binary works identically, but each position represents a power of **2** instead of 10:

```
 1   0   1   1   0   1
 │   │   │   │   │   └─ 1 × 2⁰  =  1 × 1  =  1
 │   │   │   │   └───── 0 × 2¹  =  0 × 2  =  0
 │   │   │   └───────── 1 × 2²  =  1 × 4  =  4
 │   │   └───────────── 1 × 2³  =  1 × 8  =  8
 │   └─────────────────  0 × 2⁴  =  0 × 16 =  0
 └───────────────────── 1 × 2⁵  =  1 × 32 = 32
                                             ──
                                             45
```

So **101101** in binary = **45** in decimal. Notice that every power of 2 in the table (1, 2, 4, 8, 16, 32, 64, 128, …) is worth *double* the one to its right.

## Converting Binary → Decimal: Step by Step

**Method:** Write down the powers of 2 for each position (right to left, starting at 2⁰), multiply each by the corresponding binary digit (0 or 1), then sum.

**Worked Example 1:** Convert `1100 1001` to decimal.

| Bit position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|---|
| Bit value    | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 1 |
| Power of 2   | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
| Contribution | 128 | 64 | 0 | 0 | 8 | 0 | 0 | 1 |

128 + 64 + 8 + 1 = **201**

**Worked Example 2:** Convert `0001 0110` to decimal.

Powers where the bit is 1: position 4 (16) and position 2 (4) and position 1 (2).
16 + 4 + 2 = **22**

**Shortcut:** You only need to sum the powers at positions where the bit is **1**; skip all the zeros.

## Converting Decimal → Binary: Step by Step

**Method (Division Algorithm):** Repeatedly divide by 2, recording the remainder each time. Read the remainders from **bottom to top** to get the binary number.

**Worked Example: Convert 45 to binary.**

```
45 ÷ 2 = 22  remainder 1   ← least significant bit (rightmost)
22 ÷ 2 = 11  remainder 0
11 ÷ 2 =  5  remainder 1
 5 ÷ 2 =  2  remainder 1
 2 ÷ 2 =  1  remainder 0
 1 ÷ 2 =  0  remainder 1   ← most significant bit (leftmost)
```

Read remainders bottom to top: **101101** ✓ (matches our earlier example)

**Worked Example: Convert 200 to binary.**

```
200 ÷ 2 = 100 remainder 0
100 ÷ 2 =  50 remainder 0
 50 ÷ 2 =  25 remainder 0
 25 ÷ 2 =  12 remainder 1
 12 ÷ 2 =   6 remainder 0
  6 ÷ 2 =   3 remainder 0
  3 ÷ 2 =   1 remainder 1
  1 ÷ 2 =   0 remainder 1
```

Read bottom to top: **11001000** ✓

Verify: 128 + 64 + 8 = 200 ✓

## Binary Addition

Binary addition follows the same rules as decimal, with only two digits:

| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   |

When both bits are 1, the sum is 0 and we **carry** 1 to the next column—exactly like carrying a 10 in decimal when two digits sum to 10 or more.

**Example: Add 13 (1101) + 11 (1011)**

```
  1 1 0 1   (13)
+ 1 0 1 1   (11)
─────────
  Carry: 1 1 1 0
  Sum:   1 1 0 0 0  = 24 ✓
```

## Bits, Nibbles, Bytes, and Beyond

| Term | Size | Max value | Example |
|------|------|-----------|---------|
| **bit** | 1 binary digit | 1 | `1` |
| **nibble** | 4 bits | 15 | `1011` |
| **byte** | 8 bits | 255 | `1100 1001` |
| **kilobyte (KB)** | 1,024 bytes | — | A short text file |
| **megabyte (MB)** | 1,024 KB | — | A minute of audio |
| **gigabyte (GB)** | 1,024 MB | — | A movie file |
| **terabyte (TB)** | 1,024 GB | — | A large hard drive |

A single byte can represent 2⁸ = **256** different values (0–255). With *n* bits you can represent **2ⁿ** different values.

> **Why 1,024 instead of 1,000?** Because 2¹⁰ = 1,024, the nearest power of 2 to 1,000. Computer memory is addressed in powers of 2, so it is natural to group bytes this way. (Storage manufacturers often use 1,000 bytes = 1 KB for marketing purposes, which is why a "500 GB" drive shows up as ~465 GB in an OS.)

## Quick Reference: Binary ↔ Decimal (0–15)

| Decimal | Binary | Decimal | Binary |
|---------|--------|---------|--------|
| 0 | 0000 | 8 | 1000 |
| 1 | 0001 | 9 | 1001 |
| 2 | 0010 | 10 | 1010 |
| 3 | 0011 | 11 | 1011 |
| 4 | 0100 | 12 | 1100 |
| 5 | 0101 | 13 | 1101 |
| 6 | 0110 | 14 | 1110 |
| 7 | 0111 | 15 | 1111 |

## Common Misconceptions

**"Binary numbers are bigger (more digits) so they must represent larger values."**
The number of digits tells you nothing without knowing the base. `1111` in binary = 15 in decimal. The *base* is what matters.

**"Computers work with binary internally; the programming language also works with binary."**
Programming languages work with human-friendly abstractions (integers, strings, floats). The binary representation is created automatically by the compiler or interpreter. You rarely need to think in binary while coding—but understanding it helps you understand limits (e.g., why Python integers don't overflow).

**"A kilobyte is 1,000 bytes."**
In the context of RAM and file systems, a kilobyte is traditionally 1,024 bytes. The IEC introduced "kibibyte" (KiB) for 1,024 bytes vs "kilobyte" (KB) for 1,000, but the traditional usage persists.

## Key Takeaways

- Computers use binary because transistors have only two reliable electrical states: on (1) and off (0).
- Each binary digit is a **bit**; 8 bits make a **byte**; a byte holds 256 possible values.
- Converting binary → decimal: sum powers of 2 at every position where the bit is 1.
- Converting decimal → binary: divide by 2 repeatedly; read remainders bottom to top.
- Binary addition carries just like decimal—1+1 gives a sum of 0 with a carry of 1.
