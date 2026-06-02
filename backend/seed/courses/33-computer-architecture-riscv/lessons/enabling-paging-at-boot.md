# Enabling Paging and Switching to S-Mode

After the bootloader hands control to the kernel and the kernel sets up its stack, one of the most significant transitions is **enabling virtual memory** (paging) and establishing the S-mode execution environment. Until this point, every address is physical — a dangerous state where a stray pointer can corrupt firmware or other memory regions.

## RISC-V Virtual Memory Modes

RISC-V defines several paging modes selected by the `MODE` field in the `satp` CSR:

| MODE value | Name | Address space size |
|-----------|------|--------------------|
| 0 | Bare (no paging) | Physical only |
| 8 | Sv39 | 39-bit VA → 56-bit PA |
| 9 | Sv48 | 48-bit VA → 56-bit PA |
| 10 | Sv57 | 57-bit VA → 56-bit PA |

Linux on 64-bit RISC-V commonly uses **Sv39**, which supports a 512 GB virtual address space per process with a 3-level page table.

## The `satp` CSR Layout (Sv39)

```
 63      60 59      44 43           0
+----------+----------+---------------+
|   MODE   |   ASID   |      PPN      |
| (4 bits) | (16 bits)| (44 bits)     |
+----------+----------+---------------+
```

- `MODE = 8` enables Sv39.
- `ASID` — Address Space ID for TLB tagging (reduces flushes on context switch).
- `PPN` — Physical Page Number of the root page table (level 2).

## Page Table Walk (Sv39)

A virtual address in Sv39 is split:

```
VA[63:39]  — must be sign extension of VA[38]
VA[38:30]  — VPN[2]: index into L2 (root) page table
VA[29:21]  — VPN[1]: index into L1 page table
VA[20:12]  — VPN[0]: index into L0 (leaf) page table
VA[11:0]   — page offset
```

Each page table entry (PTE) is 8 bytes:

```
 63    54 53   28 27   19 18   10 9 8 7 6 5 4 3 2 1 0
+--------+-------+-------+-------+-+-+-+-+-+-+-+-+-+-+
| Rsvd   |  PPN  |  PPN  |  PPN  |D|A|G|U|X|W|R|V| |
|        |[2]    |[1]    |[0]    | | | | | | | | | |
+--------+-------+-------+-------+-+-+-+-+-+-+-+-+-+-+
```

- `V` — Valid
- `R/W/X` — Read/Write/Execute permissions
- `U` — User-accessible
- `A/D` — Accessed/Dirty (set by hardware or software depending on implementation)

## Enabling Paging: Step by Step

The kernel (running in S-mode) enables paging by writing to `satp`:

```asm
# Assume page tables are already built in memory
# root_page_table is the physical address of the L2 table

    # Step 1: ensure all page table writes are visible
    sfence.vma zero, zero

    # Step 2: build satp value
    la   t0, root_page_table
    srli t0, t0, 12           # convert PA to PPN (divide by page size)
    li   t1, (8UL << 60)      # MODE = Sv39
    or   t0, t0, t1

    # Step 3: write satp — paging enabled from this instruction onward
    csrw satp, t0

    # Step 4: flush TLB
    sfence.vma zero, zero
```

Immediately after writing `satp`, the CPU begins translating all subsequent addresses. This means the instruction after `csrw satp` must be reachable via the new page tables — typically achieved by identity-mapping the kernel's physical range during this window.

## Identity Mapping During the Transition

Linux uses a trick: during early boot, the kernel page tables include both:

1. A **direct (identity) mapping** where `VA == PA` for the kernel's physical region.
2. The **high kernel mapping** at the kernel virtual base (e.g., `0xFFFFFFFF80000000`).

The boot code runs in the identity-mapped region, writes `satp`, then immediately jumps to the high virtual address. After that jump, the identity mapping can be removed.

## Switching to S-Mode (from OpenSBI)

OpenSBI drops to S-mode using `mret`:

```asm
    # Set MPP = 01 (S-mode) in mstatus
    li   t0, MSTATUS_MPP_S
    csrs mstatus, t0

    # Set kernel entry as the return address
    la   t0, kernel_entry
    csrw mepc, t0

    # Disable S-mode interrupts at entry
    csrw sie, zero

    mret           # atomically: mode → S-mode, PC → kernel_entry
```

## Common Pitfalls

- **Forgetting `sfence.vma` after writing `satp`.** The TLB may cache stale translations; without a fence, the first fetch in virtual space may use a wrong translation.
- **Page tables in uncacheable memory during setup.** If page table writes are not ordered before `satp` is written, the MMU may read stale data from cache.
- **Stack pointer still physical when paging starts.** `sp` must point to a virtual address that is valid in the new page tables, or the first stack access will fault.

> **Interview answer:** Paging is enabled in RISC-V by writing the page table root address and mode bits into the `satp` CSR followed by `sfence.vma`; the code must be identity-mapped at the moment of the switch so the next fetch succeeds under the new translation.
