# The Memory Management Unit (MMU)

Every load and store instruction a CPU issues goes through the **Memory Management Unit** before it ever reaches the memory bus. The MMU is the hardware block that performs virtual-to-physical address translation at full processor speed, making virtual memory transparent to software.

## Where the MMU Lives

The MMU sits between the processor pipeline and the cache/memory hierarchy:

```
CPU Core
 ├─ Fetch / Decode / Execute
 │
 ├─► MMU ──────────────────────────────────────────┐
 │    ├─ TLB (fast translation cache)               │
 │    └─ Page Table Walker (handles TLB misses)     │
 │                                                  │
 │    (physical address out)                        │
 │                                                  ▼
 └─────────────────────────────── L1 Cache / DRAM
```

On modern SoCs the MMU is part of the CPU die, not a separate chip. It operates every clock cycle for every memory reference.

## Core Responsibilities

| Responsibility | What the MMU does |
|---|---|
| Address translation | Converts virtual address → physical address using the page table |
| Permission checking | Enforces R/W/X and User/Supervisor bits per page |
| TLB management | Caches recent translations to avoid walking the page table every time |
| Fault generation | Raises exceptions on invalid or forbidden accesses |

## The satp Register (RISC-V)

The OS tells the MMU which page table to use by writing to the `satp` (Supervisor Address Translation and Protection) Control and Status Register:

```
satp (Sv39):
 63:60  = MODE   (8 = Sv39, 0 = bare/no translation)
 59:44  = ASID   (Address Space ID — 16 bits)
 43:0   = PPN    (Physical Page Number of the root page table)
```

```asm
# Switch to a new process's page table
# t0 holds the new satp value (MODE | ASID | root PPN)
csrw satp, t0
sfence.vma           # flush TLB after changing satp
```

When `MODE = 0`, the MMU is disabled and all addresses are treated as physical — this is how the machine boots and how the kernel runs before enabling virtual memory.

## Permission Checking

Every PTE carries permission bits. The MMU checks them on every access:

- **Load** from a page without the **R** bit → page fault.
- **Store** to a page without the **W** bit → page fault (common for read-only code or copy-on-write pages).
- **Jump** to a page without the **X** bit → instruction page fault (key for W^X security policy).
- **User-mode access** to a page with **U=0** → page fault (prevents user code from reading kernel memory).

This hardware enforcement is what makes kernel memory inaccessible to user programs — no amount of pointer arithmetic in C can bypass it.

## What Happens on a Permission Violation

1. The MMU raises a **trap** (exception) to the processor.
2. The processor switches to supervisor mode and jumps to the OS trap handler.
3. The OS inspects the `scause` CSR to determine the fault type (load fault, store fault, instruction fault).
4. The OS inspects `stval` to get the faulting virtual address.
5. The OS either handles the fault (e.g., allocate a new page) or terminates the process with a segmentation fault.

```
scause values (RISC-V):
  12 = Instruction page fault
  13 = Load page fault
  15 = Store/AMO page fault
```

## ASID: Address Space Identifier

An **ASID** is a tag the MMU attaches to TLB entries. Without ASIDs, every context switch (process switch) requires flushing the entire TLB because the same virtual address means different things in different processes. With ASIDs, TLB entries from process A are simply ignored when the CPU is running process B — much faster.

## Common Pitfall: MMU Is Not Optional

Developers sometimes assume they can "bypass" the MMU by writing to physical addresses directly from user space. This is impossible when virtual memory is enabled — every user-mode address goes through the MMU. Only kernel code running with special privileges can access physical memory directly (e.g., via `/dev/mem` on Linux, which is locked down on production systems).

## Interview Answer

> "The MMU is a hardware unit in the CPU that translates every virtual address to a physical address in real time, enforces per-page permissions (read/write/execute), and raises exceptions on invalid accesses. It uses the page table pointer stored in a privileged register (satp on RISC-V) and caches recent translations in a TLB."
