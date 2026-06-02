# Exercise: Simulate a Process State Machine From an Event Log

In this exercise you will implement a **process state machine simulator** that reads a sequence of OS events and tracks the state of one or more processes as they transition through the classic five-state model:

- **NEW** — being created
- **READY** — waiting for CPU
- **RUNNING** — executing on CPU
- **WAITING** — blocked on I/O or an event
- **TERMINATED** — finished execution

## What You'll Implement

You will write a program that:

1. Reads a series of `(PID, EVENT)` pairs from standard input.
2. Applies each event to the current state of the named process, following the valid state-transition rules.
3. After processing all events, prints each process's final state in ascending PID order.

## Valid Transitions

| Current State | Event | Next State |
|--------------|-------|-----------|
| (none / first seen) | `ADMIT` | NEW → READY |
| READY | `DISPATCH` | RUNNING |
| RUNNING | `IO_WAIT` | WAITING |
| RUNNING | `PREEMPT` | READY |
| RUNNING | `EXIT` | TERMINATED |
| WAITING | `IO_DONE` | READY |

Any event that is invalid for the current state should be printed as an `ERROR` line and the process state should remain unchanged.

## Skill Goals

- Model a finite state machine in code.
- Read structured input from stdin and write structured output to stdout.
- Handle edge cases (duplicate PIDs, invalid transitions, unseen PIDs).

See the companion prompt file (`os-process-state-machine-simulation-exercise.prompt.md`) for the exact input/output format, constraints, and sample test cases.
