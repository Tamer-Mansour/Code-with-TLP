# Exercise: SC_FIFO Bounded Queue Simulation

## Problem Statement

`sc_fifo` is a SystemC primitive channel that models a bounded FIFO queue with blocking read/write semantics. Writes block when the FIFO is full; reads block when it is empty. In a simulation, processes interleave: when a write would block, control passes to another process.

Simulate a simplified single-producer / single-consumer `sc_fifo` of capacity `C`. You are given a sequence of operations: `W <value>` (producer writes) and `R` (consumer reads). If a write is attempted on a full FIFO, mark it as `BLOCKED_WRITE` and skip it (the producer suspends). If a read is attempted on an empty FIFO, mark it as `BLOCKED_READ` and skip it.

Process each operation in the given order. For each:

- `W <value>`: if FIFO not full, enqueue value and print `WRITE <value> -> fifo_size=<new_size>`; else print `BLOCKED_WRITE`
- `R`: if FIFO not empty, dequeue and print `READ <value> -> fifo_size=<new_size>`; else print `BLOCKED_READ`

## Input Format

- First line: `C` (capacity, 1 <= C <= 10)
- Second line: `N` (number of operations, 1 <= N <= 30)
- Next N lines: each `W <value>` or `R`

## Output Format

- N lines, one per operation

## Constraints

- 1 <= C <= 10
- 1 <= N <= 30
- Values are integers

## Sample Input

```
2
6
W 10
W 20
W 30
R
R
R
```

## Sample Output

```
WRITE 10 -> fifo_size=1
WRITE 20 -> fifo_size=2
BLOCKED_WRITE
READ 10 -> fifo_size=1
READ 20 -> fifo_size=0
BLOCKED_READ
```

## Additional Example

Input:
```
3
5
R
W 1
W 2
W 3
W 4
```

Output:
```
BLOCKED_READ
WRITE 1 -> fifo_size=1
WRITE 2 -> fifo_size=2
WRITE 3 -> fifo_size=3
BLOCKED_WRITE
```
