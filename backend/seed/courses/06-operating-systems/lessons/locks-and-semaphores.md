# Locks, Semaphores, and Monitors

Busy-waiting (spinlocks) works for very short critical sections on multiprocessors, but most synchronization problems need primitives that **sleep** the waiting thread instead of burning CPU cycles. The OS provides three foundational abstractions: **mutexes**, **semaphores**, and **monitors**. Each has different semantics, overhead, and ideal use cases.

## Mutex (Mutual Exclusion Lock)

A **mutex** is a binary lock — either locked (owned by exactly one thread) or unlocked. Only the thread that acquired the mutex may release it (ownership semantics).

```python
import threading

balance = 1000
lock = threading.Lock()

def transfer(amount):
    global balance
    with lock:           # acquire on enter, release on exit (even on exception)
        balance -= amount
        # Critical section: only one thread here at a time
```

The `with lock` context manager ensures the mutex is released even if an exception is thrown — a common source of deadlocks avoided. Without it, a programmer must call `lock.release()` in every exit path.

### What Happens Inside mutex_lock()

```
Thread B calls lock.acquire() while Thread A holds it:

1. lock.acquire():
   - Try atomic CAS: compare lock_word to 0, set to 1
   - CAS fails (lock_word is already 1)
   - Thread B marks itself WAITING
   - Thread B adds itself to the lock's wait queue
   - Thread B calls schedule() → CPU given to another thread

2. Thread A calls lock.release():
   - Sets lock_word = 0
   - If wait queue is non-empty: wake the first waiter
   - Woken thread (B) retries CAS: succeeds this time
   - Thread B is now RUNNING, holding the lock
```

### Mutex vs. Spinlock

| | Mutex | Spinlock |
|-|-------|----------|
| Waiting thread | Sleeps (yields CPU) | Burns CPU cycles in a tight loop |
| Overhead | Syscall to sleep/wake (~1 µs) | No syscall, but wastes cycles |
| Best for | Lock held > ~1 µs | Lock held for a few dozen nanoseconds |
| Applicable on | Uniprocessor and multicore | Multicore only (pointless on 1 core) |
| Risk | Priority inversion | Livelock if poorly designed |

Linux kernel spinlocks: `spin_lock(&my_lock)` / `spin_unlock(&my_lock)` — used for short critical sections that run with interrupts disabled, where sleeping is impossible.

## Semaphore

A **semaphore** is an integer counter `S` with two atomic operations:

```
wait(S)  [also called P, down, acquire]:
    while S == 0:
        add current thread to S's wait queue
        sleep
    S -= 1      # atomic decrement

signal(S)  [also called V, up, release]:
    S += 1
    if any threads sleeping on S:
        wake one of them
```

- A **binary semaphore** (initialized to 1, max value 1) acts like a mutex — but without ownership. Any thread can call `signal()`.
- A **counting semaphore** (initialized to N) limits concurrent access to N threads simultaneously.

### Counting Semaphore: Connection Pool

```python
import threading

pool_sem = threading.Semaphore(10)   # Allow at most 10 concurrent DB connections

def query_db(query):
    pool_sem.acquire()   # blocks if 10 connections already in use
    try:
        conn = get_connection()
        return conn.execute(query)
    finally:
        pool_sem.release()   # always return the slot
```

### Producer-Consumer with Semaphores

The classic synchronization problem: producers put items in a bounded buffer; consumers take them out.

```python
import threading, collections

CAPACITY = 5
buffer   = collections.deque()
empty    = threading.Semaphore(CAPACITY)  # tracks free slots (starts at CAPACITY)
full     = threading.Semaphore(0)         # tracks filled slots (starts at 0)
mutex    = threading.Lock()               # mutual exclusion for buffer access

def producer(item):
    empty.acquire()           # wait for a free slot (blocks if buffer full)
    with mutex:
        buffer.append(item)   # critical section: add item
    full.release()            # signal: one more item available

def consumer():
    full.acquire()            # wait for an item (blocks if buffer empty)
    with mutex:
        item = buffer.popleft()  # critical section: take item
    empty.release()           # signal: one more slot freed
    return item
```

**Why three synchronization objects?** `empty` and `full` handle the "buffer full" and "buffer empty" conditions respectively. `mutex` protects the buffer from concurrent modification. If you used only `mutex`, consumers trying to get from an empty buffer would have to spin or use `wait/notify` — that's a monitor.

## Monitor

A **monitor** bundles shared data, a mutex, and **condition variables** into a single, structured object. Introduced by C.A.R. Hoare (1974), popularized by Java's `synchronized` keyword and Python's `threading.Condition`.

