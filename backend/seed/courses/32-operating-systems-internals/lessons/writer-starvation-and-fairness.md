# Writer Starvation and Fair Readers-Writers

The readers-preferred solution from the previous lesson is simple and efficient under read-heavy loads, but it can **starve writers indefinitely**. This lesson examines the starvation problem and presents two approaches to eliminate it.

## Recap: Why Writers Starve

In the readers-preferred solution, a new reader that arrives while other readers are active is allowed to join immediately — it never waits for `write_lock`. If readers arrive at a high enough rate, `reader_count` never drops to zero, so the `write_lock` is never released, and a waiting writer blocks forever.

Starvation is not a theoretical edge case: in any high-read system (web caches, DNS, in-memory databases), writes are rare but time-sensitive. A stale cache entry that cannot be evicted is a correctness bug.

## Approach 1: Writers-Preferred

Introduce a second counter and a second gate specifically to stop new readers when a writer is waiting.

```c
int   reader_count  = 0;
int   writer_count  = 0;
sem_t r_mutex       = 1;  // protects reader_count
sem_t w_mutex       = 1;  // protects writer_count
sem_t write_lock    = 1;  // exclusive write access
sem_t read_lock     = 1;  // blocks readers when writer waiting
sem_t no_readers    = 1;  // held while readers are active

// READER
void reader() {
    sem_wait(&read_lock);          // check if a writer is waiting
    sem_wait(&r_mutex);
    reader_count++;
    if (reader_count == 1)
        sem_wait(&no_readers);     // block writers
    sem_post(&r_mutex);
    sem_post(&read_lock);

    /* --- read --- */

    sem_wait(&r_mutex);
    reader_count--;
    if (reader_count == 0)
        sem_post(&no_readers);     // allow writers
    sem_post(&r_mutex);
}

// WRITER
void writer() {
    sem_wait(&w_mutex);
    writer_count++;
    if (writer_count == 1)
        sem_wait(&read_lock);      // first writer blocks new readers
    sem_post(&w_mutex);

    sem_wait(&no_readers);         // wait for active readers to finish

    /* --- write --- */

    sem_post(&no_readers);

    sem_wait(&w_mutex);
    writer_count--;
    if (writer_count == 0)
        sem_post(&read_lock);      // last writer allows readers again
    sem_post(&w_mutex);
}
```

**Effect**: when the first writer arrives, it closes `read_lock`. New readers block on `read_lock`. Existing readers finish; when the last exits, `no_readers` is signaled and the writer proceeds. Now readers can starve — the same mirror-image problem.

## Approach 2: Fair (No-Starvation) Using a Turnstile

A **turnstile** is a single semaphore that every thread — readers and writers alike — must pass through one at a time. This imposes FIFO ordering at the gate.

```c
sem_t turnstile  = 1;   // one thread passes at a time
sem_t write_lock = 1;   // exclusive write access
sem_t r_mutex    = 1;   // protects reader_count
int   reader_count = 0;

void reader() {
    sem_wait(&turnstile);   // queue fairly
    sem_post(&turnstile);   // immediately release for next reader/writer

    sem_wait(&r_mutex);
    reader_count++;
    if (reader_count == 1)
        sem_wait(&write_lock);
    sem_post(&r_mutex);

    /* --- read --- */

    sem_wait(&r_mutex);
    reader_count--;
    if (reader_count == 0)
        sem_post(&write_lock);
    sem_post(&r_mutex);
}

void writer() {
    sem_wait(&turnstile);   // blocks all new arrivals while writer waits
    sem_wait(&write_lock);
    sem_post(&turnstile);   // now releases the queue

    /* --- write --- */

    sem_post(&write_lock);
}
```

**Key insight**: when a writer arrives, it acquires the turnstile and holds it until it also holds `write_lock`. During that window, all new readers queue behind the writer inside the turnstile. Once active readers finish and the writer acquires `write_lock`, it releases the turnstile, letting the next batch of readers or writers proceed.

## Comparison

| Property | Readers-preferred | Writers-preferred | Fair turnstile |
|----------|------------------|-------------------|----------------|
| Writers can starve | Yes | No | No |
| Readers can starve | No | Yes | No |
| Readers run concurrently | Yes | Yes | Yes |
| Complexity | Low | Medium | Medium |

## C++ `shared_mutex` in Practice

The C++17 `std::shared_mutex` (and Linux's `pthread_rwlock_t`) implement readers-writers semantics with OS-level fairness guarantees:

```cpp
#include <shared_mutex>
std::shared_mutex rw;

void reader_thread() {
    std::shared_lock<std::shared_mutex> lock(rw);  // shared (read) lock
    // ... read shared data ...
}

void writer_thread() {
    std::unique_lock<std::shared_mutex> lock(rw);  // exclusive (write) lock
    // ... modify shared data ...
}
```

The standard does not mandate a specific fairness policy, but most implementations prevent indefinite starvation through OS-scheduler-level queuing.

## Common Pitfalls

- **Testing only under low load**: starvation only manifests when arrivals are frequent; correctness tests with a handful of threads rarely trigger it.
- **Assuming `rwlock` is always faster than a mutex**: if write contention is high, the reader-count bookkeeping overhead can make `rwlock` slower than a plain mutex.

## Interview Answer

**Q: How do you fix writer starvation in readers-writers?**

> Use a turnstile semaphore that every thread — reader or writer — must pass through. A waiting writer holds the turnstile, forcing new readers to queue behind it; once all current readers finish, the writer proceeds and then releases the turnstile, restoring fairness.
