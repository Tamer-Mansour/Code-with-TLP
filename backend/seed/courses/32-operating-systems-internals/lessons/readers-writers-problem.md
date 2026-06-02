# The Readers-Writers Problem

The readers-writers problem models access to a shared data store — a database table, an in-memory cache, a configuration object — where reads are safe to run concurrently but writes require exclusive access. Getting this right is critical for any high-read, low-write workload.

## Two Key Observations

1. **Multiple readers can coexist safely.** Reading does not modify state, so no two readers interfere with each other.
2. **A writer needs exclusive access.** While a writer is active, no other writer or reader may proceed.

These two observations define the access policy:

| State | New reader allowed? | New writer allowed? |
|-------|--------------------|--------------------|
| Idle  | Yes                | Yes                |
| Reading (N readers active) | Yes | No |
| Writing (1 writer active) | No | No |

## Roles and Shared State

```c
int   reader_count = 0;        // number of active readers
sem_t mutex        = 1;        // protects reader_count
sem_t write_lock   = 1;        // exclusive access for writers
```

- `mutex` is a small lock just for updating `reader_count` atomically.
- `write_lock` is the gate: held by a writer during the entire write, or by the **first** reader entering (and released by the **last** reader leaving).

## The First Readers-Writers Solution (Readers Preferred)

```c
// READER
void reader() {
    sem_wait(&mutex);
    reader_count++;
    if (reader_count == 1)
        sem_wait(&write_lock);   // first reader locks out writers
    sem_post(&mutex);

    /* --- read the shared data --- */

    sem_wait(&mutex);
    reader_count--;
    if (reader_count == 0)
        sem_post(&write_lock);   // last reader unlocks for writers
    sem_post(&mutex);
}

// WRITER
void writer() {
    sem_wait(&write_lock);       // exclusive access

    /* --- write the shared data --- */

    sem_post(&write_lock);
}
```

### How It Works

- The first reader acquires `write_lock`, blocking any writers.
- Subsequent readers increment `reader_count` but do not re-acquire `write_lock`.
- The last reader to finish releases `write_lock`, allowing a waiting writer to proceed.
- Writers simply compete for `write_lock` directly.

## Worked Example

```
Initial: reader_count=0, mutex=1, write_lock=1

T=0: Reader-1 enters → reader_count=1, acquires write_lock
T=1: Reader-2 enters → reader_count=2, write_lock already held (no-op)
T=2: Writer-1 tries → blocks on write_lock  ← writer is WAITING
T=3: Reader-3 enters → reader_count=3
T=4: Reader-1 exits  → reader_count=2
T=5: Reader-2 exits  → reader_count=1
T=6: Reader-3 exits  → reader_count=0, releases write_lock
T=7: Writer-1 unblocks, writes
```

As long as new readers keep arriving (T=3), Writer-1 cannot proceed. This is **writer starvation**.

## Why Reader Preference Causes Starvation

The readers-preferred solution never turns away a new reader while other readers are active. In a busy system, the stream of readers may be continuous — a writer queued at T=2 might wait indefinitely. This is the central flaw addressed in the next lesson.

## Three Standard Variants

| Variant | Policy | Risk |
|---------|--------|------|
| Readers preferred | No reader waits if a reader holds the lock | Writer starvation |
| Writers preferred | No new reader starts if a writer is waiting | Reader starvation |
| Fair (no starvation) | Arrivals are served in order | More complex implementation |

## Real-World Applications

- **Database read replicas**: multiple queries run in parallel; schema changes (DDL writes) require exclusive locks.
- **Linux `rwlock_t` / C++ `shared_mutex`**: the kernel and standard library both implement readers-writers semantics.
- **DNS resolver cache**: millions of lookups happen concurrently; cache updates are rare and must be exclusive.

## Common Pitfalls

- **Forgetting `mutex` around `reader_count`**: two readers incrementing simultaneously can both see `reader_count == 1` and both try to acquire `write_lock`.
- **Holding `mutex` during the read**: this serializes all readers, defeating the purpose.
- **Omitting the first/last-reader check**: every reader acquiring `write_lock` individually would serialize all reads just like a regular mutex.

## Interview Answer

**Q: Describe the readers-writers problem.**

> Multiple threads share a resource; readers may access it concurrently but writers need exclusive access. The classic semaphore solution uses a counter for active readers so the first reader locks out writers and the last reader releases them — but this can starve writers if readers arrive continuously.
