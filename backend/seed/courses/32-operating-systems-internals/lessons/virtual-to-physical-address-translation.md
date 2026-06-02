# Virtual-to-Physical Address Translation Step by Step

Address translation is the core duty of the Memory Management Unit (MMU). Every load and store instruction issues a virtual address; the MMU must produce a physical address before the memory bus can fetch the data. Understanding this pipeline is critical for debugging crashes, writing OS code, and answering memory-related interview questions.

## The Five-Step Pipeline

```
Virtual Address
      │
      ▼
┌─────────────────────────────────┐
│ Step 1: Split VA into VPN + Offset │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Step 2: Check the TLB (fast path) │
│  Hit → PFN found, skip to step 5  │
│  Miss → continue to step 3        │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Step 3: Walk the page table     │
│  Load PTE from memory           │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Step 4: Check PTE bits          │
│  P=0 → page fault               │
│  Protection violation → fault   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Step 5: Form physical address   │
│  PA = (PFN << offset_bits) | offset │
└─────────────────────────────────┘
```

## Step 1 — Split the Virtual Address

The number of offset bits equals log2(page size). All remaining high bits are the VPN.

```c
// 32-bit VA, 4 KB pages (12 offset bits)
#define PAGE_BITS 12
#define OFFSET_MASK ((1u << PAGE_BITS) - 1)   // 0xFFF

uint32_t va     = 0x0040107C;
uint32_t vpn    = va >> PAGE_BITS;            // 0x00401
uint32_t offset = va & OFFSET_MASK;           // 0x07C
```

## Step 2 — TLB Lookup

The Translation Lookaside Buffer is a small, fully-associative hardware cache of recent VPN→PFN mappings. It is checked in parallel with decoding the instruction.

- **TLB hit**: PFN is returned in 1–5 clock cycles. No memory access needed.
- **TLB miss**: Must perform a page table walk (step 3).

TLB miss rate is typically under 1% in well-behaved programs because of spatial and temporal locality.

## Step 3 — Page Table Walk

On a TLB miss the MMU (or OS, on software-TLB architectures like MIPS) reads the PTE:

```
PTE address = page_table_base + vpn * sizeof(PTE)
```

On a 4-level x86-64 table this is actually four sequential memory reads (PML4 → PDPT → PD → PT), each indexed by a 9-bit slice of the VPN.

## Step 4 — Validate the PTE

```
if PTE.Present == 0:
    raise PageFault(va, FAULT_NOT_PRESENT)
if write_access and PTE.Writable == 0:
    raise PageFault(va, FAULT_PROTECTION)
if user_mode and PTE.User == 0:
    raise PageFault(va, FAULT_PROTECTION)
```

The OS page-fault handler either loads the missing page from disk and retries, or delivers a segmentation fault signal to the process.

## Step 5 — Form the Physical Address

```c
uint32_t pfn = pte >> PAGE_BITS;              // upper 20 bits of PTE
uint32_t pa  = (pfn << PAGE_BITS) | offset;  // concatenate
```

The offset is **never modified** — it is identical in both addresses.

## Full Worked Example

**Setup:** 16-bit virtual address space, 256-byte pages (8 offset bits, 8 VPN bits). Physical RAM has 8 frames (3-bit PFN).

Page table for Process X:

| VPN | PFN | Present |
|-----|-----|---------|
| 0 | 5 | 1 |
| 1 | 2 | 1 |
| 2 | — | 0 |
| 3 | 7 | 1 |

**Translate virtual address `0x0173`:**

1. Split: VPN = `0x0173 >> 8` = `0x01` = 1; Offset = `0x0173 & 0xFF` = `0x73`
2. TLB miss (assume cold cache)
3. Load PTE for VPN 1 → PFN = 2, Present = 1
4. Validate: Present = 1, no protection issue
5. Physical address = `(2 << 8) | 0x73` = `0x0273`

**Translate virtual address `0x0200`:**

1. Split: VPN = 2; Offset = 0x00
2. Load PTE for VPN 2 → Present = 0
3. **Page fault** — OS must load the page from swap before retrying

## Performance Implications

| Event | Approximate cost |
|-------|-----------------|
| TLB hit | 1–5 cycles |
| TLB miss + page table walk (4-level) | 100–200 cycles (4 RAM reads) |
| Page fault (disk I/O) | 10,000,000+ cycles |

> **Interview answer:** The MMU splits the virtual address into VPN and offset, looks up the VPN in the TLB (fast) or walks the page table (slow), checks the Present and protection bits in the PTE, and concatenates the physical frame number with the unchanged offset to form the physical address. A missing Present bit triggers a page fault handled by the OS.
