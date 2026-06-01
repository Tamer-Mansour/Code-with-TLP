# Processes - ps, kill, signals

A process is a running program. The kernel gives each one a numeric **PID** and tracks its CPU, memory, file handles, environment, parent, and signal handlers.

## Listing processes

```bash
ps                       # your processes in current terminal
ps aux                   # everyone's, BSD-style
ps -ef                   # everyone's, System V-style
ps aux | grep nginx
pgrep nginx              # just the PIDs
pgrep -f 'python myapp'  # match against full command line

top                      # interactive
htop                     # better interactive (install separately)
btop                     # modern alternative
```

## Reading `ps aux`

```
USER PID %CPU %MEM    VSZ   RSS TTY STAT START TIME COMMAND
www  123  0.5  1.2  12345  6789 ?   Ssl  10:00 0:01 /usr/bin/nginx
```

- **VSZ** — virtual size (address space).
- **RSS** — resident set (actual RAM used).
- **STAT** — state. `R` running, `S` sleeping, `D` uninterruptible sleep, `Z` zombie, `T` stopped.

## Sending signals

```bash
kill <pid>               # SIGTERM (graceful)
kill -9 <pid>            # SIGKILL (forced)
kill -HUP <pid>          # SIGHUP (often "reload config")
kill -USR1 <pid>         # user-defined (some apps reopen logs)
killall nginx            # by name
pkill -f 'python script' # by command line pattern
```

Common signals:

| Signal     | Number | Meaning                                |
|------------|-------:|----------------------------------------|
| `SIGTERM`  | 15     | Polite "please exit"                   |
| `SIGINT`   | 2      | Ctrl-C from a terminal                 |
| `SIGHUP`   | 1      | Hang up; often "reload"                |
| `SIGKILL`  | 9      | Force kill; can't be caught or ignored |
| `SIGSTOP`  | 19     | Pause                                  |
| `SIGCONT`  | 18     | Continue                               |
| `SIGUSR1`  | 10     | App-specific                           |
| `SIGUSR2`  | 12     | App-specific                           |

Prefer SIGTERM over SIGKILL. SIGKILL bypasses cleanup — your app can leak files, locks, or half-flushed buffers.

## Backgrounding and jobs

```bash
sleep 100 &              # run in background
jobs                     # list background jobs in this shell
fg                       # bring last to foreground
fg %1                    # specific
bg %1                    # send to background
Ctrl-Z                   # suspend foreground job

nohup my-script &        # don't die when terminal closes
disown %1                # detach from shell
```

For long-running tasks across SSH sessions, use **`tmux`** or **`screen`** — proper terminal multiplexers.

## Resource limits

```bash
ulimit -n                # max open files
ulimit -n 65535          # raise
ulimit -a                # everything
```

A common production bug: hitting the default 1024 open-files limit. Raise via `/etc/security/limits.conf` for persistence.

## Watching a process

```bash
strace -p <pid>          # all syscalls
ltrace -p <pid>          # library calls
lsof -p <pid>            # open files, sockets
ss -tnp                  # network sockets with process names
pidstat -p <pid> 1       # CPU and memory over time
```

## Killing a stuck process

Don't reach for `kill -9` first. Try:

1. `kill <pid>` (SIGTERM) — give it 5–10 seconds.
2. `kill -INT <pid>` (Ctrl-C equivalent) — may unstick differently.
3. `kill -9 <pid>` (SIGKILL) — last resort.

If it's stuck on disk I/O (`D` state), even SIGKILL won't bring it down; the kernel waits for the I/O. Often you need to fix the underlying I/O issue (e.g., reconnect lost NFS).

## Process tree

```bash
pstree
ps -ejH
```

Parent-child relationships matter — killing a parent doesn't kill its children unless they're in the same process group and you use `kill -<sig> -<pgid>`.

## systemd note

Service processes are usually managed by **systemd**. Use `systemctl stop my-service` rather than killing the PID directly. Covered in the next lesson.
