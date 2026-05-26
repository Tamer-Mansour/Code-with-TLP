# Memory Management: Allocation, Paging, and Segmentation

Efficient memory management is one of the OS's hardest problems. The OS must allocate physical memory to processes, protect them from each other, support more total memory usage than physically available, and do all this with minimal overhead on every single memory access.

## Physical vs. Virtual Memory

| Concept | Description |
|---------|-------------|
| **Physical memory (RAM)** | The actual DRAM chips — a flat array of bytes with hardware addresses (0 to RAM_SIZE−1) |
| **Virtual memory** | The illusion given to each process — a private, contiguous address space from 0 to 2^48−1 (on 64-bit Linux) |
| **Page table** | The per-process data structure that maps virtual page numbers to physical frame numbers |
| **MMU** | The CPU's Memory Management Unit — hardware that performs VA→PA translation on every memory access |

The MMU uses the page table to transparently translate every virtual address. If the translation fails (page not in memory), the MMU raises a **page fault** exception, and the OS handles it.

## The Problem: Fragmentation

Early OSes divided RAM into fixed or variable regions — both approaches fail at scale.

```
Fixed partitioning (equal 4MB slices):
  [ OS(8MB) | P1(4MB) | P2(4MB) | P3(4MB) | empty(4MB) ]
  P1 uses 1 MB but occupies 4 MB → INTERNAL FRAGMENTATION (wasted space inside partition)

Variable partitioning (fit processes exactly):
  [ OS(8MB) | P1(3MB) | hole(1MB) | P2(5MB) | hole(1MB) | P3(4MB) | hole(3MB) ]
  Total free = 5MB, but largest contiguous hole = 3MB → EXTERNAL FRAGMENTATION
  A process needing 4MB cannot run even though 5MB is free!
```

**Compaction** (defragmentation) moves all processes to eliminate holes — but requires updating every pointer inside every process (impractical) and halts the system during the move.

## Paging: The Solution to Fragmentation

**Paging** eliminates external fragmentation by splitting both physical memory and virtual address spaces into fixed-size units:

- **Page**: a fixed-size chunk of virtual address space (typically 4 KB on x86-64).
- **Frame**: a fixed-size chunk of physical memory (same size as a page).

Any page can be placed in any free frame — no physical contiguity required.

### Address Translation

```
Virtual address (48-bit on Linux x86-64):
  ┌──────────────────────────────────────┬────────────────┐
  │    Virtual Page Number (VPN)         │  Page Offset   │
  │        bits [47:12]                  │   bits [11:0]  │
  └──────────────────────────────────────┴────────────────┘
                   │                              │
                   │ Page Table lookup            │ (unchanged)
                   ▼                              │
  Physical Frame Number (PFN) ◄──────────────────┘
                                Physical Address = (PFN << 12) | Offset
```

**Example:** Virtual address `0x0040_1234` with 4KB pages.
- Offset = `0x234` (last 12 bits)
- VPN = `0x401`
- Page table says VPN `0x401` → PFN `0x8A3`
- Physical address = `0x8A3` << 12 | `0x234` = `0x8A3_234`

### Translation Lookaside Buffer (TLB)

Walking the page table for every memory access would require 4–5 extra memory reads per access (for multi-level page tables) — a 5× slowdown. The **TLB** is a fast, fully-associative hardware cache inside the CPU that stores recent VPN→PFN translations.

```
VA access → TLB lookup
  ├── TLB HIT  (>99% of accesses): PFN found → ~1 cycle → done
  └── TLB MISS (<1% of accesses):
       ├── Hardware page table walk (x86: hardware-managed)
       │   or software handler (MIPS/RISC-V: software-managed)
       ├── Loads the PTE into TLB → evicts an old entry (LRU)
       └── ~100 cycles (if page table is in L1/L2 cache)
```

Modern Intel CPUs have a 64-entry L1 data TLB and a 512-entry L2 TLB. With 4KB pages and 512 TLB entries, only (512 × 4KB = 2MB) of working set can be covered without TLB misses. For a database working on 100MB, TLB misses become significant — motivating **huge pages**.

**TLB flush:** On a context switch to a different process (different page table), the OS must invalidate all TLB entries (or use ASIDs — Address Space IDs — to tag entries per process). TLB flush is one of the main costs of process context switching.

## Multi-Level Page Tables

