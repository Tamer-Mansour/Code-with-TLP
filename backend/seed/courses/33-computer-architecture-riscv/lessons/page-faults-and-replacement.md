# Page Faults and Page Replacement

Not every valid virtual page needs to live in physical RAM at all times. The OS exploits this to run programs larger than available memory, implement lazy allocation, and share copy-on-write pages. The mechanism that makes all of this work is the **page fault**.

## What Is a Page Fault?

A **page fault** is a CPU exception raised by the MMU when a virtual address cannot be translated to a physical address. There are three distinct causes:

| Fault Type | Cause | OS Action |
|---|---|---|
| **Minor (soft) fault** | Page is valid but not yet in RAM (demand paging, CoW) | Map a frame, resume |
| **Major (hard) fault** | Page must be read from disk (swap) | I/O, then map, resume |
| **Invalid fault** | Address is not mapped at all (null deref, buffer overflow) | Send SIGSEGV to process |

RISC-V `scause` values:
- `12` — Instruction page fault
- `13` — Load page fault
- `15` — Store/AMO page fault

## The Page Fault Handler Flow

```
1. MMU raises page fault exception
2. CPU saves PC and registers, switches to supervisor mode
3. Kernel trap handler reads:
     scause  → fault type (load/store/instruction)
     stval   → faulting virtual address
4. Kernel looks up the process's virtual memory areas (VMAs)
5. Decision:
     a) VMA exists, page not present → allocate frame, fill it, update PTE, flush TLB, return
     b) VMA exists, write to read-only → copy-on-write? duplicate frame; else SIGSEGV
     c) No VMA → SIGSEGV (segmentation fault)
6. Kernel returns from trap; CPU retries the faulting instruction
```

The faulting instruction is **retried**, not skipped. The second attempt succeeds because the page is now present.

## Demand Paging

Modern OSes do not load an entire program into RAM at startup. Instead they:

1. Mark all pages as **not present** in the page table.
2. On the first access to each page, a page fault fires.
3. The kernel allocates a physical frame, copies the data from the executable file, marks the PTE valid, and resumes.

This is why large programs start quickly: only the pages actually needed are ever loaded.

```c
// After mmap(), pages are not in RAM yet:
char *buf = mmap(NULL, 1 << 30, PROT_READ, MAP_PRIVATE, fd, 0);

// First read from buf[0] causes a page fault:
char c = buf[0];   // page fault → kernel loads page 0 → resume
```

## Copy-on-Write (CoW)

After `fork()`, the child shares all physical frames with the parent. Both page tables point to the same frames, but both are marked read-only. On the first write by either process:

1. A **store page fault** fires.
2. The kernel detects CoW: it duplicates the frame.
3. The writing process gets its own copy; the PTE is updated to point to the new frame and marked writable.
4. The other process still points to the original frame.

This makes `fork()` O(1) instead of O(address space size).

## Page Replacement: What Happens When RAM Is Full?

When the kernel needs a new physical frame but none are free, it must **evict** an existing page:

1. Choose a **victim** page using a replacement policy.
2. If the victim page is **dirty** (D bit set), write it to the swap partition/file.
3. Update the victim's PTE: mark it invalid (V=0), store swap location.
4. Use the freed frame for the new page.

## Page Replacement Policies

| Policy | How it works | Notes |
|---|---|---|
| **OPT** | Evict the page used furthest in the future | Optimal, not implementable |
| **LRU** | Evict the least recently used page | Approximated in hardware |
| **Clock (Second Chance)** | Sweep through pages; skip A-bit=1, evict A-bit=0 | Practical approximation of LRU |
| **FIFO** | Evict the oldest page in RAM | Simple; suffers Belady's anomaly |
| **LFU** | Evict least frequently used | Thrashes with burst access patterns |

Linux uses a variant of **Clock** (the two-list clock) with the A (accessed) and D (dirty) bits set by hardware.

## Thrashing

**Thrashing** occurs when the working set of a process (the pages it actively uses) exceeds available physical RAM. The system spends more time handling page faults than executing instructions. Solutions:

- Reduce the number of runnable processes (suspend some).
- Add more RAM.
- Use huge pages to reduce page-fault frequency.

## Common Pitfall: Minor vs. Major Faults

A **minor** fault is cheap (no disk I/O) — the kernel just maps a frame. A **major** fault involves disk I/O and can take milliseconds. Profiling tools (`/proc/<pid>/stat`, `perf`, `valgrind`) distinguish these. A high major-fault rate is a sign of memory pressure.

## Interview Answer

> "A page fault is an MMU exception triggered when a virtual page is not present in physical RAM. The OS fault handler either allocates a frame and maps the page (minor/soft fault), reads it from swap (major/hard fault), or terminates the process if the address is invalid. Page replacement policies like Clock/LRU choose which existing page to evict when RAM is full."
