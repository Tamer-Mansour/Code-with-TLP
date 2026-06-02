# How Privilege Interacts with Virtual Memory

Virtual memory and privilege modes are deeply intertwined in RISC-V. The page table not only maps addresses but also encodes permission bits that the hardware enforces differently depending on the current privilege level. Understanding this interaction is essential for writing correct OS kernels and secure software.

## The satp Register: Enabling Paging

Virtual memory is disabled at reset. It is activated by writing a nonzero mode to `satp` (Supervisor Address Translation and Protection):

```
satp layout (RV64, Sv39 mode):
 ┌───────┬────────────┬──────────────────────────────────┐
 │ MODE  │    ASID    │              PPN                 │
 │[63:60]│  [59:44]   │            [43:0]                │
 └───────┴────────────┴──────────────────────────────────┘

MODE values:
  0  = Bare (no translation)
  8  = Sv39 (3-level, 39-bit VA)
  9  = Sv48 (4-level, 48-bit VA)
  10 = Sv57 (5-level, 57-bit VA)
```

Writing to `satp` is a privileged operation — only S-Mode and M-Mode can do it.

## Page Table Entry Permission Bits

Each leaf PTE (Page Table Entry) carries three permission bits:

| Bit | Name | Meaning |
|---|---|---|
| R | Read | Page is readable |
| W | Write | Page is writable |
| X | Execute | Page contains executable instructions |

Plus two bits that control cross-privilege access:

| Bit | Name | Meaning |
|---|---|---|
| U | User | U-Mode code can access this page |
| — | (no U bit) | Only S-Mode and above can access |

## How the Hardware Enforces Privilege-Based Access

```
Access attempt at virtual address VA:
  1. Walk page tables using PPN in satp.
  2. Find leaf PTE.
  3. Check R/W/X bits for the access type.
  4. Check U-bit vs. current privilege level:
       ─ Current mode = U-Mode:
           U-bit must be SET or the access faults.
       ─ Current mode = S-Mode:
           if SUM bit in sstatus is CLEAR:
               U-bit must be CLEAR or the access faults.
           if SUM bit in sstatus is SET:
               U-Mode pages are accessible (temporary kernel access).
  5. If any check fails → Page Fault exception.
```

This means a U-Mode process literally cannot read kernel pages, because those PTEs have U=0.

## The SUM Bit: Supervisor User Memory Access

Normally, S-Mode cannot read pages marked U=1. This prevents a class of kernel bugs where kernel code accidentally dereferences a user-supplied pointer. The kernel must explicitly opt in:

```c
// Copy 'n' bytes from user-space address 'src' (kernel code, S-Mode)
void copy_from_user(void *dst, const void __user *src, size_t n) {
    // Set SUM=1 to temporarily allow user-page access
    csr_set(sstatus, SSTATUS_SUM);
    memcpy(dst, src, n);   // user pointer now accessible
    csr_clear(sstatus, SSTATUS_SUM);
}
```

Keeping SUM clear by default provides defense-in-depth against accidentally trusting user pointers.

## The MXR Bit: Make eXecutable Readable

If a page has X=1 but R=0 (execute-only), the hardware normally faults on a read. Setting `MXR` in `mstatus`/`sstatus` relaxes this: execute-only pages become readable. This is sometimes used to allow execute-only memory while still permitting kernel reads during page fault handling.

## ASID: Address Space Identifiers

The ASID field in `satp` allows the TLB to cache entries from multiple address spaces simultaneously. Without ASIDs, every context switch requires a full TLB flush (`sfence.vma`). With ASIDs:

```asm
# Context switch: load new page table with a new ASID
csrw  satp, new_satp_with_asid   # new ASID selects new address space
sfence.vma                        # still needed if ASID wraps or is reused
```

The OS assigns ASIDs from a pool. When the pool is exhausted, it flushes the TLB and reassigns.

## Physical Memory Protection vs. Virtual Memory

PMP (Physical Memory Protection, configured in M-Mode) and virtual memory are independent but stacked:

```
U-Mode access:
  Virtual address → (page table walk) → physical address
  Physical address → (PMP check) → allowed or faulted

S-Mode access with paging on:
  Virtual address → (page table walk) → physical address
  Physical address → (PMP check, if PMP is configured for S-Mode)

M-Mode access:
  Physical address only (no page table walk)
  PMP check applies
```

PMP provides a second layer of protection even if the page table is misconfigured.

## Common Pitfall

Forgetting `sfence.vma` after modifying PTEs or writing `satp` is the single most common virtual-memory bug in kernel development. The CPU's TLB may hold a stale translation, causing:

- Old mappings to remain accessible (security hole).
- New mappings to fault (correctness bug).

Always issue `sfence.vma` after any PTE modification that affects current execution or after switching page tables.

## Worked Example: Page Fault Dispatch in the Kernel

```c
// scause values for page faults
#define CAUSE_INSN_PAGE_FAULT   12
#define CAUSE_LOAD_PAGE_FAULT   13
#define CAUSE_STORE_PAGE_FAULT  15

void page_fault_handler(long cause, uintptr_t stval) {
    // stval contains the faulting virtual address
    struct vm_area *vma = find_vma(current->mm, stval);

    if (!vma) {
        send_signal(current, SIGSEGV);   // no mapping at all
        return;
    }
    if (cause == CAUSE_STORE_PAGE_FAULT && !(vma->prot & PROT_WRITE)) {
        send_signal(current, SIGSEGV);   // write to read-only mapping
        return;
    }
    // Allocate a physical page and install the PTE
    handle_demand_paging(vma, stval);
    sfence_vma_addr(stval);              // flush TLB entry for this VA
}
```

> **Interview answer:** Virtual memory and privilege interact through PTE U-bits: pages with U=0 are kernel-only and fault on U-Mode access, while S-Mode is additionally blocked from U=1 pages unless SUM is set in sstatus, ensuring hardware-enforced isolation between kernel and user address spaces.
