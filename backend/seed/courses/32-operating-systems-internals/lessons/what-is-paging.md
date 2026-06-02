# What Is Paging? Frames, Pages, and Offsets

Paging is the dominant physical-memory management scheme used by modern operating systems. It eliminates external fragmentation by dividing both virtual memory and physical memory into fixed-size units, then mapping virtual units to physical units independently for each process.

## The Core Idea

Without paging, allocating a contiguous block of RAM for every process wastes space and creates gaps (external fragmentation) that are hard to reuse. Paging sidesteps this by splitting everything into uniform chunks:

- **Page** — a fixed-size block of **virtual** address space.
- **Frame** (physical page frame) — a fixed-size block of **physical** RAM, the same size as a page.
- **Page size** — always a power of two: 4 KB (most common), 2 MB, or 1 GB (huge pages on x86-64).

Because pages and frames are the same size, any page can be stored in any free frame. The OS keeps a table that records which frame holds which page for each process.

## Virtual Address Structure

A virtual address is divided into two fields by splitting its bits at the boundary determined by the page size:

```
Virtual Address (32-bit example, 4 KB pages):
+-----------------------------+------------+
|   Virtual Page Number (VPN) |   Offset   |
|         20 bits             |   12 bits  |
+-----------------------------+------------+
```

- **Page size = 2^offset_bits**. For 4 KB pages: 2^12 = 4096 bytes.
- **Number of pages in address space = 2^VPN_bits**. For 20-bit VPN: 2^20 = 1 048 576 pages.
- **Offset** is the byte position *within* the page. It is copied unchanged into the physical address.

## Physical Address Structure

```
Physical Address:
+-----------------------------+------------+
| Physical Frame Number (PFN) |   Offset   |
|         N bits              |   12 bits  |
+-----------------------------+------------+
```

The offset is identical in both addresses; only the page/frame number changes.

## Why Powers of Two Matter

Because the page size is always a power of two, splitting an address requires only bit operations — no division:

```c
// Page size = 4096 (0x1000), 12 offset bits
uint32_t vaddr   = 0x12345678;
uint32_t vpn     = vaddr >> 12;   // upper 20 bits -> 0x12345
uint32_t offset  = vaddr & 0xFFF; // lower 12 bits -> 0x678
```

This makes the hardware translation unit (the MMU) fast and simple.

## Worked Example

**Given:** 32-bit virtual address space, 4 KB pages, physical RAM = 16 KB (4 frames).

| Frame | Contents |
|-------|----------|
| 0 | Process A page 2 |
| 1 | Process B page 0 |
| 2 | Process A page 0 |
| 3 | Process A page 1 |

Process A's virtual address `0x00001050`:
- VPN = `0x00001050 >> 12` = `1` (page 1)
- Offset = `0x00001050 & 0xFFF` = `0x050`
- Page 1 is stored in Frame 3 (from the table above)
- Physical address = `(3 << 12) | 0x050` = `0x00003050`

## Key Benefits of Paging

- **No external fragmentation** — every frame is the same size.
- **Simple free-list management** — the OS tracks free frames with a bitmap or linked list.
- **Isolation** — each process has its own page table; the MMU enforces it.
- **Enables virtual memory** — pages not currently needed can be evicted to disk (demand paging).

## Common Pitfalls

- Confusing the VPN with the physical frame number — they are different until the page table translates one to the other.
- Forgetting that the offset is never translated; it passes through unchanged.
- Assuming page size is always 4 KB — Linux supports huge pages (2 MB / 1 GB) to reduce TLB pressure.

> **Interview answer:** Paging divides virtual and physical memory into equal fixed-size pages/frames. A virtual address splits into a virtual page number (index into the page table) and an offset (byte within the page); the page table maps VPN to physical frame number, and the offset is appended unchanged to form the physical address.
