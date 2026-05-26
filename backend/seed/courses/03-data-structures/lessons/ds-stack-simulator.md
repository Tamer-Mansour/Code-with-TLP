# Exercise: Stack Simulator

Process a sequence of PUSH, POP, and TOP commands and produce the correct output for each query command.

## Approach

Maintain a Python list as the backing store.

- `PUSH x`: `stack.append(x)`
- `POP`: `stack.pop()` if non-empty, else print `"EMPTY"`
- `TOP`: `stack[-1]` if non-empty, else print `"EMPTY"`
