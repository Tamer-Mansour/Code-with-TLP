# Exercise: Set-Associative Cache Simulator

This exercise extends the direct-mapped cache simulator to support N-way set-associativity with LRU replacement — the design used in real L1 and L2 caches.

## Background

A **set-associative cache** with N ways can hold N cache lines per set. When the set is full and a new block arrives, the **Least Recently Used (LRU)** block is evicted.

Address decomposition (same as direct-mapped):

```
block_offset_bits = log2(B)
set_index_bits    = log2(C)
tag_bits          = remaining address bits

set_index = (address >> block_offset_bits) & (C - 1)
tag       = address >> (block_offset_bits + set_index_bits)
```

LRU tracking: maintain an ordered list per set. On a hit, move the accessed block to the "most recently used" position. On a miss, if the set is full, evict the block at the "least recently used" position.

## When Does Associativity Help?

With a **direct-mapped** (1-way) cache, two addresses that map to the same set evict each other on every access — a **conflict miss**. A 2-way cache lets both reside simultaneously, eliminating the conflict.

## Task

Simulate the described cache. Read the configuration and access sequence from stdin, print `<hits> <misses>`.

## Example

```
Input:
4 4 1 8
0
4
8
12
0
4
8
12

Output: 4 4
```

The direct-mapped cache (N=1) has 4 sets. Addresses 0, 4, 8, 12 each map to set 0, 1, 2, 3. After the first four cold misses, each address revisits its unique set and hits on the second pass.
