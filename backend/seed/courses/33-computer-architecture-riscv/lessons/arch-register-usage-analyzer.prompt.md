# Exercise Prompt: Map Register Numbers to ABI Names

## Problem Statement

Write a program that reads RISC-V register numbers from stdin and prints their full ABI information. This tests your knowledge of the RISC-V calling convention register table.

## Input Format

- The first line contains a single integer **N** (1 ≤ N ≤ 20): the number of register queries.
- The next **N** lines each contain a single integer **R** representing a register number.
- R may be any integer (including negative or > 31 — handle gracefully).

## Output Format

For each register number R, print exactly one line in the format:

```
x<R> | <ABI name> | <role description> | <preservation class>
```

Where:
- `<R>` is the register number as printed (even if invalid).
- `<ABI name>` is the standard ABI name (e.g., `zero`, `ra`, `sp`, `a0`).
- `<role description>` is a short description of the conventional role.
- `<preservation class>` is one of: `caller-saved`, `callee-saved`, `special`.

For invalid register numbers (R < 0 or R > 31), print:

```
x<R> | invalid register number
```

## ABI Register Table Reference

| x# | ABI | Role | Class |
|----|-----|------|-------|
| 0 | zero | hardwired zero | special |
| 1 | ra | return address | caller-saved |
| 2 | sp | stack pointer | callee-saved |
| 3 | gp | global pointer | special |
| 4 | tp | thread pointer | special |
| 5 | t0 | temporary 0 | caller-saved |
| 6 | t1 | temporary 1 | caller-saved |
| 7 | t2 | temporary 2 | caller-saved |
| 8 | s0/fp | saved register 0 / frame pointer | callee-saved |
| 9 | s1 | saved register 1 | callee-saved |
| 10 | a0 | argument 0 / return value 0 | caller-saved |
| 11 | a1 | argument 1 / return value 1 | caller-saved |
| 12 | a2 | argument 2 | caller-saved |
| 13 | a3 | argument 3 | caller-saved |
| 14 | a4 | argument 4 | caller-saved |
| 15 | a5 | argument 5 | caller-saved |
| 16 | a6 | argument 6 | caller-saved |
| 17 | a7 | argument 7 / syscall number | caller-saved |
| 18 | s2 | saved register 2 | callee-saved |
| 19 | s3 | saved register 3 | callee-saved |
| 20 | s4 | saved register 4 | callee-saved |
| 21 | s5 | saved register 5 | callee-saved |
| 22 | s6 | saved register 6 | callee-saved |
| 23 | s7 | saved register 7 | callee-saved |
| 24 | s8 | saved register 8 | callee-saved |
| 25 | s9 | saved register 9 | callee-saved |
| 26 | s10 | saved register 10 | callee-saved |
| 27 | s11 | saved register 11 | callee-saved |
| 28 | t3 | temporary 3 | caller-saved |
| 29 | t4 | temporary 4 | caller-saved |
| 30 | t5 | temporary 5 | caller-saved |
| 31 | t6 | temporary 6 | caller-saved |

## Constraints

- 1 ≤ N ≤ 20
- Register numbers may be any integer in the range [-100, 100].
- Output must match exactly (spacing, pipes, capitalization).
- No external libraries required; pure standard library only.

## Sample Input

```
5
0
1
10
8
32
```

## Sample Output

```
x0 | zero | hardwired zero | special
x1 | ra | return address | caller-saved
x10 | a0 | argument 0 / return value 0 | caller-saved
x8 | s0/fp | saved register 0 / frame pointer | callee-saved
x32 | invalid register number
```
