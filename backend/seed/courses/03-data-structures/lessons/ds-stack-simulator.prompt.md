# Stack Simulator

Simulate a stack that supports three commands and print the result of each `TOP` or `POP` command.

## Commands

- `PUSH x` — push integer `x` onto the stack.
- `POP` — remove the top element and print it. If the stack is empty print `EMPTY`.
- `TOP` — print the top element without removing it. If the stack is empty print `EMPTY`.

## Input Format

- Line 1: a single integer `q` — the number of commands.
- The next `q` lines: one command per line.

## Output Format

Print one line of output for each `POP` or `TOP` command.

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
TOP
POP
POP
POP
PUSH 1

Output:
3
3
5
EMPTY
```