A 64-bit address space has 2^36 possible 4KB pages. A flat page table with 8-byte entries would need:

```
2^36 entries × 8 bytes = 512 GB per process
```

This is larger than most systems' total RAM — impossible. Solution: **multi-level page tables** that only allocate page table memory for regions actually used.

Linux x86-64 uses a **4-level (or 5-level) page table**:

```
Virtual address bits [47:0]:
  [47:39]  [38:30]  [29:21]  [20:12]  [11:0]
    PGD      PUD      PMD      PTE      Offset
   (9 bits) (9 bits) (9 bits) (9 bits) (12 bits)

CR3 register → PGD (Page Global Directory) base physical address
  PGD[bits47:39] → PUD entry
    PUD[bits38:30] → PMD entry
      PMD[bits29:21] → PTE (Page Table Entry)
        PTE[bits20:12] → Physical Frame Number
          + Offset = Physical Address
```

For a process that only uses code (1 page), stack (2 pages), and heap (10 pages):
- Only 3 PGD entries, 3 PUD entries, 3 PMD entries, and 13 PTE entries need to exist.
- Total page table memory: ~4 pages (16KB) instead of 512GB.

**Five-level page tables** (Linux 5.5+, `CONFIG_X86_5LEVEL`): adds another level for 57-bit virtual addresses, supporting up to 128 PB of virtual address space per process.

## Segmentation

**Segmentation** divides a program's address space into logical, variable-size units (**segments**): code, data, stack, heap. Each segment has a **base address** and a **limit (size)**.

```
Logical address: (segment selector, offset)
Physical address:
  if offset >= limit → segfault (protection violation)
  else: segment_base[selector] + offset
```

**Advantages:** matches programmer intuition (code segment is read-only, stack segment is private). **Disadvantage:** variable-size segments cause external fragmentation.

Modern x86-64 CPUs have full segment hardware, but Linux and Windows use a flat model: all segment bases are set to 0, all limits to 2^64. Effectively, segmentation is disabled and everything is done via paging. The only vestige is the **FS and GS registers** used for thread-local storage (TLS).

## Paging + Segmentation (Historical)

Some systems (e.g., early x86 with 286/386 protected mode) combined both: a virtual address was first checked against a segment descriptor, then the resulting linear address was translated through the page table. Linux on x86 technically does both, but segments are all the same (base=0), so segmentation is a no-op.

## Huge Pages

The default 4KB page means a process using 1GB of memory needs 262,144 PTE entries and potentially many TLB misses. **Huge pages** (2MB or 1GB on x86-64) reduce TLB pressure dramatically:

| Page Size | TLB Coverage (1024 entries) | Use Case |
|-----------|----------------------------|---------|
| 4 KB | 4 MB | Default — lowest internal fragmentation |
| 2 MB | 2 GB | Databases (PostgreSQL, MySQL), JVM heap |
| 1 GB | 1 TB | High-performance computing, ML training |

Linux supports huge pages via `mmap(MAP_HUGETLB)` or **Transparent Huge Pages (THP)** — the kernel automatically promotes 4KB page groups to 2MB pages when possible.

## How malloc() Works

`malloc()` in glibc manages the heap using two mechanisms:
1. `brk()`/`sbrk()` syscall: extends the heap break pointer for small allocations.
2. `mmap(MAP_ANONYMOUS)` syscall: allocates a new, independent region for large allocations (≥ 128KB typically).

The kernel does not actually allocate physical frames at `malloc` time — it only maps virtual address space. Physical frames are allocated **on first access** (when the page fault fires for each new virtual page). This is **lazy allocation** or **demand paging**.

## Key Takeaways

- **Paging** maps fixed-size virtual pages to physical frames, eliminating external fragmentation.
- The **MMU + TLB** translate virtual addresses to physical in hardware; TLB hits cost ~1 cycle, misses ~100 cycles.
- **Multi-level page tables** (4 levels on Linux x86-64) allow 48-bit virtual address spaces without giant flat tables — only used entries cost memory.
- **Segmentation** divides by logical meaning (code, data, stack) but causes fragmentation; modern OSes use a flat-paging model.
- **Huge pages** (2MB, 1GB) reduce TLB pressure for large working sets — critical for databases and ML.
- `malloc()` requests virtual memory; physical frames are only allocated on first access (demand paging).
