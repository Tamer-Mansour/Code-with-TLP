# Segmentation With Paging

Pure segmentation allocates variable-length regions in physical memory. That flexibility is also its weakness: as segments are created and destroyed, physical memory develops gaps — a problem called **external fragmentation**. Pure paging, on the other hand, eliminates external fragmentation but ignores the logical structure of programs. **Segmented paging** combines both schemes to get the best of each.

## The Core Idea

In segmented paging, the programmer still sees a segmented address space (code, data, heap, stack). But each segment is **not placed as one contiguous block of physical memory**. Instead, each segment is itself divided into fixed-size pages, and those pages are scattered anywhere in physical memory via a per-segment page table.

The address translation chain becomes two-level:

```
Logical address: < segment# | page# | offset >
         |
   Segment table (one entry per segment)
         |
    Points to --> Page table for this segment
         |
    Page table entry --> Physical frame number
         |
    Physical address: < frame# | offset >
```

## Address Structure

A typical logical address under segmented paging has three fields:

| Field | Bits | Meaning |
|---|---|---|
| s (segment) | ~4–8 | Which segment descriptor to use |
| p (page) | ~8–12 | Which page within that segment |
| d (offset) | ~12 | Byte offset within the page |

The full address width is `s + p + d` bits. For a 32-bit system with 4 KB pages (12-bit offset), common split is 4 bits segment + 16 bits page + 12 bits offset.

## Step-by-Step Translation

1. Extract `s`, `p`, and `d` from the logical address.
2. Index the **segment table** with `s` to get the segment descriptor. Check Valid bit; check offset (`p` + `d`) against segment limit; check permissions.
3. Read the **page table base address** from the segment descriptor.
4. Index the **page table** with `p` to get the page table entry (PTE). Check the Present bit.
5. Extract the **frame number** from the PTE.
6. Assemble the physical address: `frame_number × page_size + d`.

```c
// Pseudocode for segmented-paging translation
uint32_t translate(uint16_t s, uint16_t p, uint16_t d) {
    SegDesc seg = segment_table[s];
    assert(seg.valid && d < seg.limit);
    assert(seg.perms & required_perm);

    PageTableEntry pte = seg.page_table[p];
    assert(pte.present);

    return (pte.frame << PAGE_BITS) | d;
}
```

## Memory Overhead

Each process now requires:
- One **segment table** (small — one entry per logical region, typically < 16 entries).
- One **page table per segment** (potentially large if the segment is big).

This is actually better than a single flat page table for sparse address spaces, because unallocated segments have no page table at all — no memory is wasted representing them.

## Worked Example

Segment table for a process:

| Seg | Page Table Base | Limit (bytes) | Perms |
|---|---|---|---|
| 0 | 0x3000 | 0x8000 | R-X |
| 1 | 0x5000 | 0x2000 | RW- |

Page size = 4 KB (0x1000).

Logical address: `<1, 1, 0x200>` (segment 1, page 1, offset 0x200)

- Segment 1 valid, limit 0x2000 → page 1, offset 0x200 is within range (page 1 starts at 0x1000, 0x1200 < 0x2000).
- Go to page table at physical 0x5000, read entry 1: frame = 0x42.
- Physical address = `0x42 × 0x1000 + 0x200 = 0x42200`.

## Why Operating Systems Moved On

Modern systems (x86-64, ARM64) replaced segmented paging with **multi-level pure paging** for three reasons:

1. **64-bit virtual spaces** are too large for practical segment tables.
2. **TLB design** is far simpler with a single-level logical address than with a (segment, page, offset) triple.
3. Compilers already provide logical separation through ELF/PE sections; the OS enforces it via page-level permissions (NX bit, write-protect).

Solaris historically used segmented paging (via `segmap`, `segvn` kernel objects). Linux and Windows use pure multi-level paging but retain the *concept* of segments through VMA (Virtual Memory Area) descriptors.

**Interview answer:** Segmented paging divides each logical segment into fixed-size pages. Translation first looks up the segment descriptor to find a per-segment page table, then uses the page number to find the physical frame. This gives logical program structure from segmentation while eliminating external fragmentation through paging.
