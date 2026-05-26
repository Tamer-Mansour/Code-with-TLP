# Stack Command Processor

Implement a `Stack` class and process a sequence of commands from standard input.

## Commands

- `PUSH <value>` — push the integer `value` onto the top of the stack
- `POP` — remove and print the top element; if the stack is empty, print `EMPTY`
- `PEEK` — print the top element without removing it; if the stack is empty, print `EMPTY`
- `SIZE` — print the number of elements currently in the stack

## Input Format

The first line is an integer `N` — the number of commands.
The next `N` lines each contain one command.

## Output Format

- `POP`: print the popped value, or `EMPTY` if the stack was empty.
- `PEEK`: print the top value, or `EMPTY` if the stack is empty.
- `SIZE`: print the integer count.
- `PUSH`: no output.

## Example

**Input:**
```
7
PUSH 10
PUSH 20
PEEK
SIZE
POP
POP
POP
```

**Output:**
```
20
2
20
10
EMPTY
```
