# Custom Exception Hierarchy

## Problem Statement

Define a custom exception hierarchy and write a `process(cmd)` function that raises the appropriate exception.

**Exception classes to define:**

- `AppError(Exception)` — base exception (accepts a message string)
- `ValidationError(AppError)` — raised when input fails validation
- `NotFoundError(AppError)` — raised when a command is not recognized

**Function to implement:**

```python
def process(cmd: str) -> str:
    ...
```

Rules for `process`:

1. If `cmd` is an empty string, raise `ValidationError("empty input")`.
2. If `cmd` is not one of `"start"`, `"stop"`, `"status"`, raise `NotFoundError(f"unknown: {cmd}")`.
3. Otherwise return `f"OK: {cmd}"`.

**Input format:**

Read lines from stdin until EOF. Each line (after stripping the newline) is passed to `process(cmd)`.

- A line that was originally blank in the input becomes an empty string after stripping `\n` — this should trigger `ValidationError`.

**Output format:**

For each line, print either:
- The string returned by `process(cmd)` on success, or
- `<ExceptionClassName>: <message>` on failure (using `type(e).__name__`)

## Examples

**Example 1**

Input (the third line is blank):
```
start
hello

stop
status
```

Output:
```
OK: start
NotFoundError: unknown: hello
ValidationError: empty input
OK: stop
OK: status
```

**Example 2**

Input:
```
status
stop
start
```

Output:
```
OK: status
OK: stop
OK: start
```

**Example 3**

Input (blank line only):
```

```

Output:
```
ValidationError: empty input
```

**Example 4**

Input:
```
run
jump
start
```

Output:
```
NotFoundError: unknown: run
NotFoundError: unknown: jump
OK: start
```

## Constraints

- Number of input lines: 1 – 100
- Lines may be blank (representing empty commands)
- You must catch at the `AppError` level (catching parent catches all subclasses)
