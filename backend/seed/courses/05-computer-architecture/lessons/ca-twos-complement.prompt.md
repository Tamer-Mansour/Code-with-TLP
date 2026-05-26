# Two's Complement Converter

Given a positive integer **N** and a bit width **W**, output the **W-bit two's complement** binary representation of **−N** (the negation of N).

## Input Format

A single line containing two integers separated by a space:
```
N W
```
- `1 <= N <= 2^(W-1) - 1` (so −N fits in W bits without overflow, except N=2^(W-1) which maps to itself)
- `4 <= W <= 16`

## Output Format

A single line: the W-bit two's complement binary string for −N (MSB first, exactly W characters of '0' and '1', no spaces).

## Examples

**Input:**
```
5 8
```
**Output:**
```
11111011
```

**Explanation:** −5 in 8-bit two's complement is 11111011 (flip 00000101 → 11111010, add 1 → 11111011).

**Input:**
```
1 4
```
**Output:**
```
1111
```

**Explanation:** −1 in 4-bit two's complement is 1111.
