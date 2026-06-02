# Prompt: Cache Address Decoder

## Problem Statement

A cache controller must split every memory address into three fields before it can check for a hit: the **tag** (identifies which memory block is cached), the **index** (selects the cache set), and the **byte offset** (selects a byte within the cache line).

Given a cache configuration and a list of hexadecimal memory addresses, output the decoded tag, index, and offset for each address.

## Address Field Formulas

```
offset_bits = log2(line_size_bytes)
index_bits  = log2(number_of_sets)
tag_bits    = address_bits - index_bits - offset_bits

offset = address & ((1 << offset_bits) - 1)
index  = (address >> offset_bits) & ((1 << index_bits) - 1)
tag    = address >> (offset_bits + index_bits)
```

## Input Format

```
line_size sets associativity address_bits
hex_addr_1
hex_addr_2
...
```

- Line 1: four space-separated integers.
  - `line_size` — cache line size in bytes (power of 2, 16–128).
  - `sets` — number of cache sets (power of 2, 1–256).
  - `associativity` — N-way (1–16; not needed for decoding but provided for context).
  - `address_bits` — width of the address in bits (16 or 32).
- Lines 2+: one address per line as an unsigned hexadecimal integer **without** a `0x` prefix.
- At most 20 addresses.

## Output Format

For each address, one line in exactly this format:

```
tag=<decimal> index=<decimal> offset=<decimal>
```

All values are printed as non-negative base-10 integers separated by single spaces, in the order shown.

## Constraints

- `line_size` is always a power of 2 and in [16, 128].
- `sets` is always a power of 2 and in [1, 256].
- `address_bits` is 16 or 32.
- All hex addresses fit within `address_bits` (no leading `0x`).
- 1 ≤ number of addresses ≤ 20.
- No negative addresses.

## Sample Input 1

```
64 16 4 32
000007C4
00001FC4
00000040
```

## Sample Output 1

```
tag=1 index=15 offset=4
tag=7 index=15 offset=4
tag=0 index=1 offset=0
```

### Explanation of Sample 1

Configuration: line_size=64, sets=16, address_bits=32.
- offset_bits = log2(64) = 6
- index_bits  = log2(16) = 4
- tag_bits    = 32 - 4 - 6 = 22

Address `0x000007C4` = decimal 1988:
- offset = 1988 & 0x3F = 1988 & 63 = 4
- index  = (1988 >> 6) & 0xF = 31 & 15 = 15
- tag    = 1988 >> 10 = 1

Address `0x00001FC4` = decimal 8132:
- offset = 8132 & 63 = 4
- index  = (8132 >> 6) & 15 = 127 & 15 = 15
- tag    = 8132 >> 10 = 7

Address `0x00000040` = decimal 64:
- offset = 64 & 63 = 0
- index  = (64 >> 6) & 15 = 1 & 15 = 1
- tag    = 64 >> 10 = 0

## Sample Input 2

```
32 8 2 16
0000
0020
01FF
```

## Sample Output 2

```
tag=0 index=0 offset=0
tag=0 index=1 offset=0
tag=1 index=7 offset=31
```

### Explanation of Sample 2

Configuration: line_size=32, sets=8, address_bits=16.
- offset_bits = log2(32) = 5
- index_bits  = log2(8)  = 3
- tag_bits    = 16 - 3 - 5 = 8

Address `0x0000` = 0: offset=0, index=0, tag=0
Address `0x0020` = 32: offset=0, index=1, tag=0
Address `0x01FF` = 511: offset=31, index=7, tag=1

## Time Limit

3000 ms

## Memory Limit

256 MB
