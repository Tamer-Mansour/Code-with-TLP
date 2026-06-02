# Problem: Convert a 32-bit Integer Between Big- and Little-Endian

## Description

Given a 32-bit unsigned integer (provided as an 8-digit uppercase hex string) and a source endian format, convert it to the opposite endian format and output the result as an 8-digit uppercase hex string.

The conversion rule: to swap endianness of a 32-bit value, reverse the order of its 4 bytes.

## Input Format

Two lines:
1. An 8-character uppercase hex string representing the 32-bit value (e.g., `DEADBEEF`)
2. The source endian format: either `BIG` or `LITTLE`

## Output Format

A single line: the 8-character uppercase hex string of the converted value.

## Constraints

- The hex string is always exactly 8 uppercase characters: `0-9`, `A-F`
- Source endian is always `BIG` or `LITTLE`
- No leading/trailing whitespace in output

## Sample Input 1

```
DEADBEEF
BIG
```

## Sample Output 1

```
EFBEADDE
```

**Explanation:** `0xDEADBEEF` in big-endian has bytes `DE AD BE EF`. Reversing gives `EF BE AD DE` = `0xEFBEADDE`.

## Sample Input 2

```
0A0B0C0D
LITTLE
```

## Sample Output 2

```
0D0C0B0A
```

**Explanation:** `0x0A0B0C0D` stored little-endian; byte-swapping to big-endian gives `0x0D0C0B0A`.

## Notes

- The conversion is symmetric: BIG→LITTLE and LITTLE→BIG both perform the same byte reversal.
- Treat the input simply as 4 bytes in a specific order; endian label only contextualises meaning — the byte swap operation itself is identical either way.
