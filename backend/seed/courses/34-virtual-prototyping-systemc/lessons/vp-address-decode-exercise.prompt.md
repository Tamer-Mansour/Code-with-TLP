# Prompt: Decode an Address to a Target and Offset

## Problem Statement

You are implementing the decode step of a TLM router. Given an address map and a set of query addresses, determine for each address which region it belongs to and compute the target-local offset.

## Input Format

```
Line 1:    N   (integer, number of address map entries, 1 <= N <= 20)
Lines 2..N+1:  <name> <base_hex> <size_hex>
               name is a single word (no spaces)
               base_hex and size_hex are hex integers with "0x" prefix
Line N+2:  Q   (integer, number of query addresses, 1 <= Q <= 20)
Lines N+3..N+Q+2:  <addr_hex>   (hex integer with "0x" prefix)
```

Regions in the map are guaranteed to be non-overlapping.

## Output Format

For each query address, print one line:

- If the address falls within a region (`base <= addr < base + size`):
  ```
  <name> 0x<offset>
  ```
  where `<offset>` is printed in lowercase hex with **no leading zeros** (but `0x0` for offset zero).

- If the address does not fall in any region:
  ```
  UNMAPPED
  ```

## Constraints

- All addresses and sizes fit in a 64-bit unsigned integer.
- Region sizes are at least 1 byte.
- No two regions overlap.
- `0x` prefix is always present on hex values in input.

## Sample Input

```
4
Flash 0x08000000 0x00080000
SRAM 0x20000000 0x00020000
GPIOA 0x40023800 0x00000400
TIM2 0x40000000 0x00000400
5
0x08000000
0x20000040
0x400239FF
0x40023C00
0x10000000
```

## Sample Output

```
Flash 0x0
SRAM 0x40
GPIOA 0x1ff
UNMAPPED
UNMAPPED
```

## Explanation

- `0x08000000` is exactly at the Flash base, so offset = 0.
- `0x20000040` is 64 bytes into SRAM.
- `0x400239FF` is `0x400239FF - 0x40023800 = 0x1FF` into GPIOA. The region ends at `0x40023BFF` so this is valid.
- `0x40023C00` is one byte past GPIOA's last byte (`0x40023BFF`), so it is UNMAPPED.
- `0x10000000` falls in a gap between Flash and SRAM — UNMAPPED.
