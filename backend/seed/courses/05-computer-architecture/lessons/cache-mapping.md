# Cache Mapping and Address Decomposition

To determine whether a memory access hits or misses in O(1) time, the cache controller decomposes every memory address into three fields and looks up the corresponding set. This lesson walks through the complete bit-level arithmetic with multiple worked examples.

## Address Decomposition

For a cache with the following parameters:
- **C** = number of sets
- **B** = bytes per cache line (block size)
- **N** = associativity (ways per set)
- Total cache capacity = C × N × B bytes

A physical address is split into three fields (from low to high bits):

```
|       Tag        |   Set Index   |  Block Offset  |
  [addr_bits-1 : s+o]  [s+o-1 : o]   [o-1 : 0]

Block Offset bits  o = log2(B)      selects byte within the cache line
Set Index bits     s = log2(C)      selects which set to look in
Tag bits           t = addr_bits − s − o   compared against stored tags
```

The tag is what the hardware compares to determine a hit or miss. It uniquely identifies which memory block occupies a given cache set.

## Worked Example 1: Direct-Mapped Cache

**Configuration:**
- 16 KB direct-mapped (N=1)
- 64-byte cache lines → C = 16384 / 64 = 256 sets
- 32-bit address space

```
o = log2(64) = 6   (bits 5:0)
s = log2(256) = 8  (bits 13:6)
t = 32 - 8 - 6 = 18 (bits 31:14)
```

**Decompose address 0x00002C80:**

```
0x00002C80 = 0000 0000 0000 0000 0010 1100 1000 0000

Bits 31:14 (tag)   = 00 0000 0000 0000 00  = 0x0000  → tag = 0
Bits 13:6  (index) = 10 1100 10             = 0b10110010 = 0xB2 = 178
Bits  5:0  (offset)= 00 0000                = 0

→ Look in set 178, compare tag against stored tag 0.
  If stored tag = 0 AND valid bit = 1: HIT, return byte at offset 0 in that line.
  Otherwise: MISS, fetch 64 bytes from memory starting at 0x00002C80 & ~0x3F = 0x00002C80.
```

**Decompose address 0x00006C80 (same offset and index, different tag):**

```
0x00006C80 = 0000 0000 0000 0000 0110 1100 1000 0000
Bits 31:14 (tag)    = 00 0000 0000 0000 01 = 0x0001 → tag = 1
Bits 13:6  (index)  = 10 1100 10 = 178
Bits  5:0  (offset) = 0

→ Set 178, tag 1. Conflicts with the previous block (both map to set 178)!
   Loading 0x00006C80 evicts 0x00002C80 from set 178.
```

## Worked Example 2: 4-Way Set-Associative Cache

**Configuration:**
- 32 KB, 4-way set-associative
- 64-byte cache lines → Number of sets C = 32768 / (4 × 64) = 128
- 32-bit address space

```
o = log2(64)  = 6   (bits 5:0)
s = log2(128) = 7   (bits 12:6)
t = 32 - 7 - 6 = 19 (bits 31:13)
```

**Access trace and hit/miss determination:**

Addresses (decimal → hex): 0, 64, 128, 192, 0, 64

```
B = 64 bytes, so block_number = addr / 64

addr=0:    block 0,  set = 0 mod 128 = 0,  tag = 0>>7 = 0
  → Set 0, Way 0: MISS (cold), load tag=0

addr=64:   block 1,  set = 1 mod 128 = 1,  tag = 0
  → Set 1, Way 0: MISS (cold), load tag=0

addr=128:  block 2,  set = 2 mod 128 = 2,  tag = 0
  → Set 2: MISS, load

addr=192:  block 3,  set = 3 mod 128 = 3,  tag = 0
  → Set 3: MISS, load

addr=0:    block 0,  set = 0,  tag = 0
  → Set 0: HIT (Way 0 still holds tag=0)

addr=64:   block 1,  set = 1,  tag = 0
  → Set 1: HIT
```

Result: 4 misses, 2 hits. Hit rate = 2/6 = 33%.

## Worked Example 3: Full Trace with Conflict Misses

**Configuration:** Direct-mapped, C=4 sets, B=4 bytes, 8-bit address space.

```
o = log2(4)  = 2   (bits 1:0)
s = log2(4)  = 2   (bits 3:2)
t = 8 - 2 - 2 = 4  (bits 7:4)
```

**Address trace (decimal):** 0, 4, 8, 12, 0, 4, 16, 20

