# Interview Drill: Process vs Thread Questions

This lesson walks through the most frequently asked process-vs-thread interview questions at software engineering and systems roles. For each question, you get the expected crisp answer plus the follow-up a strong candidate raises unprompted.

---

## Q1. What is the difference between a process and a thread?

**Crisp answer:** A process is an isolated execution environment with its own address space, file descriptors, and OS resources. A thread is an execution context within a process that shares the address space and resources with peer threads but has its own stack, registers, and program counter.

**Raise unprompted:** The key trade-off is isolation vs. communication speed. Threads communicate via shared memory (fast, no copy), but a crash in one thread can corrupt shared state and kill the whole process. Separate processes are isolated but must use IPC.

---

## Q2. What is shared between threads in the same process?

| Shared | Not Shared |
|---|---|
| Virtual address space (code, heap, globals) | Stack |
| Open file descriptors | Registers / PC |
| Signal handlers | errno (TLS) |
| Current working directory | Signal mask |
| Memory maps | Thread ID |

**Crisp answer:** Threads share the code, heap, global variables, file descriptors, signal handlers, and memory mappings. Each thread has its own stack, register set, program counter, signal mask, and errno (via thread-local storage).

---

## Q3. Why is creating a thread cheaper than creating a process?

**Crisp answer:** `fork()` must duplicate (or CoW-mark) the entire page table and all OS metadata for the new address space. `pthread_create` only allocates a new stack (a single `mmap` call) and a Thread Control Block — the rest of the process's resources are simply shared.

**Common follow-up — "How much cheaper?"** Thread creation: ~5–20 µs. Process creation: ~50–500 µs depending on address space size and kernel version.

---

## Q4. What happens to other threads when one thread calls `exit()`?

**Crisp answer:** `exit()` terminates the entire process, killing all threads immediately. If you want only the calling thread to end, call `pthread_exit()` instead.

```c
// terminates ALL threads
exit(0);

// terminates only the calling thread; others keep running
pthread_exit(NULL);
```

---

## Q5. What is a race condition? Give a concrete example.

**Crisp answer:** A race condition occurs when two threads access shared mutable state concurrently and the result depends on scheduling order.

```c
// Global counter, two threads each increment 1000 times
int counter = 0;

void *inc(void *_) {
    for (int i = 0; i < 1000; i++)
        counter++;    // read-modify-write is NOT atomic on x86 without lock prefix
    return NULL;
}
// Expected: 2000. Actual: anywhere from 1000 to 2000.
```

**Fix:** Use `_Atomic int counter` or protect with a mutex.

---

## Q6. What is a deadlock? What are its four necessary conditions?

**Crisp answer:** Deadlock is a state where two or more threads are each waiting for a resource held by another, forming a cycle that never resolves.

The four conditions (Coffman, 1971 — must ALL hold):

1. **Mutual exclusion** — resources cannot be shared.
2. **Hold and wait** — a thread holds a resource and waits for another.
3. **No preemption** — resources cannot be forcibly taken.
4. **Circular wait** — a cycle exists in the wait graph.

**Prevention tip:** Always acquire locks in a consistent global order to break circular wait.

---

## Q7. What is the difference between user-level and kernel-level threads?

**Crisp answer:** User-level threads are managed by a runtime library; the kernel sees one scheduling entity per process. They switch cheaply (no syscall) but a blocking call stalls all of them. Kernel-level threads are scheduled by the OS directly; each can block independently and run in true parallel, but creation and context switches involve syscall overhead.

**Follow-up:** Go goroutines are M:N — many goroutines multiplexed onto a pool of OS threads, combining fast creation with true parallelism.

---

## Q8. Why are thread context switches cheaper than process context switches?

**Crisp answer:** A thread switch leaves the page table base register (`cr3`) unchanged, so the TLB stays valid and the cache stays warm. A process switch loads a new `cr3`, causing a TLB flush and cache cold-start — potentially 10–100x more latency.

---

## Q9. What is thread-local storage and when would you use it?

**Crisp answer:** TLS gives each thread its own private copy of a variable, backed by a per-thread memory block pointed to by the `fs` register on x86-64. Use it for per-thread state that would otherwise require a lock: per-thread error codes (`errno`), allocator caches, profiling buffers, or PRNG seeds.

---

## Q10. Can two threads in the same process run on two different CPU cores simultaneously?

**Crisp answer:** Yes — with kernel-level threads (1:1 model). The kernel scheduler can place two threads on two cores. This is true parallelism. With user-level threads (N:1 model) all threads share one kernel thread and cannot run truly in parallel.

---

## Quick-Reference Cheat Sheet

```
Process  = address space + resources + ≥1 threads
Thread   = PC + registers + stack (shares everything else in process)

fork()   = new process, new address space, expensive
clone()  = new thread (or process), shares address space, cheap

Shared:  code, heap, globals, fds, signal handlers, mmaps
Private: stack, regs, PC, errno, signal mask, TID, TLS

User thread switch:   ~100–500 ns, no TLB flush
Kernel thread switch: ~1–3 µs, no TLB flush (same process)
Process switch:       ~10–200 µs, TLB flush + cache cold-start
```
