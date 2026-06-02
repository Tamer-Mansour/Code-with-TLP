# Multilevel Page Tables

A flat single-level page table for a 64-bit process would need to store 2^52 entries (with 4 KB pages), consuming petabytes of RAM — clearly impractical. Multilevel page tables solve this by building a **tree of tables**: inner nodes hold pointers to the next-level tables, and only the leaf nodes that are actually needed are allocated.

## The Core Insight

Most processes use only a small fraction of their 64-bit address space. With a multilevel design, you only allocate inner tables for regions the process actually touches. Unused regions simply have a NULL pointer in a higher-level table — no memory wasted.

## Two-Level Page Table (32-bit Example)

Split the 20-bit VPN into two 10-bit halves:

```
Virtual Address (32-bit, 4 KB pages):
+----------+----------+------------+
|  VPN[1]  |  VPN[0]  |   Offset   |
|  10 bits |  10 bits |  12 bits   |
+----------+----------+------------+
```

Translation steps:

1. Use `VPN[1]` (10 bits) to index into the **Page Directory** — contains 1024 entries pointing to second-level tables.
2. Use `VPN[0]` (10 bits) to index into the **Page Table** pointed to by that directory entry.
3. Read the PTE → extract PFN.
4. Concatenate PFN + offset → physical address.

```
Page Directory (4 KB, 1024 entries × 4 bytes)
  [0] → Page Table for VPN[1]=0
  [1] → Page Table for VPN[1]=1
  ...
  [1023] → NULL (not allocated)

Each Page Table (4 KB, 1024 entries × 4 bytes)
  [k] → PTE for actual page
```

If a process only uses 4 MB at the bottom and 4 MB at the top of its address space, only 2 Page Directories and 2 leaf tables need to be allocated — far less than a full flat table.

## Four-Level Page Table (x86-64)

Modern x86-64 uses a 48-bit virtual address with 4 levels, each indexed by 9 bits:

```
Virtual Address (48-bit canonical):
+-------+-------+-------+-------+------------+
| PML4  | PDPT  |  PD   |  PT   |   Offset   |
| 9 bits| 9 bits| 9 bits| 9 bits|  12 bits   |
+-------+-------+-------+-------+------------+
```

| Level | Table Name | Size |
|-------|-----------|------|
| 1 | Page Map Level 4 (PML4) | 4 KB (512 × 8-byte entries) |
| 2 | Page Directory Pointer Table (PDPT) | 4 KB per allocated entry |
| 3 | Page Directory (PD) | 4 KB per allocated entry |
| 4 | Page Table (PT) | 4 KB per allocated entry |

CR3 holds the physical address of the PML4. Each level adds a pointer indirection, so a full walk on a cold TLB costs 4 memory reads.

Linux on x86-64 also supports a 5-level design (PML5) for 57-bit addresses, expanding the address space to 128 PB.

## Huge Pages

Each level of the table has a **Page Size** bit that can short-circuit the walk:

- PD entry with PS=1 → maps a **2 MB huge page** (skips the PT level).
- PDPT entry with PS=1 → maps a **1 GB huge page** (skips PD and PT levels).

Huge pages reduce TLB pressure for large working sets (databases, HPC) at the cost of potential internal fragmentation.

## Memory Cost Analysis

For a process using a 32-bit address space with 4 KB pages and a 2-level scheme:

| Scenario | Memory used |
|----------|-------------|
| Flat single-level | Always 4 MB |
| 2-level, 1 page allocated | 4 KB (dir) + 4 KB (one leaf) = 8 KB |
| 2-level, fully packed | 4 KB + 1024×4 KB ≈ 4 MB (same worst case) |

The worst case matches the flat table; the best case is dramatically better.

## Code Sketch — Two-Level Walk

```c
typedef uint32_t pte_t;

pte_t* page_directory;  // physical base, 1024 entries

uint32_t translate(uint32_t va) {
    uint32_t vpn1   = va >> 22;          // top 10 bits
    uint32_t vpn0   = (va >> 12) & 0x3FF; // next 10 bits
    uint32_t offset = va & 0xFFF;

    pte_t dir_entry = page_directory[vpn1];
    if (!(dir_entry & PRESENT)) page_fault();

    pte_t* page_table = (pte_t*)(dir_entry & ~0xFFF); // strip flags
    pte_t  pte        = page_table[vpn0];
    if (!(pte & PRESENT)) page_fault();

    uint32_t pfn = pte >> 12;
    return (pfn << 12) | offset;
}
```

## Common Pitfalls

- Forgetting that each level table must be page-aligned (the lower 12 bits of a table pointer are used for flags, not address bits).
- Assuming 4 levels on all 64-bit systems — ARM64 uses 3 or 4 levels depending on VA size; RISC-V supports Sv39 (3-level) and Sv48 (4-level).
- Overlooking that a TLB miss now costs multiple RAM accesses, making TLB hit rate even more important.

> **Interview answer:** A multilevel page table replaces the huge flat array with a tree of smaller tables, only allocating inner nodes for virtual address regions the process actually uses. x86-64 uses four 9-bit-indexed levels (PML4 → PDPT → PD → PT) plus a 12-bit offset, with CR3 pointing to the PML4.
