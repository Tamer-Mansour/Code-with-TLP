# Binary ↔ Decimal Converter

Write a program that reads conversion requests from standard input, one per line, until EOF.

Each line has the format: `<PREFIX> <NUMBER>`

- If `PREFIX` is `B`, interpret `NUMBER` as a binary string (containing only `0` and `1`) and print its decimal integer value.
- If `PREFIX` is `D`, interpret `NUMBER` as a decimal integer and print its binary representation without leading zeros. Exception: the number `0` should print as `0`.

Print one result per line, in the same order as the input.

## Input format

Each line: `B <binary_string>` or `D <decimal_integer>`

## Output format

One integer or binary string per line.

## Example

**Input:**
```
B 1010
D 13
B 11111111
D 0
```

**Output:**
```
10
1101
255
0
```
