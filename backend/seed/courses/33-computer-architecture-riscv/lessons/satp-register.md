# The satp Register and Address Space Switching

The `satp` CSR (Supervisor Address Translation and Protection) is the single register that arms and aims the RISC-V virtual memory system. Writing `satp` enables paging, sets the paging mode, and points the hardware at the root page table for the current address space. Understanding `satp` is essential for writing a context-switching kernel.

## satp Layout (RV64)

```
 63      60 59        44 43                              0
   MODE       ASID                    PPN
  (4 bits)  (16 bits)              (44 bits)
```

| Field | Bits | Purpose |
|---|---|---|
| MODE | 63:60 | Paging mode: 0=Bare, 8=Sv39, 9=Sv48, 10=Sv57 |
| ASID | 59:44 | Address Space ID — identifies the address space for TLB tagging |
| PPN | 43:0 | Physical Page Number of the root page-table page |

For RV32, `satp` is 32 bits: `MODE(1) | ASID(9) | PPN(22)`.

## MODE Field Values

| Value | Name | Description |
|---|---|---|
| 0 | Bare | No translation; physical addresses used directly |
| 8 | Sv39 | 39-bit virtual addressing, 3 levels |
| 9 | Sv48 | 48-bit virtual addressing, 4 levels |
| 10 | Sv57 | 57-bit virtual addressing, 5 levels |

A MODE value of `Bare` disables translation — this is the default after reset and the state M-mode normally runs in.

## Enabling Paging

To enable Sv39 paging, the kernel:

1. Builds the root page table in physical memory.
2. Computes the PPN of that page: `ppn = (uintptr_t)root_pt >> 12`.
3. Writes `satp = (8UL << 60) | (asid << 44) | ppn`.
4. Issues `SFENCE.VMA` to flush stale TLB entries.

```c
static void enable_sv39(uintptr_t root_pt_phys, uint16_t asid) {
    uintptr_t ppn  = root_pt_phys >> 12;
    uintptr_t satp = (8UL << 60) | ((uintptr_t)asid << 44) | ppn;

    asm volatile(
        "csrw satp, %0\n"
        "sfence.vma zero, zero\n"
        :
        : "r"(satp)
        : "memory"
    );
}
```

After the `csrw`, all subsequent S-mode (and U-mode) load/store/fetch instructions use virtual addressing. M-mode is unaffected — it always uses physical addresses unless `mstatus.MPRV` is set.

## Address Space Switching on Context Switch

Each process has its own root page table. On a context switch:

```c
void switch_address_space(struct task *next) {
    uintptr_t ppn  = next->root_pt_phys >> 12;
    uint16_t  asid = next->asid;
    uintptr_t satp = (8UL << 60) | ((uintptr_t)asid << 44) | ppn;

    asm volatile("csrw satp, %0" :: "r"(satp) : "memory");
    // With ASID support, no sfence.vma needed if ASID is unique
}
```

**ASID optimization:** If the hardware supports ASIDs (check `satp` ASID field width > 0), TLB entries are tagged with the ASID. Switching to a different ASID automatically filters out stale TLB entries from the old process — no global `SFENCE.VMA` required. Without ASID support (ASID field always 0), a full `SFENCE.VMA` is required on every context switch.

## Reading satp

Reading `satp` reveals the current address space:

```asm
csrr a0, satp       # Read satp into a0
srli a1, a0, 44     # Shift right to isolate ASID in low 16 bits
andi a1, a1, 0xFFFF # Mask to 16 bits
```

## Common Pitfalls

- **Writing `satp` from U-mode.** `satp` is an S-mode register; a U-mode `csrw` raises an illegal-instruction exception.
- **Forgetting `SFENCE.VMA` after changing `satp`.** TLB entries cached for the old mapping will cause incorrect translations until flushed.
- **PPN alignment.** The root page table must be 4 KiB-aligned; passing an unaligned address silently truncates the low bits, pointing the hardware at the wrong table.
- **Enabling paging with an incomplete table.** If the kernel's own mappings are absent from the new page table, the very next instruction fetch (which now goes through the MMU) will page-fault.

## Interview Answer

> "`satp` holds three fields: MODE (selects Bare/Sv39/Sv48), ASID (tags TLB entries for cheap context switching), and PPN (the physical page number of the root page table). Writing `satp` enables paging immediately; it must be followed by `SFENCE.VMA` to flush stale TLB entries unless ASIDs are in use."
