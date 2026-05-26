# Hexadecimal Converter

Write a program that converts numbers between decimal and hexadecimal.

Read lines from standard input until EOF. Each line has the format `<PREFIX> <NUMBER>`:

- If `PREFIX` is `H`, interpret `NUMBER` as a hexadecimal string (using uppercase letters A–F) and print its decimal integer value.
- If `PREFIX` is `D`, interpret `NUMBER` as a non-negative decimal integer and print its uppercase hexadecimal representation without leading zeros. Exception: the number `0` prints as `0`.

## Input format

Each line: `H <hex_string>` or `D <decimal_integer>`

`<hex_string>` contains only digits `0-9` and uppercase letters `A-F`.

## Output format

One result per line, in input order.
- For `H` inputs: print the decimal integer.
- For `D` inputs: print the uppercase hexadecimal string (no `0x` prefix).

## Example

**Input:**
```
H FF
D 255
H 1A
D 0
H 10
D 16
```

**Output:**
```
255
FF
26
0
16
16
```
