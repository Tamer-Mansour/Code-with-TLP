# Kernel Preemption and Reentrancy

One of the most subtle and consequential aspects of kernel design is deciding **when the kernel itself can be interrupted**. This affects latency, throughput, and the complexity of synchronization throughout the entire codebase.

## Non-Preemptible Kernels

Early UNIX kernels were **non-preemptible**: once a thread entered kernel mode (via a system call or interrupt), it ran to completion before the scheduler could switch to another thread. This greatly simplified synchronization — kernel code didn't need locks because no other kernel code could run concurrently on the same CPU.

**Drawback:** A long system call (e.g., reading from a slow device) would block all other threads from getting CPU time, causing jitter and poor real-time response.

## Preemptible Kernels

A **preemptible kernel** allows the scheduler to preempt a thread even while it is executing kernel code. Linux became fully preemptible with the `CONFIG_PREEMPT` option (introduced ~2.5 kernel series).

```
Thread A                      Thread B (higher priority, becomes runnable)
   |                               |
   | in kernel: copy_to_user()     |
   |                               | <- scheduler fires timer interrupt
   |   <- preempted!               |
                                   | runs immediately
```

**Why this matters for real-time systems:** With a preemptible kernel, a high-priority task can preempt a low-priority task even mid-syscall, reducing **worst-case scheduling latency** from "time to complete the longest system call" to "length of preemption-disabled critical sections."

## Preemption Points

Even in a preemptible kernel, preemption is disabled in certain critical sections:

- **Interrupt handlers** — cannot be preempted; they are already running at interrupt priority.
- **Spinlock-held sections** — `spin_lock()` calls `preempt_disable()` in Linux.
- **`rcu_read_lock()` sections** — RCU read sides are non-preemptible in classic RCU.

```c
// Linux kernel: explicit preemption control
spin_lock(&my_lock);        // disables preemption (on UP) + acquires lock
/* critical section */
spin_unlock(&my_lock);      // re-enables preemption

// or manually:
preempt_disable();
/* no preemption here */
preempt_enable();           // may trigger a reschedule if TIF_NEED_RESCHED is set
```

## Reentrancy

A function is **reentrant** if it can be safely called by multiple concurrent execution contexts (threads, interrupt handlers) simultaneously. In the kernel, reentrancy is non-negotiable because:

- Multiple CPUs in an SMP system can simultaneously execute the same kernel function.
- An interrupt handler can interrupt a thread that is partway through a system call.

**Requirements for a reentrant kernel function:**
- No use of unprotected global or static mutable state.
- Any shared state accessed only through appropriate locks.
- No assumptions about execution order between concurrent callers.

```c
// NOT reentrant — shared static buffer, no lock
char *bad_itoa(int n) {
    static char buf[20];   // shared!
    sprintf(buf, "%d", n);
    return buf;
}

// Reentrant — caller-supplied buffer
char *good_itoa(int n, char *buf, size_t len) {
    snprintf(buf, len, "%d", n);
    return buf;
}
```

## PREEMPT_RT: The Real-Time Linux Patch

The `PREEMPT_RT` patch (now being merged upstream) extends preemptibility further:

- Converts most spinlocks to **sleeping locks** (mutexes), allowing preemption even in formerly atomic sections.
- Makes interrupt handlers run in kernel threads that can be preempted.
- Achieves worst-case scheduling latencies in the **tens of microseconds** on modern hardware.

This is used in industrial automation, robotics, and audio production where determinism matters more than peak throughput.

## Key Trade-offs

| Kernel type | Worst-case latency | Sync complexity | Throughput |
|-------------|-------------------|-----------------|------------|
| Non-preemptible | Long (full syscall) | Low | Highest |
| Preemptible (`CONFIG_PREEMPT`) | Medium | Medium | High |
| Fully preemptible (`PREEMPT_RT`) | Very low | High | Slightly lower |

## Common Pitfall

A common bug: holding a spinlock and then calling code that sleeps. On a non-RT kernel this causes a panic ("BUG: scheduling while atomic"); on an RT kernel with sleeping spinlocks it can cause priority inversion.

> **Interview answer:** "A preemptible kernel allows the scheduler to interrupt a thread even inside a system call, reducing worst-case latency; reentrancy means kernel functions must be safe for concurrent invocation, requiring that no unprotected mutable global state is used."
