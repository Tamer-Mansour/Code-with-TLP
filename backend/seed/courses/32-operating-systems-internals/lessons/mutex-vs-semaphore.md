# Mutex vs Semaphore: Ownership and Use Cases

Mutexes and semaphores both prevent race conditions, but they model different problems. Confusing them is a classic interview trap — and a real source of bugs in production systems.

## The Central Difference: Ownership

| Property | Mutex | Semaphore |
|---|---|---|
| Owner | Yes — the locking thread | No — any thread can signal |
| Purpose | Mutual exclusion | Mutual exclusion OR signaling |
| Counter | Binary (0/1 implicitly) | Integer (0 to N) |
| Priority inheritance | Usually supported | Usually not supported |
| Recursive locking | Supported (with recursive mutex) | Not applicable |

A mutex has an **owner**: the thread that acquires it is the only thread that may release it. A semaphore is ownerless: one thread can wait on it and a completely different thread can signal it.

## When to Use a Mutex

Use a mutex when you want to protect **shared mutable state** that only one thread should access at a time, and the same logical thread that entered the critical section must leave it.

```cpp
std::mutex mtx;
std::vector<int> shared_list;

void append(int val) {
    std::lock_guard<std::mutex> lk(mtx);
    shared_list.push_back(val);  // protected by the lock
}
```

The ownership rule matters for correctness: an OS with priority inheritance can temporarily boost the mutex owner's priority to avoid priority inversion. This only works because the owner is known.

## When to Use a Semaphore

Use a semaphore for two distinct scenarios:

**1. Signaling — one thread notifies another**

```c
sem_t event;
sem_init(&event, 0, 0);  // start at 0 so the consumer blocks immediately

// Thread A (producer/interrupt handler)
produce_data();
sem_post(&event);          // signal: data is ready

// Thread B (consumer)
sem_wait(&event);          // block until signaled
consume_data();
```

A mutex cannot express this pattern cleanly: you cannot lock a mutex you do not own, so the producer cannot "unlock" the consumer's wait.

**2. Resource pool throttling**

```c
sem_t db_connections;
sem_init(&db_connections, 0, 10);  // allow up to 10 concurrent connections

void handle_request() {
    sem_wait(&db_connections);   // block if all 10 are in use
    query_database();
    sem_post(&db_connections);   // release one slot
}
```

## Side-by-Side Comparison

```
Scenario: protect a linked list
  Correct choice: Mutex
  Why: one owner, reciprocal lock/unlock

Scenario: producer-consumer event notification
  Correct choice: Semaphore (binary, initial value 0)
  Why: producer signals; consumer waits — different threads

Scenario: limit concurrent access to 5 resources
  Correct choice: Counting semaphore (initial value 5)
  Why: tracks available count, not a single critical section
```

## Common Mistakes

- **Using a binary semaphore as a mutex:** Any thread can accidentally release it, breaking the critical section. If thread B crashes before posting, no ownership violation is detected; with a mutex, the OS can detect an unlocked abandoned mutex and wake waiters.
- **Using a mutex for signaling:** You must lock the mutex in the waiting thread first, which means the signaling thread cannot lock it — the pattern breaks down.
- **Recursive locking with a non-recursive mutex:** Deadlock on the same thread; use a recursive mutex or redesign.

## Priority Inversion — Why Ownership Matters

When a high-priority thread H waits on a mutex held by low-priority thread L, and medium-priority thread M preempts L, H is indirectly blocked by M — a priority inversion. Because the OS knows L owns the mutex, it can apply **priority inheritance**: temporarily boost L to H's priority so L finishes and releases the lock quickly. Semaphores have no owner, so this fix cannot be applied.

## Quick Decision Rule

```
Need mutual exclusion (same thread locks and unlocks)?  → Mutex
Need to signal between different threads?               → Semaphore (binary, value=0)
Need to throttle access to N resources?                 → Counting semaphore
```

> **Interview answer:** Use a mutex for mutual exclusion where the same thread must lock and unlock (supports priority inheritance, recursive locking). Use a semaphore for signaling between threads or throttling access to N resources — because it has no ownership, any thread can signal it.
