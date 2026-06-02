# Shared Memory IPC and Its Synchronization Cost

Shared memory is the **fastest IPC mechanism** available on any Unix-like system. It lets two or more processes map the same physical memory pages into their respective virtual address spaces, enabling direct reads and writes with **zero copy overhead** after setup. But speed comes with a cost: the kernel provides no automatic synchronization, so any concurrent access requires explicit locking by the application.

## How Shared Memory Works

The OS uses its virtual memory system to map the same physical page frames into multiple processes' page tables. After the mapping is established, a write by process A is instantly visible to process B — there is no system call, no copy, no kernel involvement in the data path.

```
Process A                    Process B
Virtual Addr 0x7f000000  -->  Physical Page 0x4A2000  <-- Virtual Addr 0x6f000000
```

Both virtual addresses point to the same RAM. A 64-byte write by A is readable by B as soon as the CPU cache is coherent — which on x86 is guaranteed by hardware.

## POSIX Shared Memory API

```c
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

// --- Writer process ---
int main_writer() {
    // Create shared memory object
    int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0644);
    ftruncate(fd, 4096);           // set size

    // Map into address space
    void *ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
                     MAP_SHARED, fd, 0);
    close(fd);                     // fd no longer needed after mmap

    strcpy((char *)ptr, "Hello from writer!");
    munmap(ptr, 4096);
    return 0;
}

// --- Reader process ---
int main_reader() {
    int fd = shm_open("/myshm", O_RDONLY, 0);
    void *ptr = mmap(NULL, 4096, PROT_READ, MAP_SHARED, fd, 0);
    close(fd);

    printf("Read: %s\n", (char *)ptr);

    munmap(ptr, 4096);
    shm_unlink("/myshm");          // remove the name
    return 0;
}
```

The shared memory object lives in `/dev/shm` (a tmpfs) on Linux. It persists until `shm_unlink` is called or the system reboots.

## The Synchronization Problem

Because both processes share raw memory with no kernel mediation, concurrent access without synchronization produces **data races** — undefined behavior where both processes see torn writes or stale cache lines.

The standard solution is a **POSIX semaphore or mutex placed inside the shared memory region itself**, initialized with the `PTHREAD_PROCESS_SHARED` attribute:

```c
#include <pthread.h>
#include <sys/mman.h>

typedef struct {
    pthread_mutex_t lock;
    int counter;
} SharedData;

// In the writer (initializer):
SharedData *sd = mmap(NULL, sizeof(SharedData),
                      PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);

pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
pthread_mutex_init(&sd->lock, &attr);

// In either process:
pthread_mutex_lock(&sd->lock);
sd->counter++;
pthread_mutex_unlock(&sd->lock);
```

Without `PTHREAD_PROCESS_SHARED`, a mutex only works between threads of the same process — a subtle bug that can take hours to diagnose.

## System V Shared Memory (Legacy)

```c
#include <sys/shm.h>
key_t key = ftok("/tmp/myapp", 1);
int shmid = shmget(key, 4096, IPC_CREAT | 0644);
void *ptr = shmat(shmid, NULL, 0);   // attach
// ... use ptr ...
shmdt(ptr);                           // detach
shmctl(shmid, IPC_RMID, NULL);        // destroy
```

System V shared memory is still found in PostgreSQL and older databases. POSIX `shm_open` is preferred for new code.

## Performance vs. Synchronization Trade-off

| Mechanism | Data copies | Synchronization required | Throughput |
|---|---|---|---|
| Pipes | 2 (user→kernel→user) | None (built-in serialization) | ~3 GB/s |
| Message queues | 2 | None | ~1–2 GB/s |
| Shared memory | 0 | Explicit (mutex / semaphore) | Memory bandwidth limited (~50+ GB/s) |

Shared memory shines for **large, bulk transfers** (video frames, sensor streams, database buffers). For small, frequent messages, the synchronization overhead of acquiring a lock can erase the copy savings.

## Common Pitfalls

- **Missing `PTHREAD_PROCESS_SHARED`** — mutex silently becomes thread-local only.
- **Forgetting `shm_unlink`** — the object persists across process restarts, causing stale data bugs.
- **ABA race on ring buffers** — a lock-free design requires careful use of `atomic_compare_exchange` or memory barriers.
- **ftruncate before mmap** — mapping a zero-length object causes a SIGBUS on first access.

## Interview Answer

> "Shared memory maps the same physical pages into multiple processes' address spaces, giving zero-copy data transfer at memory-bandwidth speeds. The trade-off is that the kernel provides no ordering or mutual exclusion — you must add a process-shared mutex or semaphore. It is the right choice for large, bulk transfers; for small, frequent messages, the locking overhead can make message queues faster in practice."
