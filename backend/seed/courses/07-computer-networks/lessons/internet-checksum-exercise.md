# Exercise: Internet Checksum

Compute the **Internet checksum** (one's complement sum) of a sequence of 16-bit words given as space-separated decimal integers.

The Internet checksum algorithm:
1. Sum all 16-bit words using one's complement addition (add any carry back in).
2. Take the one's complement of the result (bitwise NOT, keeping only 16 bits).

Print the result as a decimal integer.

## Input Format

A single line of space-separated non-negative integers, each fitting in 16 bits (0–65535).

## Output Format

A single decimal integer — the checksum (16-bit, 0–65535).

## Example

Input:
```
46336 5888
```

`46336 = 0xB500`, `5888 = 0x1700`

Sum: `0xB500 + 0x1700 = 0xCC00`  
One's complement: `~0xCC00 & 0xFFFF = 0x33FF = 13311`

Output:
```
13311
```
