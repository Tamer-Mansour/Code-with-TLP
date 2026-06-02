# How Subtraction Works in the ALU

Modern ALUs do not contain a separate subtraction circuit. Instead, they reuse the adder hardware and exploit a clever property of **two's complement** representation: subtraction can be performed as addition.

## Two's Complement Refresher

In two's complement, the negative of a number `n` is computed as:

```
-n = ~n + 1     (bitwise NOT, then add 1)
```

This means `A - B = A + (-B) = A + (~B + 1) = A + ~B + 1`.

The "+1" comes from setting the carry-in of the adder to 1 instead of 0. No extra hardware is needed.

## The ALU Adder/Subtractor Circuit

A single adder block handles both ADD and SUB using one control bit (`Sub`):

```
Operand going into adder:
  If Sub=0  →  B enters unchanged,          Cin = 0   → computes A + B
  If Sub=1  →  B is bitwise inverted (~B),  Cin = 1   → computes A + ~B + 1 = A - B
```

The XOR trick achieves the conditional inversion cheaply: `B_in[i] = B[i] XOR Sub`. When `Sub=0`, `B_in[i] = B[i]` (unchanged). When `Sub=1`, `B_in[i] = ~B[i]` (inverted).

```
For each bit i:
  B_modified[i] = B[i] XOR Sub
  (A[i], B_modified[i], Cin=Sub) → Full Adder → Sum[i], Cout[i]
```

## RISC-V Implementation

In RISC-V, `ADD` and `SUB` are encoded in the R-type format. They share `funct3 = 000` and differ only in bit 5 of `funct7`:

| Instruction | funct7[5] | Operation |
|-------------|-----------|-----------|
| ADD rd,rs1,rs2 | 0 | rd = rs1 + rs2 |
| SUB rd,rs1,rs2 | 1 | rd = rs1 - rs2 |

The ALU control unit routes `funct7[5]` directly to the `Sub` input of the adder/subtractor.

```asm
# RISC-V subtraction example
# t0 = 10, t1 = 3, t2 = t0 - t1 = 7
addi t0, zero, 10
addi t1, zero, 3
sub  t2, t0, t1      # t2 = 7
```

## Worked Example: 8-bit Subtraction

Compute 9 - 5 in 8-bit two's complement:

```
A =  9  → 0000_1001
B =  5  → 0000_0101

Step 1: Invert B    → ~B = 1111_1010
Step 2: Add A + ~B  →  0000_1001
                     + 1111_1010
                     ----------
                       0000_0011  (with Cin=0, partial sum)

Step 3: Add Cin=1  →  0000_0011 + 1 = 0000_0100 = 4  ✓
```

The carry-in of 1 is what completes the two's complement negation of B.

## Detecting Unsigned vs. Signed Results

After subtraction, two flags are relevant:

- **Carry flag (unsigned borrow)**: In subtraction, `Cout=0` after `A + ~B + 1` means a **borrow** occurred (A < B unsigned). Some architectures invert this; check your ISA specification.
- **Overflow flag (signed)**: Overflow if the carry into the sign bit differs from the carry out of the sign bit. E.g., subtracting a negative number from a positive number that wraps into negative territory.

```python
def alu_sub_8bit(a, b):
    """Simulate 8-bit ALU subtraction using adder trick."""
    b_inv = (~b) & 0xFF          # bitwise NOT, masked to 8 bits
    result_full = a + b_inv + 1  # add with carry-in = 1
    result = result_full & 0xFF  # keep 8 bits
    carry = (result_full >> 8) & 1
    # For subtraction: borrow = NOT carry
    borrow = 1 - carry
    zero = 1 if result == 0 else 0
    return result, borrow, zero

print(alu_sub_8bit(9, 5))   # (4, 0, 0) — no borrow, not zero
print(alu_sub_8bit(3, 5))   # (254, 1, 0) — borrow occurred (unsigned underflow)
```

## Common Pitfalls

- **Borrow vs. carry convention**: some ISAs set the carry flag on unsigned underflow (borrow), others clear it. RISC-V does not have a flags register — comparisons use dedicated `SLT`/`SLTU` instructions.
- **Signed vs. unsigned comparison**: `SUB` + sign check gives signed comparison; `SUBU` + carry gives unsigned comparison. Mixing them is a classic bug.
- **Two's complement edge case**: the minimum signed value (e.g., `-128` for 8-bit) has no positive counterpart — negating it overflows back to itself.

> **Interview answer:** The ALU performs subtraction by inverting the second operand and setting carry-in to 1, which computes A + (~B) + 1 = A - B using the two's complement identity — no separate subtractor circuit is needed.
