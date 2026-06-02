# Blocking vs Non-Blocking System Calls

When a system call cannot complete immediately, the kernel must decide what to do with the calling thread. This decision — block or return immediately — has profound implications for program architecture and throughput.

## What Makes a Syscall Block?

A system call blocks when the resource it needs is not ready:

- `read()` on a socket — no data has arrived yet.
- `read()` on a disk file — the page is not in cache (I/O miss).
- `accept()` on a server socket — no client has connected.
- `flock()` — another process holds the lock.
- `nanosleep()` — waiting for a timer to fire.

When the kernel decides to block, it:

1. Sets the thread's state to `TASK_INTERRUPTIBLE` (or `TASK_UNINTERRUPTIBLE`).
2. Places the thread on a wait queue associated with the resource.
3. Calls `schedule()` — the scheduler picks another thread to run.
4. When the resource becomes ready, an interrupt or wakeup call moves the thread back to `TASK_RUNNING`.

```
Thread calls read() on empty socket
  │
  ▼
Kernel: no data → task_state = TASK_INTERRUPTIBLE
  │               add to socket wait queue
  ▼
scheduler() → run other threads
  │
  ▼ (data arrives, NIC interrupt fires)
Socket wakeup → wake_up_interruptible(wait_queue)
  │
  ▼
Thread state = TASK_RUNNING → resumes in kernel
  │
  ▼
copy_to_user, return to user space
```

## Non-Blocking Mode: O_NONBLOCK

Setting `O_NONBLOCK` on a file descriptor changes the contract: instead of sleeping, the syscall returns immediately with `EAGAIN` (or `EWOULDBLOCK`) if it cannot make progress.

```c
int fd = socket(AF_INET, SOCK_STREAM, 0);

// Make socket non-blocking
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);

// Now read() returns immediately
ssize_t n = read(fd, buf, sizeof(buf));
if (n < 0 && errno == EAGAIN) {
    // No data yet — try later
}
```

Non-blocking I/O requires the application to poll or use an event notification mechanism (select, poll, epoll) rather than relying on the kernel to sleep.

## Blocking vs Non-Blocking Trade-offs

| Aspect | Blocking | Non-Blocking |
|---|---|---|
| Programming model | Simple, sequential | Event loop, callbacks |
| Thread per connection | Yes (one per client) | No (one thread, N clients) |
| CPU when idle | Zero (thread sleeps) | Depends on polling strategy |
| Latency | Possibly higher under load | Low (no sleep overhead) |
| Use case | CLI tools, simple scripts | High-concurrency servers |

## epoll: Efficient Non-Blocking Notification

The canonical Linux pattern for high-concurrency servers:

```c
int epfd = epoll_create1(0);

struct epoll_event ev = {
    .events  = EPOLLIN | EPOLLET,  // Edge-triggered
    .data.fd = client_fd,
};
epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);

// Event loop
struct epoll_event events[64];
while (1) {
    int n = epoll_wait(epfd, events, 64, -1);  // blocks here
    for (int i = 0; i < n; i++) {
        // events[i].data.fd is ready — read without blocking
        handle(events[i].data.fd);
    }
}
```

`epoll_wait` itself blocks (the event loop thread sleeps), but when it returns, all returned fds are guaranteed to have data — so `read()` on them will not block.

## TASK_INTERRUPTIBLE vs TASK_UNINTERRUPTIBLE

| State | Signal Wakes It? | Appears as |
|---|---|---|
| `TASK_INTERRUPTIBLE` | Yes (`EINTR` returned) | `S` in `ps` |
| `TASK_UNINTERRUPTIBLE` | No | `D` in `ps` |

Disk I/O often uses `TASK_UNINTERRUPTIBLE` to avoid partial I/O corruption. A process stuck in `D` state (often "D sleep") cannot be killed with `SIGKILL` — it must complete or the kernel must wake it.

## io_uring: Async Syscalls

Modern Linux (5.1+) provides `io_uring` — a shared ring buffer between user space and kernel that allows submitting batches of I/O operations without any syscall per operation, and collecting completions asynchronously.

```c
// Submit 1000 reads with a single syscall
io_uring_submit(&ring);
// Poll completion ring without syscalls
io_uring_peek_cqe(&ring, &cqe);
```

`io_uring` eliminates the blocking/non-blocking dichotomy for many workloads.

**Interview answer:** A blocking syscall puts the thread in `TASK_INTERRUPTIBLE` and calls `schedule()` until the resource is ready; a non-blocking fd (O_NONBLOCK) causes the syscall to return `EAGAIN` immediately instead, requiring the caller to use `epoll` or similar to know when to retry.
