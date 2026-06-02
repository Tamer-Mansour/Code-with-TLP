# Prompt: Compute Struct Size With Alignment and Padding

## Problem Statement

Simulate the C compiler's struct layout algorithm. Given a list of fields with types, compute the byte offset of each field and the total struct size, accounting for padding and trailing alignment.

## Type Table

| Type | Size (bytes) | Alignment (bytes) |
|---|---|---|
| char | 1 | 1 |
| short | 2 | 2 |
| int | 4 | 4 |
| float | 4 | 4 |
| double | 8 | 8 |
| pointer | 8 | 8 |

## Layout Algorithm

1. Start at offset 0. Track `max_align = 1`.
2. For each field in order:
   a. Look up the field's `align` and `size`.
   b. If `current_offset % align != 0`, advance `current_offset` to the next multiple of `align`.
   c. Record `field_offset = current_offset`.
   d. Update `max_align = max(max_align, align)`.
   e. Advance `current_offset += size`.
3. After all fields, if `current_offset % max_align != 0`, round up to the next multiple of `max_align`. This is the total size.

## Input Format

```
N
field_name_1 type_1
field_name_2 type_2
...
field_name_N type_N
```

- First line: integer `N` (1 <= N <= 20).
- Next `N` lines: field name (alphanumeric, no spaces) and type (one of `char`, `short`, `int`, `float`, `double`, `pointer`).

## Output Format

Print exactly `N + 1` lines:

```
field_name_1: offset O1
field_name_2: offset O2
...
field_name_N: offset ON
total: T
```

All values are non-negative integers. No extra whitespace or blank lines.

## Constraints

- 1 <= N <= 20
- Field names are 1–32 characters, `[a-zA-Z0-9_]`
- Types are strictly from the table above (lowercase)
- No duplicate field names guaranteed

## Sample Input 1

```
3
a char
b int
c char
```

## Sample Output 1

```
a: offset 0
b: offset 4
c: offset 8
total: 12
```

## Sample Input 2

```
4
x double
y char
z short
w int
```

## Sample Output 2

```
x: offset 0
y: offset 8
z: offset 10
w: offset 12
total: 16
```

**Explanation:** `x` (double, align=8) at 0. `y` (char, align=1) at 8. `z` (short, align=2): offset 9 is not a multiple of 2, advance to 10. `w` (int, align=4): offset 12 is a multiple of 4. Total used = 16. max_align=8, 16 % 8 == 0 so total = 16.

## Sample Input 3 (all chars — no padding)

```
3
a char
b char
c char
```

## Sample Output 3

```
a: offset 0
b: offset 1
c: offset 2
total: 3
```
