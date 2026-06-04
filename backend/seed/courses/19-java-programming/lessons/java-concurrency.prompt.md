# Task Scheduler Simulation

Simulate a fixed-size thread pool scheduling tasks.

Read:
- `T` on the first line — number of threads (0-indexed)
- `N` on the second line — number of tasks
- `N` space-separated integers on the third line — task durations

All threads start free at time `0`. For each task (in order from task `0` to task `N-1`), assign it to the thread that becomes free **earliest**. On a tie in finish time, pick the thread with the **smallest index**.

Print one line per task in arrival order:
```
Task <i>: thread <t>, finishes at <time>
```

## Example

**Input**
```
2
4
3 1 4 2
```

**Output**
```
Task 0: thread 0, finishes at 3
Task 1: thread 1, finishes at 1
Task 2: thread 1, finishes at 5
Task 3: thread 0, finishes at 5
```

## Constraints

- `1 <= T <= 10`
- `1 <= N <= 100`
- `1 <= duration <= 100`
