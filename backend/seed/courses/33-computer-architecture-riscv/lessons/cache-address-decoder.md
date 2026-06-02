# Exercise: Decode an Address into Tag/Index/Offset

In this exercise you will implement the address-decoding logic that every cache controller performs in hardware. Given a cache configuration and a list of memory addresses, your program must split each address into its **tag**, **index (set number)**, and **byte offset** fields.

## Background

Every cache address is split into three fields, from least significant to most significant:

```
[ TAG | INDEX | OFFSET ]
```

- **Offset** — `log2(line_size)` bits. Selects a byte within the cache line.
- **Index** — `log2(number_of_sets)` bits. Selects which set (or slot for direct-mapped) to inspect.
- **Tag** — remaining upper bits. Stored in the cache to verify a hit.

For an N-way set-associative cache:

```
number_of_sets = total_cache_size / (line_size * N)
offset_bits    = log2(line_size)
index_bits     = log2(number_of_sets)
tag_bits       = address_bits - index_bits - offset_bits
```

## What You Will Implement

Write a program that reads a cache configuration and one or more hex addresses, then prints the tag, index, and offset for each address in decimal.

## Input Format

```
line_size_bytes sets associativity address_bits
addr1
addr2
...
```

- First line: four space-separated integers — cache line size (power of 2), number of sets (power of 2), associativity (N-way, unused for the decode itself), and address width in bits.
- Following lines: one hex address per line (no `0x` prefix), up to 20 addresses.

## Output Format

For each address, print one line:

```
tag=<decimal> index=<decimal> offset=<decimal>
```

## Sample Input

```
64 16 4 32
000007C4
00001FC4
00000040
```

## Sample Output

```
tag=1 index=15 offset=4
tag=7 index=15 offset=4
tag=0 index=1 offset=0
```

## Constraints

- Line size: 16 to 128 bytes, always a power of 2.
- Sets: 1 to 256, always a power of 2.
- Associativity: 1 to 16.
- Address bits: 16 or 32.
- All addresses fit within address_bits.
- Number of addresses: 1 to 20.

## Getting Started

The core operation is pure bit manipulation:

```python
offset_bits = int(math.log2(line_size))
index_bits  = int(math.log2(sets))
tag_bits    = address_bits - index_bits - offset_bits

offset_mask = (1 << offset_bits) - 1
index_mask  = (1 << index_bits)  - 1

offset = addr & offset_mask
index  = (addr >> offset_bits) & index_mask
tag    = addr >> (offset_bits + index_bits)
```

Implement this logic, read the input, and print the decoded fields for each address.
