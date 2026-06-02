# Prompt: Hex to Binary and Back

## Problem Statement

Write a program that converts between hexadecimal and binary number representations.

## Input Format

Each line of input is one of:
```
HEX_TO_BIN <hex_string>
BIN_TO_HEX <binary_string>
```

- `hex_string` contains only hex digits (0-9, A-F, a-f). Length is between 1 and 16 characters.
- `binary_string` contains only '0' and '1'. Length is between 4 and 64 characters and is always a multiple of 4.

Input ends at EOF. There are 1 to 20 operations per test case.

## Output Format

For each operation, print one line:
- `HEX_TO_BIN` → the binary string, 4 bits per hex digit, no spaces, no prefix. Always uppercase source digits are normalized (case-insensitive input).
- `BIN_TO_HEX` → the hexadecimal string, uppercase A-F, no `0x` prefix, no leading zeros EXCEPT: if the value is zero, output `0`.

## Constraints

- Hex input is case-insensitive (both `0xAB` style input is NOT given — just the digits).
- For `HEX_TO_BIN`, output has length = 4 × len(hex_string). Always emit all leading zeros.
- For `BIN_TO_HEX`, suppress leading zeros in output, but output `0` for an all-zero input.
- No extra whitespace in output.

## Sample Input

```
HEX_TO_BIN A
HEX_TO_BIN 0F
HEX_TO_BIN DEADBEEF
BIN_TO_HEX 1010
BIN_TO_HEX 00001111
BIN_TO_HEX 11011110101011011011111011101111
BIN_TO_HEX 0000
```

## Sample Output

```
1010
00001111
11011110101011011011111011101111
A
F
DEADBEEF
0
```

## Explanation

- `A` hex → `1010` binary (4 bits for one digit).
- `0F` hex → `00001111` (0→0000, F→1111).
- `DEADBEEF` → each digit maps to 4 bits: D=1101, E=1110, A=1010, D=1101, B=1011, E=1110, E=1110, F=1111.
- `1010` binary → A hex (= 10 decimal).
- `00001111` → leading zero nibble suppressed → `F`.
- `0000` → all zeros → output `0`.

## Notes

- The table to internalize: 0=0000, 1=0001, 2=0010, 3=0011, 4=0100, 5=0101, 6=0110, 7=0111, 8=1000, 9=1001, A=1010, B=1011, C=1100, D=1101, E=1110, F=1111.
- For `BIN_TO_HEX`, group bits from the LEFT into groups of 4, convert each group, then strip leading zeros.
