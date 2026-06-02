# Quiz: Page Faults and Demand Paging

**Q1. Which hardware register on x86-64 holds the virtual address that caused a page fault?**
- [ ] RIP
- [ ] RSP
- [x] CR2
- [ ] CR3

The CPU automatically writes the faulting virtual address into CR2 when a page-fault exception is raised; the kernel reads it at the start of the fault handler.

---

**Q2. A process dereferences a pointer to a demand-paged heap page that has never been accessed before. What is the most likely outcome?**
- [ ] The process receives SIGSEGV and terminates
- [x] The kernel handles the page fault silently, allocates a zeroed frame, and the process continues normally
- [ ] The CPU raises a general protection fault and the OS reboots
- [ ] The access returns zero without any kernel intervention

Demand paging is designed for this case. The present bit is 0, but the address is covered by a valid VMA, so the kernel resolves the fault transparently.

---

**Q3. What is the key difference between a minor and a major page fault?**
- [ ] Minor faults affect user-space; major faults affect the kernel
- [ ] Minor faults involve the TLB; major faults involve the page table
- [x] A major fault requires disk I/O to resolve; a minor fault does not
- [ ] Minor faults are caused by null pointers; major faults by stack overflows

The classification is purely about whether the missing page must be fetched from disk (major) or is already present in physical memory (minor).

---

**Q4. Thrashing occurs when:**
- [ ] A process writes to a read-only memory segment
- [ ] The TLB hit rate falls below 50%
- [ ] A process accesses memory faster than the CPU cache can serve it
- [x] The sum of all processes' working sets exceeds available physical RAM, causing constant page eviction and re-faulting

Thrashing is a whole-system phenomenon caused by over-commitment of physical memory relative to total working set demand.

---

**Q5. A program calls `malloc(4096)` and then immediately writes to the returned buffer. Which sequence of events is correct on Linux with demand paging?**
- [ ] `malloc` allocates a physical frame; the write succeeds with no faults
- [ ] The write causes SIGSEGV because the page is not yet mapped
- [x] `malloc` records the allocation in the heap metadata; the write triggers a minor page fault; the kernel zero-fills a frame and maps it; the write succeeds
- [ ] `malloc` zero-fills the frame eagerly to avoid any fault on first access

`malloc` in glibc uses `brk`/`mmap` to expand the virtual address space but does not immediately back the pages with physical frames. The first write faults in the page.

---

**Q6. After `fork()`, the parent writes to a previously shared page. The kernel implements Copy-on-Write. Which signals or faults are involved?**
- [ ] SIGSEGV is sent to the parent; no page fault occurs
- [ ] A major page fault occurs; the page is reloaded from disk
- [x] A protection-violation page fault occurs; the kernel allocates a new frame, copies the page, and remaps the parent's PTE with write permission — no signal is delivered
- [ ] No fault occurs; the write silently corrupts the child's view of the page

CoW uses a write-protect page fault (error code: P=1, W=1) to intercept the first write to a shared page and create a private copy. The parent resumes normally after the copy.
