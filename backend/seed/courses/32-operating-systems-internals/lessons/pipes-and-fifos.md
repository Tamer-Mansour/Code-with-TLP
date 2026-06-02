# Pipes and Named Pipes (FIFOs)

Pipes are the oldest and most ubiquitous IPC mechanism in Unix-like systems. They are unidirectional byte streams managed entirely by the kernel. Understanding them deeply is a rite of passage for systems engineers because their simplicity hides several sharp edges.

## Anonymous Pipes

An anonymous pipe is created with the `pipe()` system call, which returns two file descriptors: `fd[0]` for reading and `fd[1]` for writing. The kernel backs the pipe with an in-memory circular buffer (typically 64 KB on Linux).

```c
#include <unistd.h>
#include <stdio.h>

int main() {
    int fd[2];
    pipe(fd);                      // create pipe

    if (fork() == 0) {
        // child: writer
        close(fd[0]);              // close unused read end
        write(fd[1], "hello\n", 6);
        close(fd[1]);
    } else {
        // parent: reader
        close(fd[1]);              // close unused write end
        char buf[32];
        int n = read(fd[0], buf, sizeof(buf));
        write(STDOUT_FILENO, buf, n);
        close(fd[0]);
    }
    return 0;
}
```

**Critical rule:** Always close the end you do not use. A reader will block forever waiting for EOF if any process holds the write end open — even if no writer will ever write again.

## Pipe Semantics

- **Atomic writes up to PIPE_BUF** (at least 512 bytes, typically 4096) are guaranteed not to interleave with other writers.
- Writes larger than `PIPE_BUF` may interleave if multiple writers exist.
- Reading from an empty pipe **blocks** until data arrives or all write ends are closed (EOF).
- Writing to a pipe with no readers raises **SIGPIPE** (or returns `EPIPE` if SIGPIPE is ignored).

## Named Pipes (FIFOs)

Anonymous pipes require a shared ancestor (fork). Named pipes, created with `mkfifo()`, appear as special files in the filesystem and allow **unrelated processes** to communicate.

```bash
mkfifo /tmp/my-pipe

# Terminal 1 — writer
echo "data from producer" > /tmp/my-pipe

# Terminal 2 — reader (blocks until writer connects)
cat /tmp/my-pipe
```

```c
// Create programmatically
#include <sys/stat.h>
mkfifo("/tmp/my-pipe", 0644);

// Open like a regular file
int wfd = open("/tmp/my-pipe", O_WRONLY);  // blocks until reader opens
int rfd = open("/tmp/my-pipe", O_RDONLY);  // blocks until writer opens
```

Both `open()` calls block until **both ends** are connected by default. Pass `O_NONBLOCK` to avoid blocking on `open()`.

## Performance Characteristics

| Property | Value |
|---|---|
| Default buffer | 64 KB (Linux), configurable via `fcntl(F_SETPIPE_SZ)` |
| Copy overhead | 2 copies (user->kernel, kernel->user) |
| Throughput | ~3–6 GB/s on loopback (benchmark, varies) |
| Latency | Microseconds for small messages |

Because data passes through the kernel buffer, each write-read pair involves **two copies**. This is fine for most workloads but becomes the bottleneck for large, high-frequency data — that's when shared memory wins.

## Common Pitfalls

- **Not closing unused pipe ends** — causes hangs on EOF.
- **Blocking open on FIFOs** — `open()` with `O_RDONLY` blocks until a writer arrives; design accordingly.
- **Treating pipes as message boundaries** — pipes are byte streams, not message streams. A `write(fd, buf, 100)` may be received as two `read()` calls of 60 and 40 bytes.

## Worked Example: Two-Stage Pipeline

```c
// Build: ls | sort
int fd[2];
pipe(fd);

if (fork() == 0) {          // ls
    dup2(fd[1], STDOUT_FILENO);
    close(fd[0]); close(fd[1]);
    execlp("ls", "ls", NULL);
}
if (fork() == 0) {          // sort
    dup2(fd[0], STDIN_FILENO);
    close(fd[0]); close(fd[1]);
    execlp("sort", "sort", NULL);
}
close(fd[0]); close(fd[1]); // parent closes both
wait(NULL); wait(NULL);
```

## Interview Answer

> "An anonymous pipe is a kernel byte-stream buffer shared between related processes via inherited file descriptors. A FIFO extends this to unrelated processes through a filesystem name. Both are unidirectional; writes block when the buffer is full, reads block when it's empty. The key pitfall is forgetting to close unused ends, which prevents EOF."
