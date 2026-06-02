# Threads vs Processes: Shared State and Cost

Modern programs routinely do many things at once — downloading data while rendering UI, handling multiple network connections, or parallelizing computation across CPU cores. The two primary OS abstractions for concurrency are **processes** and **threads**.

## What Is a Process?

A process is an independent program instance with its own virtual address space, file descriptor table, and OS-managed resources. The OS scheduler treats each process as an isolated unit. Creating a process is expensive: the kernel must allocate a new page table, copy (or copy-on-write) the parent's memory mappings, and set up a new execution context.

```bash
# On Linux, fork() creates a child process
# strace shows the heavy syscall cost
strace -e trace=clone,execve ./my_program
```

Inter-process communication (IPC) requires explicit mechanisms — pipes, sockets, shared memory, or message queues — because each process sees only its own address space.

## What Is a Thread?

A thread is a unit of execution that lives **inside** a process. All threads in a process share:

- The heap and global variables
- Open file descriptors
- Signal handlers and signal masks
- The code (text) segment

Each thread has its **own**:

- Stack (typically 1–8 MB by default)
- Program counter (instruction pointer)
- Register set
- Thread-local storage (TLS)

Creating a thread is far cheaper than forking a process because no new address space is needed. On Linux, `clone()` with shared flags underlies both `fork()` and `pthread_create()`.

```cpp
#include <pthread.h>
#include <stdio.h>

void* hello(void* arg) {
    printf("Thread sees global data\n");
    return nullptr;
}

int main() {
    pthread_t t;
    pthread_create(&t, nullptr, hello, nullptr);
    pthread_join(t, nullptr);
}
```

## Cost Comparison

| Operation | Approx. cost (Linux x86-64) |
|---|---|
| `fork()` (copy-on-write) | ~100 µs |
| `pthread_create()` | ~10 µs |
| Context switch (process) | ~5–10 µs |
| Context switch (thread, same process) | ~1–3 µs |

These numbers vary by workload and hardware, but the trend is clear: threads are lighter.

## Shared State: Power and Peril

The shared address space is threads' greatest advantage and their most dangerous characteristic. Two threads can communicate through a simple global variable — no IPC needed. But this also means both threads can **read and write the same memory simultaneously**, which leads to race conditions when no synchronization is used.

```cpp
int counter = 0;  // shared by all threads — dangerous without a lock!

void increment() {
    counter++;  // NOT atomic: read → modify → write
}
```

## When to Use Processes vs Threads

| Scenario | Prefer |
|---|---|
| Fault isolation (one crash should not kill all) | Processes |
| High parallelism, shared data structures | Threads |
| Security sandbox (browser tab, plugin) | Processes |
| Low latency communication between tasks | Threads |
| Different programming languages in one app | Processes (via IPC) |

## The C++ Memory Model

C++11 introduced a formal memory model that defines how threads observe each other's writes. Without explicit synchronization (`std::mutex`, `std::atomic`, etc.), concurrent accesses to the same variable are **undefined behavior** — the compiler and CPU can reorder operations freely.

> **Interview answer:** A thread is a lightweight execution unit that shares the heap and globals with other threads in the same process. Threads are cheaper to create and switch between than processes, but shared state requires synchronization to avoid data races.
