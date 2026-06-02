# TLB Hit vs Miss and the Walk Path

When the CPU translates a virtual address, exactly one of two things happens: it either finds a valid mapping in the TLB (a **hit**) or it does not (a **miss**). The cost difference between these two outcomes is enormous — typically 1–5 cycles for a hit versus 50–200 cycles for a miss — and that gap drives many design decisions in OS and runtime code.

## The TLB Hit Path

On a hit the hardware:

1. Extracts the Virtual Page Number (VPN) from the address.
2. Checks the TLB in parallel across all entries (fully associative lookup).
3. Verifies the valid bit and, if applicable, the ASID matches the current process.
4. Checks that the requested operation (read/write/execute) is allowed by the protection bits.
5. Returns the Physical Frame Number (PFN) and concatenates it with the page offset to form the physical address.

Total cost: roughly **1–4 cycles** — invisible to the programmer in practice.

## The TLB Miss Path

On a miss the mapping must be found by **walking the page table**. How this happens depends on the architecture:

### Hardware-Managed TLB Walk (x86, ARM with VMSA)

The hardware MMU walks the page table autonomously without OS involvement:

```
CPU detects TLB miss
  → CR3 register (x86) holds base physical address of PGD
  → Hardware reads PGD[VPN[3]]  → PUD base
  → Hardware reads PUD[VPN[2]]  → PMD base
  → Hardware reads PMD[VPN[1]]  → PTE base
  → Hardware reads PTE[VPN[0]]  → PFN + flags
  → TLB entry installed
  → Instruction retried
```

On x86-64 with 4-level paging, this walk touches **4 physical memory locations**. If those page-table pages are not in the data cache, each one is a full cache miss — easily 200+ cycles total.

### Software-Managed TLB Walk (MIPS, SPARC, some RISC-V)

The hardware raises a **TLB-miss exception** and jumps to an OS handler:

```asm
# Simplified MIPS TLB miss handler
.tlb_miss:
    mfc0  $k0, $BadVAddr      # faulting virtual address
    srl   $k0, $k0, 12        # extract VPN
    # compute page table entry address
    lw    $k1, 0($k0)         # load PTE from OS page table
    mtc0  $k1, $EntryLo0      # write PFN + flags into TLB
    tlbwr                      # write random TLB entry
    eret                       # return and retry
```

This is more flexible (the OS can use any page table format) but adds interrupt overhead. A fast software handler on MIPS executes in roughly 10–20 cycles; a slow one can take hundreds.

## Worked Example: 4-Level x86-64 Walk

A process accesses virtual address `0x0000_7F3A_1234_5678`:

```
VPN[3] = bits[47:39] = 0x00F   → index into PGD
VPN[2] = bits[38:30] = 0x0E8   → index into PUD
VPN[1] = bits[29:21] = 0x091   → index into PMD
VPN[0] = bits[20:12] = 0x045   → index into PTE
offset = bits[11:0]  = 0x678   → byte offset in page

Physical address = PFN × 4096 + 0x678
```

The hardware performs four 8-byte reads (one per table level) before it can service the original load.

## Impact on Real Code

```c
// This pattern causes TLB thrashing: array of pointers scattered across many pages
Node* nodes[1000000];
for (int i = 0; i < N; i++) {
    process(nodes[i]->value);  // each nodes[i] may live on a different page
}

// Better: store values in a flat array (fewer unique pages touched)
int values[1000000];
for (int i = 0; i < N; i++) {
    process(values[i]);
}
```

## Common Pitfalls

- **Assuming page-table pages are cached.** A cold TLB miss often chains into cache misses for each level of the page table — the actual penalty can be 4× worse than a simple estimate.
- **Forgetting protection checks.** Even on a TLB hit, the hardware checks permission bits. A write to a read-only page raises a protection fault even when the VPN is in the TLB.
- **Ignoring huge-page walk shortcuts.** A 2 MB page collapses the 4-level walk to 3 levels; a 1 GB page collapses it to 2. Modern OS kernels use transparent huge pages to reduce walk depth.

**Interview answer:** "A TLB hit costs ~1–4 cycles — the hardware returns the physical frame number directly. A miss triggers a page-table walk, which on x86-64 reads four memory locations (one per level). If those page-table pages are not cached, the total penalty can exceed 200 cycles."
