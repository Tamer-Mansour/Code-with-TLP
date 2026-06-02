# Prompt: Simulate Timer-Driven Preemption Over a Tick Schedule

## Problem Description

Simulate a Round-Robin preemptive scheduler driven by a timer tick. Each tick, the running process is charged one unit of CPU time. When a process exhausts its quantum or finishes its burst, it is either re-queued (if preempted) or removed (if done). Print per-tick output and a summary.

## Input Format

```
N Q T
name1 burst1
name2 burst2
...
nameN burstN
```

- `N` — number of processes (1 ≤ N ≤ 10)
- `Q` — time-slice quantum in ticks (1 ≤ Q ≤ 20)
- `T` — total simulation ticks (1 ≤ T ≤ 100)
- Each `namei` is a string of 1–8 uppercase letters; `bursti` is an integer 1 ≤ bursti ≤ 50
- All processes arrive at tick 1 (ready from the start)
- Process order in input defines initial queue order

## Output Format

For each tick 1 through T (or until all processes complete, whichever comes first), print:

```
Tick <tick>: <name> (remaining: <remaining>)
```

Where `remaining` is the burst remaining **after** this tick is charged.

When all processes have completed before T ticks, stop printing tick lines.

Then print a blank line, followed by the summary — one line per process in original input order:

```
<name> done at tick <finish_tick>
```

If a process did not finish within T ticks, print:

```
<name> not finished
```

## Scheduling Rules

1. At each tick, the process at the front of the ready queue runs for one tick.
2. Decrement that process's remaining burst by 1. Decrement its current-quantum counter by 1.
3. If remaining burst == 0: process is done. Record finish tick. Remove from queue.
4. Else if current-quantum counter == 0: preempt — move process to back of queue. Reset quantum counter to Q.
5. Else: process continues next tick (stays at front of queue, quantum counter already decremented).
6. If queue becomes empty, stop (all done).

## Constraints

- No third-party libraries. Pure Python stdlib only.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input 1

```
3 2 10
A 3
B 4
C 2
```

## Sample Output 1

```
Tick 1: A (remaining: 2)
Tick 2: A (remaining: 1)
Tick 3: B (remaining: 3)
Tick 4: B (remaining: 2)
Tick 5: C (remaining: 1)
Tick 6: C (remaining: 0)
Tick 7: A (remaining: 0)
Tick 8: B (remaining: 1)
Tick 9: B (remaining: 0)

A done at tick 7
B done at tick 9
C done at tick 6
```

**Trace for Sample 1:**
- Tick 1: A runs (burst 3→2, quantum used 1/2)
- Tick 2: A runs (burst 2→1, quantum used 2/2) → preempt, move to back. Queue: B, C, A
- Tick 3: B runs (burst 4→3, quantum 1/2)
- Tick 4: B runs (burst 3→2, quantum 2/2) → preempt, move to back. Queue: C, A, B
- Tick 5: C runs (burst 2→1, quantum 1/2)
- Tick 6: C runs (burst 1→0) → done at tick 6. Queue: A, B
- Tick 7: A runs (burst 1→0) → done at tick 7. Queue: B
- Tick 8: B runs (burst 2→1, quantum 1/2)
- Tick 9: B runs (burst 1→0) → done at tick 9. Queue empty. Stop.

## Sample Input 2

```
2 3 5
X 10
Y 10
```

## Sample Output 2

```
Tick 1: X (remaining: 9)
Tick 2: X (remaining: 8)
Tick 3: X (remaining: 7)
Tick 4: Y (remaining: 9)
Tick 5: Y (remaining: 8)

X not finished
Y not finished
```
