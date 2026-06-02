# TLB Flushes, ASIDs, and Context Switches

Every time the OS switches between two processes, it switches page tables — the new process maps virtual addresses completely differently from the old one. This raises an immediate question: what happens to the TLB entries from the previous process?

## The Naive Solution: Flush the Entire TLB

The simplest approach is to **invalidate every TLB entry** on every context switch. On x86, this is accomplished by reloading the CR3 register:

```asm
; Switch to new process page table (x86-64)
mov rax, [new_process.cr3]
mov cr3, rax               ; reloading CR3 flushes the entire TLB
```

This guarantees correctness: no process can ever see another process's mappings. The cost is that every TLB entry accumulated by the outgoing process is discarded. After a context switch, the incoming process must rebuild its TLB from scratch — every first access to each page misses and triggers a page-table walk.

**The cold-start penalty** is severe on modern machines. A web server that frequently context-switches between many short-lived tasks can spend a significant fraction of its CPU time refilling TLBs after switches.

## A Better Solution: Address Space Identifiers (ASIDs)

Most modern MMUs support **Address Space Identifiers** (called ASIDs on ARM and MIPS, PCIDs — Process Context Identifiers — on x86 since Ivy Bridge). An ASID is a small integer (typically 8–16 bits) that is stored alongside each TLB entry as a tag.

When the CPU checks the TLB it must match **both** the VPN and the ASID. Entries belonging to a different process are simply ignored on lookup — they do not produce a hit.

```
TLB Entry (with ASID):
  [ ASID | VPN | PFN | V | R/W | D | ... ]

Lookup succeeds only if:
  entry.asid == current_process.asid
  AND entry.vpn == requested_vpn
  AND entry.valid == 1
```

With ASIDs, a context switch requires only:

1. Load the new process's page-table base address.
2. Update the current ASID register to the new process's ASID.

No TLB flush is needed. Entries from both processes coexist in the TLB and are disambiguated by their ASID tags.

## ASID Exhaustion

Because ASIDs are a finite resource (e.g., 256 values for an 8-bit ASID field), the OS must handle exhaustion:

- The OS maintains a map from `(process, cpu)` → `asid`.
- When all ASID values are in use and a new one is needed, the OS performs a **global TLB flush** and reassigns ASIDs from scratch.
- This is a rare event in practice — Linux tracks "ASID generations" and flushes only once per full ASID cycle.

```
ARM64 ASID management (simplified):
  asid_generation = 0
  next_asid = 1

  allocate_asid(process):
    if next_asid > MAX_ASID:
        asid_generation++
        next_asid = 1
        tlbi vmalle1     # flush TLB (all entries, EL1)
    process.asid = (asid_generation, next_asid++)
```

## Kernel Entries and Global Bits

Kernel code runs in every process's address space (mapped at high virtual addresses). If the kernel's TLB entries were flushed on every switch, kernel system calls would always cold-start. To prevent this, x86 marks kernel page table entries with the **Global (G) bit**. TLB entries tagged as global are not flushed when CR3 is reloaded.

On PCID-aware systems (x86 Ivy Bridge+), Linux uses a more sophisticated scheme where the kernel keeps a set of active PCIDs and avoids issuing CR3 reloads with the flush bit set whenever possible (the INVPCID instruction allows selective invalidation).

## Meltdown and TLB Design

The Meltdown vulnerability (CVE-2017-5754) exploited the fact that kernel mappings existed in user-mode page tables. The fix — Kernel Page Table Isolation (KPTI) — removes kernel mappings from user-mode page tables entirely. The consequence is that every syscall now switches CR3 twice (once into kernel space, once back), causing a TLB flush on each side unless PCIDs are used to keep both sets of entries active simultaneously.

## Summary Table

| Technique | Flush on Switch? | Overhead | Support |
|---|---|---|---|
| Full TLB flush (no ASID) | Yes | High | All MMUs |
| ASID / PCID | No (usually) | Low | ARM, MIPS, x86 ≥ Ivy Bridge |
| Global bit (kernel pages) | No | None | x86 |
| Huge pages | — | Reduces miss cost | Most modern CPUs |

**Interview answer:** "Without ASIDs, every context switch flushes the TLB, causing a cold-start penalty as the new process refills it. With ASIDs (or PCIDs on x86), each TLB entry is tagged with a process identifier, so entries from multiple processes coexist and no flush is needed on a switch — as long as ASID values have not been exhausted."
