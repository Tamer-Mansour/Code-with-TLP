# Interview Drill: IPC Mechanisms

This lesson presents the IPC questions most commonly asked in systems-engineering interviews at companies like Google, Meta, Microsoft, and Jane Street. For each question, the answer a candidate should give is marked explicitly. Internalize the one-line crisp answer first, then add depth if the interviewer probes.

---

## Q1: What is the difference between a pipe and a message queue?

**Crisp answer:** A pipe is an unstructured byte stream with no message boundaries; a message queue preserves message boundaries and supports priority ordering.

**Depth:** Pipes are simpler and built into the shell ecosystem. Message queues add typing and priority, at the cost of a per-message kernel overhead and a configured max size. If message boundaries matter (e.g., you're sending discrete job records), a queue is safer than implementing your own framing on a pipe.

---

## Q2: Why is shared memory the fastest IPC mechanism?

**Crisp answer:** After the initial mapping, data passes directly between processes via shared physical memory pages — zero kernel involvement, zero copies.

**Depth:** Every other mechanism (pipe, socket, message queue) copies data into a kernel buffer and back. Shared memory skips both copies. The cost is that the application must synchronize access itself with mutexes, semaphores, or lock-free atomics. On NUMA systems, ensure the shared region is allocated on the same NUMA node as both processes to avoid cross-node latency.

---

## Q3: How do you safely receive a signal in a multithreaded program?

**Crisp answer:** Block the signal in all threads except a dedicated signal-handling thread that calls `sigwaitinfo()` or `signalfd()` synchronously.

**Depth:** Async signal delivery in a multithreaded program is hazardous — the signal may be delivered to any thread, and signal handlers share the async-signal-safe restriction. The standard pattern is:
1. `pthread_sigmask` to block the signals in all threads.
2. One dedicated thread calls `sigwaitinfo()` in a loop.
3. That thread then posts to a mutex-protected queue or condition variable.

---

## Q4: What is the self-pipe trick and why is it used?

**Crisp answer:** Write one byte into a pipe inside a signal handler (which is async-signal-safe) so that the `select`/`epoll` event loop wakes up when a signal arrives.

**Depth:** `select` and `epoll` cannot wait on signals directly. The self-pipe converts a signal into an I/O event. Linux `signalfd()` is the modern replacement but has slightly different semantics (must be combined with `sigprocmask`).

---

## Q5: A write to a pipe returns `EPIPE` instead of blocking. What happened?

**Crisp answer:** All read ends of the pipe were closed — there is no reader. The kernel sends `SIGPIPE` (or returns `EPIPE` if the signal is ignored) rather than blocking the writer forever.

**Depth:** This is why server processes should ignore or handle `SIGPIPE`. HTTP servers commonly set `SO_NOSIGPIPE` or ignore `SIGPIPE` so that a dropped client connection does not kill the server process.

---

## Q6: When would you choose Unix domain sockets over shared memory?

**Crisp answer:** When you need bidirectional communication, multiple clients, or protocol compatibility — UDS gives the full socket API at near-shared-memory speeds for small payloads.

**Depth:** UDS allows many clients to connect independently, each with their own connection state. Shared memory needs a separate coordination mechanism per client pair. UDS also supports `SOCK_SEQPACKET`, which adds message boundaries without TCP's complexity. For payloads under ~1 KB, UDS and shared memory latency are within a few microseconds of each other.

---

## Q7: What is a zombie process and what IPC mechanism is involved?

**Crisp answer:** A zombie is a process that has exited but whose exit status has not been collected by the parent; the kernel uses `SIGCHLD` to notify the parent and the parent must call `waitpid()`.

**Depth:** The kernel holds the exit status (a small struct) in the process table until the parent calls `wait`/`waitpid`. If the parent never does, the entry stays (zombie). A process with millions of short-lived children that never calls `waitpid` will exhaust the PID namespace. Setting `SIGCHLD` to `SIG_IGN` or using `SA_NOCLDWAIT` tells the kernel to auto-reap.

---

## Q8: What does `PIPE_BUF` guarantee?

**Crisp answer:** Writes up to `PIPE_BUF` bytes (at least 512, usually 4096) to a pipe are **atomic** — they will not interleave with concurrent writes from other processes.

**Depth:** This guarantee holds only when the write size does not exceed `PIPE_BUF`. Larger writes may be split and interleaved. Use fixed-size records at or below `PIPE_BUF` if you need atomicity without a higher-level protocol.

---

## Quick-Reference Table

| Question topic | One-line answer |
|---|---|
| Pipe vs. message queue | Byte stream vs. message boundaries + priority |
| Shared memory speed | Zero copies after mapping |
| Signal safety in threads | Block + dedicated `sigwaitinfo` thread |
| Self-pipe trick | Convert signal to I/O event for `select`/`epoll` |
| EPIPE cause | All read ends closed |
| UDS vs. shared memory | API + multi-client vs. raw speed |
| Zombie process | Unreaped child; collect with `waitpid` |
| PIPE_BUF | Atomic write guarantee up to that size |
