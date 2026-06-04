# Stack Operations

Implement a stack data structure using a Python list and process a series of commands from standard input.

Supported commands (one per line, read until EOF):

| Command       | Behaviour |
|---------------|-----------|
| `PUSH <value>`| Push the integer `<value>` onto the stack. Produces no output. |
| `POP`         | Remove and print the top value. If the stack is empty, print `Empty`. |
| `PEEK`        | Print the top value without removing it. If empty, print `Empty`. |
| `SIZE`        | Print the number of elements currently on the stack. |

## Input

Multiple lines, each containing one command. Input ends at EOF.

## Output

One line of output for each `POP`, `PEEK`, or `SIZE` command, in order.

## Example

**Input:**
```
PUSH 5
PUSH 3
PEEK
POP
SIZE
POP
POP
```

**Output:**
```
3
3
1
5
Empty
```

## Hints

- Use a Python list and its `append()` / `pop()` methods.
- To read until EOF: `import sys; for line in sys.stdin:`
- Check `if not self._data:` to detect an empty stack.
- The `SIZE` command prints `len(self._data)`, not the top value.
