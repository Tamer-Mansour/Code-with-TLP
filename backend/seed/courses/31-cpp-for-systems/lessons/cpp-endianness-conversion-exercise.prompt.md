# Prompt: Convert Integers Between Endianness

## Task

Read unsigned 32-bit integers from standard input (one per line, given as 8-character hexadecimal strings without the `0x` prefix). For each integer, output its byte-swapped value as an 8-character uppercase hexadecimal string.

Byte swapping reverses the order of the four bytes. For example, `0x12345678` becomes `0x78563412`.

## Input Format

- Each line contains exactly one hexadecimal string representing a 32-bit unsigned integer.
- The string is exactly 8 hex characters (uppercase or lowercase, no `0x` prefix).
- Input ends at EOF.
- Number of lines: 1 to 100.

## Output Format

- For each input line, output one line containing exactly 8 uppercase hexadecimal characters representing the byte-swapped value.
- Zero-pad as necessary (e.g. `00000001` not `1`).

## Constraints

- Input values are valid 32-bit unsigned hex strings.
- No blank lines in input.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample

### Input
```
12345678
DEADBEEF
00000001
AABBCCDD
```

### Output
```
78563412
EFBEADDE
01000000
DDCCBBAA
```

## Explanation

- `12345678` → bytes are `12`, `34`, `56`, `78` → reversed: `78`, `56`, `34`, `12` → `78563412`
- `DEADBEEF` → bytes are `DE`, `AD`, `BE`, `EF` → reversed: `EF`, `BE`, `AD`, `DE` → `EFBEADDE`
- `00000001` → bytes are `00`, `00`, `00`, `01` → reversed: `01`, `00`, `00`, `00` → `01000000`
- `AABBCCDD` → bytes are `AA`, `BB`, `CC`, `DD` → reversed: `DD`, `CC`, `BB`, `AA` → `DDCCBBAA`
