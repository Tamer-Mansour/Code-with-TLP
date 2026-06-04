# Exercise: Direct-Mapped Cache Simulator

This exercise builds on cache address decomposition theory by simulating a real direct-mapped cache with hexadecimal addresses — the way memory addresses actually appear in architecture courses and hardware documentation.

## What Makes This Different

Unlike the existing Cache Hit/Miss Simulator (which takes decimal addresses), this exercise:

- Accepts hex addresses (e.g., `0x1A4`) matching real-world notation.
- Reports per-access HIT/MISS status followed by a hit rate percentage.
- Emphasizes understanding conflict misses — when two addresses map to the same cache line.

## Conflict Misses Illustrated

With CACHE_SIZE=16, BLOCK_SIZE=4 (4 cache lines):

```
Address 0x00 → index 0, tag 0
Address 0x10 → index 0, tag 1   ← same index as 0x00!

Alternating accesses to 0x00 and 0x10 produce a MISS on every single access.
This is a conflict miss — neither address stays in cache because they fight for the same line.
```

A set-associative cache with 2 ways would eliminate this conflict entirely.

## Approach

1. Parse `CACHE_SIZE`, `BLOCK_SIZE`, compute `num_lines = CACHE_SIZE // BLOCK_SIZE`.
2. Compute `offset_bits = int(log2(BLOCK_SIZE))`, `index_bits = int(log2(num_lines))`.
3. For each hex address, extract `index` and `tag` using bit shifts and masks.
4. Check and update the cache array accordingly.
5. Output HIT/MISS and final hit rate.
