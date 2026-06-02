# Exercise: Decode Device Register Fields From a Memory-Mapped Value

Device registers pack multiple fields into a single 32-bit (or 64-bit) word. Every embedded and systems driver developer must be comfortable extracting those fields with bitwise masking and shifting. This exercise gives you a realistic register layout and asks you to decode it.

## Background

Real hardware datasheets describe registers like this:

```
STATUS_REG (offset 0x04) — 32-bit read-only
  [31:16]  ERROR_CODE    — 16-bit error code (0 = no error)
  [15:12]  SPEED         — link speed: 0=10M, 1=100M, 2=1G, 3=10G
  [11:8]   CHANNEL       — DMA channel number (0–15)
  [7:4]    RESERVED      — ignore
  [3]      FULL_DUPLEX   — 1 if full duplex, 0 if half
  [2]      LINK_UP       — 1 if link is established
  [1]      TX_BUSY       — 1 if transmit DMA in progress
  [0]      RX_BUSY       — 1 if receive DMA in progress
```

To extract a field from a 32-bit register value `v`:

```python
def extract(v, msb, lsb):
    width = msb - lsb + 1
    mask = (1 << width) - 1
    return (v >> lsb) & mask
```

## What You Will Implement

Write a Python program that:

1. Reads one line from stdin: a single 32-bit register value as a hexadecimal string (e.g., `0x1A2B0432`).
2. Decodes the following fields using bit manipulation:
   - `ERROR_CODE` bits [31:16]
   - `SPEED` bits [15:12]
   - `CHANNEL` bits [11:8]
   - `FULL_DUPLEX` bit [3]
   - `LINK_UP` bit [2]
   - `TX_BUSY` bit [1]
   - `RX_BUSY` bit [0]
3. Prints each field on its own line in the format `FIELD_NAME=<decimal value>`, in the order listed above.

No external libraries needed — use only Python's built-in `int(s, 16)` for hex parsing and bitwise operators.

## Example

Input:
```
0x00000207
```

Output:
```
ERROR_CODE=0
SPEED=0
CHANNEL=2
FULL_DUPLEX=0
LINK_UP=1
TX_BUSY=1
RX_BUSY=1
```

Work through the math yourself before running — that is the skill being practiced.
