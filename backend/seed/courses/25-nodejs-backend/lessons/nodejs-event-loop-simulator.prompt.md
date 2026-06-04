# Event Loop Execution Order Simulator

In Node.js, the event loop processes tasks in a strict priority order:
synchronous code runs first, then `process.nextTick` callbacks, then Promise microtasks, then macrotasks (`setTimeout`, `setImmediate`, I/O callbacks).

Given a list of task registrations, simulate the execution order and print each task label on its own line.

## Input Format

- First line: integer `N` — the number of tasks
- Next `N` lines: each line contains a type and a label separated by a single space

Task types:
- `SYNC` — runs immediately (synchronous call stack)
- `NEXTTICK` — runs after all sync code, before microtasks (like `process.nextTick`)
- `MICROTASK` — runs after nextTick queue, before macrotasks (like a resolved Promise `.then`)
- `MACROTASK` — runs last, after all microtasks (like `setTimeout` or `setImmediate`)

## Output Format

Print each label on its own line in execution order:
1. All SYNC labels (in input order)
2. All NEXTTICK labels (in input order)
3. All MICROTASK labels (in input order)
4. All MACROTASK labels (in input order)

## Example

**Input:**
```
7
SYNC A
MACROTASK B
MICROTASK C
SYNC D
NEXTTICK E
MICROTASK F
NEXTTICK G
```

**Output:**
```
A
D
E
G
C
F
B
```

## Constraints

- 1 ≤ N ≤ 100
- Labels are single uppercase strings without spaces
- All task types are exactly one of: SYNC, NEXTTICK, MICROTASK, MACROTASK
