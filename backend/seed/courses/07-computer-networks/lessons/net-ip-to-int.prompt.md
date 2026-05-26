# IP Address to 32-bit Integer

Read a dotted-decimal IPv4 address from standard input and print its equivalent unsigned 32-bit integer value.

## Input

A single line containing a valid IPv4 address:
```
A.B.C.D
```
where A, B, C, D are integers in [0, 255].

## Output

A single integer on one line.

## Formula

```
result = A * 16777216 + B * 65536 + C * 256 + D
       = (A << 24) | (B << 16) | (C << 8) | D
```

## Examples

**Input:** `192.168.1.1`  
**Output:** `3232235777`

**Input:** `0.0.0.0`  
**Output:** `0`

**Input:** `255.255.255.255`  
**Output:** `4294967295`

## Constraints

- Use only the Python standard library.
- Input is always a valid IPv4 address.
