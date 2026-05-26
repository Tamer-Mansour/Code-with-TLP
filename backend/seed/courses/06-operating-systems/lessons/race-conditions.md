# Race Conditions and the Critical Section Problem

A **race condition** occurs when two or more threads (or processes) access shared data concurrently and the final result depends on the precise interleaving order — the "race" — of their execution. Race conditions are among the most dangerous bugs because they are **non-deterministic**: they may appear to work correctly 99.9% of the time and fail catastrophically in production under load.

## Anatomy of a Race Condition

Consider two threads both incrementing a shared counter. At the machine level, `counter += 1` is three instructions:

```
LOAD   reg ← counter    (read from memory)
ADD    reg, 1            (increment in register)
STORE  counter ← reg    (write back to memory)
```

If two threads interleave on a single core (or run truly in parallel on two cores):

```
Time  Thread A (CPU 0)           Thread B (CPU 1)    counter
 1    LOAD  reg_A ← counter      —                   = 5
 2    —                           LOAD  reg_B ← counter   = 5
 3    ADD   reg_A = 6             —
 4    —                           ADD   reg_B = 6
 5    STORE counter ← 6           —                   → 6
 6    —                           STORE counter ← 6   → 6  ← BUG!
```

Expected result: 7. Actual result: 6. **One increment is silently lost.** With N threads each doing M increments, the final value could be anywhere between M and N×M.

## Reproducing the Bug in Python

```python
import threading

counter = 0

def increment(n):
    global counter
    for _ in range(n):
        counter += 1   # THREE MACHINE INSTRUCTIONS — NOT ATOMIC

threads = [threading.Thread(target=increment, args=(100_000,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()

print(counter)   # Expected: 400000, Actual: varies (e.g., 358,201)
```

Run this multiple times and you get a different wrong answer each time — the hallmark of a race condition.

## The Critical Section Problem

A **critical section** is any code segment that accesses shared mutable state. The problem: design a protocol so that only one thread enters its critical section at a time.

A correct solution must satisfy all three properties simultaneously:

| Property | Formal Meaning |
|----------|---------------|
| **Mutual exclusion** | At most one thread is in its critical section at any moment |
| **Progress** | If no thread is in the critical section and some thread wants to enter, eventually one enters (no infinite deferral among competing threads) |
| **Bounded waiting** | There exists a bound on the number of times other threads can enter the critical section before a waiting thread gets its turn (no starvation) |

These properties are necessary conditions. A solution that provides only mutual exclusion but not bounded waiting allows a thread to wait forever (starvation).

## A Broken "Solution" — The Flag Problem

```python
flag = [False, False]

def thread_0():
    flag[0] = True          # Signal intent
    while flag[1]:          # Wait if thread 1 wants in
        pass
    # critical section
    flag[0] = False

def thread_1():
    flag[1] = True
    while flag[0]:
        pass
    # critical section
    flag[1] = False
```

**Deadlock scenario:**
```
Thread 0: flag[0] = True
Thread 1: flag[1] = True    ← happens before thread 0 checks
Thread 0: while flag[1] → True → waits
Thread 1: while flag[0] → True → waits
→ Both wait forever: DEADLOCK
```

This breaks the **progress** property: no thread is in the critical section but neither can enter.

## Peterson's Algorithm (Correct for 2 Threads)

```python
flag = [False, False]
turn = 0

def enter_critical(i):
    j = 1 - i
    flag[i] = True      # "I want in"
    turn = j            # "But you go first" (polite gesture)
    while flag[j] and turn == j:
        pass            # Busy-wait: if the other wants in AND it's their turn, wait

def exit_critical(i):
    flag[i] = False     # "I'm done"
```

**Why it works:**
- **Mutual exclusion:** For both to be in the critical section, we'd need `flag[0]=True, flag[1]=True, turn=0, turn=1` simultaneously — impossible (turn is one value).
- **Progress:** If thread 1 doesn't want in (`flag[1]=False`), thread 0 enters immediately regardless of `turn`.
- **Bounded waiting:** If thread 1 is in the critical section and exits, it sets `flag[1]=False`, allowing thread 0 to enter.

