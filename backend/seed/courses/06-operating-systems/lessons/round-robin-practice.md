# Practice: Round-Robin Scheduling

Round-Robin is the most common preemptive scheduling algorithm in time-sharing systems. This exercise has you simulate it and compute the average waiting time.

## Review: Round-Robin Algorithm

```
Algorithm (all processes arrive at t=0, placed in queue in order):

queue = deque([P1, P2, ..., Pn])
time = 0

while queue is not empty:
    p = queue.popleft()
    if p.remaining <= quantum:
        time += p.remaining       # process finishes
        p.remaining = 0
        p.finish_time = time
    else:
        p.remaining -= quantum
        time += quantum
        queue.append(p)           # re-queue at the back

For each process i:
    wait_i = finish_time_i - burst_time_i
average_wait = sum(wait_i) // n
```

## Worked Example (4 processes, quantum=3)

```
Bursts: P1=6, P2=4, P3=8, P4=2

t= 0: P1 runs 3 → remaining=3;  queue: [P2,P3,P4,P1]
t= 3: P2 runs 3 → remaining=1;  queue: [P3,P4,P1,P2]
t= 6: P3 runs 3 → remaining=5;  queue: [P4,P1,P2,P3]
t= 9: P4 runs 2 → DONE, finish=11; queue: [P1,P2,P3]
t=11: P1 runs 3 → DONE, finish=14; queue: [P2,P3]
t=14: P2 runs 1 → DONE, finish=15; queue: [P3]
t=15: P3 runs 3 → remaining=2;  queue: [P3]
t=18: P3 runs 2 → DONE, finish=20

Wait: P1=14-6=8, P2=15-4=11, P3=20-8=12, P4=11-2=9
Average = 40 // 4 = 10
```

Now implement the Round-Robin simulator.
