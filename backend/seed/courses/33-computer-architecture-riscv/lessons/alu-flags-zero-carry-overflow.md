# ALU Status Flags: Zero, Carry, Sign, Overflow

Every ALU operation produces more information than just a result. It also sets a group of **status flags** — single bits that record properties of the result. Branch instructions and conditional code depend on these flags to make decisions.

## The Four Core Flags

| Flag | Abbreviation | Meaning |
|------|-------------|---------|
| Zero | Z | Result is all zeros |
| Carry | C | Unsigned carry-out or borrow occurred |
| Sign (Negative) | N or S | Result's most-significant bit (MSB) is 1 |
| Overflow | V or OVF | Signed arithmetic produced an out-of-range result |

## Zero Flag (Z)

The zero flag is set when every bit of the result is 0. Hardware implementation: OR all result bits together, then invert.

```
Z = NOR(Result[N-1], Result[N-2], ..., Result[0])
```

Use cases:
- Equality test: `if (A == B)` → compute `A - B`, branch if Z=1
- Loop counter: `if (counter == 0)` → branch if Z=1

```c
// Compiler translates this to: SUB + branch-if-zero
if (a == b) { ... }
```

## Carry Flag (C)

The carry flag captures the carry-out from the MSB position of an addition, or the inverse-borrow from subtraction.

- **Addition**: C=1 means the result does not fit in N bits (unsigned overflow).
- **Subtraction**: C=0 (borrow) means A < B in unsigned interpretation — conventions vary by ISA.

```
C = Cout[N-1]   (the carry-out of the most-significant full adder)
```

Common uses:
- Multi-word addition: add the lower 32 bits, then `ADC` (add with carry) for the upper 32 bits.
- Unsigned comparison: `A - B` with C=0 (borrow) → A < B unsigned.

```asm
# x86 multi-word 64-bit add using carry flag
add  eax, ecx     ; add lower 32 bits, sets C
adc  edx, esi     ; add upper 32 bits + carry
```

## Sign (Negative) Flag (N)

The sign flag is simply the MSB of the result, copied directly.

```
N = Result[N-1]
```

In two's complement, MSB=1 means the value is negative. Used in signed comparisons:
- After `A - B`, if N=1 and OVF=0, then A < B (signed).
- If N XOR OVF = 1, then A < B (signed, accounting for overflow).

## Overflow Flag (V / OVF)

Overflow occurs when signed arithmetic produces a result outside the representable range. For 8-bit signed integers, the range is -128 to +127.

The hardware rule:
```
OVF = Carry_into_MSB XOR Carry_out_of_MSB
```

In other words, compare the carry entering the sign bit position with the carry leaving it. If they differ, the sign bit was "corrupted" — overflow occurred.

Overflow cases:
- **Positive + Positive = Negative** (result overflowed into sign bit)
- **Negative + Negative = Positive** (result underflowed past minimum)
- Overflow never occurs when adding operands of opposite signs

```python
def add_8bit_with_flags(a, b):
    """Signed 8-bit addition with all four ALU flags."""
    result_full = (a & 0xFF) + (b & 0xFF)
    result = result_full & 0xFF

    carry     = (result_full >> 8) & 1
    zero      = 1 if result == 0 else 0
    sign      = (result >> 7) & 1

    # Overflow: positive+positive=negative or negative+negative=positive
    a_sign = (a >> 7) & 1
    b_sign = (b >> 7) & 1
    r_sign = sign
    overflow = 1 if (a_sign == b_sign) and (r_sign != a_sign) else 0

    return result, {'Z': zero, 'C': carry, 'N': sign, 'V': overflow}

print(add_8bit_with_flags(100, 50))   # overflow: 150 > 127
print(add_8bit_with_flags(200, 100))  # carry: 300 > 255 (unsigned)
print(add_8bit_with_flags(5, -5))     # zero flag set
```

## RISC-V and Flags

RISC-V does **not** have a dedicated flags register. Instead, comparisons are explicit instructions:

| RISC-V instruction | Equivalent flag check |
|--------------------|-----------------------|
| `BEQ rs1, rs2, L` | Jump if rs1 - rs2 sets Z |
| `BLT rs1, rs2, L` | Jump if rs1 < rs2 (signed) |
| `BLTU rs1, rs2, L` | Jump if rs1 < rs2 (unsigned) |
| `SLT rd, rs1, rs2` | rd = 1 if rs1 < rs2 (signed), else 0 |

This is a deliberate design choice: explicit comparisons are simpler to pipeline than flag registers, which create data hazards.

## Flag Combinations for Signed Comparisons

| Condition | Flag expression |
|-----------|----------------|
| A == B | Z = 1 |
| A != B | Z = 0 |
| A < B (signed) | N XOR V = 1 |
| A >= B (signed) | N XOR V = 0 |
| A < B (unsigned) | C = 0 (borrow) |
| A >= B (unsigned) | C = 1 |

## Common Pitfalls

- **Carry and Overflow are independent**: carry is for unsigned; overflow is for signed. Setting carry does not imply overflow and vice versa.
- **RISC-V has no flags register**: code that expects a persistent flag from the previous instruction will fail — RISC-V uses compare-and-branch instructions instead.
- **Overflow on subtraction**: when subtracting, overflow can occur (e.g., -128 - 1 = +127 in 8-bit signed), but it requires the same XOR-of-carries hardware check.

> **Interview answer:** The four ALU flags — Zero (result is 0), Carry (unsigned overflow/borrow), Sign (MSB of result), and Overflow (signed range exceeded, detected by XOR-ing the carries into and out of the sign bit) — are computed combinationally alongside the result and drive all conditional branch decisions.
