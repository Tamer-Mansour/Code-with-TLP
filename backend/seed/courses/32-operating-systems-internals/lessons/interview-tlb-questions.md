# Interview Drill: TLB and Translation Performance

This lesson collects the most common TLB and address-translation interview questions. For each question, you get the key concepts to hit and a crisp one-or-two-sentence model answer — the kind of answer that lands well in a 45-minute systems design or OS fundamentals interview.

---

## Q1. What is the TLB and why does it exist?

**Concepts to hit:** translation lookaside buffer, virtual-to-physical mapping cache, page-table walk cost.

**Model answer:** "The TLB is a small, fast hardware cache inside the CPU that stores recent virtual-to-physical page mappings. Without it, every memory access would require 2–5 additional memory reads to walk the page table, making virtual memory prohibitively slow."

---

## Q2. What happens on a TLB miss on x86-64?

**Concepts to hit:** hardware page-table walk, CR3 register, 4-level PML4 structure, page fault if P=0.

**Model answer:** "The hardware MMU walks the four-level page table autonomously, reading one entry per level from physical memory using CR3 as the root. If it finds a valid Present bit at every level it installs the mapping and retries the instruction; otherwise it raises a page fault to the OS."

---

## Q3. What is the Effective Memory Access Time formula for a TLB?

**Concepts to hit:** hit ratio h, memory access time t_mem, page-table levels k, formula.

**Model answer:** `EMAT = h × t_mem + (1-h) × (k+1) × t_mem`. At 95% hit ratio with a 2-level table and 100 ns memory, EMAT ≈ 110 ns versus 300 ns without any TLB."

---

## Q4. Why does a context switch hurt TLB performance, and how do ASIDs fix it?

**Concepts to hit:** page-table switch, full TLB flush, ASID tag, cold-start penalty, PCID on x86.

**Model answer:** "Without ASIDs, switching processes requires flushing all TLB entries because VPNs are only meaningful within one address space. ASIDs tag each entry with a process identifier so entries from multiple processes coexist — no flush is needed on a switch unless the ASID namespace is exhausted."

---

## Q5. What is the difference between a hardware-managed and a software-managed TLB?

**Concepts to hit:** MMU walks automatically (x86/ARM) vs. TLB-miss exception to OS (MIPS), flexibility vs. latency.

**Model answer:** "Hardware-managed TLBs (x86, ARM) have the MMU walk a fixed-format page table automatically — low miss latency but the format is dictated by the ISA. Software-managed TLBs (MIPS) raise an exception on every miss and let the OS install the mapping — any page table format works, but the exception overhead is higher."

---

## Q6. What is a VIPT cache and why does it require a size constraint?

**Concepts to hit:** virtually indexed / physically tagged, parallel TLB and cache lookup, aliasing, index bits ≤ page offset bits.

**Model answer:** "VIPT uses virtual address bits to index cache sets (fast, parallel with TLB) but compares using physical tags (from TLB). To avoid aliasing, the number of index bits must not exceed the page-offset width, meaning cache size ÷ associativity ≤ page size (e.g., ≤ 4 KB for a direct-mapped cache with 4 KB pages)."

---

## Q7. How do huge pages improve TLB performance?

**Concepts to hit:** coverage per entry (4 KB vs 2 MB vs 1 GB), fewer entries needed for same working set, databases/JVMs.

**Model answer:** "A 2 MB huge page gives one TLB entry 512× the coverage of a 4 KB page. A process with a 512 MB heap needs 131,072 normal TLB entries but only 256 huge-page entries to achieve 100% coverage — well within a typical 512-entry TLB. This is why databases and the JVM use huge pages."

---

## Q8. What is TLB shootdown and when is it needed?

**Concepts to hit:** multi-core TLBs are independent, unmapping a page requires invalidating all CPUs' TLBs, IPI (inter-processor interrupt), INVLPG.

**Model answer:** "When the OS unmaps a page (e.g., `munmap`, COW fork), every CPU that might have the old mapping in its TLB must invalidate it. The OS sends an inter-processor interrupt (IPI) to all other cores, each of which executes INVLPG (x86) or TLBI (ARM) for the affected address. This coordination overhead is called a TLB shootdown and can be expensive on highly parallel workloads."

---

## Common Pitfalls to Avoid in Interviews

- Confusing the TLB with the data cache — they work in sequence, not as alternatives.
- Saying "TLB miss goes to the OS" without qualifying whether the architecture is hardware- or software-managed.
- Forgetting that EMAT depends on the workload's hit ratio, not just hardware specs.
- Assuming context switches always flush the TLB — modern kernels use ASIDs/PCIDs to avoid this.
- Ignoring the TLB shootdown cost in multi-core memory management discussions.
