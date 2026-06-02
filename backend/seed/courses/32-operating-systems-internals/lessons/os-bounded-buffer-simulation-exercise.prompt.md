# Prompt: Simulate a Bounded Buffer From an Operation Trace

## Problem Description

Simulate a bounded circular buffer given a capacity and a sequence of producer/consumer operations. After each operation print the result and the current buffer contents.

## Input Format

```
Line 1: N          (integer, 1 <= N <= 20, buffer capacity)
Line 2: K          (integer, 1 <= K <= 100, number of operations)
Lines 3..K+2: one operation per line, either:
    PRODUCE <value>   (value is a positive integer)
    CONSUME
```

## Output Format

For each operation, print exactly one line:

- `PRODUCE <value>`: 
  - If buffer is full: `FULL`
  - Otherwise: `PRODUCED <value> [<item1> <item2> ...]`
    where items are listed oldest-first (head to tail order).

- `CONSUME`:
  - If buffer is empty: `EMPTY`
  - Otherwise: `CONSUMED <value> [<item1> <item2> ...]`
    where `<value>` is the item removed and items are the remaining contents oldest-first.

If the buffer is empty after an operation, print `[]` for the contents portion.

## Constraints

- `1 <= N <= 20`
- `1 <= K <= 100`
- Values in `PRODUCE` are positive integers in range `[1, 1000]`
- Use a circular buffer with FIFO semantics (oldest item consumed first)

## Sample Input 1

```
3
6
PRODUCE 10
PRODUCE 20
PRODUCE 30
PRODUCE 40
CONSUME
CONSUME
```

## Sample Output 1

```
PRODUCED 10 [10]
PRODUCED 20 [10 20]
PRODUCED 30 [10 20 30]
FULL
CONSUMED 10 [20 30]
CONSUMED 20 [30]
```

## Sample Input 2

```
2
4
CONSUME
PRODUCE 5
CONSUME
CONSUME
```

## Sample Output 2

```
EMPTY
PRODUCED 5 [5]
CONSUMED 5 []
EMPTY
```

## Notes

- The buffer is circular: after filling slot N-1 the next write goes to slot 0 (if free).
- Track item count separately to distinguish full from empty (do not rely on head == tail alone).
- All output tokens on a line are separated by a single space. The bracket list uses spaces between items but no spaces inside the brackets adjacent to items.
