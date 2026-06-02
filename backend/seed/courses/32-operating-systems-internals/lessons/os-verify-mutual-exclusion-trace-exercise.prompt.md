# Prompt: Verify Mutual Exclusion Holds in a Lock Trace

## Problem Description

You are given a serialized event log from a multithreaded program. Each event records one thread acquiring or releasing a named lock. Your task is to detect any mutual-exclusion violations: moments where a thread attempts to acquire a lock that is already held by a different thread.

## Input Format

```
Line 1: E          (integer, 1 <= E <= 200, number of events)
Lines 2..E+1: one event per line in the format:
    <thread_id> <action> <lock_name>
```

- `thread_id`: a positive integer identifying the thread (1-indexed)
- `action`: either `LOCK` or `UNLOCK`
- `lock_name`: a string of alphanumeric characters (no spaces), e.g. `mutex_A`

## Output Format

Process events in order. For each `LOCK` event that violates mutual exclusion (the lock is already held by a **different** thread), print:

```
VIOLATION: thread <T1> holds <lock_name>, thread <T2> attempted lock at event <N>
```

where `T1` is the thread currently holding the lock, `T2` is the thread attempting to lock it, and `N` is the 1-based event number (counting from line 2 of input).

For `UNLOCK` events and non-violating `LOCK` events, print nothing.

After processing all events, if no violations were found, print:

```
OK
```

If one or more violations were found, do **not** print `OK`.

## Constraints

- `1 <= E <= 200`
- Thread IDs are integers in range `[1, 50]`
- Lock names are non-empty alphanumeric strings, length 1-20
- An `UNLOCK` by a thread that does not hold the lock is ignored (no output)
- A thread locking a lock it already holds is **not** a violation (reentrant behavior is assumed allowed)
- Multiple violations may occur in one trace

## Sample Input 1

```
6
1 LOCK mutex_A
2 LOCK mutex_B
2 LOCK mutex_A
1 UNLOCK mutex_A
2 UNLOCK mutex_A
2 UNLOCK mutex_B
```

## Sample Output 1

```
VIOLATION: thread 1 holds mutex_A, thread 2 attempted lock at event 3
```

## Sample Input 2

```
4
1 LOCK mutex_A
1 UNLOCK mutex_A
2 LOCK mutex_A
2 UNLOCK mutex_A
```

## Sample Output 2

```
OK
```

## Notes

- The trace is serialized (one event at a time) but represents concurrent execution.
- A violation at event N does not stop processing; continue checking remaining events.
- A thread that attempts to lock a lock it already holds is **not** a violation (print nothing for that event).
