# Copy-on-Write and Lazy Allocation

Two of the most impactful memory-saving techniques in modern OS design are **Copy-on-Write (CoW)** and **lazy (demand) allocation**. Both defer real physical work until it is absolutely necessary — making `fork()` fast, memory allocation cheap, and shared libraries efficient.

## Lazy Allocation (Demand Paging)

When a process calls `malloc(N)` or `mmap(...)`, the OS updates its virtual address space metadata but does **not** immediately allocate physical frames or zero memory. Physical pages are allocated only when the process first **accesses** (reads or writes) a virtual page.

```
malloc(4096)   → virtual range reserved, no physical frame yet
first write    → MMU: no mapping → page fault
               → OS: allocate frame, zero it, install mapping
               → process continues — transparent to the program
```

Benefits:
- **Faster allocation** — no physical memory touch at `malloc` time.
- **Lower peak RSS** — pages never touched never consume RAM.
- **Overcommit** — the OS can grant more virtual memory than RAM because most is never used simultaneously.

Cost: the first access to each page pays a minor fault (~1–5 µs). For latency-sensitive code, pre-fault with `mlock()`.

## Copy-on-Write

**CoW** is an optimization for sharing read-only data between multiple address spaces. The classic example is `fork()`.

### fork() Without CoW

Without CoW, `fork()` must copy the entire parent address space — potentially gigabytes — before the child can run. This is catastrophically slow when the child immediately calls `exec()` (the common pattern for shell commands).

### fork() With CoW

```
Parent process (8 GB address space)
    │
    ├─ fork() called
    │
    ▼
Child process created:
  All page table entries point to SAME physical frames as parent.
  Both parent and child pages marked READ-ONLY.

Parent writes to page X:
  MMU: write to read-only page → protection fault
  OS: allocate new frame, copy page X into it, mark writable,
      update PARENT's page table entry
  → parent has its own private copy of page X

Child writes to page Y:
  Same process → child gets its own private copy of page Y

Pages never written → shared forever (zero physical cost)
```

The entire `fork()` system call completes in microseconds regardless of address space size, because no data is copied — only page table entries are duplicated and permissions are toggled.

```c
pid_t pid = fork();
if (pid == 0) {
    // Child: if it just calls exec(), zero pages were ever copied!
    execve("/bin/ls", argv, envp);
}
// Parent: continues; its pages are still shared until written.
```

## CoW in Other Contexts

### Anonymous mmap

When a new anonymous page is first read before being written, Linux maps it to a global **zero page** (a single, permanently read-only, zeroed physical frame shared by all processes). Only on the first write is a fresh frame allocated.

```
Process reads newly-allocated page → maps to zero page (shared, free)
Process writes to that page        → CoW fault → private zeroed frame
```

### Shared Libraries

`libc.so` is loaded once into physical memory. All processes that use it map the same physical frames read-only (or execute-only) into their address spaces. No copying. If a library page were ever modified (unusual), CoW would give that process a private copy.

### `fork()` in Python / Redis

Redis and CPython's multiprocessing module heavily exploit `fork()` + CoW:

```python
import os
data = [0] * 10_000_000   # 80 MB list
pid = os.fork()
if pid == 0:
    # Child reads 'data' for a snapshot — no physical copy made!
    # Only pages the child writes get duplicated.
    os._exit(0)
```

## Pitfall: CoW and Reference Counting

Linux tracks CoW pages using a **reference count** on each physical frame. When the count drops to 1 (only one process references it), the remaining process's page table entry is silently upgraded to writable — avoiding a fault on the next write.

Forgetting this can mislead profiling: a process's RSS (Resident Set Size) will grow after `fork()` as CoW pages are gradually duplicated by writes — even if no explicit allocation was made.

```bash
# Watch RSS grow due to CoW faults after fork:
/usr/bin/time -v ./program 2>&1 | grep "Maximum resident"
```

**Interview answer:** Lazy allocation defers physical frame assignment until first access, and Copy-on-Write shares physical pages between processes (especially after `fork`) by marking them read-only and making a private copy only when a write occurs — both techniques dramatically reduce actual physical memory consumption without changing program semantics.
