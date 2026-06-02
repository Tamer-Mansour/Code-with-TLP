# What Is Segmentation?

Segmentation is a memory management scheme that divides a process's address space into **variable-length logical units** called segments. Unlike paging — which splits memory into fixed-size pages with no regard for program structure — segmentation mirrors the way programmers actually think about a program: code is separate from data, the stack grows independently, and shared libraries are their own regions.

## The Programmer's View

Every running program naturally consists of distinct logical pieces:

- **Text segment** — compiled machine instructions (read-only)
- **Data segment** — initialized global and static variables
- **BSS segment** — zero-initialized or uninitialized globals
- **Heap segment** — dynamically allocated memory, grows upward
- **Stack segment** — local variables and call frames, grows downward
- **Shared library segments** — code/data mapped from external `.so`/`.dll` files

Segmentation formalizes this view: the OS assigns each logical region its own base address in physical memory and tracks its size (limit). The CPU enforces that no access escapes the declared bounds.

## A Logical Address in Segmented Memory

Under segmentation, a logical (virtual) address is a pair:

```
<segment number, offset>
```

The **segment number** selects an entry from the process's *segment table*. The **offset** is the byte position within that segment. The hardware adds the segment's base to the offset to produce the physical address:

```
physical address = segment_table[seg_num].base + offset
```

If `offset >= segment_table[seg_num].limit`, the CPU raises a **segmentation fault** (SIGSEGV). This is the origin of that infamous error.

## Why Variable Length?

Fixed-size partitions waste space: a 4 KB code region forced into a 64 KB partition wastes 60 KB. Segmentation allocates exactly as many bytes as each logical unit needs at the time it is created. The heap segment, for example, can grow by requesting more physical frames from the OS without disturbing any other segment.

## Protection and Sharing

Each segment table entry carries permission bits:

| Permission Bit | Meaning |
|---|---|
| R (read) | load instructions allowed |
| W (write) | store instructions allowed |
| X (execute) | instruction fetch allowed |

These bits make sharing safe. Two processes can point their text segment entries to the **same physical base address** (shared read-only code), while their stack and heap segments remain private — the hardware enforces the protection automatically.

## Worked Example

Suppose a process has three segments:

| Seg # | Base | Limit | Perms |
|---|---|---|---|
| 0 (text) | 0x00400000 | 0x2000 | R-X |
| 1 (data) | 0x00600000 | 0x1000 | RW- |
| 2 (stack) | 0x7FFF0000 | 0x8000 | RW- |

The logical address `<1, 0x200>` translates to:

```
physical = 0x00600000 + 0x200 = 0x00600200  ✓ (offset < limit 0x1000)
```

The logical address `<1, 0x2000>` would fault because `0x2000 >= 0x1000`.

## Segmentation vs. Flat Address Spaces

Modern x86-64 Linux uses a **flat (paged) address space** — segment registers (`CS`, `DS`, `SS`) are set to span the entire 64-bit space, so segmentation is effectively disabled at the OS level. Protection and isolation are handled by the page table instead. However, the *concept* of logical segments lives on in the ELF binary format and in the OS loader that maps each section into virtual memory.

## Common Pitfalls

- Confusing a **segment fault** with a page fault — they are distinct hardware events.
- Forgetting that segment limits are in **bytes**, not pages.
- Assuming segments are contiguous in physical memory — each segment is placed independently, so they often are not adjacent.

**Interview answer:** Segmentation divides a process's virtual address space into variable-length logical regions (code, data, stack, heap). Each region is addressed by a segment number plus an offset; the hardware validates the offset against a per-segment limit and adds the segment's base address to produce the physical address.
