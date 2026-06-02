# Exercise: Pack and Unpack Status Flags Into a Byte

In this exercise you will implement both directions of bit-flag encoding — the same operations a kernel uses when storing process status, CPU flags, or device register states in a compact byte.

## What You Will Implement

You will read a sequence of named flag operations and apply them to a single-byte status register, then report the final value and the state of each individual flag.

## The Status Byte Layout

The byte has 4 named flags in its lower 4 bits:

| Bit | Name | Meaning |
|---|---|---|
| 0 (LSB) | `READY` | Process is ready to run |
| 1 | `BLOCKED` | Process is waiting on I/O |
| 2 | `ERROR` | An error occurred |
| 3 | `DONE` | Process has finished |
| 4–7 | (reserved) | Always 0 |

## Skills Practiced

- Setting bits with OR and a mask
- Clearing bits with AND and an inverted mask
- Toggling bits with XOR
- Reading individual flag states from a packed byte

## Approach

```python
READY   = 1 << 0  # 0b00000001
BLOCKED = 1 << 1  # 0b00000010
ERROR   = 1 << 2  # 0b00000100
DONE    = 1 << 3  # 0b00001000

status = 0

# Set READY:   status |= READY
# Clear READY: status &= ~READY
# Toggle DONE: status ^= DONE
# Test READY:  bool(status & READY)
```

## Your Task

Read operations from standard input, apply them to a byte register, and output the final register value and the individual flag states. See the prompt file for the complete input/output specification and sample cases.
