# Virtual Memory, Pages, and the MMU

Virtual memory is one of the most important abstractions an OS provides. It gives every process the illusion of owning the entire address space while the physical RAM is shared and managed invisibly underneath.

## Why Virtual Memory Exists

Without virtual memory:

- Two programs could overwrite each other's data.
- A buggy program could corrupt the OS kernel.
- Programs would be limited to physical RAM size.
- Loading a program would require knowing its exact physical placement.

Virtual memory solves all four problems by inserting a translation layer between the addresses a program uses and the addresses that actually exist in RAM.

## Virtual vs. Physical Addresses

| Term | Meaning |
|---|---|
| **Virtual address** | The address a CPU instruction references (what your code sees) |
| **Physical address** | The actual address on the RAM chips |
| **Translation** | Performed by the MMU on every memory access |

Each process has its own **virtual address space** (typically 48-bit on x86-64 Linux, giving 256 TB). Two processes can each have a pointer to address `0x7fff0000` and they will map to completely different physical frames.

## Pages and Frames

The address space is divided into fixed-size chunks:

- **Page** — a chunk of the virtual address space (commonly **4 KB** on x86).
- **Frame** (or physical page frame) — the corresponding chunk of physical RAM.

A **page table** is a per-process data structure mapping virtual page numbers (VPN) to physical frame numbers (PFN).

```
Virtual address: [  VPN  |  Offset  ]
                 [  20b  |   12b    ]   (for 4 KB pages)
```

The offset within a page is the same in both virtual and physical space — only the VPN is translated.

## The Memory Management Unit (MMU)

The MMU is hardware (part of the CPU) that performs address translation on every load and store:

1. Extract the **virtual page number (VPN)** from the address.
2. Look up the VPN in the **page table** (or TLB — see below).
3. Get the **physical frame number (PFN)**.
4. Combine PFN with the **offset** to form the physical address.

```
Physical address = (PFN << page_size_bits) | offset
```

If no valid mapping exists, the MMU raises a **page fault**, which traps to the OS.

## The TLB: Translation Lookaside Buffer

Walking the page table on every memory access is expensive. The **TLB** is a small, fast, fully-associative cache inside the CPU that stores recent VPN→PFN translations.

- A **TLB hit** resolves translation in 1–2 cycles.
- A **TLB miss** causes a hardware (or software) page-table walk — typically 20–100+ cycles.
- Context switches **flush the TLB** (or tag entries with an ASID to avoid flushing).

> **Interview answer:** The MMU translates virtual to physical addresses using page tables; the TLB caches recent translations to avoid the full walk on every access.

## Page Table Entries and Protection Bits

Each page table entry (PTE) contains:

- **Present bit** — is the page in RAM?
- **Read / Write / Execute bits** — access permissions.
- **Dirty bit** — has the page been written?
- **Accessed bit** — has the page been read?
- **Physical frame number**.

Attempting to write a read-only page triggers a **protection fault** (segfault in user space).

## Demand Paging and Swap

Not all pages need to be in RAM at once:

1. OS loads only the pages a process actually touches (**demand paging**).
2. When RAM is full, the OS evicts cold pages to **swap space** on disk.
3. Accessing a swapped-out page raises a page fault; the OS reads the page back.

This allows processes to use more memory than physical RAM, at the cost of disk I/O when swap is hit heavily (**thrashing**).

## Multi-Level Page Tables

A flat 4 GB page table for a 32-bit process would itself be 4 MB. Modern systems use **multi-level page tables** (2, 3, or 4 levels on x86-64) so that only the portions of the address space actually used need entries.

```
48-bit virtual address on x86-64:
[ PML4 (9b) | PDPT (9b) | PD (9b) | PT (9b) | Offset (12b) ]
```

Each level is a 512-entry table; only present levels are allocated.

## Common Pitfalls

- Confusing page size (virtual granularity) with frame size (they are always equal).
- Forgetting that TLB is flushed on context switch — this is a real scheduling cost.
- Assuming virtual addresses are contiguous in physical memory — they are not.
