# Bitwise AND, OR, XOR, NOT, Shifts

Bitwise operators are the primitive vocabulary of register manipulation. Every read-modify-write cycle on hardware is composed from exactly these operations.

## The Six Operators

| Operator | C symbol | Truth table key | Typical use |
|----------|----------|-----------------|-------------|
| AND | `&` | 1 only if both inputs are 1 | Clear bits, mask |
| OR | `\|` | 1 if either input is 1 | Set bits |
| XOR | `^` | 1 if inputs differ | Toggle bits |
| NOT (bitwise) | `~` | Invert every bit | Create complement mask |
| Left shift | `<<` | Move bits toward MSB | Multiply by 2^n, position a field |
| Right shift | `>>` | Move bits toward LSB | Divide by 2^n, extract a field |

## AND — Clear Bits and Masking

```cpp
uint8_t reg = 0b1011'1110;
uint8_t mask = 0b0000'1111;   // keep low nibble
uint8_t low  = reg & mask;    // 0b0000'1110 = 0x0E
```

To **clear** bit N: `reg &= ~(1u << N);`

## OR — Set Bits

```cpp
uint32_t cr = read32(CR_ADDR);
cr |= (1u << 5);               // set bit 5
write32(CR_ADDR, cr);
```

OR cannot clear a bit — it can only drive 0-bits to 1.

## XOR — Toggle Bits

```cpp
uint8_t led = 0b0000'0001;
led ^= 0b0000'0001;            // toggle bit 0 → 0b0000'0000
led ^= 0b0000'0001;            // toggle again  → 0b0000'0001
```

XOR with itself yields 0 — a fast way to zero a register or detect equality without branching: `if ((a ^ b) == 0)` means `a == b`.

## NOT — Bitwise Complement

```cpp
uint8_t mask = ~0b0000'1111;   // becomes 0b1111'0000
```

> **Pitfall:** `~1` on a 32-bit `int` produces `0xFFFFFFFE`, not `0xFE`. Always cast to the intended width or use `~(uint8_t)1` to avoid surprises with implicit integer promotions.

## Shift Operators

### Left Shift `<<`

Shifts bits toward higher positions; vacated low bits become 0.

```cpp
uint32_t field = 0x3u;
uint32_t positioned = field << 8;   // 0x00000300 — field now in bits 9:8
```

Left shift by N is equivalent to multiplication by 2^N (for unsigned values).

### Right Shift `>>`

Shifts bits toward lower positions; for **unsigned** types vacated high bits become 0 (logical shift). For **signed** types the behaviour is implementation-defined — most compilers perform arithmetic shift (replicate sign bit), but this is not guaranteed by the standard.

```cpp
uint32_t val  = 0x0000'0300u;
uint32_t out  = val >> 8;           // 0x00000003 — extracted field
```

> **Pitfall:** Always right-shift **unsigned** values when extracting fields. Shifting signed values right is non-portable.

## Operator Precedence Trap

In C/C++, bitwise operators have lower precedence than comparison (`==`, `!=`). This produces a notorious bug:

```cpp
// WRONG — reads as: reg & (1 == 0)
if (reg & 1 == 0) { ... }

// CORRECT — parenthesise the bitwise expression
if ((reg & 1) == 0) { ... }
```

Always parenthesise bitwise sub-expressions.

## Worked Example — Constructing a Control Word

A peripheral expects a 32-bit control register with:
- Bits 1:0 = mode (2 bits)
- Bits 5:2 = prescaler (4 bits)
- Bit 7 = enable

```cpp
uint32_t make_ctrl(uint8_t mode, uint8_t prescaler, bool enable) {
    uint32_t val = 0;
    val |= (mode      & 0x3u);          // bits 1:0
    val |= ((prescaler & 0xFu) << 2);   // bits 5:2
    val |= ((enable ? 1u : 0u)   << 7); // bit 7
    return val;
}
// make_ctrl(2, 5, true) → 0b1001_0110 = 0x96
```

## Compound Assignment Shortcuts

```cpp
reg &= mask;    // reg = reg & mask
reg |= mask;    // reg = reg | mask
reg ^= mask;    // reg = reg ^ mask
reg <<= n;      // reg = reg << n
reg >>= n;      // reg = reg >> n
```

**Interview answer:** "AND clears bits, OR sets bits, XOR toggles bits. Shifts position fields. I always parenthesise bitwise expressions and shift unsigned types to avoid undefined or implementation-defined behaviour."
