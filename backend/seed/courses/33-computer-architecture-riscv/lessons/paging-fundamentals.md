# Paging: Pages, Frames, and Page Tables

The address translation system does not work one byte at a time — that would require a billion-entry lookup table. Instead it works in fixed-size chunks called **pages**.

## Pages and Frames

- A **page** is a fixed-size, contiguous block of the **virtual** address space.
- A **frame** (or *page frame*) is the corresponding fixed-size block of **physical** memory.
- On most systems — including RISC-V Sv39 — the default page size is **4 KiB (4096 bytes)**.

Because both pages and frames are the same size, the mapping is simple: one page maps to exactly one frame (or is unmapped).

```
Virtual Address Space           Physical Memory (RAM)
┌──────────────┐                ┌──────────────┐
│  Page 0      │ ──────────────►│  Frame 5     │
├──────────────┤                ├──────────────┤
│  Page 1      │ ──── (swap) ──►│  (on disk)   │
├──────────────┤                ├──────────────┤
│  Page 2      │ ──────────────►│  Frame 1     │
└──────────────┘                └──────────────┘
```

## Splitting an Address into Page Number + Offset

Every address is split into two fields:

```
┌─────────────────────┬──────────────────┐
│  Virtual Page Number│   Page Offset    │
│       (VPN)         │    (12 bits)     │
└─────────────────────┴──────────────────┘
```

For a 4 KiB page, 12 bits encode the offset (2^12 = 4096). The remaining bits form the VPN, which is the **index** into the page table.

**Example (32-bit address space, 4 KiB pages):**

| Field | Bits | Range |
|---|---|---|
| Virtual Page Number | 31:12 | 0 – 1,048,575 |
| Page Offset | 11:0 | 0 – 4095 |

```
Virtual address: 0x00403ABC
Binary: 0000 0000 0100 0000 0011 | 1010 1011 1100
                    VPN = 0x403          Offset = 0xABC
```

## The Page Table

The **page table** is a data structure (usually an array in kernel memory) that maps VPNs to **Page Table Entries (PTEs)**. Each PTE stores:

- The **Physical Frame Number (PFN)** — where in RAM this page lives.
- **Valid/Present bit (V)** — is this mapping active?
- **Read/Write/Execute bits (R/W/X)** — permission flags.
- **Dirty bit (D)** — has this page been written since it was loaded?
- **Accessed bit (A)** — has this page been read or written recently?
- **User/Supervisor bit (U)** — accessible from user mode?

RISC-V Sv32 PTE layout (32 bits):

```
 31          10 | 9  8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0
┌──────────────┬──────┬───┬───┬───┬───┬───┬───┬───┬───┐
│     PPN      │  RSW │ D │ A │ G │ U │ X │ W │ R │ V │
└──────────────┴──────┴───┴───┴───┴───┴───┴───┴───┴───┘
PPN = Physical Page Number (= PFN)
```

## Full Translation Example

Given:
- Virtual address: `0x00403ABC`
- VPN: `0x403` (1027 decimal)
- PTE at index 1027 contains PFN `0x0018`

Physical address = `(PFN << 12) | Offset` = `0x0018_000 | 0xABC` = **`0x0018_0ABC`**

```python
vpn    = 0x00403ABC >> 12   # = 0x403
offset = 0x00403ABC & 0xFFF # = 0xABC
pfn    = page_table[vpn]    # = 0x18 (from PTE)
phys   = (pfn << 12) | offset
print(hex(phys))            # 0x180abc
```

## Page Table Size — Why It Matters

A flat (single-level) page table for a 32-bit address space with 4 KiB pages needs 2^20 = **1,048,576 entries**. At 4 bytes each that is 4 MiB — per process. For 64-bit address spaces it becomes completely impractical (terabytes), which is why **multi-level page tables** exist (covered in a later lesson).

## Common Pitfall

The page offset is **never translated** — it passes straight through from the virtual address to the physical address unchanged. Only the VPN portion is looked up in the page table. This is a frequent source of confusion on exams.

## Interview Answer

> "Paging divides both virtual and physical memory into equal-size chunks (pages and frames). A page table, indexed by the virtual page number, maps each virtual page to a physical frame. The page offset bits bypass translation entirely and are appended to the frame number to form the final physical address."
