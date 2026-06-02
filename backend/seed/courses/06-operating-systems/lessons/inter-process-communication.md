# Inter-Process Communication (IPC)

Processes run in separate virtual address spaces — by design, one process cannot read another's memory. Yet real systems constantly need processes to cooperate: a web server spawns worker processes that share request queues; a shell pipes the output of `grep` into `sort`. The OS provides **Inter-Process Communication (IPC)** mechanisms for exactly this purpose.

## IPC Taxonomy

| Mechanism | Data Direction | Persistence | Kernel Involvement |
|-----------|---------------|-------------|-------------------|
| Pipe (unnamed) | Unidirectional | Until closed | Per read/write |
| Named pipe (FIFO) | Unidirectional | File-lifetime | Per read/write |
| Message queue | Bidirectional | Kernel-managed | Per message |
| Shared memory | Both | Explicit unmap | Setup only |
| Socket | Both | Connection lifetime | Per send/recv |
| Signal | One-way notification | None | Delivery only |

## Pipes

A **pipe** is a FIFO byte stream with a read end and a write end. The kernel maintains a small in-kernel buffer (typically 64 KB on Linux).

```python
import os, sys

# Create the pipe — returns two file descriptors
read_fd, write_fd = os.pipe()

pid = os.fork()
if pid == 0:
    # Child: close write end, read from pipe
    os.close(write_fd)
    data = os.read(read_fd, 1024)
    print(f"Child received: {data.decode()}")
    os.close(read_fd)
else:
    # Parent: close read end, write to pipe
    os.close(read_fd)
    os.write(write_fd, b"hello from parent")
    os.close(write_fd)   # EOF signal to child
    os.waitpid(pid, 0)
```

When the writer closes the write end, the reader gets **EOF** (0 bytes returned). If the reader closes first, the writer gets `SIGPIPE` (broken pipe). The shell idiom `ls | grep .py` is implemented exactly this way — the shell calls `pipe()`, `fork()` twice, and redirects stdout/stdin to the pipe file descriptors using `dup2()`.

## Shared Memory

Shared memory is the **fastest IPC mechanism** — data is not copied through the kernel; both processes map the same physical pages into their virtual address spaces and access them directly.

```
Process A                 Kernel               Process B
Virtual Space             Physical RAM         Virtual Space
┌──────────┐              ┌──────────┐         ┌──────────┐
│          │   mmap()     │          │  mmap()  │          │
│ 0x7f000  │ ─────────►  │ page 420 │ ◄─────── │ 0x7e000  │
│ (mapped) │              │ (shared) │          │ (mapped) │
└──────────┘              └──────────┘          └──────────┘
```

```python
import mmap, os

# POSIX shared memory via a file (simplified)
shm_fd = os.open("/tmp/shm_example", os.O_CREAT | os.O_RDWR, 0o600)
os.ftruncate(shm_fd, 4096)

# Map into this process's address space
mem = mmap.mmap(shm_fd, 4096)
mem.write(b"shared data\x00")   # write at current position

pid = os.fork()
if pid == 0:
    mem.seek(0)
    print(f"Child reads: {mem.read(11)}")   # "shared data"
    mem.close()
else:
    os.waitpid(pid, 0)
    mem.close()
os.close(shm_fd)
```

**Critical caveat:** shared memory requires explicit synchronization (a semaphore or mutex in shared memory) — two processes writing simultaneously without locking causes data corruption, just like threads with a shared variable.

## Message Queues

A **POSIX message queue** (or System V `msgget/msgsnd/msgrcv`) lets processes exchange discrete typed messages. Unlike pipes, messages preserve boundaries (it is not a raw byte stream), and the queue persists in the kernel until explicitly deleted.

```
Producer ──► mq_send(queue, msg, priority) ──► [kernel queue] ──► mq_receive() ──► Consumer
```

Message queues are well-suited for task dispatch systems where workers pull jobs from a shared queue without sharing any other state.

## Signals

A **signal** is a software interrupt that notifies a process of an event asynchronously. Common signals:

| Signal | Number | Default Action | Meaning |
|--------|--------|---------------|---------|
| `SIGINT` | 2 | Terminate | Ctrl+C from terminal |
| `SIGTERM` | 15 | Terminate | Polite termination request |
| `SIGKILL` | 9 | Terminate | Force-kill (uncatchable) |
| `SIGSEGV` | 11 | Core dump | Invalid memory access |
| `SIGPIPE` | 13 | Terminate | Write to broken pipe |
| `SIGCHLD` | 17 | Ignore | Child process changed state |

```python
import signal, time

def handler(signum, frame):
    print(f"Caught signal {signum}, cleaning up...")

signal.signal(signal.SIGTERM, handler)   # register handler
signal.signal(signal.SIGINT, handler)    # also handle Ctrl+C

print("Running — send SIGTERM to stop")
while True:
    time.sleep(1)
```

Signals are not reliable for data transfer (only a signal number, no payload). They are used for lifecycle management: a process manager sends `SIGTERM` to gracefully stop a service, then `SIGKILL` if it doesn't respond within a timeout.

## Sockets

Sockets generalize pipes to work across machines and across unrelated processes. A **Unix domain socket** provides the same semantics as a TCP socket but stays in-kernel (no network stack overhead) — used by PostgreSQL, Docker, and systemd for local IPC.

```python
import socket, os

SOCK_PATH = "/tmp/example.sock"

# Server side (simplified)
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCK_PATH)
server.listen(1)
conn, _ = server.accept()
conn.send(b"hello from server")
conn.close()
server.close()
os.unlink(SOCK_PATH)
```

## Choosing the Right IPC Mechanism

```
Need to transfer data?
  ├─ Yes
  │   ├─ Same machine, related processes (parent/child) → Pipe
  │   ├─ Same machine, unrelated processes, byte stream → Unix socket
  │   ├─ Same machine, unrelated, message-oriented → Message queue
  │   ├─ Same machine, maximum throughput → Shared memory + semaphore
  │   └─ Across machines → TCP/UDP socket
  └─ No (just notify) → Signal
```

## Key Takeaways

- **Pipes** are the simplest IPC: unidirectional, byte-stream, exist only while both ends are open.
- **Shared memory** is fastest (zero-copy) but requires explicit synchronization to avoid races.
- **Message queues** preserve message boundaries and support priorities; the kernel buffers messages between send and receive.
- **Signals** are asynchronous notifications only — not a data channel.
- **Sockets** are the most general mechanism, working both locally (Unix sockets) and across a network (TCP/UDP).
- Every IPC mechanism other than shared memory involves at least one kernel copy per transfer — this is a real cost at high throughput.
