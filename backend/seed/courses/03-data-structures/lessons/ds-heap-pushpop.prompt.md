# Min-Heap Push/Pop Sequence

Simulate a min-heap that supports two operations and print the result of each `POP` command.

## Commands

- `PUSH x` — push integer `x` onto the min-heap.
- `POP` — remove and print the minimum element. If the heap is empty print `EMPTY`.

## Input Format

- Line 1: a single integer `q` — the number of commands.
- The next `q` lines: one command per line.

## Output Format

Print one line of output for each `POP` command.

## Constraints

- `1 <= q <= 1000`
- Push values are integers in the range [-10000, 10000].

## Examples

**Example 1**
```
Input:
7
PUSH 5
PUSH 3
PUSH 8
POP
POP
PUSH 1
POP

Output:
3
5
1
```

**Example 2**
```
Input:
3
POP
PUSH 10
POP

Output:
EMPTY
10
```
