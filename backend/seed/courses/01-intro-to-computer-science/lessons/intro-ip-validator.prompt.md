# IPv4 Address Validator

Read lines from standard input until EOF. Each line contains a string that may or may not be a valid IPv4 address.

A **valid IPv4 address** has exactly **four parts** separated by dots (`.`), where each part is a decimal integer between **0 and 255** (inclusive) with **no leading zeros** (except the number `0` itself).

For each line, print `VALID` if it is a valid IPv4 address, or `INVALID` otherwise.

## Input format

One string per line until EOF.

## Output format

`VALID` or `INVALID` for each line, in order.

## Examples

**Input:**
```
192.168.1.1
256.0.0.1
0.0.0.0
01.02.03.04
10.0.0
```

**Output:**
```
VALID
INVALID
VALID
INVALID
INVALID
```

## Rules

- Must have exactly 4 dot-separated parts.
- Each part must be a valid integer (only digit characters, no sign, no spaces).
- Each part must be in the range [0, 255].
- Leading zeros are not allowed: `01` is invalid, but `0` is valid.
