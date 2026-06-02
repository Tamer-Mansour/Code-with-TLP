# Cache Lines, Blocks, and Tags

When the CPU requests a single byte from memory, the cache does not fetch just that byte. It fetches an aligned chunk called a **cache line** (also called a **cache block**). Understanding this unit of transfer — and how the hardware uses tags to track what each line holds — is the foundation for every cache design question.

## What Is a Cache Line?

A cache line is the minimum unit of data transferred between RAM and cache. On virtually every modern processor (x86-64, ARM, RISC-V) the cache line is **64 bytes** (512 bits).

When address `0x1000_0005` is read:
1. The CPU checks whether the line containing that address is in cache.
2. If not (a miss), the cache fetches the entire 64-byte aligned block `0x1000_0000` – `0x1000_003F` from RAM.
3. The requested byte is extracted from the line and forwarded to the register.

This is why sequential array access is so efficient: the first element causes one miss; the next 15 elements (for 4-byte ints in a 64-byte line) are already in cache.

## Anatomy of a Cache Address

To track which memory block a cache line holds, hardware splits every memory address into three fields:

```
| TAG | INDEX | OFFSET |
```

- **Offset** — which byte within the cache line. For a 64-byte line, this is the low `log2(64) = 6` bits.
- **Index** — which cache set (slot) the line maps to. Depends on the number of sets in the cache.
- **Tag** — the remaining high bits, stored alongside the data. Used to verify whether the cached line matches the requested address.

### Worked Example

Assume a direct-mapped cache with:
- 1024 bytes total capacity
- 64-byte cache lines → 1024 / 64 = **16 sets** (lines)
- 32-bit address space

Bit breakdown:

```
Offset  = log2(64)  = 6 bits   (bits 5:0)
Index   = log2(16)  = 4 bits   (bits 9:6)
Tag     = 32 - 4 - 6 = 22 bits (bits 31:10)
```

For address `0x0000_07C4` = `0000 0000 0000 0000 0000 0111 1100 0100`:

```
Binary: 0000_0000_0000_0000_0000_0111_1100_0100
                                        ------  offset = 0b000100 = 4
                                    ----        index  = 0b1111   = 15
0000_0000_0000_0000_0000_01                     tag    = 0x01
```

The cache looks in set 15. If the tag stored there is `0x01` and the valid bit is set, it is a hit. Otherwise it is a miss.

## Valid Bit and Tag Storage

Each cache line in hardware stores:

| Field       | Size (typical) | Purpose |
|-------------|----------------|---------|
| Valid bit   | 1 bit          | Is this slot populated? |
| Tag         | varies         | Which memory block is here? |
| Data        | 64 bytes       | The actual cached bytes |
| Dirty bit   | 1 bit (write-back only) | Has this line been modified? |

On power-up or a cold start, all valid bits are 0 — the cache is empty.

## Why 64 Bytes?

The 64-byte size is an industry convergence point:
- Small enough that transferring one line over the memory bus takes modest time (~10 ns on modern DDR5).
- Large enough to capture typical spatial locality (8 doubles, 16 ints, or 64 chars).

Larger lines capture more spatial locality but increase the cost of each miss and waste bandwidth when access is not sequential (e.g., pointer chasing in linked lists).

## Common Pitfall: False Sharing

In multi-core systems, two threads updating different variables that happen to sit in the **same 64-byte cache line** cause the coherence protocol to ping-pong that line between cores — even though neither thread reads the other's data. This is **false sharing** and can destroy performance.

```c
// Bad: x and y share a cache line
struct Counters { int x; int y; } c;

// Better: pad to separate cache lines
struct Counters {
    int x; char pad1[60];
    int y; char pad2[60];
};
```

> **Interview answer:** A cache line is the 64-byte chunk transferred atomically between RAM and cache. An address is split into tag (identifies which block), index (which cache set to look in), and offset (which byte within the line). The tag is stored with the data so the hardware can verify a hit.
