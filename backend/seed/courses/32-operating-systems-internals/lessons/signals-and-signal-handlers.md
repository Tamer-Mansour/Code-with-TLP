# Signals and Signal Handlers

Signals are the Unix mechanism for **asynchronous event notification**. They are small integer codes delivered to a process by the kernel, by another process, or by the process itself. Unlike other IPC mechanisms, signals carry almost no data — just the signal number — making them suitable for simple notifications rather than data transfer.

## Common Signals

| Signal | Number | Default action | Typical use |
|---|---|---|---|
| `SIGINT` | 2 | Terminate | Ctrl+C from terminal |
| `SIGTERM` | 15 | Terminate | Graceful shutdown request |
| `SIGKILL` | 9 | Terminate (uncatchable) | Force kill |
| `SIGSEGV` | 11 | Core dump | Invalid memory access |
| `SIGCHLD` | 17 | Ignore | Child process state change |
| `SIGHUP` | 1 | Terminate | Terminal hang-up / reload config |
| `SIGPIPE` | 13 | Terminate | Write to broken pipe |
| `SIGUSR1/2` | 10/12 | Terminate | Application-defined |

## Installing a Signal Handler

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

volatile sig_atomic_t g_shutdown = 0;

void handle_sigterm(int sig) {
    g_shutdown = 1;   // safe: sig_atomic_t write is async-signal-safe
}

int main() {
    struct sigaction sa = {
        .sa_handler = handle_sigterm,
        .sa_flags   = SA_RESTART,   // restart interrupted syscalls
    };
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);

    printf("PID %d running. Send SIGTERM to stop.\n", getpid());
    while (!g_shutdown) {
        sleep(1);
    }
    printf("Shutting down gracefully.\n");
    return 0;
}
```

Use `sigaction()` rather than the older `signal()` — `signal()`'s behavior is implementation-defined and inconsistent across platforms.

## Async-Signal Safety

Signal handlers can execute **at any point** in the main program, interrupting any function. This means only a restricted set of functions are safe to call from a handler (the **async-signal-safe** list in POSIX). Notably unsafe in handlers:

- `printf`, `malloc`, `free` — use internal locks that may be held when the signal arrives, causing deadlock.
- Any function that modifies global state not protected by `sig_atomic_t`.

**Safe pattern:** set a flag in the handler, check it in the main loop.

```c
// WRONG: printf in handler can deadlock
void bad_handler(int sig) { printf("caught!\n"); }

// RIGHT: set a flag, print in main
volatile sig_atomic_t got_signal = 0;
void good_handler(int sig) { got_signal = 1; }
```

## Blocking and Masking Signals

Signals can be temporarily **blocked** (masked) to create a critical section:

```c
sigset_t block_set, old_set;
sigemptyset(&block_set);
sigaddset(&block_set, SIGTERM);

// Block SIGTERM around critical section
sigprocmask(SIG_BLOCK, &block_set, &old_set);
// ... critical work ...
sigprocmask(SIG_SETMASK, &old_set, NULL);  // restore
```

A blocked signal is **pending** — it will be delivered as soon as it is unblocked.

## Sending Signals

```c
#include <signal.h>

kill(pid, SIGTERM);   // send to specific process
kill(0, SIGTERM);     // send to every process in the same process group
raise(SIGUSR1);       // send to yourself
```

`kill()` requires the sender to have permission — you cannot send arbitrary signals to processes owned by other users (except via specific capabilities).

## The Self-Pipe Trick

`select()` and `epoll()` cannot wait on signals. The classic workaround is the **self-pipe trick**: write one byte to a pipe inside the signal handler (write is async-signal-safe), then include the pipe's read end in your `select`/`epoll` set.

```c
int signal_pipe[2];
pipe(signal_pipe);
// set O_NONBLOCK on both ends

void handler(int sig) {
    char byte = (char)sig;
    write(signal_pipe[1], &byte, 1);  // async-signal-safe
}

// In event loop: select on signal_pipe[0] along with other fds
```

Linux `signalfd()` is a cleaner alternative that exposes signals as a readable file descriptor directly.

## Common Pitfalls

- **Using `signal()` instead of `sigaction()`** — behavior varies; `signal()` may reset to default after first delivery on some systems.
- **Calling non-async-signal-safe functions in handlers** — causes intermittent deadlocks.
- **Ignoring `SIGCHLD`** — causes zombie processes unless the parent calls `waitpid()`.
- **Assuming signal delivery order** — multiple pending signals of the same number collapse into one.

## Interview Answer

> "Signals are asynchronous notifications delivered to a process by the kernel or another process. They carry only a signal number, not data. Handlers must use only async-signal-safe functions; the canonical pattern is to set a `volatile sig_atomic_t` flag and act on it in the main loop. `sigaction()` is preferred over `signal()` for portable, predictable behavior."
