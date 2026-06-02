# Shared vs Not-Shared Resources Across Threads

Knowing exactly which resources are shared across threads is not just exam trivia — it directly determines what needs synchronization and what is safe to use without locks.

## The Master Table

| Resource | Shared? | Notes |
|---|---|---|
| Text (code) segment | YES | All threads execute from the same binary |
| Heap | YES | `malloc`/`free` must be synchronized |
| Global and static variables | YES | Race conditions live here |
| Open file descriptors | YES | `read(fd)` on the same fd from two threads interleaves |
| Current working directory | YES | `chdir()` affects all threads |
| Signal handlers | YES | Handler table is process-wide |
| Memory-mapped regions | YES | `mmap` regions visible to all threads |
| Stack | NO | Each thread has its own stack |
| Stack-local variables | NO | Automatic storage duration is per-thread |
| Register set | NO | CPU registers save/restored per-thread at context switch |
| Program counter (PC/IP) | NO | Each thread has its own instruction pointer |
| Thread ID (TID) | NO | Unique per thread |
| errno | NO | `errno` is a thread-local variable on POSIX |
| Thread-local storage (TLS) | NO | Explicitly per-thread |
| Signal mask | NO | Each thread can block different signals |
| Pending signals | NO | Pending signal set is per-thread |
| Scheduling priority / policy | NO | Can differ per thread |

## Why the Heap Is Shared and Dangerous

```c
// Thread 1                          // Thread 2
int *p = malloc(sizeof(int));        // also calls malloc
*p = 42;                             // writes to its own allocation
free(p);                             // safe — no data race here

// BUT if both threads share the same pointer:
extern int *shared_ptr;
*shared_ptr = 42;                    *shared_ptr = 99;
// DATA RACE — undefined behavior
```

The memory allocator itself (`malloc`/`free`) is thread-safe in glibc (it uses internal locks), but the objects you allocate are only as safe as you make them.

## Why errno Is Not Shared

Before POSIX threading, `errno` was a global integer. When threads arrived, a per-thread errno was needed:

```c
// errno is actually a macro that expands to a thread-local access
// In glibc: #define errno (*__errno_location())
// __errno_location() returns a pointer into the current thread's TLS area

// Thread 1 calls read() → errno set to EINTR
// Thread 2 calls open() → errno set to ENOENT
// Thread 1 checks errno → still EINTR (its own copy)
```

This is invisible to the programmer but critical: it means errno checking is always safe, even in multi-threaded code.

## File Descriptors: Shared but Position Is Not Always Atomic

All threads share the open file table entry, including the file offset:

```c
// Two threads reading the same fd — interleaved, unpredictable
// Thread 1
read(fd, buf1, 512);    // advances file offset by 512

// Thread 2 (concurrent)
read(fd, buf2, 512);    // sees a different 512 bytes — which 512?

// Safe alternative: use pread/pwrite which take an explicit offset
pread(fd, buf1, 512, 0);    // reads from offset 0, does not update position
pread(fd, buf2, 512, 512);  // reads from offset 512 independently
```

## Signal Handlers: Shared, But Masks Are Not

The handler function registered with `sigaction` is shared. If thread 1 calls `signal(SIGINT, my_handler)`, all threads use `my_handler`. But which thread *receives* the signal is controlled per-thread by the signal mask:

```c
// Block SIGINT in all threads except a dedicated signal-handling thread
sigset_t set;
sigemptyset(&set);
sigaddset(&set, SIGINT);
pthread_sigmask(SIG_BLOCK, &set, NULL);  // per-thread mask
```

## The Stack Is Truly Private

Local variables and alloca'd memory live on the stack. Passing a pointer to a local variable to another thread is safe **only while the owning function is still running**. A common bug:

```c
void spawn_thread() {
    int local = 42;
    pthread_create(&tid, NULL, worker, &local);  // DANGER
    return;  // local is gone; thread still holds a dangling pointer
}
```

> **Interview answer:** Threads share the code, heap, globals, open file descriptors, signal handlers, and memory mappings of their process. Each thread has its own stack, registers, program counter, errno (via TLS), signal mask, and thread ID. The key practical consequence is that any shared mutable data — heap objects, globals, shared file positions — requires synchronization, while stack-local data and TLS are inherently thread-safe.
