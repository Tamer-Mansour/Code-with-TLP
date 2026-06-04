# Promise Chain Tracer

## Problem

Simulate JavaScript's event loop execution order. You are given N task registrations. Output the labels in the order they would be printed.

**Task types:**

- `SYNC label` — executes synchronously, in registration order, before anything else
- `MICRO label` — executes as a Promise microtask, after all sync tasks, before macrotasks
- `MACRO label` — executes as a setTimeout macrotask, last of all

Within each category, tasks execute in the order they were registered.

**Execution order:** All SYNC → All MICRO → All MACRO

## Input Format

```
N
TYPE label
...
```

- Line 1: N (1 ≤ N ≤ 100)
- Next N lines: task type (SYNC, MICRO, or MACRO) followed by a label

## Output Format

One label per line, in execution order.

## Examples

**Input:**
```
5
SYNC start
MACRO timeout1
MICRO promise1
SYNC end
MICRO promise2
```

**Output:**
```
start
end
promise1
promise2
timeout1
```

**Input:**
```
4
MACRO timer
SYNC alpha
MICRO beta
SYNC gamma
```

**Output:**
```
alpha
gamma
beta
timer
```

**Input:**
```
3
MACRO only-macro
MACRO second-macro
MICRO first-micro
```

**Output:**
```
first-micro
only-macro
second-macro
```

## Constraints

- 1 ≤ N ≤ 100
- TYPE is one of: SYNC, MICRO, MACRO
- Labels are non-empty alphanumeric strings (may contain hyphens)
