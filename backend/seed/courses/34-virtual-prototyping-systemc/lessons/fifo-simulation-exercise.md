# Simulate a UART FIFO with Overflow Detection

In this exercise you will implement a simplified UART FIFO simulator in Python. The simulator reads a sequence of operations from standard input, executes them against a bounded FIFO queue, and reports the state after each operation — including overflow detection when the FIFO is full.

## What You Will Implement

Your program must simulate:

- A FIFO of configurable depth (matching real 16550 hardware: depth of 1 or 16 bytes).
- **PUSH** operations that enqueue a byte value. If the FIFO is already full, the byte is dropped and an overflow error is reported.
- **POP** operations that dequeue the front byte. If the FIFO is empty, report an underflow error.
- **STATUS** queries that print the current fill level and whether the FIFO is empty, partially full, or full.

## Skills Practiced

- Modeling bounded queues with error detection, directly analogous to how a virtual UART model tracks TX and RX FIFO state.
- Updating status flags (LSR-style) after every operation.
- Handling corner cases: overflow (OE bit in LSR), underflow (empty FIFO read), and trigger-level crossing.

## Input Format

See the prompt file `vp-fifo-simulation-exercise.prompt.md` for the full specification, sample input, and expected output.

## Getting Started

Your solution should read all operations from stdin and write results to stdout. No file I/O, no third-party libraries. Use only Python's standard library (`sys`, `collections`, etc.).

```python
import sys
from collections import deque

def solve():
    data = sys.stdin.read().split('\n')
    # TODO: parse depth, then process operations
    pass

solve()
```

Think about how a real UART driver checks LSR before writing to THR. Your FIFO model captures exactly that contract.
