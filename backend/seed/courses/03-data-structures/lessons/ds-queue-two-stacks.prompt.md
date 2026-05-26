# Queue via Two Stacks

Implement a **FIFO queue** using only two Python lists (`inbox` and `outbox`) that may only use `list.append()` and `list.pop()` (no `pop(0)`, no `deque`, no `insert`).

## Operations

- `ENQUEUE x` — add integer `x` to the back of the queue.
- `DEQUEUE` — remove and print the front element. If the queue is empty, print `EMPTY`.
- `FRONT` — print the front element without removing it. If the queue is empty, print `EMPTY`.

## Input Format

```
Q
op1
op2
...
```

- Line 1: integer Q — number of operations.
- Lines 2..Q+1: one operation per line. `ENQUEUE` lines have the format `ENQUEUE x` where x is an integer. `DEQUEUE` and `FRONT` lines are single words.

## Output Format

For each `DEQUEUE` or `FRONT` operation, print one line: the integer value, or `EMPTY`.

## Example

Input:
```
8
ENQUEUE 10
ENQUEUE 20
FRONT
DEQUEUE
DEQUEUE
DEQUEUE
ENQUEUE 5
FRONT
```

Output:
```
10
10
20
EMPTY
5
```
