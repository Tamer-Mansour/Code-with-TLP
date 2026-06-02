# User-Level vs Kernel-Level Threads

Where a thread lives — in user space or the kernel — determines who schedules it, how fast it can be created, and what happens when it blocks.

## User-Level Threads (ULT)

User-level threads are managed entirely by a runtime library. The kernel sees only one entity: the process. Internally, the library multiplexes many threads onto that one kernel scheduling unit.

**How they work:**

- A user-space scheduler (part of the runtime) performs context switches.
- Context switch is pure user-space: save/restore registers, swap stack pointers — no syscall, no privilege level change.
- The kernel has no idea multiple threads exist.

```
User space   [Thread A] [Thread B] [Thread C]
                      ↕ (library scheduler)
Kernel space        [Process P]          ← kernel sees ONE entity
```

**Advantages:**

- Context switching is extremely fast (no syscall overhead).
- Thread creation is cheap — no kernel involvement.
- Scheduling policy is fully customizable by the runtime.
- Portable: works on any OS that has processes.

**Disadvantages:**

- If any thread makes a blocking syscall (e.g., `read()` on a slow socket), the **entire process blocks** — all other ULTs freeze.
- Cannot run truly in parallel on multiple CPU cores (kernel only schedules the one process).
- Signals delivered to the process interrupt one arbitrary thread.

```c
// Green thread / coroutine context switch (user space only)
// No syscall — just swap stack pointers and restore registers
static void switch_to(struct uthread *from, struct uthread *to) {
    // Save from's registers onto from->stack
    // Restore to's registers from to->stack
    // Update current thread pointer
}
```

## Kernel-Level Threads (KLT)

Kernel-level threads are first-class citizens that the kernel knows about and schedules directly. On Linux every thread is a separate `task_struct` created with `clone(CLONE_VM | CLONE_FILES | ...)`.

**How they work:**

- `pthread_create` on Linux calls `clone()` — a kernel syscall.
- The kernel scheduler sees each thread as a schedulable entity.
- Blocking one thread does not affect siblings.

```
User space   [Thread A] [Thread B] [Thread C]
                ↕           ↕          ↕       (syscall per thread)
Kernel space  [KLT A]   [KLT B]   [KLT C]   ← kernel schedules each
```

**Advantages:**

- Blocking one thread does not stall the process.
- True hardware parallelism: threads can run on different cores simultaneously.
- Signals can be directed to a specific thread.

**Disadvantages:**

- Thread creation requires a syscall — slower than ULT.
- Context switches cross the user/kernel boundary (mode switch overhead).
- The kernel limits total thread count (typically tens of thousands).

## Side-by-Side Cost Comparison

| Operation | User-Level Thread | Kernel-Level Thread |
|---|---|---|
| Create | ~100 ns | ~10 µs (syscall) |
| Context switch | ~50–200 ns | ~1–10 µs |
| Blocking syscall | Blocks all ULTs | Only blocks one KLT |
| Parallelism | No (N:1 mapping) | Yes (1:1 mapping) |

## Real-World Examples

- **User-level:** Go goroutines (managed by the Go runtime scheduler), Erlang processes, early Java green threads, Rust async tasks.
- **Kernel-level:** POSIX pthreads on Linux (via `clone`), Windows threads (`CreateThread`).

Go's goroutine runtime is a hybrid: many goroutines run on a pool of OS threads. When a goroutine does a blocking syscall, the runtime moves other goroutines to a different OS thread so they aren't stalled.

```go
// Go: goroutines are ULTs managed by the Go runtime (GOMAXPROCS OS threads)
go func() {
    // This runs as a goroutine; may share an OS thread with thousands of others
    data := fetchFromDB()  // if this blocks, runtime parks this goroutine
    process(data)
}()
```

## Common Pitfall

Candidates sometimes say "user-level threads can't block." The correct nuance is: a **blocking syscall** blocks the entire underlying kernel thread (and thus all ULTs on it). Non-blocking I/O or async syscalls let a ULT runtime stay responsive. That's exactly what Go, Node.js, and other async runtimes do.

> **Interview answer:** User-level threads are scheduled by a runtime library with no kernel involvement, making them very cheap to create and switch, but a blocking syscall freezes all of them. Kernel-level threads are scheduled by the OS, enabling true parallelism and independent blocking, at the cost of syscall overhead for creation and context switches. Most modern systems use a hybrid that maps many user-level tasks onto a pool of kernel threads.
