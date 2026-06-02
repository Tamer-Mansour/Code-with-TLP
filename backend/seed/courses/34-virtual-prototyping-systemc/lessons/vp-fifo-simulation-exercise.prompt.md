# Exercise: Simulate a UART FIFO with Overflow Detection

## Problem Description

Simulate a bounded FIFO queue that models the TX or RX FIFO in a 16550-style UART. Process a sequence of operations and report results after each one.

## Input Format

```
Line 1: N D
  N = number of operations (1 ≤ N ≤ 100)
  D = FIFO depth (1 ≤ D ≤ 16)

Lines 2 .. N+1: one operation per line, one of:
  PUSH V     where V is an integer byte value (0-255)
  POP
  STATUS
```

## Output Format

For each operation, print exactly one line:

- `PUSH V`: 
  - If FIFO was not full: `OK <new_size>`
  - If FIFO was full (overflow): `OVERFLOW`

- `POP`:
  - If FIFO was not empty: `OK <value>`  (the byte that was removed)
  - If FIFO was empty (underflow): `UNDERFLOW`

- `STATUS`:
  - Print `SIZE <current_size> DEPTH <D> <STATE>` where `<STATE>` is one of:
    - `EMPTY` if current_size == 0
    - `FULL` if current_size == D
    - `PARTIAL` otherwise

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ D ≤ 16
- 0 ≤ V ≤ 255
- Byte values are decimal integers

## Sample Input

```
7 4
PUSH 65
PUSH 66
PUSH 67
PUSH 68
PUSH 99
STATUS
POP
```

## Sample Output

```
OK 1
OK 2
OK 3
OK 4
OVERFLOW
SIZE 4 DEPTH 4 FULL
OK 65
```

### Explanation

- PUSH 65: FIFO was empty, size becomes 1 → `OK 1`
- PUSH 66: size becomes 2 → `OK 2`
- PUSH 67: size becomes 3 → `OK 3`
- PUSH 68: size becomes 4 (now full) → `OK 4`
- PUSH 99: FIFO is full → `OVERFLOW`
- STATUS: size=4, depth=4, state=FULL → `SIZE 4 DEPTH 4 FULL`
- POP: removes front byte (65, FIFO order) → `OK 65`
