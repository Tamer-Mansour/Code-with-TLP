# Exercise: Simulate an Event Queue and Report Fire Order

## Problem Statement

You are implementing the core of a SystemC-style event scheduler. Given a list of named events with scheduled fire times, output the events in the order the scheduler would fire them.

## Input Format

```
N
name1 time1
name2 time2
...
nameN timeN
```

- First line: integer `N` (1 ≤ N ≤ 100), the number of events.
- Each of the next `N` lines: a string `name` (no spaces, 1–20 chars) and an integer `time` (0 ≤ time ≤ 1,000,000), representing the fire time in nanoseconds.
- Event names are unique within each test case.

## Output Format

Print one line per event in fire order:

```
T=<time>ns <name>
```

**Tie-breaking rule**: when multiple events share the same fire time, output them in **alphabetical order** by name (case-sensitive, standard Python string ordering).

## Constraints

- 1 ≤ N ≤ 100
- 0 ≤ time ≤ 1,000,000
- Names are unique, alphanumeric with underscores allowed.

## Sample Input 1

```
5
clk_rise 10
data_valid 25
reset 0
bus_grant 25
timeout 100
```

## Sample Output 1

```
T=0ns reset
T=10ns clk_rise
T=25ns bus_grant
T=25ns data_valid
T=100ns timeout
```

## Sample Input 2

```
3
irq 50
nmi 50
fiq 50
```

## Sample Output 2

```
T=50ns fiq
T=50ns irq
T=50ns nmi
```

## Notes

- The alphabetical tie-break models a deterministic scheduler policy — in a real SystemC implementation, processes within the same delta are ordered by registration order, but for this exercise we use alphabetical order for testability.
- Time 0 is valid and represents events scheduled during elaboration/initialization.
