# Interview Drill: Page Faults and Segfaults

This lesson collects the most frequently asked interview questions on page faults, demand paging, and segmentation faults, with model answers you can adapt and deliver confidently.

---

## Q1. What is a page fault, and is it always a bug?

**Model answer:** A page fault is a CPU exception raised by the MMU when a virtual address has no valid present mapping in the page table. It is *not* always a bug. Most page faults are normal and expected — they are how demand paging works. The kernel resolves recoverable faults silently. Only when the access is to an unmapped or permission-violated address does the kernel send SIGSEGV.

**Follow-up trap:** "So when does a page fault become a problem?" — When it happens too frequently (high fault rate → poor EAT) or when physical memory is exhausted and faults require disk I/O on every access (thrashing).

---

## Q2. What is the difference between a minor and a major page fault?

**Model answer:** A minor fault requires no disk I/O — the page is already in physical memory (e.g., shared library in page cache) but not yet mapped in the faulting process's page table. A major fault requires reading data from disk or swap, blocking the process for hundreds of microseconds to milliseconds.

**Numbers to remember:**
- Minor fault: ~1–5 µs
- Major fault: ~100 µs – 20 ms (SSD vs spinning disk)

---

## Q3. Walk me through what happens when a process dereferences a null pointer.

**Model answer:**
1. The CPU attempts to read virtual address 0x0.
2. The MMU raises a page-fault exception; CR2 = 0x0.
3. The kernel's fault handler reads CR2 and searches the process's VMA list.
4. No VMA covers address 0 — it is deliberately unmapped.
5. The kernel sends SIGSEGV to the process.
6. The default signal handler terminates the process and optionally dumps core.

---

## Q4. What causes thrashing, and how does the OS detect and prevent it?

**Model answer:** Thrashing occurs when the sum of all processes' working sets exceeds available physical RAM. Pages are evicted and immediately re-faulted, so the CPU spends almost all its time on disk I/O. Detection: monitor the `pgscan`/`pgsteal` ratio in `/proc/vmstat`, or high swap I/O from `vmstat`. Prevention: admission control — only run a process if its working set fits in available frames; suspend (swap out) entire processes to reduce multiprogramming degree.

---

## Q5. What is the working set of a process?

**Model answer:** The working set W(t, Δ) is the set of distinct pages accessed by the process during the window (t−Δ, t]. It captures temporal locality. If the working set fits in physical memory, the process runs without page faults. The OS must ensure total working set size ≤ available frames to avoid thrashing.

---

## Q6. How does demand paging reduce memory usage?

**Model answer:** When a program is loaded, the OS maps its code and data into virtual pages but sets every present bit to 0. Physical frames are allocated only when a page is first accessed. Pages that are never touched (dead code, large tables never indexed) consume zero physical memory. A 200 MB binary that only executes 20 MB of code paths uses roughly 20 MB of RAM, not 200 MB.

---

## Q7. What is the difference between SIGSEGV and SIGBUS?

**Model answer:** Both indicate invalid memory access, but the causes differ. SIGSEGV means the address is either unmapped or has wrong permissions (e.g., write to read-only, execute on NX page). SIGBUS typically means the address is mapped but the access itself is invalid — common causes are accessing beyond the end of an `mmap`'d file, or an unaligned access on a strict-alignment architecture.

---

## Q8. How does `fork()` use page faults to implement Copy-on-Write?

**Model answer:** After `fork()`, parent and child share all physical pages. The kernel marks both sets of PTEs as read-only. When either process writes to a shared page, a protection-violation page fault fires. The kernel then allocates a new frame, copies the page's content, and remaps the writer's PTE to the new frame with write permission. This "copy on write" means `fork()` is O(1) if the child immediately `exec()`s.

---

## Quick-fire cheat sheet

| Question | One-line answer |
|---|---|
| What triggers a page fault? | MMU can't translate a virtual address (present bit = 0 or no PTE) |
| What register holds the faulting address on x86? | CR2 |
| What signal does a bad-pointer dereference produce? | SIGSEGV |
| Minor fault vs major fault key difference? | Disk I/O required (major) or not (minor) |
| Best fix for thrashing? | Reduce multiprogramming degree; suspend whole processes |
| How does demand paging benefit `fork()`? | Copy-on-Write — no immediate copying of parent pages |
