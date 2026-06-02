# Exercise: Simulate a Preemptive Priority Scheduler With Aging

## Overview

In this exercise you will implement a **preemptive priority scheduler with aging** from scratch. Your simulator processes a list of processes with arrival times, burst times, and static priorities, then schedules them one millisecond at a time. Every quantum that a process spends waiting in the ready queue, its effective priority improves by one step — preventing starvation while still honoring priority for newly arrived work.

## What You Will Implement

You will write a program that:

1. **Reads** a set of processes from standard input.
2. **Simulates** preemptive scheduling tick by tick, recalculating effective priorities after each tick.
3. **Applies aging** — each tick a process spends waiting (not running), its effective priority is decremented by 1 (lower number = higher priority in this simulation).
4. **Outputs** the finish time and turnaround time for each process, in process-ID order.

## Rules

- Priority numbers are integers; **lower is higher priority** (1 beats 2).
- At each tick, pick the ready process with the lowest effective priority (ties broken by lower PID).
- A process is "ready" at tick `t` if `arrival_time <= t` and it has remaining burst > 0.
- Aging: for every tick a process waits in the ready queue, subtract 1 from its effective priority (floor at -999).
- When a new process arrives, re-evaluate priorities immediately (preemptive).
- Output lines must appear in ascending PID order.

## Skills Practiced

- Priority queue management under a dynamic key (effective priority changes each tick)
- Preemption logic: checking if a newly arrived or re-prioritized process should displace the current runner
- Starvation prevention analysis: verifying that all processes complete even when high-priority processes keep arriving

## Getting Started

Your solution should read from `stdin` and write to `stdout`. No files, no third-party libraries. A correct simulation runs in O(N × max_time) which is fast enough for the constraints given.

See the companion prompt file (`os-priority-scheduling-simulation-exercise.prompt.md`) for the exact input/output format, constraints, and sample test cases.
