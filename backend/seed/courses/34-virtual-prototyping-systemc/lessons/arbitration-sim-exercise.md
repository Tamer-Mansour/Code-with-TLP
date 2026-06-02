# Simulate Round-Robin Bus Arbitration

In this exercise you will simulate a round-robin bus arbiter. Multiple initiators submit transaction requests at different simulation time steps, and the arbiter grants the bus in strict round-robin order, computing the start time and completion time for each granted transaction.

## What You Will Implement

Write a simulation that:

1. Reads the number of masters, bus cycle time, and a per-master transaction latency.
2. Reads a list of transaction requests: which master, at what time they arrive.
3. Applies round-robin arbitration: the arbiter checks masters in order 0, 1, 2, ..., N-1, wrapping around.
4. Each transaction occupies the bus for its master's latency cycles.
5. For each transaction granted, output: master id, grant time, completion time.

## Skills Practiced

- Implementing round-robin scheduling logic
- Tracking bus availability and request queues
- Event-driven simulation thinking: "what is the earliest time the bus is free?"

## Example

With 3 masters and a bus cycle of 10 ns, if masters 0, 1, and 2 all submit requests at time 0, the arbiter grants them in order: master 0 at t=0, master 1 after master 0 completes, master 2 after master 1 completes.

## Getting Started

Read the prompt file carefully — pay attention to how "next in round-robin order" is determined even when the next master in sequence has no pending request (skip to the next one that does). Output is sorted by grant time, with ties broken by master id.
