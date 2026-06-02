# Prompt: Decode Device Register Fields From a Memory-Mapped Value

## Problem Statement

A memory-mapped device exposes a 32-bit STATUS register with the following field layout:

```
Bits [31:16]  ERROR_CODE   — 16-bit unsigned error code
Bits [15:12]  SPEED        — 4-bit link speed indicator
Bits [11:8]   CHANNEL      — 4-bit DMA channel number
Bits [7:4]    RESERVED     — ignore these bits
Bit  [3]      FULL_DUPLEX  — 1-bit flag
Bit  [2]      LINK_UP      — 1-bit flag
Bit  [1]      TX_BUSY      — 1-bit flag
Bit  [0]      RX_BUSY      — 1-bit flag
```

Given a 32-bit register value as a hexadecimal string, decode and print each field.

## Input Format

A single line containing one 32-bit hexadecimal value prefixed with `0x` (e.g., `0x00000207`). The value fits in a 32-bit unsigned integer.

## Output Format

Print exactly 7 lines, each in the format `FIELD_NAME=<decimal value>`, in this exact order:

```
ERROR_CODE=<decimal>
SPEED=<decimal>
CHANNEL=<decimal>
FULL_DUPLEX=<decimal>
LINK_UP=<decimal>
TX_BUSY=<decimal>
RX_BUSY=<decimal>
```

All values are non-negative integers in decimal (no leading zeros, except the value `0` itself).

## Constraints

- Input is always a valid 32-bit hex string in the form `0x[0-9A-Fa-f]{1,8}`.
- No external libraries required; use only Python built-ins.
- `int(s, 16)` correctly parses the input.

## Sample Input 1

```
0x00000207
```

## Sample Output 1

```
ERROR_CODE=0
SPEED=0
CHANNEL=2
FULL_DUPLEX=0
LINK_UP=1
TX_BUSY=1
RX_BUSY=1
```

**Explanation:** `0x00000207` = `0b00000000_00000000_00000010_00000111`
- Bits [31:16] = `0x0000` → ERROR_CODE = 0
- Bits [15:12] = `0b0000` → SPEED = 0
- Bits [11:8]  = `0b0010` → CHANNEL = 2
- Bit  [3]     = `0` → FULL_DUPLEX = 0
- Bit  [2]     = `1` → LINK_UP = 1
- Bit  [1]     = `1` → TX_BUSY = 1
- Bit  [0]     = `1` → RX_BUSY = 1

## Sample Input 2

```
0x00000000
```

## Sample Output 2

```
ERROR_CODE=0
SPEED=0
CHANNEL=0
FULL_DUPLEX=0
LINK_UP=0
TX_BUSY=0
RX_BUSY=0
```

## Hints

Use bitwise AND with a mask to isolate a field, then right-shift to its LSB position:

```python
v = int(input().strip(), 16)
error_code = (v >> 16) & 0xFFFF
speed      = (v >> 12) & 0xF
channel    = (v >>  8) & 0xF
full_duplex= (v >>  3) & 0x1
link_up    = (v >>  2) & 0x1
tx_busy    = (v >>  1) & 0x1
rx_busy    = (v >>  0) & 0x1
```
