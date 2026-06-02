# The Translation Lookaside Buffer (TLB)

Every memory access requires address translation. Without caching, a 3-level page table walk adds 3 extra memory reads to every single load or store — a 4× slowdown. The **Translation Lookaside Buffer (TLB)** is the hardware cache that makes this overhead nearly invisible in practice.

## What the TLB Stores

The TLB is a small, fully associative (or set-associative) hardware cache inside the MMU. Each entry maps:

```
(ASID, VPN)  →  (PFN, permission bits, flags)
```

A TLB hit returns the physical frame number in 1–2 cycles. A TLB miss triggers a page-table walk, which takes tens to hundreds of cycles.

## TLB Hit vs. Miss

```
CPU issues load at VA 0x00403ABC
         │
         ▼
  ┌─────────────────────────────────┐
  │ TLB lookup: ASID=3, VPN=0x403  │
  └──────────┬──────────────────────┘
             │
      Found? ├── YES (hit)  → use cached PFN immediately  (~1 cycle)
             │
             └── NO (miss)  → page table walk             (~50–200 cycles)
                               │
                               ▼
                         install new TLB entry
                         retry the access
```

## TLB Miss Handling: Hardware vs. Software

| Approach | Who walks the page table? | Example |
|---|---|---|
| Hardware-walked | The MMU itself (page table walker unit) | x86, ARM, RISC-V (optional) |
| Software-walked | The OS trap handler | MIPS, classic SPARC |

RISC-V leaves TLB miss handling to software by default. On a TLB miss, the processor traps to the OS, which reads the page table and issues a privileged instruction to insert the new TLB entry. This simplifies the MMU but puts more pressure on the OS trap handler to be fast.

## ASID: Avoiding Full TLB Flushes

Without **Address Space IDs (ASIDs)**, every context switch must invalidate the entire TLB because the same VPN means different things in different processes. With ASIDs, each TLB entry is tagged with the ASID of the process that owns it:

```asm
# RISC-V: flush only entries for ASID 5 at virtual address 0x1000
sfence.vma x5, x6    # x5 = vaddr, x6 = asid

# Flush all entries (no ASID filter):
sfence.vma zero, zero
```

When the OS switches from process A (ASID=1) to process B (ASID=2), it updates `satp` with the new root page table and new ASID. The TLB retains all old entries but they will never match because the ASID field will not match process B's lookups.

## TLB Reach and Huge Pages

**TLB reach** = number of TLB entries × page size.

A 64-entry L1 TLB with 4 KiB pages covers only 256 KiB — less than many working sets. This is a real bottleneck. Huge pages (2 MiB or 1 GiB) dramatically extend TLB reach:

```
64 TLB entries × 4 KiB  =   256 KiB reach
64 TLB entries × 2 MiB  =   128 MiB reach   (32× improvement)
64 TLB entries × 1 GiB  =    64 GiB reach
```

This is why databases, JVMs, and scientific computing runtimes explicitly request huge pages from the OS.

## Typical TLB Structure

Modern CPUs have a two-level TLB hierarchy:

| Level | Entries | Latency | Scope |
|---|---|---|---|
| L1 ITLB | 32–64 | 1 cycle | Instruction fetches only |
| L1 DTLB | 32–64 | 1 cycle | Data accesses only |
| L2 (unified) TLB | 512–4096 | 5–10 cycles | Both |

A miss in L2 TLB triggers the page-table walk.

## TLB Coherence Pitfall

The TLB is a **cache of the page table**. If the OS modifies a PTE (e.g., changes permissions or unmaps a page), it must **explicitly invalidate** the corresponding TLB entry — the hardware does not do this automatically. Failing to do so is a serious security bug: a process could continue accessing a page that the OS thought it had revoked.

```asm
# OS unmaps a page: clear PTE, then flush TLB
sw zero, 0(a0)          # clear PTE in memory
fence                    # ensure the store is visible
sfence.vma a1, zero     # invalidate TLB entries for this VA
```

## Interview Answer

> "The TLB is a small hardware cache inside the MMU that stores recent virtual-to-physical translations. A TLB hit costs ~1 cycle; a miss requires a page-table walk costing tens to hundreds of cycles. ASIDs allow the TLB to hold entries from multiple processes simultaneously, avoiding a full flush on every context switch. The OS must manually invalidate TLB entries whenever it changes page table mappings."
