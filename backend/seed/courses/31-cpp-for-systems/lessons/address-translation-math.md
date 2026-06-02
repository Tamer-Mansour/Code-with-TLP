# Address Translation: Page Number and Offset

Address translation is a favourite interview calculation. Given a virtual address, a page size, and a page table, you must derive the physical address. This lesson walks through the arithmetic step by step.

## The Formula

```
page_size  = 2^n  bytes   (n = number of offset bits)
VPN        = virtual_address >> n
offset     = virtual_address & (page_size - 1)
PA         = (PFN << n) | offset
```

The offset bits are the **low** bits of the address; the page number bits are the **high** bits.

## Step-by-Step Example

**Given:**
- Page size = **4 KB** = 4096 bytes = 2^12 → offset is 12 bits
- Virtual address = **0x3A9C**
- Page table: VPN 0 → PFN 5, VPN 1 → PFN 2, VPN 2 → PFN 7, VPN 3 → PFN 1

**Step 1 — Convert to binary (16-bit address for clarity):**

```
0x3A9C = 0011 1010 1001 1100
```

**Step 2 — Split into VPN and offset:**

```
Bits [15:12] = 0011 = 3    → VPN = 3
Bits [11:0]  = 1010 1001 1100 = 0xA9C → offset = 0xA9C
```

**Step 3 — Look up PFN:**

```
VPN 3 → PFN 1
```

**Step 4 — Compute physical address:**

```
PA = (PFN << 12) | offset
   = (1 << 12) | 0xA9C
   = 0x1000 | 0xA9C
   = 0x1A9C
```

**Answer: physical address = 0x1A9C.**

## Quick Reference Table

| Virtual Address | Page Size | VPN | Offset | PFN | Physical Address |
|---|---|---|---|---|---|
| 0x3A9C | 4 KB (12b) | 3 | 0xA9C | 1 | 0x1A9C |
| 0x00FF | 256 B (8b) | 0 | 0xFF | 3 | 0x03FF |
| 0x1234 | 4 KB (12b) | 1 | 0x234 | 5 | 0x5234 |

## Handling Page Faults

If a VPN is not present in the page table (present bit = 0):

1. MMU raises a **page fault** exception.
2. OS trap handler runs.
3. OS loads the page from swap (or disk) into a free frame.
4. OS updates the PTE with the new PFN and sets present bit.
5. OS returns to the faulting instruction, which re-executes successfully.

> **Interview answer:** VPN = address >> log2(page_size); offset = address & (page_size - 1); PA = (PFN << log2(page_size)) | offset.

## Two-Level Translation Example

On a system with a **two-level page table** and 16-bit addresses, 256-byte pages:

```
Bits [15:8]  → level-1 index (selects a page directory entry)
Bits [7:0]   → split again:
  Bits [7:4] → level-2 index (selects a page table entry)
  Bits [3:0] → offset within the 16-byte page
```

```
Virtual address = 0xA5B3

Binary: 1010 0101 1011 0011
L1 index  = 1010 0101 = 0xA5
L2 index  = 1011      = 0xB
Offset    = 0011      = 0x3
```

Look up L1[0xA5] → pointer to L2 table.
Look up L2[0xB] → PFN.
Combine PFN with 0x3 offset.

## C++ Code to Compute VPN and Offset

```cpp
#include <cstdint>
#include <cstdio>

void translate(uint64_t va, int page_bits) {
    uint64_t page_size = 1ULL << page_bits;
    uint64_t vpn    = va >> page_bits;
    uint64_t offset = va & (page_size - 1);
    printf("VA=0x%lX  VPN=%lu  Offset=0x%lX\n", va, vpn, offset);
}

int main() {
    translate(0x3A9C, 12);  // 4 KB pages
    translate(0x00FF,  8);  // 256 B pages
    return 0;
}
```

Output:
```
VA=0x3A9C  VPN=3  Offset=0xA9C
VA=0xFF    VPN=0  Offset=0xFF
```

## Common Interview Pitfalls

- **Forgetting the mask:** offset = VA % page_size works too, but the bit-AND form `VA & (page_size - 1)` is cleaner and faster.
- **Confusing page bits with page count:** 12 offset bits means 4 KB pages, not 12 pages.
- **Missing the shift:** PA = PFN × page_size + offset, or equivalently PFN << page_bits | offset.
- **Assuming the address is in hex vs. decimal** — always check the base before computing.
