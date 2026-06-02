# Count Set Bits (Population Count)

Counting the number of 1-bits in an integer — the **population count** or **popcount** — is a surprisingly useful operation in hardware modeling. It appears in parity checking, Hamming weight calculations, arbitration logic, and interrupt priority encoding.

## What You Will Implement

Your program reads a series of 32-bit unsigned integers and prints the number of set bits (1s) in each one.

## Why This Matters

- **Parity generation/checking:** even or odd parity is determined by `popcount(data) % 2`.
- **Interrupt mask weight:** "how many interrupts are currently pending?" is a popcount question.
- **Performance counters:** hardware performance monitor units expose event counts as bitmaps; popcount converts to a scalar.

## Algorithms to Know

### Algorithm 1 — Brian Kernighan's bit-clearing trick

Each iteration clears the lowest set bit using `n &= (n - 1)`. The loop runs exactly as many times as there are set bits.

```python
def popcount(n):
    count = 0
    while n:
        n &= n - 1   # drop the lowest set bit
        count += 1
    return count
```

Time complexity: O(set bits) — fast when the number is sparse.

### Algorithm 2 — Shift and count (naïve)

```python
def popcount_naive(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count
```

Always runs 32 iterations for a 32-bit value — slower for sparse inputs.

### Algorithm 3 — Parallel prefix (SWAR)

This divide-and-conquer approach works in O(log W) steps and is the basis of hardware popcount instructions.

```python
def popcount_swar32(n):
    n = n - ((n >> 1) & 0x55555555)
    n = (n & 0x33333333) + ((n >> 2) & 0x33333333)
    n = (n + (n >> 4)) & 0x0F0F0F0F
    n = (n * 0x01010101) & 0xFFFFFFFF
    return n >> 24
```

This is the algorithm CPUs implement in their `POPCNT` instruction (x86) and `CNT` (ARM NEON).

## Input Format

- Line 1: integer T — number of values
- Next T lines: one 32-bit unsigned integer per line (0 ≤ value ≤ 4294967295)

## Output Format

T lines, each containing the popcount of the corresponding input value.

## Example

Input:
```
4
0
255
4294967295
305419896
```

Output:
```
0
8
32
13
```

Verification:
- `0` has 0 set bits.
- `255 = 0xFF = 0b1111_1111` has 8 set bits.
- `4294967295 = 0xFFFFFFFF` has 32 set bits.
- `305419896 = 0x12345678` → count 1s in `0001 0010 0011 0100 0101 0110 0111 1000` = 13 set bits.
