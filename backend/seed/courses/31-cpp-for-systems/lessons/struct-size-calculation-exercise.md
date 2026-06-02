# Exercise: Compute Struct Size with Alignment Rules

In this exercise you will apply the alignment and padding rules you have learned to compute struct sizes and member offsets — without running any code.

## What You Will Practice

- Applying the "advance to next multiple of member alignment" rule step by step
- Adding tail padding to make the struct size a multiple of its largest member alignment
- Predicting how member reordering changes the total size
- Computing `offsetof`-equivalent byte offsets for each field

## Problem Description

You are given a series of struct definitions. For each one, compute:

1. The **offset** (in bytes) of every named member
2. The **sizeof** the entire struct

Each type has its natural alignment on a typical 64-bit platform (GCC/Clang, Linux/Windows):

| Type | Size | Alignment |
|---|---|---|
| `char` | 1 | 1 |
| `short` | 2 | 2 |
| `int` | 4 | 4 |
| `long long` | 8 | 8 |
| `double` | 8 | 8 |
| pointer | 8 | 8 |

## Input Format

- The first line is `N`, the number of struct definitions (1 ≤ N ≤ 20).
- Each struct definition begins with a line containing a single integer `M` — the number of members.
- The next `M` lines each contain a type name and a field name separated by a space.

Types used: `char`, `short`, `int`, `longlong`, `double`, `ptr` (representing a pointer).

## Output Format

For each struct, print one line containing the offsets of every member (space-separated, in declaration order) followed by the total `sizeof`, all space-separated on one line.

## Sample Input

```
3
3
int a
char b
double c
4
char a
char b
char c
int d
2
double x
char y
```

## Sample Output

```
0 4 8 16
0 1 2 4 8
0 8 16
```

## Explanation of Sample

**Struct 1:** `int a` (align 4) at 0; `char b` (align 1) at 4; 3 bytes padding; `double c` (align 8) at 8; size = 16 (8 + 8, multiple of 8).

**Struct 2:** `char a` at 0; `char b` at 1; `char c` at 2; 1 byte padding; `int d` at 4; size = 8 (4 + 4, multiple of 4).

**Struct 3:** `double x` (align 8) at 0; `char y` (align 1) at 8; 7 bytes tail padding; size = 16 (multiple of 8).

## Implement Your Solution

Write a program (Python) that reads the struct definitions from stdin and prints the required output. Use only the standard library.
