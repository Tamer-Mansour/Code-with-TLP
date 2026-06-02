# Process vs Thread: The Definitive Comparison

A process is the OS unit of resource ownership. A thread is the OS unit of execution. Every process has at least one thread, and all threads inside a process share that process's resources while running independently.

## The Core Distinction

| Property | Process | Thread |
|---|---|---|
| Address space | Private | Shared with siblings |
| Open file table | Private | Shared with siblings |
| Stack | One per process | One per thread |
| Registers / PC | N/A (no execution) | Private to each thread |
| Creation cost | High (fork + exec) | Low |
| Communication | IPC (pipes, sockets, SHM) | Direct memory read/write |
| Failure isolation | Strong — crash stays contained | Weak — one thread can kill all |

## Memory Layout: Process vs Thread

```
Process A                          Process A (multi-threaded)
┌──────────────────┐               ┌──────────────────┐
│   Stack          │               │  Thread 3 stack  │
├──────────────────┤               ├──────────────────┤
│   (grows down)   │               │  Thread 2 stack  │
│                  │               ├──────────────────┤
│   Heap           │               │  Thread 1 stack  │
├──────────────────┤               ├──────────────────┤
│   BSS / Data     │  ←— shared →  │  Heap (shared)   │
├──────────────────┤               ├──────────────────┤
│   Text (code)    │               │  BSS / Data      │
└──────────────────┘               ├──────────────────┤
                                   │  Text (shared)   │
                                   └──────────────────┘
```

All threads in a process read from the same text segment, the same global/static variables (BSS/data), and the same heap. Only the stack is per-thread.

## Creation Cost

```c
// Creating a new process — expensive
pid_t pid = fork();       // duplicates page tables (copy-on-write)
if (pid == 0) {
    execve("/bin/prog", args, env);  // replaces address space
}

// Creating a new thread — cheap
pthread_t tid;
pthread_create(&tid, NULL, my_func, arg);  // allocates a stack, sets up TCB
```

`fork()` must copy (or CoW-mark) the entire page table and duplicate all OS-level metadata. `pthread_create` only allocates a stack region (typically 8 MB reserved, a few pages committed) and a Thread Control Block.

## Communication Overhead

Threads can share data with a simple pointer dereference. Processes must serialize data across an IPC boundary:

```c
// Thread communication — zero-copy
shared_buffer[idx] = value;  // just a write

// Process communication — expensive
write(pipe_fd[1], &value, sizeof(value));  // syscall + copy
read(pipe_fd[0], &value, sizeof(value));
```

## When Processes Win

- **Fault isolation**: a browser tab crash should not kill the browser.
- **Security boundaries**: Chrome's renderer runs in a sandboxed process.
- **Different privilege levels**: a helper daemon runs as a different user.

## When Threads Win

- **Parallelism on shared data**: a web server handles many requests against the same in-memory cache.
- **Low latency creation**: a thread pool wakes a thread in microseconds; forking takes milliseconds.
- **Efficient communication**: video pipelines pass large frames between stages without copying.

## Common Pitfall

New candidates often say "threads are lighter than processes" and stop there. Be ready to follow up: threads provide no isolation — a buffer overflow in one thread corrupts the heap that all threads share, and an unhandled signal or `abort()` kills the entire process.

> **Interview answer:** A process is an isolated execution environment with its own address space. A thread is an execution context within a process that shares the address space, heap, and file descriptors with peer threads but has its own stack and registers. Threads are cheaper to create and communicate faster, but provide no fault isolation from each other.
