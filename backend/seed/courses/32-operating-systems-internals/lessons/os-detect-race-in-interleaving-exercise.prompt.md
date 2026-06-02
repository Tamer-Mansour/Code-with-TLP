# Prompt: Detect a Lost Update From an Interleaving Trace

## Problem Description

Two threads (**A** and **B**) each perform one or more increments of a shared integer `counter` (initial value `0`). An increment consists of three micro-steps executed in order:

1. `LOAD` — copy `counter` (memory) into the thread's private register.
2. `ADD` — add 1 to the thread's register.
3. `STORE` — write the register value back to `counter` (memory).

You are given a trace: a sequence of lines, each specifying which thread performed which micro-step. The trace is the actual execution order (wall-clock order).

Simulate the execution step by step, tracking the memory value of `counter` and each thread's private register. At the end report:

- The final value of `counter`.
- `YES` if a lost update occurred (final value < total number of completed STORE operations), otherwise `NO`.

## Input Format

```
Line 1: N   (integer, number of trace steps, 1 ≤ N ≤ 100)
Lines 2..N+1: "<THREAD> <STEP>"
```

- `<THREAD>` is either `A` or `B`.
- `<STEP>` is one of `LOAD`, `ADD`, `STORE`.
- The trace is guaranteed to be well-formed: each thread's steps within a single increment appear in the order LOAD → ADD → STORE (though steps from different threads/increments may interleave).
- A thread always finishes at least one complete increment triple (LOAD, ADD, STORE) per run of three steps. No partial final triples.

## Output Format

```
FINAL: <value>
LOST_UPDATE: <YES|NO>
```

## Constraints

- 3 ≤ N ≤ 99 (N is always a multiple of 3)
- Each thread performs at least 1 and at most 16 complete increments.
- `counter` starts at `0`.
- Private registers start undefined; a thread's register is only valid after a `LOAD` in the current increment.

## Sample Input 1 (no race — sequential execution)

```
6
A LOAD
A ADD
A STORE
B LOAD
B ADD
B STORE
```

### Sample Output 1

```
FINAL: 2
LOST_UPDATE: NO
```

**Trace:**
- A LOAD: rA = 0 (counter=0)
- A ADD:  rA = 1
- A STORE: counter = 1
- B LOAD: rB = 1 (counter=1)
- B ADD:  rB = 2
- B STORE: counter = 2
- Total STOREs = 2, final = 2 → no lost update.

## Sample Input 2 (classic race — lost update)

```
6
A LOAD
B LOAD
A ADD
B ADD
A STORE
B STORE
```

### Sample Output 2

```
FINAL: 1
LOST_UPDATE: YES
```

**Trace:**
- A LOAD: rA = 0 (counter=0)
- B LOAD: rB = 0 (counter=0)
- A ADD:  rA = 1
- B ADD:  rB = 1
- A STORE: counter = 1
- B STORE: counter = 1  ← overwrites A's result
- Total STOREs = 2, final = 1 → lost update.

## Additional Test Cases

### Test Case 3 — Three increments, two for A, one for B, no race

Input:
```
9
A LOAD
A ADD
A STORE
A LOAD
A ADD
A STORE
B LOAD
B ADD
B STORE
```

Expected Output:
```
FINAL: 3
LOST_UPDATE: NO
```

### Test Case 4 — Race in the middle of multiple increments

Input:
```
9
A LOAD
A ADD
A STORE
B LOAD
A LOAD
B ADD
B STORE
A ADD
A STORE
```

Expected Output:
```
FINAL: 2
LOST_UPDATE: YES
```

**Trace:**
- A LOAD: rA=0, counter=0
- A ADD: rA=1
- A STORE: counter=1
- B LOAD: rB=1, counter=1
- A LOAD: rA=1, counter=1  (A starts second increment, loads current counter=1)
- B ADD: rB=2
- B STORE: counter=2
- A ADD: rA=2
- A STORE: counter=2  (A stores 2, same as what B already stored — lost update)
- Total STOREs = 3, final = 2 → lost update (expected 3).
