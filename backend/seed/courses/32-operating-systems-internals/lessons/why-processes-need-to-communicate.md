# Why Processes Need to Communicate: IPC Overview

Modern operating systems run dozens of isolated processes simultaneously. Each process has its own virtual address space, so one process cannot directly read or write another's memory. Yet complex applications — web servers, databases, shell pipelines, microservices — constantly need to share data, coordinate actions, and signal events across process boundaries. **Inter-Process Communication (IPC)** is the collection of OS mechanisms that make this possible while preserving isolation and security.

## Why Isolation Complicates Sharing

The OS gives each process a private address space on purpose: a buggy or malicious process should not be able to corrupt its neighbors. That isolation is a feature, not an accident. But isolation creates a problem — collaboration requires a controlled channel that the kernel mediates. Every IPC mechanism is essentially a kernel-managed rendezvous point.

## The Six Classic IPC Families

| Mechanism | Direction | Persistence | Best for |
|---|---|---|---|
| Pipes (anonymous) | Unidirectional | Lives with process | Shell pipelines, parent-child |
| Named pipes (FIFOs) | Unidirectional | File system entry | Unrelated processes |
| Message queues | Bidirectional | Kernel-managed | Structured, typed messages |
| Shared memory | Bidirectional | Explicit teardown | High-throughput data |
| Sockets | Bidirectional | Network or local | Network or local RPC |
| Signals | Unidirectional | Fire-and-forget | Async notifications |

## Key Design Dimensions

When choosing an IPC mechanism, engineers weigh several dimensions:

- **Throughput vs. latency** — Shared memory avoids copies but needs synchronization. Pipes add copy overhead but are simple.
- **Synchronization burden** — Message queues impose ordering. Shared memory requires explicit locks or semaphores.
- **Persistence** — Does the channel survive if the producer dies? Message queues and named pipes can; anonymous pipes cannot.
- **Locality** — Some mechanisms (sockets) work across machines; others (shared memory) are strictly local.
- **Blocking semantics** — Most IPC primitives block the caller when no data is available, allowing the OS to schedule other work instead of busy-waiting.

## A Worked Example: Shell Pipeline

When you type `ls | grep foo`, the shell:

1. Creates an anonymous pipe — a kernel buffer with a read end and a write end.
2. Forks `ls`, replacing its `stdout` with the pipe's write end.
3. Forks `grep`, replacing its `stdin` with the pipe's read end.
4. Both processes run concurrently; `grep` blocks when the pipe is empty and wakes when `ls` writes.

```bash
# What the shell does internally (simplified)
pipe(pipefd)           # create the pipe
fork() -> ls process   # ls writes to pipefd[1]
fork() -> grep process # grep reads from pipefd[0]
```

The pipe carries ~65 KB in kernel memory (the default pipe buffer). If `ls` fills the buffer before `grep` reads, `ls` blocks — a natural flow-control mechanism called **back-pressure**.

## Common Pitfalls

- **Choosing shared memory for simplicity** — it is the fastest mechanism but also the hardest to get right; forgotten synchronization leads to data races.
- **Forgetting to close unused pipe ends** — a process holding an open write end prevents readers from seeing EOF.
- **Assuming message ordering across machines** — local IPC preserves FIFO order; network sockets can reorder if UDP is used.

## Interview Answer

> "Processes need IPC because each has an isolated address space. The OS provides pipes, message queues, shared memory, sockets, and signals as kernel-mediated channels. The choice depends on throughput needs, how much synchronization complexity the team can handle, and whether the communication crosses machine boundaries."
