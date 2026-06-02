# Prompt: Dispatch System Calls From a Numbered Argument Stream

## Problem Statement

Simulate a kernel syscall dispatcher. Read syscall records from stdin, dispatch each to the correct handler, and print results to stdout.

## Syscall Table

| Number | Name | Argument format (after number) | Behavior |
|---|---|---|---|
| 1 | `write` | `fd count string` | fd=1: print the first `count` characters of `string`, then print the bytes written. fd!=1: print -9 |
| 3 | `getpid` | *(no args)* | Print 42 |
| 4 | `getuid` | *(no args)* | Print 1000 |
| 6 | `close` | `fd` | Print 0 |
| 9 | `exit` | `status` | Print `exit(status)` and stop |
| other | — | *(ignored)* | Print -38 |

### Notes on `write` (syscall 1)

- The string argument is the third token. It may not contain spaces (for simplicity).
- `count` specifies how many characters to print (use `string[:count]`).
- If `fd == 1`: first output line = the truncated string; second output line = the integer value of count (bytes written, capped to len(string)).
- If `fd != 1`: output one line: `-9`.

### Termination

- When syscall 9 (`exit`) is encountered, print `exit(status)` and **stop reading** further input.
- If stdin ends without an exit syscall, stop normally.

## Input Format

```
<syscall_number> [arg1] [arg2] [arg3]
```

- One record per line.
- Syscall number is a non-negative integer.
- Arguments are space-separated tokens on the same line.
- The string argument for `write` contains no spaces.

## Output Format

- For each syscall (in order), print the result as described above.
- No trailing spaces. Each result on its own line.

## Constraints

- Number of records: 1 to 100.
- Syscall numbers: 0 to 999.
- `fd` for write: any integer.
- `count` for write: 1 to 1000.
- String for write: 1 to 1000 printable ASCII characters (no spaces).
- `status` for exit: any integer.

## Sample Input 1

```
3
4
1 1 5 hello
6 3
9 0
99
```

## Sample Output 1

```
42
1000
hello
5
0
exit(0)
```

(The line `99` after `exit` is never processed.)

## Sample Input 2

```
1 2 3 abc
1 1 3 abcdef
```

## Sample Output 2

```
-9
abc
3
```

## Sample Input 3

```
99
3
9 1
```

## Sample Output 3

```
-38
42
exit(1)
```

## Sample Input 4

```
6 5
4
3
```

## Sample Output 4

```
0
1000
42
```
