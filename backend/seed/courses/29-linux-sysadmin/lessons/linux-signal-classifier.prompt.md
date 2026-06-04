# Process Signal Classifier

Given a list of POSIX signal numbers, identify each signal by name and determine whether it can be caught or ignored by a process.

## Background

Linux processes communicate via **signals** — asynchronous notifications sent by the kernel or other processes. Most signals can be caught with a custom handler or ignored entirely. Two signals are special: **SIGKILL** and **SIGSTOP** cannot be caught, blocked, or ignored by user-space code. This distinction is critical for writing robust process management scripts.

## Input

- First line: integer `N` — the number of signal numbers to classify.
- Next `N` lines: one integer per line — a signal number to look up.

Use these mappings:

| Number | Name    | Catchable? |
|--------|---------|------------|
| 1      | SIGHUP  | catchable  |
| 2      | SIGINT  | catchable  |
| 9      | SIGKILL | NOT catchable |
| 15     | SIGTERM | catchable  |
| 18     | SIGCONT | catchable  |
| 19     | SIGSTOP | NOT catchable |

For any number not in the table, print `UNKNOWN: catchable assumed`.

## Output

For each of the `N` signal numbers (in order), print one line:

```
NAME: catchable
```

or

```
NAME: NOT catchable
```

or (for unknowns):

```
UNKNOWN: catchable assumed
```

## Examples

**Example 1**

Input:
```
4
15
9
2
19
```

Output:
```
SIGTERM: catchable
SIGKILL: NOT catchable
SIGINT: catchable
SIGSTOP: NOT catchable
```

**Example 2**

Input:
```
3
1
18
42
```

Output:
```
SIGHUP: catchable
SIGCONT: catchable
UNKNOWN: catchable assumed
```

**Example 3**

Input:
```
2
9
9
```

Output:
```
SIGKILL: NOT catchable
SIGKILL: NOT catchable
```

## Notes

- Input will always have exactly `N` signal numbers after the first line.
- Signal numbers are positive integers.
- The same signal number may appear more than once.
