# When Scheduling Decisions Happen

The scheduler does not run continuously — it is invoked at specific, well-defined moments. Knowing exactly when scheduling decisions happen explains why certain algorithms are classified as preemptive and others are not, and helps you predict how a timeline will evolve.

## The Four Classic Scheduling Points

Silberschatz and other standard OS texts identify four circumstances under which the CPU scheduler must (or may) make a decision:

### Point 1 — Process Switches from RUNNING to BLOCKED

When a running process issues a blocking system call (e.g., `read()`, `wait()`), it voluntarily surrenders the CPU. The scheduler must pick a new process because the current one cannot continue.

```
P1: read(fd, buf, n)   ← blocks on disk I/O
  → P1 moves to BLOCKED state
  → Scheduler runs, picks P2 from ready queue
```

**Both** non-preemptive and preemptive schedulers act here. This point is always a scheduling event.

### Point 2 — Process Terminates

When a process calls `exit()` or is killed by a signal, it releases the CPU permanently. The scheduler must pick the next process to run.

Again, **both** scheduler types act here.

### Point 3 — Process Switches from RUNNING to READY (preemption)

A hardware timer fires (time quantum expires) and the currently running process is moved back to the ready queue. This is the defining action of a preemptive scheduler.

```c
// Pseudocode: timer fires every 10ms
void on_timer_tick() {
    current_process.quantum_remaining--;
    if (current_process.quantum_remaining <= 0) {
        move_to_ready(current_process);   // Point 3
        schedule();
    }
}
```

**Only preemptive** schedulers act here. A non-preemptive scheduler ignores the timer.

### Point 4 — Process Switches from BLOCKED to READY

When an I/O operation completes, the process moves from BLOCKED back to READY. The scheduler may now decide whether the newly ready process should preempt the currently running one (if its priority is higher, for example).

```
I/O complete interrupt:
  → P1 moves from BLOCKED to READY
  → If priority(P1) > priority(current): preempt current (preemptive only)
  → Otherwise: P1 waits in ready queue
```

**Preemptive** schedulers may act here. Non-preemptive schedulers add the process to the ready queue but let the current process finish.

## Summary Table

| Scheduling Point            | Non-Preemptive | Preemptive |
|-----------------------------|:--------------:|:----------:|
| 1. RUNNING → BLOCKED        | Yes            | Yes        |
| 2. Process terminates       | Yes            | Yes        |
| 3. RUNNING → READY (timer)  | No             | Yes        |
| 4. BLOCKED → READY (I/O done) | No (waits)  | Yes (may preempt) |

Points 1 and 2 define **non-preemptive** scheduling. Points 3 and 4 additionally apply to **preemptive** scheduling.

## Kernel Scheduling Triggers in Linux

In the Linux kernel, these events are abstracted into scheduler invocations:

```bash
# You can observe scheduling events with perf or ftrace:
perf stat -e context-switches ./my_program
# Reports how many times the scheduler switched context during the run
```

The kernel marks a `need_resched` flag when any of the four points occurs. The flag is checked at safe preemption points (return from interrupt, return from system call) and triggers `schedule()`.

## Why This Matters for Algorithm Analysis

When you draw a Gantt chart by hand:

1. Check if any process **arrives** at the current time (Point 4 analogue for arrival).
2. Check if the current process **blocks or exits** (Points 1 and 2).
3. Check if the **time quantum expires** (Point 3 — preemptive only).
4. Check if a **higher-priority process** just became ready (Point 4 — preemptive only).

Miss any of these and your Gantt chart will be wrong.

## Common Pitfalls

- Forgetting that a process completing its burst is a scheduling event (Point 2), not just Point 3. Even in non-preemptive mode, when P1 finishes, the scheduler picks the next process.
- Assuming Point 4 always causes preemption. A preemptive scheduler may still keep the current process running if the newly ready process has lower or equal priority, depending on algorithm.
- Conflating "scheduling decision" with "context switch." A scheduling decision may conclude "keep running the current process," in which case no context switch occurs.

## Interview Answer

> "Scheduling decisions happen when: (1) a process blocks on I/O, (2) a process terminates, (3) a timer interrupt expires the running process's quantum, or (4) a blocked process becomes ready. Only scenarios 3 and 4 require a preemptive scheduler."
