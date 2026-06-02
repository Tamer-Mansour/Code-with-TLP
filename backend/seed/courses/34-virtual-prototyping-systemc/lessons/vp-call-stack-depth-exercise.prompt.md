# Prompt: Compute Maximum Call-Stack Depth from a Trace

## Problem Description

Parse a simplified execution trace of `CALL` and `RETURN` events. Track the call stack and report:

1. The maximum depth reached (number of frames on the stack at any point).
2. The name of the function at the top of the stack when that maximum was **first** reached.
3. If a `RETURN` is encountered when the stack is empty, print `ERROR: return on empty stack` and stop processing further commands (still print the max depth and function name computed up to that point on the lines that follow).

## Input Format

```
Line 1: N  (number of trace events, 1 ≤ N ≤ 1000)
Lines 2..N+1: one event per line
  CALL <name>   — function name is a single alphanumeric token (no spaces)
  RETURN        — return from the current top-of-stack function
```

## Output Format

```
MAX_DEPTH <d>
TOP_FUNCTION <name>
```

If a bad RETURN is encountered, print `ERROR: return on empty stack` on its own line **before** the MAX_DEPTH / TOP_FUNCTION lines.

If no CALL was ever made (depth never exceeds 0), print:
```
MAX_DEPTH 0
TOP_FUNCTION none
```

## Constraints

- 1 ≤ N ≤ 1000
- Function names are 1–32 alphanumeric characters
- The trace may have more RETURNs than CALLs (error case)
- Depth is defined as the number of frames currently on the stack after processing the event

## Sample Input 1

```
7
CALL main
CALL init
CALL memset
RETURN
CALL uart_init
RETURN
RETURN
```

## Sample Output 1

```
MAX_DEPTH 3
TOP_FUNCTION memset
```

**Trace:**
- CALL main → stack=[main], depth=1, max=1
- CALL init → stack=[main,init], depth=2, max=2
- CALL memset → stack=[main,init,memset], depth=3, max=3 (first time), top=memset
- RETURN → stack=[main,init], depth=2
- CALL uart_init → stack=[main,init,uart_init], depth=3 (not first time, top stays memset)
- RETURN → stack=[main,init], depth=2
- RETURN → stack=[main], depth=1

## Sample Input 2

```
5
CALL boot
CALL hal_init
RETURN
RETURN
RETURN
```

## Sample Output 2

```
ERROR: return on empty stack
MAX_DEPTH 2
TOP_FUNCTION hal_init
```

**Trace:**
- CALL boot → depth=1
- CALL hal_init → depth=2, max=2, top=hal_init
- RETURN → depth=1
- RETURN → depth=0
- RETURN → stack empty → ERROR

## Sample Input 3

```
3
CALL alpha
CALL beta
CALL gamma
```

## Sample Output 3

```
MAX_DEPTH 3
TOP_FUNCTION gamma
```

## Sample Input 4

```
1
RETURN
```

## Sample Output 4

```
ERROR: return on empty stack
MAX_DEPTH 0
TOP_FUNCTION none
```

## Sample Input 5

```
4
CALL setup
RETURN
CALL loop
RETURN
```

## Sample Output 5

```
MAX_DEPTH 1
TOP_FUNCTION setup
```
