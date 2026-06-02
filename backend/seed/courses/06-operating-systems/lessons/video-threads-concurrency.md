# Video: Threads, Concurrency, and Race Conditions

This video explains how threads share a process address space to achieve concurrency, why this sharing creates race conditions, and how synchronization primitives solve the critical section problem.

## What This Video Covers

- Threads vs processes: what is shared and what is private per thread
- How race conditions arise from non-atomic read-modify-write sequences
- The critical section problem and the requirements for any correct solution (mutual exclusion, progress, bounded waiting)
- Peterson's algorithm as a software-only solution
- Introduction to hardware atomic instructions (test-and-set, compare-and-swap)

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | Thread model and shared memory |
| ~12 min | Race condition demonstration |
| ~28 min | Critical section requirements |
| ~40 min | Peterson's algorithm |
| ~55 min | Hardware atomic instructions |

## Key Takeaways

Two threads incrementing a shared counter with `x = x + 1` is not atomic — the CPU executes three separate micro-operations (load, add, store) that can interleave in any order. Correct synchronization must guarantee **mutual exclusion** (only one thread in the critical section at a time), **progress** (if no thread is in the CS, one that wants to enter must be allowed), and **bounded waiting** (a thread will eventually get in, not starve forever).
