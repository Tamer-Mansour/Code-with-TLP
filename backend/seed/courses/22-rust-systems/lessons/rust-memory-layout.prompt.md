# Memory Layout Calculator

Given a Rust struct definition as a list of fields with types, compute the byte offset of each field and the struct's total size, applying Rust's default alignment rules.

## Layout Rules

1. Each field is placed at the **lowest offset that is a multiple of the field's alignment**.
2. The struct's total size is padded to a multiple of the **largest field alignment**.

## Supported Types

| Type | Size (bytes) | Alignment (bytes) |
|------|-------------|-------------------|
| `u8` / `i8` / `bool` | 1 | 1 |
| `u16` / `i16` | 2 | 2 |
| `u32` / `i32` / `f32` | 4 | 4 |
| `u64` / `i64` / `f64` / `usize` | 8 | 8 |

## Input Format

```
N
<field_name> <type>
<field_name> <type>
...  (N lines)
```

## Output Format

One line per field: `<field_name>: offset=<offset>`
Then a final line: `total_size=<size>`

## Sample Input

```
4
flag bool
value u32
count u64
short u16
```

## Sample Output

```
flag: offset=0
value: offset=4
count: offset=8
short: offset=16
total_size=24
```

## Explanation

- `flag` (bool, align=1): offset 0. Current position becomes 1.
- `value` (u32, align=4): round 1 up to 4. Offset 4. Current position becomes 8.
- `count` (u64, align=8): 8 is already aligned. Offset 8. Current position becomes 16.
- `short` (u16, align=2): 16 is already aligned. Offset 16. Current position becomes 18.
- Max alignment = 8. Round 18 up to next multiple of 8 = **24**.

## Constraints

- `1 <= N <= 10`
- All field types are from the supported type table above
- Field names are alphanumeric strings