```python
import threading

class BoundedBuffer:
    def __init__(self, capacity):
        self._buf  = []
        self._cap  = capacity
        self._lock = threading.Lock()
        self._not_full  = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item):
        with self._not_full:           # acquires self._lock
            while len(self._buf) == self._cap:
                self._not_full.wait()  # releases lock; sleeps until notified
            self._buf.append(item)
            self._not_empty.notify()   # wake a waiting consumer

    def get(self):
        with self._not_empty:
            while not self._buf:
                self._not_empty.wait()
            item = self._buf.pop(0)
            self._not_full.notify()    # wake a waiting producer
            return item
```

**`wait()` is atomic:** it simultaneously releases the lock AND suspends the thread. This is essential — if they were separate operations, a `notify()` could arrive between the unlock and the sleep, causing the notification to be lost and the consumer to sleep forever.

**Why `while` not `if` before `wait()`?** Because of **spurious wakeups** (the thread can be woken for reasons other than `notify()`) and because multiple consumers may wake up but only one gets the item. The condition must be re-checked after waking.

### Dining Philosophers — The Classic Deadlock Trap

Five philosophers sit at a round table with five forks (one between each pair). To eat, a philosopher needs both left and right forks.

**Deadlock scenario:**
```
All philosophers simultaneously pick up their LEFT fork:
  P0 holds fork0, wants fork1
  P1 holds fork1, wants fork2
  P2 holds fork2, wants fork3
  P3 holds fork3, wants fork4
  P4 holds fork4, wants fork0
→ Circular wait: deadlock!
```

**Solution 1 — Asymmetric ordering:** One philosopher picks up RIGHT fork first. This breaks circular wait.

```python
def philosopher(i, forks, n=5):
    left, right = i, (i + 1) % n
    if i == n - 1:
        left, right = right, left   # last philosopher reverses order
    with forks[left]:
        with forks[right]:
            eat()
```

**Solution 2 — Resource hierarchy:** Number forks 0–4. Always acquire lower-numbered fork first.

**Solution 3 — Waiter semaphore:** A semaphore with value 4 ensures at most 4 philosophers try simultaneously, guaranteeing at least one can complete.

## Read-Write Locks

When data is read far more often than written, a **read-write lock** maximizes concurrency:

```
State       | New Reader Request | New Writer Request
────────────────────────────────────────────────────
Unlocked    | Grant (read lock)  | Grant (write lock)
Read locked | Grant              | Block until all readers done
Write locked| Block              | Block
```

```python
# Python 3.x — use threading.Lock + a counter to implement RW semantics
import threading

class RWLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._readers = 0
        self._write_lock = threading.Lock()

    def acquire_read(self):
        with self._lock:
            self._readers += 1
            if self._readers == 1:
                self._write_lock.acquire()   # first reader blocks writers

    def release_read(self):
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_lock.release()   # last reader allows writers

    def acquire_write(self):
        self._write_lock.acquire()

    def release_write(self):
        self._write_lock.release()
```

**Writer starvation risk:** if readers arrive continuously, the writer waits forever. A fair RW lock queues arriving readers behind waiting writers.

## Priority Inversion

A dangerous interaction between mutexes and priority scheduling:

```
Priority: High(H) > Medium(M) > Low(L)
1. L acquires mutex M
2. H becomes ready, preempts L
3. H tries to acquire M → blocks (L holds it)
4. M (medium priority) becomes ready, preempts L (now running to release M)
5. H is stuck waiting for M which is stuck waiting for L which can't run!
```

**Solution — Priority Inheritance:** when H blocks on a mutex held by L, the OS temporarily raises L's priority to H's level so L can finish quickly and release the mutex.

This exact bug caused the Mars Pathfinder mission's computer to reset in 1997 (discovered and fixed remotely via uplink).

## Comparison Summary

| Primitive | Use Case | Complexity | Key Property |
|-----------|----------|-----------|--------------|
| Spinlock | Kernel, microsecond holds | Low | No syscall overhead |
| Mutex | General mutual exclusion | Low | Owner semantics; sleeps |
| Semaphore | Counting / signaling | Medium | No ownership; any thread signals |
| Monitor + Condition | Producer-consumer, bounded buffer | High | Structured; atomic wait+unlock |
| Read-Write Lock | Frequent reads, rare writes | Medium | Concurrent reads |

## Key Takeaways

- **Mutexes** provide mutual exclusion with owner semantics; blocked threads sleep rather than spin.
- **Semaphores** are integer counters — use counting semaphores to limit concurrent access to N resources.
- **Monitors** encapsulate shared data with a mutex and condition variables; `wait()` atomically releases the lock and sleeps.
- Always use `while` (not `if`) around `wait()` — spurious wakeups and multiple waiters require re-checking the condition.
- The **Dining Philosophers** illustrates how subtle circular wait deadlocks are; break it with resource ordering or a limiting semaphore.
- **Priority inversion** (Mars Pathfinder, 1997) shows that mutex + priority scheduling can interact dangerously — use priority inheritance.
