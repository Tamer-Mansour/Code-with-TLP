# Synchronization Inside the Kernel

Kernel synchronization is harder than user-space synchronization for several reasons: interrupt handlers cannot sleep, NMIs can fire at any time, and the cost of getting it wrong is a kernel panic or silent data corruption. The kernel provides a hierarchy of synchronization primitives matched to different contexts.

## The Problem: Multiple Contexts of Execution

Kernel code runs in several distinct contexts:

| Context | Can sleep? | Can be preempted? | Preempted by |
|---------|-----------|-------------------|--------------|
| Process context (syscall) | Yes | Yes (if `CONFIG_PREEMPT`) | Scheduler, IRQ |
| Softirq / tasklet | No | No (by softirq) | Hardware IRQ |
| Hardware IRQ handler | No | No | NMI only |
| NMI handler | No | No | Nothing |

Choosing the wrong primitive for a context can deadlock the system.

## Spinlocks

A **spinlock** is a busy-wait lock: the waiting CPU loops until the lock is free. This is appropriate when:
- The lock will be held for a very short time (a few instructions).
- Sleeping is impossible (interrupt context).

```c
spinlock_t my_lock = SPIN_LOCK_UNLOCKED;

// Process or interrupt context
spin_lock(&my_lock);
/* critical section — no sleep allowed here */
spin_unlock(&my_lock);

// Protecting data shared with interrupt handlers
spin_lock_irqsave(&my_lock, flags);   // also disables local IRQs
/* critical section */
spin_unlock_irqrestore(&my_lock, flags);
```

**Pitfall:** Never call any function that might sleep while holding a spinlock (e.g., `kmalloc(GFP_KERNEL)`, `copy_from_user()`).

## Mutexes

Kernel **mutexes** (sleeping locks) are used in process context when the lock might be held for longer periods or when the protected operation itself might sleep:

```c
struct mutex my_mutex;
mutex_init(&my_mutex);

mutex_lock(&my_mutex);    // sleeps if lock is unavailable
/* critical section — sleeping is OK */
mutex_unlock(&my_mutex);
```

Mutexes are simpler to reason about and more efficient under high contention, but cannot be used in interrupt context.

## Read-Write Locks and RCU

When data is read far more often than it is written, reader-writer locks and **Read-Copy-Update (RCU)** provide better scalability.

**RCU** is Linux's most sophisticated synchronization mechanism:

- Readers hold no locks and incur almost zero overhead (`rcu_read_lock()` is just a preemption disable).
- Writers make a copy of the data, modify it, then atomically publish the new pointer.
- Old versions are freed only after all ongoing readers finish ("grace period").

```c
// Reader (wait-free, no lock)
rcu_read_lock();
struct mydata *d = rcu_dereference(global_ptr);
/* use d */
rcu_read_unlock();

// Writer
struct mydata *new = kmalloc(...);
*new = *old_ptr;   /* copy */
new->field = new_value;
rcu_assign_pointer(global_ptr, new);   /* atomic publish */
synchronize_rcu();  /* wait for all readers of old */
kfree(old_ptr);
```

RCU is used pervasively in Linux for things like routing tables, network interface lists, and module lists.

## Seqlocks

A **seqlock** (sequence lock) allows readers to proceed without blocking but detect if a writer was active during the read and retry:

```c
unsigned seq;
do {
    seq = read_seqbegin(&my_seqlock);
    /* read data */
} while (read_seqretry(&my_seqlock, seq));
```

Used in Linux for `gettimeofday()` — a common, performance-sensitive, read-heavy operation where occasional retries are acceptable.

## Atomic Operations

For simple counters and flags, the kernel provides atomic types that guarantee indivisibility without locking:

```c
atomic_t refcount = ATOMIC_INIT(1);

atomic_inc(&refcount);
if (atomic_dec_and_test(&refcount))
    free_object();
```

These compile to lock-prefix instructions on x86 (`LOCK XADD`, `LOCK CMPXCHG`).

## Choosing the Right Primitive

```
Need to protect from IRQ handler?
  Yes -> spin_lock_irqsave()
  No, but in IRQ context? -> spin_lock()
  No, in process context, short hold? -> spin_lock() or mutex
  No, in process context, can sleep? -> mutex
  Read-heavy, rare writes? -> RCU or seqlock
  Simple counter? -> atomic_t
```

> **Interview answer:** "Kernel synchronization requires matching the primitive to the execution context: spinlocks in interrupt context (cannot sleep), mutexes in process context (can sleep), and RCU for read-heavy data where readers need zero overhead and writers are rare."
