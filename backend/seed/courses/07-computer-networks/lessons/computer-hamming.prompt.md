# Hamming(7,4) Error Detection and Correction

Implement Hamming(7,4) encoding and single-bit error detection/correction.

## Bit Layout

```
Position: 1   2   3   4   5   6   7
Bit type: p1  p2  d1  p3  d2  d3  d4
```

Input data string `d1d2d3d4` maps to positions 3, 5, 6, 7.
Parity bits at positions 1, 2, 4 are computed with even parity:

- `p1 = d1 ^ d2 ^ d4` (covers positions 1, 3, 5, 7)
- `p2 = d1 ^ d3 ^ d4` (covers positions 2, 3, 6, 7)
- `p3 = d2 ^ d3 ^ d4` (covers positions 4, 5, 6, 7)

Syndrome for error detection: `error_pos = s1 + 2*s2 + 4*s3` where `s1, s2, s3` are parities of positions 1,3,5,7 / 2,3,6,7 / 4,5,6,7 of the received codeword.

## Input Format

```
<data4>
<received7>
```

- Line 1: a 4-bit data string to encode (e.g. `1010`).
- Line 2: a 7-bit received codeword to check and correct (may have 0 or 1 bit errors).

## Output Format

```
Encoded: <7-bit codeword>
Error at bit: <position or "No error">
Data: <4-bit recovered data>
```

## Examples

**Input:**
```
1010
1011010
```
**Output:**
```
Encoded: 1011010
Error at bit: No error
Data: 1010
```

**Input:**
```
1011
0100011
```
**Output:**
```
Encoded: 0110011
Error at bit: 3
Data: 1011
```

**Input:**
```
0000
0000000
```
**Output:**
```
Encoded: 0000000
Error at bit: No error
Data: 0000
```
