# Prompt: Parse a Hex Byte Stream into Integers

## Task

Read a stream of hexadecimal bytes and reconstruct unsigned 32-bit integers from them according to a specified byte order.

## Input Format

- **Line 1**: space-separated hex byte values (each exactly 2 uppercase or lowercase hex characters), representing a sequence of bytes. The total number of bytes is always a multiple of 4. Maximum 100 bytes total.
- **Line 2**: a single string, either `BE` (big-endian) or `LE` (little-endian), specifying how to interpret groups of 4 bytes.

## Output Format

- For each consecutive group of 4 bytes in the input stream, output one line containing the corresponding unsigned 32-bit decimal integer.
- Output one integer per line, no trailing spaces.

## Assembly Rules

For a group of 4 bytes `b0, b1, b2, b3` (in stream order):

- **BE**: `value = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3`
- **LE**: `value = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)`

## Constraints

- Number of bytes: 4 to 100 (always a multiple of 4)
- Byte values: valid two-digit hex strings (00 to FF)
- Byte order: exactly `BE` or `LE`
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample 1

### Input
```
12 34 56 78 DE AD BE EF
BE
```

### Output
```
305419896
3735928559
```

## Sample 2

### Input
```
78 56 34 12 EF BE AD DE
LE
```

### Output
```
305419896
3735928559
```

## Sample 3

### Input
```
00 00 00 01
BE
```

### Output
```
1
```

## Sample 4

### Input
```
01 00 00 00
LE
```

### Output
```
1
```

## Explanation

In Sample 1, `12 34 56 78` in big-endian = `0x12345678` = 305419896.
In Sample 2, `78 56 34 12` in little-endian = `0x12345678` = 305419896 (same value, bytes in reverse order).
