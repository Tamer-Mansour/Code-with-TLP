# Quiz: Inter-Process Communication

**Q1. Which IPC mechanism preserves message boundaries without any application-level framing?**

- [ ] Anonymous pipe
- [ ] Unix domain socket (SOCK_STREAM)
- [x] POSIX message queue
- [ ] Shared memory

POSIX message queues deliver each `mq_send` call as a discrete unit readable in a single `mq_receive`. Pipes and SOCK_STREAM sockets are byte streams that do not preserve message boundaries; shared memory has no inherent framing at all.

---

**Q2. A process writes 200 bytes to a pipe. What does `PIPE_BUF` guarantee about this write?**

- [ ] The write will complete instantly without blocking
- [ ] The 200 bytes will be split into two separate reads
- [x] The 200 bytes will not interleave with concurrent writers on the same pipe
- [ ] The write will fail with EINVAL if 200 > PIPE_BUF

`PIPE_BUF` (at least 512 bytes, usually 4096) guarantees **atomicity** — writes at or below this size will not interleave with other writers. The guarantee says nothing about blocking or read granularity.

---

**Q3. A server calls `bind()` on a Unix domain socket path but gets `EADDRINUSE` even though no server is running. What is the most likely cause and fix?**

- [ ] The socket type must be SOCK_DGRAM for Unix domain sockets
- [ ] The path must start with a `/tmp/` prefix
- [x] A stale socket file from a previous crash still exists; call `unlink()` before `bind()`
- [ ] The server must call `listen()` before `bind()`

Unix domain socket paths are regular filesystem entries. If the server crashes, the socket file remains. `unlink(path)` before `bind()` removes the stale file.

---

**Q4. Which statement about shared memory IPC is TRUE?**

- [ ] The kernel automatically serializes concurrent writes to the shared region
- [ ] Shared memory works transparently between processes on different machines
- [ ] Using `shm_open` with POSIX makes locking unnecessary
- [x] Without a process-shared mutex or semaphore, concurrent access causes data races

The kernel maps pages but does no synchronization. Any concurrent read-write or write-write without explicit locking is a data race. `PTHREAD_PROCESS_SHARED` is required to use a pthread mutex across processes.

---

**Q5. Why should signal handlers generally NOT call `printf()`?**

- [ ] `printf` is too slow for a signal handler
- [ ] Signal handlers cannot take arguments, so `printf` format strings fail
- [x] `printf` uses internal locks that may be held when the signal arrives, causing deadlock
- [ ] `printf` modifies the signal mask, which corrupts pending signals

`printf` is not async-signal-safe because it acquires a lock on `FILE *stdout`. If the signal interrupts a `printf` in the main thread, the lock is already held, and the handler's `printf` deadlocks.

---

**Q6. Which IPC mechanism is the ONLY option when two processes are on different physical machines?**

- [ ] Named pipe (FIFO)
- [ ] POSIX shared memory
- [ ] Unix domain socket
- [x] Network socket (AF_INET or AF_INET6)

Named pipes, POSIX shared memory, and Unix domain sockets are all local-only (same OS instance). Only network sockets using `AF_INET` or `AF_INET6` can cross machine boundaries.
