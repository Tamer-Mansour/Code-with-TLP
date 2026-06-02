# Exercise Prompt: Compute Struct Size with Alignment Rules

## Overview

Given a series of C struct definitions (using simplified type names), compute the byte offset of each member and the total `sizeof` the struct, applying standard alignment and padding rules for a 64-bit platform.

## Type Sizes and Alignments

| Type token | C type | Size (bytes) | Alignment (bytes) |
|---|---|---|---|
| `char` | `char` | 1 | 1 |
| `short` | `short` | 2 | 2 |
| `int` | `int` | 4 | 4 |
| `longlong` | `long long` | 8 | 8 |
| `double` | `double` | 8 | 8 |
| `ptr` | `void*` | 8 | 8 |

## Alignment Rules

1. Start the current offset at 0.
2. For each member in declaration order:
   - Advance the current offset to the next multiple of that member's alignment (round up).
   - Record that as the member's offset.
   - Add the member's size to the current offset.
3. After all members, round the total offset up to the next multiple of the struct's alignment (= the maximum alignment of any member). This is `sizeof` the struct.

## Input Format

```
N
M
type1 field1
type2 field2
...
M
...
```

- First line: integer `N` — number of struct definitions (1 ≤ N ≤ 20)
- For each struct: integer `M` (number of members, 1 ≤ M ≤ 10), then `M` lines each with a type token and field name

## Output Format

For each struct, print one line with all member offsets (in declaration order) followed by the total sizeof, all separated by single spaces.

## Constraints

- 1 ≤ N ≤ 20
- 1 ≤ M ≤ 10
- No nested structs — all types are primitive tokens from the table above
- No bit-fields
- No `#pragma pack`
- No empty structs (M ≥ 1)

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

## Additional Examples

### Single-member struct

Input:
```
1
1
char x
```
Output:
```
0 1
```
(offset 0, sizeof=1 — rounded up to multiple of 1)

### All-same type

Input:
```
1
3
int a
int b
int c
```
Output:
```
0 4 8 12
```

### Mixed large types

Input:
```
1
4
char a
ptr p
short b
longlong n
```
Output:
```
0 8 16 24 32
```
(char at 0, 7 pad, ptr at 8, short at 16, 6 pad, longlong at 24, sizeof=32)
