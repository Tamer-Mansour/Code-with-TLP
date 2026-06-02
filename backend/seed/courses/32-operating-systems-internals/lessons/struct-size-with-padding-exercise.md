# Exercise: Compute Struct Size With Alignment and Padding

In this exercise you will simulate what a C compiler does when it lays out a struct in memory: insert padding bytes to satisfy alignment requirements, then compute the total size of the struct (including trailing padding).

## What You Will Implement

Given a list of struct fields (each with a name and a type), compute:

1. The **offset** of every field (in bytes from the start of the struct).
2. The **total size** of the struct, rounded up to the alignment of its largest field.

## Alignment Rules

Use these standard (platform-neutral) type sizes and alignments:

| Type | Size (bytes) | Alignment (bytes) |
|---|---|---|
| char | 1 | 1 |
| short | 2 | 2 |
| int | 4 | 4 |
| float | 4 | 4 |
| double | 8 | 8 |
| pointer | 8 | 8 |

The layout algorithm:
- Place fields in declaration order.
- Before placing a field, advance the current offset to the nearest multiple of that field's alignment.
- After all fields, round up the total to the largest alignment seen (trailing padding).

## Input Format

```
N
field_name1 type1
field_name2 type2
...
```

Where `N` is the number of fields and each type is one of: `char`, `short`, `int`, `float`, `double`, `pointer`.

## Output Format

Print one line per field: `field_name: offset X` (where X is the byte offset), then a final line `total: Y`.

## Example

**Input:**
```
3
a char
b int
c char
```

**Expected output:**
```
a: offset 0
b: offset 4
c: offset 8
total: 12
```

**Explanation:** `a` fits at 0. `b` needs 4-byte alignment so 3 bytes of padding are inserted and `b` lands at offset 4. `c` fits at 8. The largest alignment is 4 (`int`), so total must be a multiple of 4: 9 rounded up to 12.

## Getting Started

Your solution reads from standard input and writes to standard output. No file I/O or third-party libraries are needed. Use the type table above — do not hard-code platform-specific sizes.
