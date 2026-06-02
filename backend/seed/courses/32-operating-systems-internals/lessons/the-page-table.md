# The Page Table and Page Table Entries

A **page table** is a per-process data structure that the OS maintains in kernel memory. It maps every virtual page number (VPN) to a physical frame number (PFN), allowing the hardware Memory Management Unit (MMU) to translate addresses on every memory access.

## Structure of a Single-Level Page Table

The simplest design is a flat array indexed by the VPN:

```
page_table[VPN] = Page Table Entry (PTE)
```

For a 32-bit address space with 4 KB pages:
- VPN = 20 bits → 2^20 = **1,048,576 entries**
- If each entry is 4 bytes → **4 MB of page table per process**

With hundreds of processes, this overhead adds up fast — one reason multi-level page tables exist.

## Page Table Entry Layout (x86-32 example)

Each PTE packs the physical frame number and several control bits into one 32-bit word:

```
 31                          12 11  9  8  7  6  5  4  3  2  1  0
+------------------------------+---+--+--+--+--+--+--+--+--+--+--+
|   Physical Frame Number      |IGN|G |PS|D |A |CD|WT|U |W |P  |
+------------------------------+---+--+--+--+--+--+--+--+--+--+--+
```

| Bit | Name | Meaning |
|-----|------|---------|
| 0 | Present (P) | 1 = page is in RAM; 0 = page fault |
| 1 | Writable (W) | 1 = read/write; 0 = read-only |
| 2 | User (U) | 1 = user-mode accessible; 0 = kernel only |
| 3 | Write-Through (WT) | Cache write policy |
| 4 | Cache Disable (CD) | Bypass cache for this page |
| 5 | Accessed (A) | Set by MMU on any read or write |
| 6 | Dirty (D) | Set by MMU on any write |
| 7 | Page Size (PS) | Used in multi-level tables for huge pages |
| 31:12 | Frame Number | Physical address of the frame (upper 20 bits) |

## Locating the Page Table

The CPU register **CR3** (on x86) holds the physical address of the current process's page table base. On a context switch, the OS loads the new process's page table address into CR3, instantly switching the entire address space.

```c
// Conceptual OS context-switch snippet (x86)
void switch_to(struct process *next) {
    write_cr3(next->page_table_phys_addr); // swap address space
    // restore registers, stack pointer, etc.
}
```

## Translation Walk (hardware perspective)

On every memory access the MMU performs:

1. Extract VPN from the virtual address.
2. Multiply VPN by entry size, add to page table base → PTE address.
3. Read PTE from memory (or TLB cache).
4. Check Present bit — if 0, raise a **page fault**.
5. Combine PFN from PTE with offset from virtual address → physical address.

This walk costs a memory access itself, which is why the **Translation Lookaside Buffer (TLB)** caches recent VPN→PFN translations.

## Page Table Size Problem

| Address bits | Page size | VPN bits | Entries | Table size (4-byte PTEs) |
|-------------|-----------|----------|---------|--------------------------|
| 32 | 4 KB | 20 | 1M | 4 MB |
| 64 | 4 KB | 52 | 4P | 16 PB (impractical flat) |

This is why 64-bit systems always use multi-level page tables (2-, 3-, or 4-level) or other compact representations.

## Worked Example: Reading a PTE

Suppose a PTE for VPN 5 contains the value `0x00123867`:

```
0x00123867 = 0000 0000 0001 0010 0011 1000 0110 0111
                                                  ↑↑↑
                                                P=1, W=1, U=1
Upper 20 bits: 0x00123 → PFN = 0x123 → frame 291
```

The page is present (P=1), writable (W=1), user-accessible (U=1), and lives in frame 291.

## Common Pitfalls

- Forgetting that a PTE with P=0 does not necessarily mean the data is gone — it could be swapped out to disk.
- Assuming the page table itself lives in virtual memory — the base address stored in CR3 is a *physical* address.
- Ignoring the Accessed and Dirty bits, which the OS uses for LRU approximation and detecting which pages need write-back on eviction.

> **Interview answer:** A page table is a per-process array indexed by virtual page number; each entry (PTE) stores the physical frame number plus status bits (Present, Dirty, Accessed, protection). The hardware MMU reads it on every address translation, and the CPU register CR3 points to the current process's table base.
