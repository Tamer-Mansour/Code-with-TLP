# Exercise: Simulate Timer-Driven Preemption Over a Tick Schedule

In this exercise you will simulate a simplified preemptive scheduler driven by a timer tick. This mirrors how real operating systems use the timer interrupt to enforce time slices and rotate between processes.

## What You Will Implement

You will write a program that:

1. Reads a list of processes, each with a name and a total CPU burst (in ticks).
2. Reads a time-slice quantum (Q ticks) and the total simulation length (T ticks).
3. Simulates a **Round-Robin** scheduler where each process runs for at most Q ticks before being preempted by the timer interrupt and placed at the back of the run queue.
4. Prints a log showing which process runs at each tick (tick 1 through T), and then a completion summary.

## Key Concepts Reinforced

- The timer fires every tick — this is the preemption signal.
- A process that finishes its burst before Q ticks is removed from the queue (it voluntarily completes).
- Processes that have not yet arrived are not in the ready queue (all processes arrive at tick 1 in this simplified model).
- After T ticks, the simulation ends regardless of remaining bursts.

## What to Implement

Open the starter code (Python) and implement the `simulate` function. The skeleton handles input parsing. Your simulator must produce per-tick output and a final summary table.

```python
def simulate(processes, quantum, total_ticks):
    """
    processes: list of (name, burst) tuples, in arrival order
    quantum:   max ticks a process runs before preemption
    total_ticks: total simulation length
    Returns: list of strings to print
    """
    # TODO: implement Round-Robin tick simulation
    pass
```

## Input / Output Contract

See the companion prompt file `os-simulate-timer-ticks-exercise.prompt.md` for the full specification including stdin format, stdout format, constraints, and sample test cases.
