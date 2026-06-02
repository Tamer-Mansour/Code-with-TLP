# Prompt: Pack and Unpack Bytes into Words

## Problem Statement

You are given a series of operations. Each operation is either:

- `PACK <endian> <b0> <b1> <b2> <b3>` — pack four byte values (given as decimal integers 0-255) into a 32-bit word using the specified byte order, then print the result as an 8-digit uppercase hex string.
  - `LE`: b0 is the least-significant byte (address+0), b3 is the most-significant byte (address+3).
  - `BE`: b0 is the most-significant byte (address+0), b3 is the least-significant byte (address+3).
- `UNPACK <endian> <hex_word>` — unpack a 32-bit word (8 hex digits, no 0x prefix) into four bytes and print them as four space-separated decimal integers.
  - `LE`: print LSB first (byte at address+0 first).
  - `BE`: print MSB first (byte at address+0 first).

## Input Format

```
N
PACK|UNPACK <endian> <args...>
...
```

- First line: integer N (1 ≤ N ≤ 200)
- Next N lines: one operation each.

## Output Format

- For `PACK`: one line containing the 8-digit uppercase hex result.
- For `UNPACK`: one line containing four space-separated decimal integers (0–255).

## Constraints

- 1 ≤ N ≤ 200
- Byte values for PACK are integers in [0, 255].
- Hex words for UNPACK are valid 8-character hex strings.
- Endian is exactly `LE` or `BE`.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
4
PACK LE 239 190 173 222
PACK BE 222 173 190 239
UNPACK LE DEADBEEF
UNPACK BE DEADBEEF
```

## Sample Output

```
DEADBEEF
DEADBEEF
239 190 173 222
222 173 190 239
```

## Explanation

- `PACK LE 239 190 173 222`: b0=0xEF(239) is LSB → word = 0xDE(222)<<24 | 0xAD(173)<<16 | 0xBE(190)<<8 | 0xEF(239) = 0xDEADBEEF
- `PACK BE 222 173 190 239`: b0=0xDE(222) is MSB → word = 0xDE<<24 | 0xAD<<16 | 0xBE<<8 | 0xEF = 0xDEADBEEF
- `UNPACK LE DEADBEEF`: LSB first → 0xEF=239, 0xBE=190, 0xAD=173, 0xDE=222
- `UNPACK BE DEADBEEF`: MSB first → 0xDE=222, 0xAD=173, 0xBE=190, 0xEF=239
