# Process States and the State Transition Diagram

A process does not simply run from start to finish uninterrupted. It moves through a series of **states** as the OS schedules it, waits for I/O, responds to signals, and eventually terminates. Understanding these states — and the events that trigger transitions — is essential for reasoning about scheduling, debugging, and system performance.

## The Five Classic States

| State | Meaning |
|-------|---------|
| **New** | The process is being created; PCB allocated, resources being set up. |
| **Ready** | The process is loaded in memory and waiting for the CPU. |
| **Running** | The process is actively executing on a CPU core. |
| **Waiting** (Blocked) | The process is waiting for an event — I/O completion, a lock, a signal. |
| **Terminated** (Zombie) | The process has finished; resources released, but PCB retained until parent calls `wait()`. |

## State Transition Diagram

```
         admitted
  [New] ──────────→ [Ready] ←───────────────────┐
                       │                         │
           scheduler   │ dispatch                │ I/O complete /
           preempt ↑   ↓                         │ event arrives
                   [Running] ──────────→ [Waiting]
                       │       I/O request /
                       │       wait for event
                       │ exit()
                       ↓
                  [Terminated]
```

### Transition Descriptions

- **New → Ready**: The OS finishes setting up the process (loads ELF, maps memory, sets up PCB). The process is placed in the ready queue.
- **Ready → Running**: The scheduler selects this process and dispatches it to a CPU (restores registers from PCB).
- **Running → Ready**: A timer interrupt fires (preemption), or a higher-priority process becomes ready. The CPU registers are saved to the PCB and the process goes back to the ready queue.
- **Running → Waiting**: The process makes a blocking system call (e.g., `read()` on a socket, `sleep()`, `wait()` for a child) or waits on a mutex/semaphore.
- **Waiting → Ready**: The awaited event completes (disk returns data, timer expires, lock released). The process is moved back to the ready queue — it does NOT go directly to Running.
- **Running → Terminated**: The process calls `exit()`, returns from `main()`, or receives a fatal signal. The kernel cleans up resources; the process enters the Zombie state until the parent collects the exit status.

## Extended States in Real Kernels

Linux uses a richer set, visible via `ps` or `/proc/<pid>/status`:

| `ps` code | Linux state | Meaning |
|-----------|-------------|---------|
| `R` | TASK_RUNNING | Running or in ready queue |
| `S` | TASK_INTERRUPTIBLE | Waiting, can be woken by signal |
| `D` | TASK_UNINTERRUPTIBLE | Waiting on I/O, cannot be interrupted (unkillable!) |
| `T` | TASK_STOPPED | Suspended by SIGSTOP or debugger |
| `Z` | EXIT_ZOMBIE | Terminated, awaiting parent's `wait()` |
| `X` | EXIT_DEAD | Being fully removed (transient) |

The `D` state is infamous: a process stuck waiting for a failing disk can stay in `D` indefinitely and cannot be killed with `SIGKILL`. Only the event it waits for (or a reboot) can free it.

## Worked Example: Watching State Changes

```bash
# Observe a sleeping process
sleep 60 &
SLEEPPID=$!

# It should be in state 'S' (interruptible sleep)
ps -p $SLEEPPID -o pid,stat,cmd

# Force to stopped state
kill -STOP $SLEEPPID
ps -p $SLEEPPID -o pid,stat,cmd   # now 'T'

# Resume
kill -CONT $SLEEPPID
ps -p $SLEEPPID -o pid,stat,cmd   # back to 'S'
```

## Why the Ready → Running Distinction Matters

A common misconception is that "not blocked = running". In reality, a CPU with 4 cores can only run 4 processes at once. All other ready processes are queued. The interval a process spends in the ready queue waiting for a CPU is **scheduling latency** — a key metric in real-time systems.

## Common Pitfalls

- **Assuming Waiting → Running is direct**: The process always passes through Ready first. This is critical for scheduler fairness analysis.
- **Forgetting the Zombie state**: A process that calls `exit()` is not immediately gone. If the parent never calls `wait()`, the zombie lingers, consuming a PCB and a PID slot — too many zombies can exhaust the PID space.
- **Ignoring TASK_UNINTERRUPTIBLE**: This state is why `kill -9` sometimes appears to fail. The process is alive but cannot respond to any signal until its kernel wait completes.

> **Interview answer:** A process cycles through New, Ready, Running, Waiting, and Terminated states. Key transitions are: scheduler dispatch (Ready → Running), preemption or blocking I/O (Running → Ready or Waiting), event completion (Waiting → Ready), and exit (Running → Terminated/Zombie).
