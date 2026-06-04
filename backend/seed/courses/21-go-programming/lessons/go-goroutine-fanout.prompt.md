# Goroutine Fan-Out Simulation

## Problem

In Go, fan-out dispatches N independent tasks to goroutines. Each goroutine sends its result to a shared channel when it finishes. Because goroutines run concurrently, results arrive in **completion order** (determined by how much work each task requires), not submission order.

Simulate this: given N tasks, each with an ID and a work value (the number of milliseconds it would take), output the results sorted by completion time (work value) ascending. For tasks with equal work values, sort by task ID ascending.

Each output line should be:
```
Task <id> done in <work>ms
```

## Input Format

```
N
id1 work1
id2 work2
...
```

- Line 1: `N`, number of tasks (1 <= N <= 1000)
- Next N lines: task ID and work value (both positive integers)

## Output Format

N lines sorted by work ascending, then by task ID ascending for ties.

## Example

**Input:**
```
5
3 10
1 40
4 20
2 10
5 30
```

**Output:**
```
Task 2 done in 10ms
Task 3 done in 10ms
Task 4 done in 20ms
Task 5 done in 30ms
Task 1 done in 40ms
```

**Explanation:** Tasks 2 and 3 both have work=10 (finish first). Task 2's ID (2) < Task 3's ID (3), so Task 2 appears first in the tie. Task 4 finishes next (work=20), then Task 5 (30), then Task 1 (40).

## Constraints

- 1 <= N <= 1000
- 1 <= task ID <= 10000
- 1 <= work value <= 10000
- Task IDs are unique
