# Interview Drill: Virtual Memory Questions

These are the virtual memory questions that appear most frequently in systems engineering, kernel, and senior backend interviews. For each, study the crisp answer first, then read the deeper context.

---

## Q1. What is the difference between virtual and physical memory?

**Crisp answer:** Virtual addresses are per-process labels used by the CPU; physical addresses are actual RAM locations on the memory bus. The MMU translates between them using the process's page table on every memory access.

**Deeper context:** Two processes can use the same virtual address and get completely different data because their page tables map it to different physical frames. This is the foundation of process isolation.

---

## Q2. What happens when a process accesses an unmapped virtual address?

**Crisp answer:** The MMU raises a page fault. The OS handler checks whether the address is within a valid VMA (virtual memory area). If valid, it allocates a physical frame and updates the page table. If invalid, it sends SIGSEGV.

**Deeper context:** There are two fault types — a **minor fault** (page in memory but not yet mapped, no I/O) and a **major fault** (page on disk, requires I/O). The first access to a freshly `malloc`-ed page is always a minor fault due to demand paging.

---

## Q3. Why is `fork()` fast even for large processes?

**Crisp answer:** `fork()` uses Copy-on-Write — the child's page tables initially point to the same physical frames as the parent, marked read-only. Physical copying happens lazily only when either process writes to a shared page.

**Deeper context:** A shell spawning `ls` on a 2 GB process copies approximately zero bytes. If the child calls `exec()` immediately, even the eventual CoW writes are skipped. The only real work is duplicating the page table structure itself (a few thousand entries).

---

## Q4. What is the TLB and why does it matter?

**Crisp answer:** The Translation Lookaside Buffer is a small hardware cache of recent virtual-to-physical translations inside the MMU. A TLB hit costs ~1 cycle; a miss requires a full page table walk at ~10–100 cycles.

**Deeper context:** TLB misses become a bottleneck for workloads with large, random-access memory footprints. Using **huge pages** (2 MB or 1 GB instead of 4 KB) reduces the number of TLB entries needed by up to 512×, dramatically cutting miss rate for large datasets.

---

## Q5. What does the Linux OOM killer do, and how can you protect a process?

**Crisp answer:** When RAM and swap are exhausted, the OOM killer selects the process with the highest `oom_score` (based on memory use and age) and sends it `SIGKILL`. Set `oom_score_adj` to `-1000` to make a process immune.

```bash
echo -1000 > /proc/$(pidof critical-service)/oom_score_adj
```

**Deeper context:** The OOM killer is the last resort when overcommit bites. The better fix is setting `vm.overcommit_memory=2` and proper `cgroup` memory limits so the system never reaches OOM in the first place.

---

## Q6. What is ASLR and what does it protect against?

**Crisp answer:** Address Space Layout Randomization randomizes the base addresses of the stack, heap, and shared libraries on each process launch, preventing attackers from hardcoding addresses in exploits.

**Deeper context:** ASLR combined with PIE (position-independent executables) and NX (non-executable stack) forms the core of modern exploit mitigation. Bypasses exist (information leaks), but ASLR raises the bar significantly.

---

## Q7. Can `malloc` return non-NULL but then fail later?

**Crisp answer:** Yes — with Linux's default overcommit, `malloc` always succeeds. The failure happens silently when the process tries to write the page and the OOM killer terminates it instead.

**Deeper context:** Code relying on `malloc` returning `NULL` for OOM handling is broken on Linux with default settings. For reliable OOM detection, use `mlockall(MCL_FUTURE)` (locks all future pages; fails immediately on OOM) or check `/proc/meminfo` before large allocations.

---

## Q8. What is thrashing?

**Crisp answer:** Thrashing is when the combined working sets of all processes exceed available RAM, causing continuous page faults as every newly-loaded page immediately evicts another needed page, resulting in near-zero useful CPU work.

**Deeper context:** Classic symptom: `vmstat 1` shows `si`/`so` (swap-in/swap-out) both > 0 and large, while `us` (user CPU) is near zero. Diagnosis confirms thrashing; solution is reducing working set size, adding RAM, or using cgroup memory limits to isolate workloads.

---

## Q9. How does a shared library save memory compared to static linking?

**Crisp answer:** A shared library's text (code) pages are mapped into every process's address space but backed by a **single set of physical frames** — 100 processes using `libc.so` share one physical copy of its 2 MB code, not 100 copies.

**Deeper context:** This works because code pages are read-only (and execute-only on systems with PKU). Data pages in shared libraries are CoW-shared and diverge per-process only if written. PLT/GOT entries in each process are writable and process-private.

---

## Q10. What is the difference between RSS and VSZ?

**Crisp answer:** VSZ (Virtual Size) is the total virtual address space reserved by the process; RSS (Resident Set Size) is how much of that is currently backed by physical RAM frames.

**Deeper context:** A process that `mmap`s a 10 GB file has 10 GB of VSZ but perhaps only 100 MB of RSS if only a fraction is actively accessed. RSS also counts shared pages (libc code), so summing RSS across all processes double-counts shared frames — use `/proc/meminfo`'s `MemFree` for system-wide pressure.

```bash
ps -o pid,vsz,rss,comm -p $$
# VSIZ in KB, RSS in KB
```

---

**Interview answer (meta):** The pattern across all virtual memory questions is: understand the **indirection** (virtual → physical via MMU), the **deferred work** (lazy allocation, CoW), and the **cost** (TLB misses, page faults, swap latency) — every specific question is a variation on these three themes.
