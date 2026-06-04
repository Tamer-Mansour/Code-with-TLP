# RAII Lock Manager Trace

## Problem Description

Simulate a simplified RAII-based mutex system across multiple threads. You are given a trace of events that represent what each thread attempts to do, processed strictly in the order they appear in the input.

## Commands

Each line of stdin contains one command:

| Command | Effect |
|---|---|
| `LOCK tid mid` | Thread `tid` tries to acquire mutex `mid`. If the mutex is free, it acquires it and prints `tid ACQUIRED mid`. If already held by another thread, `tid` blocks and prints `tid BLOCKED on mid`. |
| `UNLOCK tid mid` | Thread `tid` releases mutex `mid`. Print `tid RELEASED mid`. If any threads are blocked waiting on `mid`, the first one (FIFO order) now acquires it: print `next_tid ACQUIRED mid`. |
| `WORK tid` | If thread `tid` is **not** blocked on any mutex, print `tid WORKING`. If `tid` is blocked, skip silently (a blocked thread cannot work). |

## Output Format

Exact strings, one per event (some events produce two output lines: the UNLOCK line plus the ACQUIRED line for the newly unblocked thread):

- `LOCK tid mid` when free: `tid ACQUIRED mid`
- `LOCK tid mid` when held: `tid BLOCKED on mid`
- `UNLOCK tid mid`: `tid RELEASED mid` (then optionally `next_tid ACQUIRED mid`)
- `WORK tid` when not blocked: `tid WORKING`
- `WORK tid` when blocked: *(no output)*

## Constraints

- Thread ids and mutex ids are uppercase letters/digits, length 1–10.
- At most 100 commands per test case.
- `UNLOCK` is only called by the thread currently holding the mutex.
- A thread will not attempt to `LOCK` a mutex it already holds.

## Sample Input 1

```
LOCK T1 M1
LOCK T2 M1
WORK T1
WORK T2
UNLOCK T1 M1
WORK T2
```

## Sample Output 1

```
T1 ACQUIRED M1
T2 BLOCKED on M1
T1 WORKING
T1 RELEASED M1
T2 ACQUIRED M1
T2 WORKING
```

**Explanation:** T1 acquires M1. T2 tries and blocks. T1 works (unblocked). T2 is blocked, so `WORK T2` produces no output. T1 unlocks — print `T1 RELEASED M1`, then immediately unblock T2 (FIFO): print `T2 ACQUIRED M1`. T2 is now unblocked and works.

## Sample Input 2

```
LOCK T1 MA
LOCK T1 MB
LOCK T2 MA
LOCK T3 MB
WORK T2
WORK T3
UNLOCK T1 MA
UNLOCK T1 MB
WORK T2
WORK T3
```

## Sample Output 2

```
T1 ACQUIRED MA
T1 ACQUIRED MB
T2 BLOCKED on MA
T3 BLOCKED on MB
T1 RELEASED MA
T2 ACQUIRED MA
T1 RELEASED MB
T3 ACQUIRED MB
T2 WORKING
T3 WORKING
```

## Sample Input 3

```
LOCK A M1
LOCK B M1
LOCK C M1
UNLOCK A M1
UNLOCK B M1
WORK C
```

## Sample Output 3

```
A ACQUIRED M1
B BLOCKED on M1
C BLOCKED on M1
A RELEASED M1
B ACQUIRED M1
B RELEASED M1
C ACQUIRED M1
C WORKING
```