```
addr=0:   binary 00000000 → tag=0000, set=00=0, offset=00  MISS  (cold)
          Set 0 ← tag=0

addr=4:   binary 00000100 → tag=0000, set=01=1, offset=00  MISS  (cold)
          Set 1 ← tag=0

addr=8:   binary 00001000 → tag=0000, set=10=2, offset=00  MISS  (cold)
          Set 2 ← tag=0

addr=12:  binary 00001100 → tag=0000, set=11=3, offset=00  MISS  (cold)
          Set 3 ← tag=0

addr=0:   tag=0, set=0 → STORED tag=0 → HIT ✓

addr=4:   tag=0, set=1 → STORED tag=0 → HIT ✓

addr=16:  binary 00010000 → tag=0001, set=00=0, offset=00  MISS  (conflict!)
          Set 0 ← tag=1  (evicts addr=0's block!)

addr=20:  binary 00010100 → tag=0001, set=01=1, offset=00  MISS  (conflict!)
          Set 1 ← tag=1  (evicts addr=4's block!)
```

Final: 6 misses, 2 hits. The conflict misses at addr=16 and addr=20 evicted the previously useful entries.

## Write Policies

### Write-Through

Every write immediately updates both the cache and the backing memory:

```
CPU write → cache line updated → memory updated in same cycle (or buffered)
```

- Pro: memory is always consistent (no stale data for other devices).
- Con: every write generates a memory bus transaction. With a 64-byte cache line and 4-byte writes, only 6.25% of each line is "payload" — very inefficient.
- Typically paired with a **write buffer** that queues memory writes, hiding some latency.

### Write-Back

Writes update only the cache line. A **dirty bit** per cache line tracks modifications:

```
CPU write → cache line updated + dirty bit set
...later...
Eviction of dirty line → write line to memory first, then evict
```

- Pro: multiple writes to the same cache line generate only one memory transaction (when evicted).
- Con: memory may be stale. Critical for **cache coherence** (multi-core) and **DMA** (device reads stale memory).

### Write-Allocate vs No-Write-Allocate

On a **write miss** (writing to an address not currently in cache):

- **Write-allocate** (used with write-back): allocate a new cache line, fetch the old memory block to fill it (so we have the unwritten bytes), then write.
- **No-write-allocate** (used with write-through): write directly to memory without allocating a cache line. If the address is read again soon, it will miss again.

**Standard pairing**: write-back + write-allocate; write-through + no-write-allocate.

## AMAT and the Benefit of Multiple Cache Levels

```
AMAT = t_hit_L1 + MR_L1 × (t_hit_L2 + MR_L2 × (t_hit_L3 + MR_L3 × t_DRAM))
```

**Worked calculation:**

| Level | Hit time | Miss rate |
|-------|----------|-----------|
| L1 | 4 cycles | 4% |
| L2 | 12 cycles | 20% |
| L3 | 40 cycles | 30% |
| DRAM | 200 cycles | — |

```
AMAT = 4 + 0.04 × (12 + 0.20 × (40 + 0.30 × 200))
     = 4 + 0.04 × (12 + 0.20 × (40 + 60))
     = 4 + 0.04 × (12 + 0.20 × 100)
     = 4 + 0.04 × (12 + 20)
     = 4 + 0.04 × 32
     = 4 + 1.28
     = 5.28 cycles
```

Without L2 and L3: AMAT = 4 + 0.04 × 200 = 12 cycles. The multi-level cache cuts AMAT from 12 to 5.28 cycles — 2.3× better.

## Virtual vs Physical Caches

Most L1 caches are **PIPT (Physically Indexed, Physically Tagged)**: they use the physical address (after TLB translation) for both the index and the tag. This avoids aliasing (two virtual addresses mapping to the same physical location appearing as separate cache entries) but requires TLB lookup before cache lookup — adding latency.

**VIPT (Virtually Indexed, Physically Tagged)** caches use the virtual address for the index but the physical tag for the comparison. If the page offset (bottom 12 bits for 4 KB pages) contains all the index bits, VIPT behaves like PIPT without aliasing — this is why L1 caches are limited to 32 KB when using 6 offset bits + 6 index bits = page-offset-aligned. Apple M-series L1 caches use 64 KB with a 4-way VIPT design that avoids aliasing at the cost of some complexity.

## Cache Coherence (Multi-Core Preview)

In a multi-core CPU, each core has its own L1 and L2 caches. When two cores hold copies of the same cache line and one modifies it, the other core's copy becomes **stale**.

The **MESI protocol** tags each cache line with one of four states:
- **M** (Modified): line is dirty; only this cache has it.
- **E** (Exclusive): line is clean; only this cache has it.
- **S** (Shared): line may exist in multiple caches (all clean).
- **I** (Invalid): line is not valid in this cache.

When core A writes to a Shared line, it broadcasts an **invalidate** message, setting all other caches' copy to Invalid before proceeding. This ensures coherence at the cost of inter-core traffic.
