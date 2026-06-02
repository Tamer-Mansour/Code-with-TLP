# Hardware vs Software-Managed TLBs

When a TLB miss occurs, something must find the correct page-table entry and install it into the TLB. Architectures take two fundamentally different approaches: let the hardware do it automatically, or raise an exception and let the OS handle it. The choice affects page-table flexibility, interrupt overhead, and OS complexity.

## Hardware-Managed TLBs

On x86, x86-64, and ARM (with the VMSAv8-64 table format), the MMU autonomously walks the page table in hardware when a TLB miss occurs. The hardware is hard-coded to expect a specific page-table format (e.g., x86-64's 4-level PML4 structure).

**Walk sequence on x86-64:**

```
TLB miss detected
  ↓
Hardware reads CR3 → PGD base physical address
  ↓
Reads PGD[VPN[3]] → checks P bit, reads PUD base
  ↓
Reads PUD[VPN[2]] → checks P bit, reads PMD base
  ↓
Reads PMD[VPN[1]] → checks P bit, reads PTE base
  ↓
Reads PTE[VPN[0]] → checks P bit, extracts PFN
  ↓
Installs entry in TLB, retries faulting instruction
```

If any "Present" bit is clear, the hardware raises a **page fault** (exception) and hands control to the OS page-fault handler.

### Advantages

- **Low latency:** No exception overhead, no OS involvement on a miss.
- **Simple OS:** The OS only needs to handle page faults (P=0), not every TLB miss.
- **Predictable timing:** The walk duration is bounded (k memory reads for k levels).

### Disadvantages

- **Inflexible page table format:** The OS must use the exact structure the hardware expects. Innovative page table designs (hash tables, inverted tables) require hardware support or emulation layers.
- **Coupled to silicon:** Changing the walk algorithm requires new hardware.

## Software-Managed TLBs

On MIPS (classic), SPARC, PA-RISC, and some RISC-V configurations, a TLB miss raises a **TLB-miss exception** that vectors directly to an OS handler. The hardware provides the faulting virtual address but does not walk the page table.

```c
/* Simplified Linux/MIPS TLB miss handler (C pseudocode) */
void tlb_miss_handler(ulong bad_vaddr) {
    pte_t *pte = lookup_pte(current->mm, bad_vaddr);
    if (!pte || !pte_present(*pte)) {
        do_page_fault(bad_vaddr);   // normal page fault
        return;
    }
    /* Install the mapping */
    write_entryhi(bad_vaddr & PAGE_MASK);
    write_entrylo0(pte_val(*pte));
    tlbwr();   // write into a random TLB slot
    return;    // eret resumes faulting instruction
}
```

### Advantages

- **Flexible page table format:** The OS can use any in-memory structure — hash tables (inverted page tables), segmented tables, Radix trees — as long as the miss handler can translate from VPN to PFN.
- **Simple hardware:** The MMU is smaller; no page-walk logic in silicon.
- **OS control:** The handler can implement custom policies (e.g., page coloring, NUMA placement) transparently.

### Disadvantages

- **Higher miss latency:** Every miss incurs exception overhead (pipeline flush, privilege switch, handler execution). A typical MIPS handler takes 10–20 cycles; a slow one much more.
- **Complex OS handler:** The handler must be extremely fast and written in assembly. Any bug causes a recursive TLB miss (TLB refill on the handler's own stack page), which must be handled carefully.
- **Nested miss problem:** The handler itself may touch virtual addresses that are not in the TLB, causing a recursive miss. MIPS reserves a wired set of TLB entries for the handler to map its own data.

## Comparison Table

| Property | Hardware-Managed | Software-Managed |
|---|---|---|
| Who handles miss | MMU hardware | OS exception handler |
| Page-table format | Fixed by ISA | Any (OS chooses) |
| Miss latency | Low (~4 memory reads) | Higher (exception + handler) |
| OS complexity | Lower | Higher |
| Common architectures | x86, x86-64, ARM | MIPS, SPARC, some RISC-V |
| Inverted page tables | Hard (need HW support) | Easy |

## Hybrid Approaches

Modern ARM supports both: the hardware can walk a standard VMSAv8-64 page table, but if the entry type indicates a "fault" the OS page-fault handler takes over. RISC-V Sv39/Sv48 also uses hardware walking for standard page tables but allows software-managed TLBs in custom MMU configurations.

## Which Is Better?

Neither is universally superior. x86's hardware-managed approach wins on latency-critical workloads. MIPS-style software management wins for research OSes, microkernels, and exotic memory models. The trend in commercial CPUs is toward hardware management because miss latency matters more than flexibility on modern workloads.

**Interview answer:** "Hardware-managed TLBs (x86, ARM) have the MMU autonomously walk a fixed-format page table on a miss — low latency but inflexible. Software-managed TLBs (MIPS) raise a TLB-miss exception and let the OS install the mapping — flexible page table formats but higher miss overhead due to exception entry and handler execution."
