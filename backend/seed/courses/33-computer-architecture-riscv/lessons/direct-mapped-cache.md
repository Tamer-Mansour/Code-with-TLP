# Direct-Mapped Cache

A **direct-mapped cache** is the simplest cache organisation: each memory block maps to exactly one cache slot. There is no choice about where a block goes — the index bits in the address determine the slot, and only one block can occupy that slot at any given time.

## How It Works

Given a cache with `S` slots (sets), a memory block at address `A` maps to slot `A mod S`. Because `S` is always a power of two, this is implemented by extracting the low-order `log2(S)` bits of the block address — no division needed.

```
Slot number = (block address) mod S
            = index field of the physical address
```

When a read request arrives:

1. Extract the **index** field → go to that slot.
2. Check the **valid bit** → if 0, it's a cold miss.
3. Compare the stored **tag** to the address tag field.
   - Match → **hit**, return data.
   - No match → **conflict miss**, evict the current line, fetch the new block from RAM.

## Worked Example

Cache configuration:
- Total size: 8 KB = 8192 bytes
- Line size: 64 bytes → 8192 / 64 = **128 slots**
- 32-bit address space

Bit breakdown:

```
Offset = log2(64)  =  6 bits  (bits 5:0)
Index  = log2(128) =  7 bits  (bits 12:6)
Tag    = 32 - 7 - 6 = 19 bits (bits 31:13)
```

Access sequence for two arrays `A` and `B`, each 8 KB, both starting at addresses that produce the same index field:

```c
double a[1024];   // 8 KB, starts at 0x0000_0000
double b[1024];   // 8 KB, starts at 0x0000_2000
```

`a[0]` is at `0x0000_0000` → index 0.
`b[0]` is at `0x0000_2000` → index 0 (different tag).

Accessing `a[0]` then `b[0]` evicts `a[0]`'s line. A loop over both arrays in alternation suffers a conflict miss on every access — **cache thrashing**.

## Hardware Simplicity

Direct-mapped cache requires no replacement policy logic — there is never a choice. The comparator circuit compares exactly one stored tag. This makes L1 caches in some designs direct-mapped because the single tag comparison keeps cycle time short.

```
Read request:
  index bits → SRAM row select
  tag bits   → single comparator
  hit/miss   → 1-cycle decision
```

## Advantages and Disadvantages

| Aspect         | Direct-Mapped |
|----------------|---------------|
| Hardware cost  | Lowest — one comparator per set |
| Access time    | Fastest — parallel tag check and data read possible |
| Conflict misses | Highest — blocks with same index evict each other |
| Thrashing risk | High — two hot arrays at same index are fatal |

## Avoiding Thrashing: Practical Tips

- **Pad arrays** so their sizes are not exact multiples of the cache size.
- **Interleave** data structures so competing hot data maps to different indices.
- **Use a higher-associativity cache** (the real hardware fix — covered in the next lesson).

```c
// Padding trick: add one extra element to shift the base address
double a[1024 + 8];  // 64 extra bytes moves 'a' to a different cache index
double b[1024];
```

## Conflict Miss vs Cold Miss vs Capacity Miss

- **Cold (compulsory) miss** — first access to any block; inevitable.
- **Conflict miss** — two blocks map to the same slot and evict each other; direct-mapped suffers the most.
- **Capacity miss** — the working set is larger than the cache; even a fully associative cache would miss.

> **Interview answer:** In a direct-mapped cache, each memory block maps to exactly one slot determined by `(block_address) mod (number_of_slots)`. It is the fastest and simplest design but prone to conflict misses — two blocks with the same index evict each other even when most cache slots are empty.
