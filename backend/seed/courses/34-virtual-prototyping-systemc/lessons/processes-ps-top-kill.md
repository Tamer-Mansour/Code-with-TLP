# Processes: ps, top, kill

A SystemC simulation is a process. When it hangs due to a deadlock, consumes 100 % CPU unexpectedly, or you need to run several simulations in parallel, you need to inspect and control processes from the command line. `ps`, `top`, and `kill` are the three essential tools.

---

## What Is a Process?

Every running program on Linux is a process with a unique **PID** (Process ID). Processes have:

- An owner (the user who started them)
- CPU and memory usage
- A state: running (R), sleeping (S), stopped (T), zombie (Z)
- A parent process (the shell that launched them)

---

## ps — Process Snapshot

`ps` prints a static snapshot of currently running processes.

```bash
# Processes in the current terminal session only
ps

# All processes, full details (most common form)
ps aux

# All processes in a tree (shows parent-child relationships)
ps axjf

# Filter by name
ps aux | grep sim_top
```

### Understanding `ps aux` columns

```
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
tamer     4821 98.2  3.1 512000 64000 pts/0    R+   10:00   2:14 ./sim_top
```

| Column | Meaning |
|--------|---------|
| PID | Process ID |
| %CPU | CPU usage percentage |
| %MEM | Resident memory percentage |
| VSZ | Virtual memory size (KB) |
| RSS | Resident set size — actual RAM used (KB) |
| STAT | State: R=running, S=sleeping, Z=zombie, T=stopped |
| TIME | Total CPU time consumed |
| COMMAND | Executable and arguments |

---

## top — Live Process Monitor

`top` shows a continuously updating list of processes sorted by CPU usage.

```bash
top
```

Key interactive commands inside `top`:

| Key | Action |
|-----|--------|
| `q` | Quit |
| `P` | Sort by CPU (default) |
| `M` | Sort by memory |
| `k` | Kill a process (prompts for PID) |
| `1` | Toggle per-CPU breakdown |
| `/` | Filter by process name |

**For VP work:** Launch a SystemC simulation, then open `top` in a second terminal to watch its CPU and memory grow over simulation time.

```bash
# Alternative: htop is more user-friendly (install with: sudo apt install htop)
htop
```

---

## kill — Send Signals to a Process

`kill` sends a **signal** to a process. The process can handle or ignore some signals; others terminate it unconditionally.

```bash
# Graceful termination (SIGTERM = signal 15, the default)
kill 4821

# Forceful kill — cannot be caught or ignored (SIGKILL = signal 9)
kill -9 4821

# List all signal names
kill -l
```

### Common signals

| Signal | Number | Default action | When to use |
|--------|--------|----------------|-------------|
| SIGTERM | 15 | Terminate | First attempt — gives the process a chance to clean up |
| SIGKILL | 9 | Kill immediately | Process ignores SIGTERM or is truly frozen |
| SIGINT | 2 | Interrupt | Same as Ctrl+C |
| SIGSTOP | 19 | Pause | Suspend a simulation |
| SIGCONT | 18 | Resume | Resume a paused simulation |

### killall and pkill

```bash
# Kill all processes with this name
killall sim_top

# Kill by pattern (partial name)
pkill sim_

# Kill by user
pkill -u tamer sim_top
```

---

## Worked Example — Dealing with a Hung Simulation

```bash
# 1. Simulation appears frozen; find its PID
ps aux | grep sim_top
# tamer  7842 99.9  4.2 ...  ./sim_top --cycles 1000000

# 2. Try graceful termination first
kill 7842

# 3. If still running after a few seconds, force kill
kill -9 7842

# 4. Confirm it is gone
ps aux | grep sim_top
# (no output means it is gone)
```

---

## Background and Foreground Jobs

```bash
# Run a long simulation in the background
./sim_top &
# [1] 8023   <- job number and PID

# Check background jobs
jobs

# Bring it to the foreground
fg %1

# Suspend the foreground process (Ctrl+Z), then send to background
bg %1
```

---

## Checking System Load

```bash
# One-line summary: uptime and load averages
uptime
# 10:35:21 up 2 days,  1:12,  3 users,  load average: 3.21, 2.88, 2.40

# Load average over 1, 5, 15 minutes.
# Values above the number of CPU cores indicate overloading.
nproc   # number of logical CPUs
```

> **Interview answer:** `ps aux` lists all running processes with their PIDs and resource usage. `top` shows a live view sorted by CPU. `kill -9 PID` forcefully terminates a process that ignores the default SIGTERM signal. For VP work this matters when a simulation deadlocks and must be stopped manually.
