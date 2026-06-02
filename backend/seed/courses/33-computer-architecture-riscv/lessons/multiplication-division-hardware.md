# Hardware Multiplication and Division

Multiplication and division are orders of magnitude more complex than addition. Understanding their hardware trade-offs explains why CPUs historically had separate multiply/divide units and why these operations still have higher latency than ADD.

## Why Multiplication is Hard

Multiplying two N-bit numbers produces a 2N-bit result. For 32×32 bits, the full product is 64 bits wide. The naive schoolbook approach requires N additions of shifted partial products — that is O(N) additions, each of N bits. For N=32 this means 32 32-bit additions: far too slow for a single-cycle datapath.

## Schoolbook (Shift-and-Add) Algorithm

The hardware analogue of long multiplication:

```
Multiply A × B:
  product = 0
  for i in 0..N-1:
      if B[i] == 1:
          product += A << i
```

Each step checks one bit of the multiplier B. If that bit is 1, it adds a shifted version of A into the running product. With N=32, this takes up to 32 additions.

```python
def multiply_unsigned(a, b, bits=8):
    """Shift-and-add multiplication, unsigned."""
    product = 0
    for i in range(bits):
        if (b >> i) & 1:
            product += a << i
    return product

print(multiply_unsigned(13, 11))  # 143
```

## Booth's Algorithm (Signed Multiplication)

Booth's algorithm handles signed two's complement multiplication and reduces the number of additions by encoding runs of 1-bits in the multiplier. A run of k ones (e.g., `0111100`) becomes `+1 shift` at the start and `-1 shift` at the end, replacing k additions with 2 operations.

Modified Booth encoding (Booth-2) examines 2 bits at a time, approximately halving the number of partial products. This is the basis of most hardware multipliers.

| Bits examined | Operation |
|---------------|-----------|
| 00 | +0 (skip) |
| 01 | +A |
| 10 | -A |
| 11 | +0 (skip) |

## Wallace Tree Multiplier

Instead of adding partial products sequentially, a **Wallace tree** uses a tree of carry-save adders (CSA) to reduce all N partial products to just two numbers in O(log N) depth, then finishes with a single fast adder.

```
N partial products
  → Round 1 CSA: N → ceil(2N/3) results
  → Round 2 CSA: ceil(2N/3) → ceil(4N/9) results
  ...
  → 2 numbers remaining
  → Final carry-propagate adder (CLA)
```

A Wallace tree 32-bit multiplier typically completes in 6-8 gate delays — versus 32+ for shift-and-add.

## RISC-V Multiplication Instructions

RISC-V's M extension adds dedicated multiply/divide instructions:

| Instruction | Operation | Result |
|-------------|-----------|--------|
| `MUL rd,rs1,rs2` | Signed × Signed | Lower 32 bits |
| `MULH rd,rs1,rs2` | Signed × Signed | Upper 32 bits |
| `MULHU rd,rs1,rs2` | Unsigned × Unsigned | Upper 32 bits |
| `MULHSU rd,rs1,rs2` | Signed × Unsigned | Upper 32 bits |
| `DIV rd,rs1,rs2` | Signed divide | Quotient |
| `DIVU rd,rs1,rs2` | Unsigned divide | Quotient |
| `REM rd,rs1,rs2` | Signed remainder | Remainder |
| `REMU rd,rs1,rs2` | Unsigned remainder | Remainder |

```asm
# 64-bit product of two 32-bit signed integers
mul  t0, a0, a1     # t0 = lower 32 bits of a0 × a1
mulh t1, a0, a1     # t1 = upper 32 bits of a0 × a1
# full 64-bit result is in {t1, t0}
```

## Division Hardware

Division is even harder than multiplication and is typically implemented with **restoring** or **non-restoring** iterative algorithms, or SRT (Sweeney-Robertson-Tocher) division for higher-performance implementations.

A basic restoring divider works like long division:

```
Divide A by B:
  remainder = A
  quotient  = 0
  for i from N-1 down to 0:
      remainder = remainder - (B << i)
      if remainder >= 0:
          quotient |= (1 << i)
      else:
          remainder += (B << i)   # restore
```

This takes O(N) iterations, each requiring a subtraction and a comparison. A 32-bit divider needs 32 cycles — typical hardware divide latency is 20-80 cycles.

## Latency Comparison

| Operation | Typical latency (modern CPU) |
|-----------|------------------------------|
| ADD / SUB | 1 cycle |
| Shift | 1 cycle |
| MUL (32-bit) | 3-5 cycles |
| DIV (32-bit) | 20-80 cycles |

## Common Pitfalls

- **Integer overflow on multiply**: two 32-bit values can produce a 64-bit result. Using only the lower 32 bits silently drops the upper half — always use `MULH` when the product might overflow.
- **Division by zero**: RISC-V specifies that `DIV x, x, zero` returns `-1` (all ones) for quotient and the dividend for remainder; x86 generates a fault. Always check the divisor.
- **Signed vs. unsigned**: mixing `MUL` and `MULHU` for the upper bits gives the wrong answer. Use `MULH` for signed × signed, `MULHU` for unsigned × unsigned.

> **Interview answer:** Hardware multipliers use Wallace trees (carry-save adder trees) to reduce N partial products to two values in O(log N) time before a final fast adder; division is inherently sequential — most hardware dividers iterate one bit per cycle, giving 20-80 cycle latency versus 1 cycle for addition.
