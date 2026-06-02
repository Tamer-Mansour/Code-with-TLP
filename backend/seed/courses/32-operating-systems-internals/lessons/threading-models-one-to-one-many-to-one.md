# Threading Models: 1:1, N:1, and M:N

Threading models describe how user-visible threads map onto kernel scheduling entities. The choice of model determines parallelism potential, blocking behavior, and creation cost.

## N:1 — Many User Threads, One Kernel Thread

All user threads in a process are multiplexed onto a single kernel thread by a user-space scheduler.

```
User space:   T1  T2  T3  T4  T5
               \   |   |   |  /
                [library scheduler]
                        |
Kernel space:          KT1        ← only one kernel thread
```

**Characteristics:**

- Context switch is pure user space — very fast.
- One blocking syscall blocks all user threads.
- No true parallelism even on multi-core hardware.
- Kernel has no visibility into thread count or identity.

**Historical use:** Early Java "green threads" (pre-1.3), early POSIX thread libraries on Solaris.

**When it still makes sense:** Systems with thousands of lightweight coroutines that never block on slow I/O (compute-bound pipelines, cooperative simulation loops).

## 1:1 — One User Thread per Kernel Thread

Each user thread is backed by its own kernel thread. This is the dominant model on modern Linux and Windows.

```
User space:   T1   T2   T3
               |    |    |
Kernel space: KT1  KT2  KT3   ← kernel schedules each independently
```

**Characteristics:**

- One blocked thread does not affect others.
- True hardware parallelism on SMP.
- Thread creation costs a syscall.
- Context switches cross the user/kernel boundary.
- Kernel thread limits apply (Linux: /proc/sys/kernel/threads-max, typically 32K–4M).

**Implementations:** Linux pthreads (NPTL), Windows `CreateThread`, macOS Grand Central Dispatch (underlying threads).

```bash
# Check Linux thread limit
cat /proc/sys/kernel/threads-max     # e.g., 126975
cat /proc/sys/vm/max_map_count       # related virtual address limit
```

## M:N — Many User Threads on M Kernel Threads (M < N)

A pool of M kernel threads serves N user threads. The user-space runtime scheduler decides which user thread runs on which kernel thread.

```
User space:   T1  T2  T3  T4  T5  T6
               \   |    \ /    |   /
          [runtime scheduler / work-stealing]
               /              \
Kernel space: KT1             KT2    ← M kernel threads, N user threads
```

**Characteristics:**

- When a user thread blocks, the runtime can move another user thread to an idle kernel thread — no stall.
- True parallelism up to M cores.
- Runtime complexity is significant (scheduler must handle blocking syscalls, signal delivery).
- Best of both worlds in theory; complex in practice.

**Implementations:** Go runtime (`GOMAXPROCS` kernel threads, unlimited goroutines), Erlang VM, early Windows UMS (User-Mode Scheduling), Haskell GHC runtime.

### Go's M:N Scheduler in Practice

```
Goroutines (G):  G1 G2 G3 G4 G5 G6 ... G10000
                 distributed across
OS threads (M):  M1  M2  M3  M4         (= GOMAXPROCS, default = num CPUs)
                 each M has a local run queue (P = processor context)

When G blocks on syscall:
  - Runtime parks G on the M making the syscall
  - A "handoff" gives the P (processor) to another idle M
  - Other goroutines keep running
```

## Comparison Table

| Model | Parallelism | Blocking behavior | Creation cost | Complexity |
|---|---|---|---|---|
| N:1 | None | One blocks all | Very low | Low |
| 1:1 | Full (up to cores) | Independent | Moderate (syscall) | Low |
| M:N | Full (up to M cores) | Handled by runtime | Very low | High |

## Which Model Should You Recommend?

- **Default choice:** 1:1 (pthreads / OS threads) — simple, debuggable, supported everywhere.
- **Millions of concurrent tasks:** M:N via a language runtime (Go, Erlang) or async framework (asyncio, Tokio).
- **Compute-only with zero blocking:** N:1 (coroutines) — minimize scheduling overhead.

## Common Pitfall

Many candidates conflate M:N with "async/await." Async frameworks (Node.js, Python asyncio) typically use a single-threaded event loop (N:1) for async I/O, not a true M:N scheduler. Go's runtime is the canonical M:N example.

> **Interview answer:** N:1 maps all user threads to one kernel thread — cheap but no parallelism and one blocking call stalls everything. 1:1 gives each user thread its own kernel thread — true parallelism and independent blocking at the cost of syscall overhead. M:N runs many user threads on a pool of M kernel threads, combining low creation cost with true parallelism, but requires a sophisticated runtime scheduler; Go is the best-known production example.
