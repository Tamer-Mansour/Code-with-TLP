# Prompt: Simulate a Stack — Push/Pop and Report Top

## Problem Description

Simulate a fixed-capacity downward-growing integer stack. The stack pointer (SP) starts at `capacity` (one past the last valid index) and moves toward index 0 on each push.

- **PUSH n**: If SP == 0, print `OVERFLOW`; otherwise decrement SP then store n at index SP.
- **POP**: If SP == capacity, print `UNDERFLOW`; otherwise read the value at index SP, print it, then increment SP.
- **TOP**: If SP == capacity, print `UNDERFLOW`; otherwise print the value at index SP (SP does not change).

After all commands, print `SP <sp>` where `<sp>` is the final stack pointer value.

## Input Format

```
Line 1: capacity  (integer, 1 ≤ capacity ≤ 100)
Lines 2..N: one command per line — PUSH <int> | POP | TOP
```

The number of commands does not exceed 200. Integer values fit in a 32-bit signed integer.

## Output Format

For each `POP` or `TOP` command that succeeds, print the integer value on its own line.
For each `OVERFLOW` or `UNDERFLOW` event, print `OVERFLOW` or `UNDERFLOW` respectively.
On the final line, print `SP <value>` where `<value>` is the final SP.

## Constraints

- 1 ≤ capacity ≤ 100
- Up to 200 commands
- No blank lines in input; commands are uppercase
- PUSH arguments fit in a 32-bit signed integer

## Sample Input 1

```
4
PUSH 10
PUSH 20
PUSH 30
TOP
POP
POP
POP
POP
```

## Sample Output 1

```
30
30
20
10
UNDERFLOW
SP 4
```

**Trace:**
- Start: SP=4, stack=[]
- PUSH 10: SP=3, stack[3]=10
- PUSH 20: SP=2, stack[2]=20
- PUSH 30: SP=1, stack[1]=30
- TOP: print stack[1]=30, SP stays 1
- POP: print stack[1]=30, SP=2
- POP: print stack[2]=20, SP=3
- POP: print stack[3]=10, SP=4
- POP: SP==capacity(4), UNDERFLOW
- Final: SP 4

## Sample Input 2

```
2
PUSH 5
PUSH 7
PUSH 9
POP
TOP
```

## Sample Output 2

```
OVERFLOW
7
5
SP 1
```

**Trace:**
- Start: SP=2, stack=[]
- PUSH 5: SP=1, stack[1]=5
- PUSH 7: SP=0, stack[0]=7
- PUSH 9: SP==0, OVERFLOW
- POP: print stack[0]=7, SP=1
- TOP: print stack[1]=5, SP stays 1
- Final: SP 1
