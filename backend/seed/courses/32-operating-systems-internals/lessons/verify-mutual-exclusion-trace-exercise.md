# Exercise: Verify Mutual Exclusion Holds in a Lock Trace

In this exercise you will act as a runtime monitor: given a log of lock and unlock events from multiple threads, determine whether mutual exclusion was ever violated — that is, whether two or more threads held the same lock simultaneously.

## What You Will Implement

Given a sequence of events in the form `<thread_id> <LOCK|UNLOCK> <lock_name>`, your program must:

1. Track which thread currently holds each named lock.
2. Detect any moment where a `LOCK` event occurs for a lock already held by a different thread.
3. Report all violations, or confirm that no violation occurred.

This is exactly the kind of trace analysis a lock-checker tool (like Helgrind or ThreadSanitizer's lock-order checker) performs internally.

## Skills Practiced

- Reasoning about concurrent event traces
- Identifying critical section violations from a serialized log
- Understanding that a serialized trace represents one possible interleaving of concurrent threads

## Getting Started

Read the prompt file for the exact input/output format, constraints, and sample test cases. Implement your solution in Python using only the standard library.

Think of the problem as maintaining a dictionary from `lock_name -> thread_id` for currently held locks. A violation occurs when a thread tries to lock a lock whose dictionary entry is already set to a different thread id.

Your solution should handle multiple distinct lock names and detect multiple violations in a single trace.
