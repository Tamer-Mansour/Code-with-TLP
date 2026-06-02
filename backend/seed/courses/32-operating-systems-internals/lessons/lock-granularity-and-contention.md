# Lock Granularity, Contention, and Convoying

Getting a mutex correct is only half the challenge. Getting it **fast** requires understanding granularity, contention, and the convoy effect — three concepts that explain why concurrent code often scales poorly.

## Lock Granularity

**Granularity** describes how much data a single lock protects.

| Granularity | One lock protects | Trade-off |
|---|---|---|
| **Coarse** | The entire data structure | Simple, but low parallelism — one thread at a time |
| **Fine** | A small part (e.g., one row, one shard) | High parallelism, but complex and more lock overhead |

### Coarse-Grained Example

```cpp
// One mutex for the entire hash map
std::mutex map_mtx;
std::unordered_map<int, int> table;

void insert(int k, int v) {
    std::lock_guard<std::mutex> lk(map_mtx);
    table[k] = v;
}
```

Simple, but 16 threads serialise completely — no real parallelism.

### Fine-Grained Example

```cpp
// One mutex per bucket (shard)
constexpr int SHARDS = 16;
std::mutex shard_mtx[SHARDS];
std::unordered_map<int, int> shards[SHARDS];

void insert(int k, int v) {
    int s = k % SHARDS;
    std::lock_guard<std::mutex> lk(shard_mtx[s]);
    shards[s][k] = v;
}
```

Threads accessing different shards run in parallel. The downside is complexity: cross-shard operations (e.g., iterating all keys) must acquire multiple locks — risking deadlock if lock order is not enforced.

## Contention

**Contention** occurs when multiple threads compete for the same lock simultaneously. High contention means most lock acquisitions block, and throughput collapses.

```
Low contention:  thread acquires lock → no wait → proceeds immediately
High contention: thread acquires lock → waits in queue → kernel reschedules → runs
                 (adds microseconds per critical section entry)
```

### Measuring Contention

```bash
# Linux: perf can measure futex contention (mutex sleeps)
perf stat -e 'syscalls:sys_enter_futex' ./my_program
```

A large number of `futex` calls under load signals high mutex contention.

### Reducing Contention

1. **Reduce critical section size** — do as little work as possible while holding the lock.
2. **Increase granularity** — shard the data structure.
3. **Use read-write locks** — many readers can proceed concurrently; writers are exclusive.
4. **Use lock-free data structures** — eliminate locks entirely for the common path.
5. **Thread-local data** — if each thread has its own copy, no lock is needed.

## The Convoy Effect

A **convoy** forms when a slow thread holds a lock and many fast threads pile up behind it. Even after the slow thread releases the lock, those threads are already queued — they wake one by one in a convoy, each spending time in the kernel wake-up path, rather than all progressing concurrently.

```
Timeline:
  T0 acquires lock (slow I/O)
  T1, T2, T3, T4 all arrive → all block → kernel queues them
  T0 releases lock → T1 wakes → T1 runs (fast)
  T1 releases → T2 wakes → ...
  Even though T1-T4 are fast, they run serially due to queueing
```

The convoy is self-reinforcing: the constant context-switch overhead slows the system further, causing more arrivals to block.

### Breaking a Convoy

- **Avoid lock hold during I/O**: release the lock before a blocking system call.
- **Use try-lock and back-off**: if a thread cannot immediately acquire the lock, it does other work and retries later — prevents pile-up.
- **Use unfair locking with barging**: some mutex implementations let a new arriving thread "barge" past the wait queue if the lock is momentarily free (Linux futex does this by default, reducing convoy formation).

```cpp
// Avoid holding lock across I/O
void process(int fd) {
    // Step 1: read shared config WITHOUT holding mutex
    Config cfg;
    {
        std::lock_guard<std::mutex> lk(mtx);
        cfg = shared_config;   // quick copy
    }
    // Step 2: do slow I/O outside the critical section
    write(fd, cfg.data, cfg.len);
}
```

## Worked Example — Before and After

```cpp
// Before: coarse lock, I/O inside critical section
std::mutex big_lock;
void save(Record r) {
    std::lock_guard<std::mutex> lk(big_lock);
    serialize(r);         // slow: allocates memory
    write_to_disk(r);     // slow: blocks on disk
}

// After: fine lock, minimal critical section
void save(Record r) {
    auto bytes = serialize(r);   // outside lock
    {
        std::lock_guard<std::mutex> lk(disk_queue_mtx);
        disk_queue.push(bytes);  // fast: in-memory push only
    }
    // Background writer thread drains disk_queue
}
```

> **Interview answer:** Lock granularity controls how much data one lock protects — coarser is simpler but limits parallelism; finer increases parallelism but adds complexity. Contention occurs when threads compete for the same lock, and the convoy effect is the cascading slowdown that results when many threads queue behind a slow lock holder. Fix it by shortening critical sections and keeping blocking operations outside the lock.
