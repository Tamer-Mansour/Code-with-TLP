# mmap, Shared Memory, and File Mapping

`mmap` is one of the most powerful system calls in POSIX. It maps a file or anonymous memory region directly into a process's virtual address space, enabling zero-copy I/O, shared memory between processes, and efficient large-file access.

## What mmap Does

```c
void* mmap(void* addr, size_t length, int prot, int flags, int fd, off_t offset);
```

- Returns a pointer to a region of virtual memory.
- If `fd` is a file descriptor, the region is **backed by the file** — reading/writing the memory reads/writes the file.
- If `fd == -1` and `flags` includes `MAP_ANONYMOUS`, the region is backed by swap space (anonymous mapping).
- The OS sets up page table entries lazily; actual pages are faulted in on first access.

## File-Backed Mapping: Zero-Copy File I/O

```cpp
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdio>

int main() {
    int fd = open("data.bin", O_RDONLY);
    struct stat st;
    fstat(fd, &st);

    // Map the entire file into virtual memory
    char* data = static_cast<char*>(
        mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0));

    // Access file content as a normal array — no read() calls
    printf("First byte: %02X\n", (unsigned char)data[0]);

    munmap(data, st.st_size);
    close(fd);
    return 0;
}
```

**Why it is faster than `read()` for large files:**

- No kernel-to-user copy — the page cache and the user mapping share the same physical frames.
- `read()` copies data from the page cache into a user buffer: two copies. `mmap` is one mapping, zero copies.

> **Interview answer:** `mmap` maps file pages directly into the virtual address space, eliminating the kernel-to-user copy that `read()` requires, making it ideal for large random-access files.

## Anonymous Mapping: Heap Alternative

```cpp
// Allocate 1 MB of private, zeroed memory (like a custom malloc)
void* mem = mmap(nullptr, 1 << 20,
                 PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
// ... use mem ...
munmap(mem, 1 << 20);
```

`malloc` itself uses `mmap` for large allocations (typically > 128 KB on glibc) and `brk` for small ones.

## Shared Memory Between Processes

`MAP_SHARED` + a file descriptor lets two processes share physical pages:

```cpp
// Process A: write to shared region
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0666);
ftruncate(fd, 4096);
int* shared = static_cast<int*>(
    mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
*shared = 42;

// Process B: read from same named shared memory
int fd2 = shm_open("/myshm", O_RDONLY, 0666);
int* shared2 = static_cast<int*>(
    mmap(nullptr, 4096, PROT_READ, MAP_SHARED, fd2, 0));
printf("Value: %d\n", *shared2);  // prints 42
```

Both processes see the **same physical frames** via different virtual addresses. Writes are immediately visible to the other process (with appropriate memory ordering barriers).

## Protection Flags

| `prot` flag | Effect |
|---|---|
| `PROT_READ` | Pages can be read |
| `PROT_WRITE` | Pages can be written |
| `PROT_EXEC` | Pages can be executed (JIT compilers use this) |
| `PROT_NONE` | No access — useful for guard pages |

## Private vs. Shared Mappings

| `flags` | Write behavior |
|---|---|
| `MAP_PRIVATE` | Writes trigger copy-on-write; changes are **not** written back to the file |
| `MAP_SHARED` | Writes are written back to the underlying file or shared with other processes |

## `msync` and Durability

For `MAP_SHARED` file mappings, writes are cached in the page cache and may not hit disk immediately:

```cpp
msync(data, length, MS_SYNC);   // flush dirty pages to disk now
msync(data, length, MS_ASYNC);  // schedule flush, return immediately
```

Failing to `msync` before crash can lose data — important for databases and write-ahead logs.

## Common Use Cases

| Use Case | Mapping Type |
|---|---|
| Reading a large binary file randomly | `MAP_PRIVATE | PROT_READ` |
| Writing a log file with crash safety | `MAP_SHARED | PROT_WRITE` + `msync` |
| IPC between two processes | `shm_open` + `MAP_SHARED` |
| JIT-compiled code | `MAP_ANONYMOUS + PROT_EXEC` |
| Stack guard page | `PROT_NONE` anonymous mapping |

## Common Pitfalls

- **Not calling `munmap`**: the mapping persists for the process's lifetime; forgetting it is a resource leak.
- **Using `MAP_SHARED` without synchronization**: two processes writing the same offset race — use a semaphore or `futex`.
- **Accessing past `st_size`**: SIGBUS on Linux if the mapped region extends beyond the file.
- **Assuming `mmap` is always faster**: for small sequential reads, `read()` with a large buffer can win due to read-ahead; `mmap` shines for large random-access patterns.
