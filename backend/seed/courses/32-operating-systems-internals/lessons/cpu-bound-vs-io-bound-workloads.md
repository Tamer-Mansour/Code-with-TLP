# CPU-Bound vs I/O-Bound Workloads

Every running process alternates between two kinds of activity: **CPU bursts** (doing computation) and **I/O bursts** (waiting for a disk read, network packet, keyboard input, etc.). How much time a process spends in each activity defines its character — and drives how the scheduler should treat it.

## CPU-Bound Processes

A **CPU-bound** process spends most of its time executing instructions. Its CPU bursts are long and its I/O bursts are few and short (or nonexistent).

Examples:
- Video encoder / transcoder
- Scientific simulation (e.g., fluid dynamics, Monte Carlo)
- Cryptographic hash computation
- Matrix multiplication

```python
# CPU-bound example: pure computation, no I/O
def is_prime(n):
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Running this for large n keeps the CPU busy for a long time
```

A CPU-bound process with a 10-second burst will hog a core for 10 seconds if the scheduler does not preempt it. Non-preemptive schedulers struggle here because other processes starve.

## I/O-Bound Processes

An **I/O-bound** process spends most of its time waiting for I/O. Its CPU bursts are short — often just a few milliseconds — and it frequently transitions to the BLOCKED state.

Examples:
- Web server handling HTTP requests (read socket, write socket)
- Database query engine (disk seeks)
- Text editor waiting for keystrokes
- File copy utility

```c
// I/O-bound pattern: short compute, then wait
while (fgets(line, sizeof(line), file)) {   // blocks on disk I/O
    process_line(line);                     // short CPU burst
    write_result(output_file, line);        // blocks again
}
```

I/O-bound processes voluntarily give up the CPU quickly (they block). A good scheduler keeps the CPU busy by immediately picking another runnable process whenever one blocks.

## Why the Distinction Matters for Scheduling

| Property             | CPU-Bound          | I/O-Bound          |
|----------------------|--------------------|--------------------|
| CPU burst length     | Long               | Short              |
| I/O burst frequency  | Rare               | Frequent           |
| CPU utilization      | High               | Low per burst      |
| Interaction feel     | Batch / background | Interactive / snappy |
| Scheduling priority  | Usually lower      | Usually higher     |

Giving I/O-bound processes higher priority is generally beneficial because they voluntarily release the CPU very soon anyway. Prioritizing them keeps disks and network cards busy in parallel, which increases overall system throughput.

If a CPU-bound process is given the same priority as an interactive I/O-bound process, the user will notice sluggish response — keystrokes are delayed because the encoder is burning the CPU.

## CPU Burst Distribution

In practice, CPU burst lengths follow a roughly exponential distribution: many short bursts and a few very long ones. This is why schedulers often use a **predicted burst length** (via exponential averaging) rather than a fixed time quantum:

```
τ_{n+1} = α * t_n + (1 - α) * τ_n
```

- `t_n` = actual burst length just measured
- `τ_n` = previous prediction
- `α` = smoothing factor (typically 0.5)

This is the foundation of the **Shortest-Job-First (SJF)** and **Shortest-Remaining-Time-First (SRTF)** schedulers discussed in the next module.

## Common Pitfalls

- Assuming all server processes are I/O-bound. A compute-heavy API endpoint (e.g., real-time image resize) can be CPU-bound even inside a web server.
- Ignoring mixed workloads. Many real applications switch character over time — a database may be I/O-bound during a full-table scan but CPU-bound during in-memory sorting.
- Conflating "I/O-bound" with "slow." An I/O-bound process can still have very high throughput if its short CPU bursts are efficient.

## Interview Answer

> "A CPU-bound process has long CPU bursts and rarely blocks; an I/O-bound process has short CPU bursts and frequently blocks on I/O. Schedulers typically give I/O-bound processes higher priority because they release the CPU quickly anyway, keeping both CPU and I/O devices busy."
