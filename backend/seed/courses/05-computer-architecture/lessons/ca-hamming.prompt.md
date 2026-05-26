# Hamming Distance and Parity

Given two binary strings of equal length, compute their Hamming distance (the number of bit positions where they differ) and the even parity bit of the first string.

## Input

```
One line: two binary strings separated by a space (equal length, at least 1 bit)
```

## Output

```
Line 1: Hamming distance (non-negative integer)
Line 2: Even parity bit of the first string (0 or 1)
```

## Even Parity Definition

The even parity bit is 0 if the string contains an even number of 1-bits; 1 if it contains an odd number. (Adding the parity bit to the string makes the total count of 1s even.)

## Examples

```
Input:  10110 01001
Output:
5
1
```

Explanation: strings differ at all 5 positions (1≠0, 0≠1, 1≠0, 1≠0, 0≠1) → Hamming distance = 5. `10110` has three 1-bits (odd) → even parity bit = 1.

```
Input:  11001100 10100101
Output:
4
0
```

Explanation: `11001100` vs `10100101` differ at 4 positions. `11001100` has four 1-bits (even) → parity bit = 0.

## Constraints

- Binary strings contain only `0` and `1`.
- Both strings have the same length (1–64 characters).
