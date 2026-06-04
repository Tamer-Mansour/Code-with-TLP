# Exercise: Delta-Cycle Event Ordering Simulator

## Problem Statement

In SystemC the scheduler runs evaluation/update cycles at the same simulated timestamp before advancing time. These are called delta cycles. An event notified with `SC_ZERO_TIME` fires in the next delta cycle at the same timestamp; an immediate notification fires in the current delta cycle.

You are given a list of events. Each line contains: `<timestamp> <delta_offset> <process_name>`. Simulate the SystemC scheduler: sort events first by timestamp (ascending), then by delta_offset (ascending), then by process_name (alphabetical) as a tiebreaker. Print each event in the order the scheduler would execute it, formatted as `T=<timestamp>d<delta>: <process_name>`.

## Input Format

- First line: integer `N` (number of events, 1 <= N <= 20)
- Next N lines: `<timestamp> <delta> <name>` where timestamp and delta are non-negative integers and name is an alphanumeric string with no spaces

## Output Format

- N lines, each `T=<timestamp>d<delta>: <name>`

## Constraints

- 1 <= N <= 20
- 0 <= timestamp <= 1,000,000
- 0 <= delta <= 100
- Process names contain only letters, digits, and underscores

## Sample Input

```
5
10 1 process_B
10 0 process_A
5 0 process_C
10 0 process_D
5 1 process_E
```

## Sample Output

```
T=5d0: process_C
T=5d1: process_E
T=10d0: process_A
T=10d0: process_D
T=10d1: process_B
```

## Additional Example

Input:
```
3
100 2 alpha
100 0 beta
100 1 gamma
```

Output:
```
T=100d0: beta
T=100d1: gamma
T=100d2: alpha
```
