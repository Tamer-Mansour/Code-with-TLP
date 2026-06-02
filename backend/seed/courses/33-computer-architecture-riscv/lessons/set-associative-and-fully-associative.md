# Set-Associative and Fully Associative Caches

Direct-mapped cache suffers from conflict misses because only one block can occupy each slot. **Set-associative** and **fully associative** caches add flexibility — a block can go into any of several slots — reducing conflicts at the cost of slightly more hardware.

## Set-Associative Cache

An **N-way set-associative cache** groups its slots into **sets** of N lines each. A memory block maps to exactly one set (determined by the index bits), but within that set it can occupy any of the N **ways**.

```
Number of sets = Total lines / N
Index bits     = log2(Number of sets)
```

For each access:
1. Use index bits to select the set.
2. **Compare the tag against all N ways in parallel** (N comparators).
3. If any way matches and is valid → hit; return data from that way.
4. If no match → miss; choose a victim way using the replacement policy, then load the new block.

### Worked Example

Cache: 16 KB, 64-byte lines, 4-way set-associative.

```
Total lines = 16384 / 64 = 256
Sets        = 256 / 4    = 64
Offset bits = log2(64)   = 6
Index bits  = log2(64)   = 6
Tag bits    = 32 - 6 - 6 = 20
```

Two arrays that caused thrashing in a direct-mapped cache now have **4 chances** to coexist in the same set. As long as no more than 4 hot blocks map to the same set, there are no conflict misses.

### Common Associativity Levels

| N-way | Typical use |
|-------|-------------|
| 2-way | Older L1 caches |
| 4-way | Common L1 today |
| 8-way | L2 caches |
| 16-way | L3 caches |

## Fully Associative Cache

A **fully associative cache** has a single set that contains all lines. A block can go anywhere. There is no index field — the entire remaining address (after the offset) is the tag.

```
Offset bits = log2(line size)
Tag bits    = address bits - offset bits
Index bits  = 0
```

Every access must compare the incoming tag against **all** stored tags simultaneously. This requires N comparators (one per line). For large caches this is prohibitively expensive in silicon area and power, so fully associative is reserved for small, critical structures like TLBs (Translation Lookaside Buffers) and small victim caches.

## Comparison

| Property           | Direct-Mapped | N-Way Set-Associative | Fully Associative |
|--------------------|---------------|-----------------------|-------------------|
| Sets               | # lines       | # lines / N           | 1                 |
| Ways per set       | 1             | N                     | All lines         |
| Comparators needed | 1             | N                     | All lines         |
| Conflict misses    | Highest       | Reduced by N          | Zero              |
| Hardware cost      | Lowest        | Moderate              | Highest           |
| Replacement policy | None needed   | Required              | Required          |

## Visualising a 2-Way Set-Associative Cache

```
Set 0:  [ Way 0: tag=0x1A | data ] [ Way 1: tag=0x3C | data ]
Set 1:  [ Way 0: tag=0x02 | data ] [ Way 1: empty         ]
Set 2:  [ Way 0: tag=0x5F | data ] [ Way 1: tag=0x11 | data ]
...
```

A new block mapping to Set 1 can fill Way 1 without evicting anything. The same block mapping to Set 0 (full) would need to evict Way 0 or Way 1 based on the replacement policy.

## The Associativity Sweet Spot

Studies consistently show:
- Going from 1-way to 2-way cuts conflict misses dramatically.
- Going from 2-way to 4-way gives another significant improvement.
- Beyond 8-way, the returns diminish and the comparator cost grows linearly.

Modern L1 caches are typically **4-way to 8-way set-associative** — enough associativity to eliminate most conflicts while keeping the tag lookup within a single clock cycle.

## RISC-V Context

RISC-V does not mandate a cache organisation; it is implementation-defined. Open-source RISC-V cores (SiFive E21, CVA6) typically use 4-way set-associative L1 caches matching industry norms.

> **Interview answer:** An N-way set-associative cache divides the cache into sets, each holding N lines. A block maps to one set by index but can use any of its N ways, reducing conflict misses. Fully associative allows any block in any line — zero conflicts but hardware cost proportional to cache size, so it is used only for small structures like TLBs.
