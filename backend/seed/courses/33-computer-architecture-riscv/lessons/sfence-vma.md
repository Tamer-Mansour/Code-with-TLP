# TLB Management with SFENCE.VMA

The TLB (Translation Lookaside Buffer) caches page table walk results so the MMU does not reload them from memory on every instruction fetch or data access. Whenever the OS modifies page tables, it must invalidate stale TLB entries — otherwise the CPU will use outdated translations, potentially allowing a process to access memory it no longer has permission to touch. RISC-V provides the `SFENCE.VMA` instruction for exactly this purpose.

## Instruction Syntax

```asm
SFENCE.VMA rs1, rs2
```

| Operand | Meaning |
|---|---|
| `rs1 = x0` | Flush translations for **all** virtual addresses |
| `rs1 = reg` | Flush translations for the single virtual address in `reg` |
| `rs2 = x0` | Flush translations for **all** ASIDs |
| `rs2 = reg` | Flush translations for the single ASID in `reg` |

The four combinations give a 2×2 scope:

| Form | Effect |
|---|---|
| `sfence.vma zero, zero` | Full TLB flush — all VAs, all ASIDs |
| `sfence.vma rs1, zero` | Flush one VA across all ASIDs |
| `sfence.vma zero, rs2` | Flush all VAs for one ASID |
| `sfence.vma rs1, rs2` | Flush one VA for one ASID (most targeted) |

## When to Use SFENCE.VMA

| OS Operation | Recommended Form |
|---|---|
| Unmap a page from one process | `sfence.vma va_addr, asid` |
| Change permissions on a page | `sfence.vma va_addr, asid` |
| Free and reuse a page | `sfence.vma va_addr, asid` |
| Context switch (no ASID support) | `sfence.vma zero, zero` |
| Context switch (with ASID support) | No fence needed |
| Change root page table (`satp` write) | `sfence.vma zero, zero` |
| Kernel self-map modification | `sfence.vma va_addr, zero` |

## Ordering Semantics

`SFENCE.VMA` is both a TLB invalidation and a **memory ordering fence**. It guarantees:

1. All prior stores (to page table entries in memory) are visible to the hardware page table walker before subsequent translations proceed.
2. All prior implicit translations (cached in the TLB) for the specified scope are discarded.

This makes it safe to call immediately after writing a PTE:

```c
// Unmap a page: zero-out the PTE then flush
pte[vpn0] = 0;                          // clear V bit

asm volatile(
    "sfence.vma %0, %1"
    :
    : "r"(virtual_addr), "r"((long)asid)
    : "memory"
);
```

## SFENCE.VMA vs fence vs fence.i

| Instruction | Purpose |
|---|---|
| `fence` | Reorders MMIO/memory loads and stores |
| `fence.i` | Synchronizes instruction cache with data memory (for self-modifying code) |
| `sfence.vma` | Invalidates TLB entries and orders page-table writes |

These are orthogonal. Modifying an MMIO-backed "page table" would need all three; modifying a normal DRAM page table needs only `sfence.vma`.

## Performance Considerations

A global `sfence.vma zero, zero` is expensive on hardware with large TLBs or multi-core designs that must broadcast the invalidation. Best practices:

- Use targeted `sfence.vma rs1, rs2` whenever possible.
- Use ASIDs to avoid full flushes on context switches.
- Batch page-table modifications and issue a single `sfence.vma` at the end.
- On multi-core systems, sending IPIs to other harts to execute `sfence.vma` is required — the instruction only flushes the executing hart's TLB.

## Multi-Hart Consideration

`SFENCE.VMA` flushes only the TLB on the hart that executes it. If a page mapping is shared across cores (kernel mappings, shared libraries), the OS must:

1. Modify the PTE.
2. Send an Inter-Processor Interrupt (IPI) to all other harts sharing the address space.
3. Each receiving hart executes `sfence.vma` in its IPI handler.

This is called a **TLB shootdown** and is a significant source of overhead in high-core-count systems.

## Common Pitfalls

- **Missing `sfence.vma` after `csrw satp`.** Writing `satp` does not automatically flush the TLB. The next translation will use the new root table but may still find stale cached entries.
- **Forgetting cross-hart shootdown.** Modifying a shared kernel PTE without IPIing other harts leaves them with stale entries — a serious security and correctness bug.
- **Confusing `fence.i` and `sfence.vma`.** If you wrote machine code to a buffer and want to execute it, you need `fence.i`, not `sfence.vma`.

## Interview Answer

> "`SFENCE.VMA` invalidates TLB entries for an optional specific virtual address and/or ASID, and also acts as a memory fence ensuring prior page-table stores are visible to the hardware walker. It must be executed after any PTE modification, after writing `satp`, and on all harts that share the address space (via IPI/TLB shootdown)."
