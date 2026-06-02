# Quiz: Virtual Memory and Address Spaces

Test your understanding of virtual memory concepts covered in this module.

---

**Q1. Two processes both print the value `0x7fff1234abc0` as the address of a local variable. What is true?**

- [ ] They are sharing the same physical memory location.
- [x] They have separate virtual addresses that map to different physical frames.
- [ ] This is impossible; each process must get a unique virtual address.
- [ ] The OS must have misconfigured the page tables.

_Virtual addresses are per-process. The same virtual address in two separate processes maps to different physical frames through their independent page tables._

---

**Q2. A process calls `malloc(1 GB)` and the call returns a non-NULL pointer. Which statement is most accurate on a Linux system with default overcommit settings?**

- [ ] 1 GB of physical RAM has been reserved and zeroed.
- [ ] The call will always fail because 1 GB exceeds available swap.
- [x] Virtual address space is reserved but no physical frames are allocated yet; they are allocated on first access.
- [ ] The kernel immediately compresses existing pages to make room.

_Linux uses demand paging and overcommit: `malloc` succeeds by reserving virtual space. Physical frames are allocated only when pages are first touched (written), triggering minor page faults._

---

**Q3. What hardware register does the MMU use to locate the current process's page table on x86-64?**

- [ ] `RSP` (stack pointer)
- [ ] `PTBR` (a dedicated register in user space)
- [x] `CR3` (control register 3)
- [ ] `GDTR` (global descriptor table register)

_On x86-64, `CR3` holds the physical base address of the top-level page table (PML4). The OS updates it on every context switch to switch address spaces._

---

**Q4. A process calls `fork()`. Before either the parent or child writes to any page, how many physical frames hold the parent's heap data?**

- [ ] Double — both parent and child get their own copy immediately.
- [ ] Zero — the heap is stored on disk after fork.
- [x] The same number as before the fork — pages are shared read-only via Copy-on-Write.
- [ ] Half — the OS splits the pages between parent and child.

_Copy-on-Write means `fork()` only copies the page table structure. Physical frames are shared (read-only) until a write triggers a fault, at which point only the written page is copied._

---

**Q5. What is the primary purpose of the TLB (Translation Lookaside Buffer)?**

- [ ] To back up page tables to disk during low-memory conditions.
- [ ] To store recently used disk pages for faster swap-in.
- [x] To cache recent virtual-to-physical address translations so the page table does not need to be walked on every memory access.
- [ ] To enforce W^X (write-XOR-execute) permissions on memory pages.

_The TLB is a small, fast hardware cache inside the MMU. A TLB hit (~1 cycle) avoids the multi-level page table walk (~10–100 cycles) that would otherwise be required for every single memory access._

---

**Q6. When the OOM killer selects a victim process, what is the primary metric it uses?**

- [ ] The process that has been running the longest.
- [ ] The process owned by the user with the most processes.
- [x] The process with the highest `oom_score`, which is based primarily on physical memory consumption relative to system memory.
- [ ] Always the most recently started process.

_Linux computes an `oom_score` (0–1000) for each process, weighted heavily by RSS (resident physical memory). Administrators can influence this with `oom_score_adj` — setting it to `-1000` makes a process immune from the OOM killer._
