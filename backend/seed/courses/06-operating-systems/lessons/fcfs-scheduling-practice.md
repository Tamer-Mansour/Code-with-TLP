# Practice: FCFS Scheduling Simulation

This exercise reinforces the **First-Come, First-Served (FCFS)** CPU scheduling algorithm by having you implement a simulator that computes average waiting time.

## Review: FCFS Algorithm

```
Sort processes by arrival time (ties broken by order of input)
time = 0
for each process p in sorted order:
    if time < p.arrival:
        time = p.arrival   # CPU idles until process arrives
    p.wait = time - p.arrival
    time += p.burst
average_wait = sum(p.wait for p in processes) // n
```

## Key Points

- FCFS is **non-preemptive** — once a process starts, it runs to completion.
- If the CPU is idle (no ready process), it fast-forwards to the next arrival.
- Average waiting time uses **integer (floor) division**.

## Worked Example

```
n=4 processes:
  P1: arrival=0, burst=6
  P2: arrival=0, burst=4
  P3: arrival=0, burst=8
  P4: arrival=0, burst=2

Gantt: | P1(0-6) | P2(6-10) | P3(10-18) | P4(18-20) |
Waiting: P1=0, P2=6, P3=10, P4=18
Total = 34, average = 34 // 4 = 8
```

Now implement the simulator below.
