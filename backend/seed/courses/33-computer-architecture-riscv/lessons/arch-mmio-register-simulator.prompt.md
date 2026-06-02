# Exercise Prompt: Simulate Reads/Writes to an MMIO Register Map

## Background

You are building a software simulator for a minimal UART peripheral modelled as a set of 32-bit memory-mapped registers. The simulator processes a sequence of register operations and produces output that mirrors what a real UART driver would observe.

## Register Map

| Offset | Name | Description |
|---|---|---|
| 0 | TXDATA | Write: queue a TX byte (low 8 bits). Read: always returns 0. |
| 4 | TXSTATUS | Bit 0 = TX ready flag. Starts as 1. Clears to 0 after a TXDATA write; restores to 1 before the next operation is processed. |
| 8 | RXDATA | Read: returns next pre-loaded RX byte in bits 7:0; sets bit 31 (RX empty flag) if no more RX data. Write: ignored. |
| 12 | IE | Interrupt Enable. Simple R/W register, initial value 0. |
| 16 | ISTAT | Interrupt Status. Write-1-to-clear: writing a value clears only the bits that are 1 in the written value. Initial value 0. |

TXSTATUS detail: After processing a WRITE to offset 0, the TX ready flag is 0. Before processing the *next* operation (of any kind), it automatically restores to 1.

## Input Format

Line 1: `R <rx_bytes_space_separated>` — the pre-loaded receive bytes as a sequence of integers (0–255), or `R` with nothing after it for an empty RX FIFO.

Lines 2..N: one operation per line, either:
- `W <offset> <value>` — write `value` (unsigned 32-bit integer) to register at `offset`
- `READ <offset>` — read the register at `offset`; print its 32-bit value

Offsets are always one of: 0, 4, 8, 12, 16.

## Output Format

For every `READ` operation: print the 32-bit register value as a decimal integer on its own line.
For every `W` to offset 0 (TXDATA): print `TX:<char>` where `<char>` is the ASCII character corresponding to the low 8 bits of the written value.
No output for writes to offsets 4, 8, 12, 16.

## Constraints

- At most 200 operations.
- RX buffer has at most 64 pre-loaded bytes.
- All values fit in unsigned 32-bit integers.
- Offsets are always valid (0, 4, 8, 12, 16).

## Sample

### Input
```
R 72 101 108 108 111
W 0 65
READ 4
W 0 66
READ 4
READ 8
READ 8
READ 8
W 12 3
READ 12
W 16 5
READ 16
```

### Expected Output
```
TX:A
1
TX:B
1
72
101
108
3
0
```

### Explanation

- `R 72 101 108 108 111` — RX FIFO pre-loaded with bytes for 'H','e','l','l','o'.
- `W 0 65` — write 'A' (65) to TXDATA → prints `TX:A`. TXSTATUS bit 0 clears.
- `READ 4` — before this read the TX ready flag auto-restores to 1 → prints `1`.
- `W 0 66` — write 'B' (66) → prints `TX:B`. TXSTATUS bit 0 clears.
- `READ 4` — auto-restores to 1 → prints `1`.
- `READ 8` — returns 72 ('H'), the first RX byte.
- `READ 8` — returns 101 ('e').
- `READ 8` — returns 108 ('l').
- `W 12 3` — writes 3 to IE register.
- `READ 12` — returns 3.
- `W 16 5` — ISTAT W1C: clears bits 0 and 2 (value 5 = 0b101). ISTAT was 0, so it stays 0.
- `READ 16` — returns 0.