**Caveat:** Peterson's algorithm assumes **sequential consistency** — memory operations complete in program order. Modern CPUs reorder loads and stores for performance. On x86, you'd need a `MFENCE` (memory fence) instruction after the `turn = j` write to prevent reordering with the `while` check. This is why OS-level primitives (mutexes) use hardware-guaranteed atomics.

## Hardware Atomic Instructions

Modern CPUs provide **atomic read-modify-write** instructions that cannot be interrupted between the read and the write:

### Test-and-Set (TAS)

```
TAS(addr):   # atomic
    old = *addr
    *addr = 1
    return old
```

Spinlock using TAS:
```python
lock = 0   # 0 = free, 1 = held

def acquire():
    while test_and_set(lock) == 1:
        pass   # spin until lock was 0

def release():
    lock = 0   # plain write suffices on x86 (has implicit store barrier)
```

### Compare-and-Swap (CAS)

More powerful than TAS — used for lock-free data structures:

```
CAS(addr, expected, new):  # atomic
    if *addr == expected:
        *addr = new
        return True
    return False
```

```python
# CAS-based increment (lock-free)
def safe_increment():
    while True:
        old = counter          # read
        new = old + 1          # compute
        if CAS(counter, old, new):   # only writes if nobody else changed it
            break              # success
        # else: retry (another thread changed counter between our read and CAS)
```

CAS is the foundation of lock-free data structures (Michael-Scott queue, lock-free hash tables) and is exposed in Python via `ctypes` or in C++ as `std::atomic<int>::compare_exchange_strong()`.

### Fetch-and-Add

```
FAA(addr, delta):  # atomic
    old = *addr
    *addr += delta
    return old
```

`counter.fetch_add(1)` in C++ atomics performs an atomic increment — no spinloop needed for simple counters.

## Memory Model and Reordering

Modern CPUs (x86, ARM, RISC-V) can execute instructions **out of order** and delay memory writes to optimize performance. Two threads on different cores may see memory updates in different orders:

```
Thread A (core 0):     Thread B (core 1):
  data = 42             while (!flag): pass
  flag = 1              assert data == 42   ← might FAIL on ARM/RISC-V!
```

On x86, stores are only reordered with earlier loads (store-load reordering). On ARM, all four types of reordering are possible. **Memory barriers** (`MFENCE`, `SFENCE`, `LFENCE` on x86; `DMB` on ARM; `fence` on RISC-V) prevent specific reorderings.

Mutex acquire/release operations include implicit memory barriers — that's part of why `pthread_mutex_lock()` is safe across cores.

## TOCTOU: Time-of-Check to Time-of-Use

A race condition that exists even **without** data races — a logical race between checking a condition and using the result:

```python
# TOCTOU bug in file access check
import os

def write_to_file(path, data):
    if os.access(path, os.W_OK):   # check: is it writable?
        # Attacker replaces the file with a symlink to /etc/shadow HERE
        with open(path, 'w') as f:
            f.write(data)          # use: now writing to /etc/shadow!
```

Fix: open the file atomically (e.g., `O_CREAT|O_EXCL`, or check permissions after opening with `fstat(fd)` rather than `stat(path)`).

## Data Races vs. Race Conditions

| Term | Meaning | Detectable By |
|------|---------|--------------|
| **Data race** | Two threads access same memory, ≥1 writes, no sync | ThreadSanitizer (TSan) |
| **Race condition** | Program result depends on scheduling order | Manual testing, fuzzing |

A data race always implies a race condition. A race condition can exist without a data race (TOCTOU). TSan (Clang/GCC thread sanitizer) detects data races at ~5–20× runtime overhead, invaluable for catching threading bugs in test environments.

## Key Takeaways

- A **race condition** occurs when concurrent threads share mutable state without coordination — results are non-deterministic.
- The **critical section** must be protected; correct solutions provide mutual exclusion, progress, and bounded waiting.
- **Peterson's algorithm** is correct for 2 threads but requires memory fence instructions on modern CPUs.
- Hardware atomic instructions (TAS, CAS, FAA) are the basis of all OS synchronization primitives.
- **Memory ordering** matters: CPU reordering can cause races even when source code looks sequential.
- **TOCTOU** bugs are logical races that exist even without data races — check with open files, not path names.
- Tools like **ThreadSanitizer (TSan)** detect data races dynamically; use them in your CI pipeline.
