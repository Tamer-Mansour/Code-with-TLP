# Quiz: Threads: User vs Kernel and What Is Shared

**Q1. Which of the following is NOT shared between threads in the same process?**

- [ ] The heap
- [ ] Open file descriptors
- [x] The thread's stack
- [ ] Global variables

Each thread requires its own private call stack to track its own function call chain, local variables, and return addresses. All other options are shared across threads within the same process.

---

**Q2. A web server creates one OS thread per incoming connection. After handling 50,000 simultaneous connections, performance collapses. What is the most likely root cause?**

- [ ] The heap is exhausted because threads share it
- [ ] TLS cannot hold more than 32,768 entries
- [x] Each kernel thread consumes stack memory and a kernel TCB, exhausting resources at scale
- [ ] User-level threads cannot handle more than 10,000 connections

Kernel threads each require a stack (default 8 MB reserved on Linux) and a kernel data structure. At 50,000 threads, the virtual address space for stacks alone approaches 400 GB, and the kernel TCB table becomes a scheduling bottleneck. This is the classic "C10K problem."

---

**Q3. A thread calls `exit(0)`. What happens to the other threads in the same process?**

- [ ] They continue running; only the calling thread terminates
- [ ] They are suspended until a new thread calls `pthread_resume`
- [x] The entire process terminates and all threads are killed immediately
- [ ] They receive SIGTERM and can choose to ignore it

`exit()` is a process-level call that tears down the entire process. To terminate only the calling thread, a thread should call `pthread_exit()` instead.

---

**Q4. What is the primary reason a process context switch is more expensive than a thread context switch within the same process?**

- [ ] The kernel must send a signal to all threads in the outgoing process
- [ ] Process PCBs are larger than Thread Control Blocks
- [x] Switching processes loads a new page table base, causing a TLB flush and cold cache
- [ ] The kernel must checkpoint all open file descriptors

The dominant cost is the TLB flush triggered by loading a new `cr3` (page table base) register. TLB misses that follow force costly page-table walks for every subsequent memory access. Thread switches within the same process leave `cr3` unchanged.

---

**Q5. Which threading model allows millions of goroutines in Go while still achieving true hardware parallelism?**

- [ ] N:1 — all goroutines on a single kernel thread
- [ ] 1:1 — one kernel thread per goroutine
- [x] M:N — many goroutines multiplexed over a pool of kernel threads
- [ ] 1:N — one goroutine per multiple kernel threads

Go's runtime scheduler implements M:N threading: `GOMAXPROCS` OS threads serve as carriers for an arbitrary number of goroutines. When a goroutine blocks on a syscall, the runtime hands off the processor context to another OS thread so other goroutines continue running in parallel.

---

**Q6. A developer uses `__thread int cache_hits = 0;` in a C multi-threaded server. What is true about `cache_hits`?**

- [ ] All threads share one `cache_hits` counter; access must be protected by a mutex
- [ ] The variable is stored in the process heap and is zero-initialized on each access
- [x] Each thread has its own private copy of `cache_hits`; no synchronization is needed
- [ ] The variable is read-only after the first thread initializes it

`__thread` (equivalent to `thread_local` in C11/C++) declares a Thread-Local Storage variable. The compiler generates accesses via the `fs` segment register on x86-64, pointing to each thread's own TLS block. The copies are completely independent, requiring no locks.
