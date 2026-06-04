# Direct-Mapped Cache Simulator

A **direct-mapped cache** is the simplest cache organization: every memory block maps to exactly one cache slot (set). Understanding it in depth is the fastest path to understanding all other cache organizations, because set-associative caches are just groups of direct-mapped caches operating in parallel.

## Address Decomposition

For a direct-mapped cache with `C` bytes total and `B` bytes per block:

```
Number of sets (lines) = C / B

offset_bits = log2(B)      — selects byte within a block
index_bits  = log2(C/B)    — selects the cache slot
tag_bits    = XLEN - index_bits - offset_bits
```

For a 64-byte cache with 16-byte blocks (4 sets):

```
offset_bits = log2(16) = 4    (bits [3:0])
index_bits  = log2(4)  = 2    (bits [5:4])
tag_bits    = 32 - 2 - 4 = 26 (bits [31:6])
```

Address `0x00000014` = 20 decimal:

```
binary: 0000 0000 0000 0000 0000 0000 0001 0100
tag    = 0b000000...000 = 0
index  = 0b01 = 1
offset = 0b0100 = 4
```

## Cache Lookup Logic

On every access (read or write):

1. Extract `index` from the address to select the cache slot.
2. Compare the stored `tag` in that slot against the address `tag`.
3. Check the `valid` bit.
4. If both match: **HIT** — the data is in cache.
5. Otherwise: **MISS** — fetch the entire block from memory into this slot, replacing whatever was there.

## Write Policy: Write-Allocate

This simulator uses **write-allocate** (also called fetch-on-write): on a write miss, the block is first loaded into the cache, then the write proceeds. This pairs with a **write-back** policy in most real implementations (dirty data is written to memory only on eviction), but the simulator tracks only hits and misses.

The alternative (no-write-allocate) skips loading on a write miss, sending the write directly to memory.

## Conflict Misses: The Pitfall of Direct Mapping

Addresses that differ only in their tag but share the same index will **thrash** each other out of the cache. Classic example with a 64-byte/16-byte-block cache (4 sets, index uses bits [5:4]):

```
0x00000000 → index=0
0x00000040 → index=0   ← same slot as 0x00
0x00000080 → index=0   ← same slot again
```

Accessing these three addresses in a loop causes every access to be a miss, even though the cache has room for four distinct blocks. This conflict-miss problem motivates set-associative caches.

## Miss Classification: The Three Cs

| Miss Type       | Cause                                    | Cure                                 |
|-----------------|------------------------------------------|--------------------------------------|
| Compulsory (cold) | First access to a block ever           | Prefetching, larger blocks           |
| Capacity        | Working set larger than cache            | Larger cache                         |
| Conflict        | Two blocks map to the same index/set     | Higher associativity, victim cache   |

Direct-mapped caches suffer maximally from conflict misses compared to higher-associativity designs of the same total size.

## AMAT Refresher

Average Memory Access Time (AMAT):

```
AMAT = Hit_time + Miss_rate × Miss_penalty
```

A 32 KiB L1 cache with 1-cycle hit time, 5% miss rate, and 100-cycle miss penalty to DRAM gives:

```
AMAT = 1 + 0.05 × 100 = 6 cycles
```

## RISC-V and Caches

The RISC-V ISA is intentionally silent about cache implementation — it specifies no cache size, associativity, or replacement policy. Real cores range from no cache (bare Ibex microcontroller) to multi-level inclusive/exclusive hierarchies (SiFive HiFive Unmatched, BOOM OOO core). The `FENCE` instruction provides explicit memory ordering across the hierarchy when needed.

## Further Reading

- *Computer Organization and Design RISC-V Edition* by Patterson and Hennessy — Chapter 5: Large and Fast: Exploiting Memory Hierarchy.
- *Digital Design and Computer Architecture: RISC-V Edition* by Harris and Harris — Chapter 8: Memory Systems, with free companion slides at https://pages.hmc.edu/harris/ddca/ddcarv.html.
- MIT 6.004 Computation Structures — Problem sets on cache performance (https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/).
