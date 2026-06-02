# Exercise: Apply Write-1-to-Clear Register Semantics

## Problem Description

Simulate a 32-bit W1C (Write-1-to-Clear) Interrupt Status Register (ISR) subject to a sequence of hardware events and firmware writes.

Rules:
- The ISR starts at `0x00000000`.
- `HW_SET <hex_mask>`: hardware ORs the mask into ISR — `isr |= mask`.
- `FW_WRITE <hex_value>`: firmware writes the value using W1C semantics — bits in ISR where the written value has a 1 are cleared: `isr &= ~written_value`.

After each operation, print the current ISR value.

## Input Format

```
Line 1: N   (number of operations, 1 <= N <= 1000)
Lines 2..N+1: one operation per line:
    HW_SET <hex_value>
    or
    FW_WRITE <hex_value>
```

Hex values are given with the `0x` prefix and represent unsigned 32-bit integers.

## Output Format

N lines, one per operation. Each line is the ISR value after that operation, printed as lowercase hexadecimal with `0x` prefix and exactly 8 hex digits (zero-padded). Example: `0x00000006`.

## Constraints

- 1 <= N <= 1000
- All hex values are valid 32-bit unsigned integers
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
4
HW_SET 0x00000005
HW_SET 0x00000003
FW_WRITE 0x00000001
FW_WRITE 0x00000006
```

## Sample Output

```
0x00000005
0x00000007
0x00000006
0x00000000
```

## Explanation

- After `HW_SET 0x5`: ISR = 0 | 0x5 = 0x5.
- After `HW_SET 0x3`: ISR = 0x5 | 0x3 = 0x7.
- After `FW_WRITE 0x1`: ISR = 0x7 & ~0x1 = 0x7 & 0xFFFFFFFE = 0x6.
- After `FW_WRITE 0x6`: ISR = 0x6 & ~0x6 = 0x6 & 0xFFFFFFF9 = 0x0.

## Additional Test Cases

**Test 2 — FW writes 0 (no bits cleared):**
```
3
HW_SET 0x000000ff
FW_WRITE 0x00000000
HW_SET 0x00000001
```
Expected:
```
0x000000ff
0x000000ff
0x000000ff
```

**Test 3 — Firmware clears only some bits:**
```
2
HW_SET 0xffffffff
FW_WRITE 0x0000ffff
```
Expected:
```
0xffffffff
0xffff0000
```

**Test 4 — Interleaved HW and FW:**
```
5
HW_SET 0x00000010
HW_SET 0x00000020
FW_WRITE 0x00000010
HW_SET 0x00000001
FW_WRITE 0xffffffff
```
Expected:
```
0x00000010
0x00000030
0x00000020
0x00000021
0x00000000
```
