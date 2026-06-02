# The Page Fault Handling Path Step by Step

Understanding the exact sequence of events during a page fault is essential for kernel interviews and for diagnosing performance problems. This lesson traces the path from the offending instruction all the way back to user-space execution resuming.

## Step 1 — The MMU fires the hardware exception

The CPU attempts a memory access. The MMU walks the page table in hardware (on modern CPUs) and finds either no entry or a present-bit of zero. The hardware:

- Saves the current privilege level and flags.
- Writes the faulting virtual address into `CR2` (x86) or `FAR_EL1` (ARM64).
- Pushes the error code and instruction pointer onto the kernel stack.
- Jumps to the page-fault vector in the Interrupt Descriptor Table (IDT).

## Step 2 — The kernel entry stub

The low-level assembly entry point (e.g., `asm_exc_page_fault` on Linux) saves all general-purpose registers onto the kernel stack, then calls the C-level handler `do_page_fault()` (or `handle_mm_fault()` at the next layer).

```asm
; x86-64 simplified entry (Linux arch/x86/entry/entry_64.S)
asm_exc_page_fault:
    push  %rax           ; save caller registers
    ...
    call  do_page_fault  ; jump to C handler
```

## Step 3 — Identify the faulting address and the VMA

The kernel reads `CR2` to get the virtual address, then walks the process's **Virtual Memory Area** (VMA) list (an rb-tree in Linux's `mm_struct`) to find which VMA — if any — covers that address.

```
VMA found?
  No  → invalid address → send SIGSEGV → done
  Yes → check permissions (read/write/exec match error code?)
          No  → protection fault → send SIGSEGV → done
          Yes → proceed to resolve
```

## Step 4 — Decide how to satisfy the fault

Depending on the VMA type, the kernel calls the appropriate *fault handler*:

| VMA backing | Handler action |
|---|---|
| Anonymous (heap/stack) | Allocate a zeroed physical frame |
| File-backed (`mmap`) | Read the page from the file system or page cache |
| Swap-backed | Read the page from the swap device |
| Copy-on-Write | Allocate a new frame, copy the parent's content |

For a **major fault** (data must come from disk), the process is put to sleep and a disk I/O is submitted. For a **minor fault** (page is already in memory, just not mapped), the PTE is updated immediately.

## Step 5 — Update the page table entry

Once the physical frame is ready:

1. The kernel writes the physical frame number and permission bits into the PTE.
2. The present bit is set to 1.
3. On SMP systems, a TLB shootdown IPI is sent to other CPUs if needed.

```c
// Conceptual PTE update (Linux mm/memory.c style)
set_pte_at(mm, address, ptep, mk_pte(page, vma->vm_page_prot));
update_mmu_cache(vma, address, ptep);
```

## Step 6 — Return to user space

The kernel unwinds the exception stack, restores all saved registers, and executes `iretq` (x86) or `eret` (ARM). The CPU re-executes the *same instruction* that caused the fault — this time the PTE is present, the MMU walk succeeds, and the instruction completes normally.

```
User instruction → #PF → kernel handler → PTE updated → iretq
                                                           │
                                            CPU re-runs same instruction
                                            (now succeeds silently)
```

## The full timeline at a glance

```
1. MMU walk fails       (~0 ns extra — hardware)
2. Save context          (~100 ns)
3. Find VMA              (~200 ns)
4. Allocate/copy frame   (~1–5 µs for minor fault)
5. Disk I/O if needed    (~100–500 µs for major fault)
6. Update PTE + TLB      (~200 ns)
7. iretq, re-execute     (~100 ns)
```

A minor page fault adds roughly 1–5 microseconds of latency. A major fault adds hundreds of microseconds — the cost of a disk seek.

**Interview answer:** The page fault path is: MMU raises the exception → kernel reads CR2 → finds the VMA → allocates or loads the missing page → writes the PTE → returns via iretq, re-executing the faulting instruction, which now succeeds.
