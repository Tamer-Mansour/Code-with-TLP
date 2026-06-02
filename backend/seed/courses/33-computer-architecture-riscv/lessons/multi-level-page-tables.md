# Multi-Level and Hierarchical Page Tables

A flat, single-level page table works fine for 32-bit address spaces if you do not mind allocating up to 4 MiB of page-table memory per process. For 64-bit address spaces it fails completely: a Sv39 flat table would need 2^27 entries × 8 bytes = **1 GiB per process**. Multi-level page tables solve this by making the table itself sparse.

## The Key Insight: Most of the Address Space Is Empty

A real process uses only a tiny fraction of its 256 TiB (Sv48) virtual address space — perhaps a few hundred megabytes spread across text, heap, stack, and shared libraries. A flat page table wastes memory representing all the unmapped regions. A **tree of page tables** only allocates nodes for regions that are actually mapped.

## Two-Level Page Tables (Sv32)

Sv32 divides the 20-bit VPN into two 10-bit halves:

```
VA (32 bits):
 ┌──────────┬──────────┬──────────────────┐
 │  VPN[1]  │  VPN[0]  │     Offset       │
 │ 10 bits  │ 10 bits  │   12 bits        │
 └──────────┴──────────┴──────────────────┘
```

```
Root page table (L1):  1024 entries × 4 B = 4 KiB   (one page)
  Each valid L1 entry points to a:
  L0 page table:       1024 entries × 4 B = 4 KiB   (one page)
    Each valid L0 entry = a PTE pointing to a physical frame.
```

If a large region of the virtual address space is unmapped, the corresponding L1 entries are simply marked invalid — no L0 tables are allocated for those regions at all.

**Worst-case size**: all 1024 L1 entries valid → 1 + 1024 = 1025 pages = ~4 MiB. Same as the flat table, but that only happens when the entire address space is mapped.

**Typical size**: 1 L1 page + a handful of L0 pages = tens of KiB.

## Three-Level Page Tables (Sv39)

RISC-V Sv39 supports a 39-bit virtual address space (512 GiB), splitting the 27-bit VPN into three 9-bit groups:

```
VA (64 bits, bits 38:0 used):
 ┌─────────┬─────────┬─────────┬──────────────────┐
 │ VPN[2]  │ VPN[1]  │ VPN[0]  │     Offset       │
 │ 9 bits  │ 9 bits  │ 9 bits  │   12 bits        │
 └─────────┴─────────┴─────────┴──────────────────┘
```

Walk:

```
1. L2_PTE_addr = (satp.PPN << 12) + VPN[2] * 8
2. Read L2 PTE → L2_PPN
3. L1_PTE_addr = (L2_PPN << 12) + VPN[1] * 8
4. Read L1 PTE → L1_PPN
5. L0_PTE_addr = (L1_PPN << 12) + VPN[0] * 8
6. Read L0 PTE → PFN + permissions
7. PA = (PFN << 12) | Offset
```

Three physical memory reads per page-table walk (before TLB caching).

## Four-Level Page Tables (Sv48 / x86-64)

Sv48 adds a fourth level for a 48-bit virtual address space (~256 TiB). x86-64 uses an identical scheme (PML4 → PDPT → PD → PT). Each level adds one memory access to the walk.

| Scheme | Levels | VA bits | Virtual range |
|---|---|---|---|
| Sv32 | 2 | 32 | 4 GiB |
| Sv39 | 3 | 39 | 512 GiB |
| Sv48 | 4 | 48 | 256 TiB |
| Sv57 | 5 | 57 | 128 PiB |

## Superpages (Huge Pages)

Any intermediate-level PTE can be marked as a **leaf** (non-pointer) PTE, meaning it directly encodes a physical frame number for a large region. This is called a **superpage** (RISC-V) or **huge page** (Linux):

- Sv39 L1 leaf PTE: maps 2 MiB at once.
- Sv39 L2 leaf PTE: maps 1 GiB at once.

Superpages reduce the number of TLB entries needed for large contiguous mappings (e.g., kernel code, GPU buffers) and eliminate intermediate table levels for those regions.

## Inverted Page Tables (Alternative)

An alternative used on some architectures (IBM POWER) is the **inverted page table**: one global table indexed by physical frame number, containing the virtual page that maps to each frame. This is O(physical RAM) rather than O(virtual address space), but lookups require hashing and collision handling.

## The Cost of Multi-Level Walks

A 3-level page-table walk = 3 memory accesses + 1 final access = 4× slowdown for every load/store if no caching. This is exactly why the **TLB** exists (next lesson).

## Common Pitfall: Root Table Must Fit in One Page

Each level of the page table occupies exactly one physical page (for the RISC-V schemes). The root table pointer in `satp` points to a single 4 KiB page. The entire tree is composed of 4 KiB nodes. This is deliberate — it keeps `mmap`/`munmap` simple and aligns cleanly with the physical allocator.

## Interview Answer

> "Multi-level page tables are trees where each node is one page. Inner nodes are arrays of pointers to child tables; leaf nodes are PTEs. Only nodes for actively mapped regions are allocated, so sparse address spaces use very little memory. The tradeoff is multiple memory accesses per TLB miss — one per level."
