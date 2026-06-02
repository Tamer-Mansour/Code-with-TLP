# Prompt: Simulate a Preemptive Priority Scheduler With Aging

## Problem Description

Simulate a preemptive priority scheduler with aging on a single CPU.

You are given N processes. Each process has:
- A unique integer ID (PID)
- An arrival time (the tick at which it enters the ready queue)
- A burst time (total ticks of CPU it needs)
- A static priority (integer; lower = higher priority)

**Scheduling rules (applied each tick):**

1. Advance the clock to the next arrival if the CPU is idle and no process is ready.
2. Among all processes that have arrived and still have remaining burst > 0, compute each one's **effective priority**:
   ```
   effective_priority = static_priority - ticks_spent_waiting
   ```
   `ticks_spent_waiting` resets to 0 whenever the process gets the CPU (even for one tick).
3. Run the process with the **lowest effective priority** for one tick. Break ties by lowest PID.
4. After the tick, increment `ticks_spent_waiting` by 1 for every ready process (arrived and not yet finished) that did NOT run this tick.
5. Repeat until all processes finish.

**Output:** For each process in ascending PID order, print one line:
```
PID finish_time turnaround_time
```
where `turnaround_time = finish_time - arrival_time`.

## Input Format

```
N
PID arrival_time burst_time static_priority
PID arrival_time burst_time static_priority
...
```

- Line 1: integer N (number of processes, 1 ≤ N ≤ 20)
- Lines 2..N+1: four space-separated integers per line
- All values are non-negative integers
- Burst times are 1–100; arrival times are 0–200; static priorities are 1–20
- PIDs are distinct positive integers given in arbitrary order

## Output Format

N lines, one per process, in ascending PID order:
```
<PID> <finish_time> <turnaround_time>
```

## Constraints

- 1 ≤ N ≤ 20
- 1 ≤ burst_time ≤ 100
- 0 ≤ arrival_time ≤ 200
- 1 ≤ static_priority ≤ 20
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input 1

```
3
1 0 10 3
2 0 4 1
3 0 6 2
```

## Sample Output 1

```
1 20 20
2 7 7
3 15 15
```

**Explanation:** All three processes arrive at t=0. P2 has the highest priority (1) so it runs first, but aging quickly brings P3 (priority 2) to the front as well. P2 and P3 interleave due to aging, with P1 (lowest base priority 3) receiving service last. Aging prevents P1 from starving indefinitely despite its low base priority.

## Sample Input 2

```
1
5 3 7 10
```

## Sample Output 2

```
5 10 7
```

**Explanation:** Single process arrives at t=3. CPU is idle from t=0 to t=3. Process runs for 7 ticks (t=3 to t=10). Finish=10, Turnaround=10-3=7.

## Notes for Implementation

- Process the clock tick by tick; do not skip time (except when the CPU is idle and no process is ready — then jump to the next arrival).
- The `ticks_spent_waiting` counter for a process only increments when it is in the ready queue (arrived, not yet finished) but not running this tick. It does NOT increment before the process arrives.
- When a process gets the CPU, its `ticks_spent_waiting` resets to 0 for that tick (and stays 0 as long as it keeps running uninterrupted).
- A process that just finished does not continue to accumulate wait ticks.
