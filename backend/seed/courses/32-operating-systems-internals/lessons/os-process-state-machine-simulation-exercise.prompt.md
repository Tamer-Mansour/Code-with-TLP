# Prompt: Simulate a Process State Machine From an Event Log

## Problem Description

You are given a log of OS events, each targeting a specific process (identified by a PID). Simulate the five-state process model and report each process's final state.

### States

`NEW`, `READY`, `RUNNING`, `WAITING`, `TERMINATED`

A process starts implicitly in the `NEW` state before its first event. Processes that receive no events do not appear in the output.

### Valid Transitions

| Current State | Event    | Next State |
|--------------|----------|------------|
| NEW          | ADMIT    | READY      |
| READY        | DISPATCH | RUNNING    |
| RUNNING      | IO_WAIT  | WAITING    |
| RUNNING      | PREEMPT  | READY      |
| RUNNING      | EXIT     | TERMINATED |
| WAITING      | IO_DONE  | READY      |

Any other `(state, event)` combination is invalid: print an error line and leave the process state unchanged.

## Input Format

```
N
PID_1 EVENT_1
PID_2 EVENT_2
...
PID_N EVENT_N
```

- First line: integer `N` (1 ≤ N ≤ 100) — number of events.
- Each of the next `N` lines contains a positive integer `PID` and an event string, separated by a single space.
- PIDs are positive integers (1 ≤ PID ≤ 9999).
- Events are exactly one of: `ADMIT`, `DISPATCH`, `IO_WAIT`, `IO_DONE`, `PREEMPT`, `EXIT`.

## Output Format

For each **invalid transition**, print immediately (in encounter order):
```
ERROR <PID> <EVENT> invalid in state <CURRENT_STATE>
```

After processing all events, print one line per process that appeared at least once, sorted by PID in **ascending numeric order**:
```
<PID> <FINAL_STATE>
```

Error lines appear **before** the final-state summary lines.

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ PID ≤ 9999
- All event strings are from the valid list above.

## Sample Input

```
5
1 ADMIT
2 ADMIT
1 DISPATCH
1 IO_WAIT
2 DISPATCH
```

## Sample Output

```
1 WAITING
2 RUNNING
```

**Explanation:**
- PID 1: NEW →(ADMIT)→ READY →(DISPATCH)→ RUNNING →(IO_WAIT)→ WAITING. Final state: WAITING.
- PID 2: NEW →(ADMIT)→ READY →(DISPATCH)→ RUNNING. Final state: RUNNING.
- Sorted by PID ascending.

## Additional Example With an Error

**Input:**
```
4
1 ADMIT
1 IO_WAIT
1 DISPATCH
1 EXIT
```

**Output:**
```
ERROR 1 IO_WAIT invalid in state READY
1 TERMINATED
```

**Explanation:**
- ADMIT: NEW → READY.
- IO_WAIT from READY is invalid — error printed, state stays READY.
- DISPATCH: READY → RUNNING.
- EXIT: RUNNING → TERMINATED.
