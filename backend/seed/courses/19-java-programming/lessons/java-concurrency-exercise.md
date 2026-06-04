# Exercise: Task Scheduler Simulation

Real Java concurrency involves threads and synchronisation, but the *algorithmic* thinking behind a multi-threaded scheduler can be tested with a deterministic simulation. This problem mirrors the scheduling decisions an `ExecutorService` makes when assigning tasks to a fixed thread pool.

## The problem: task scheduling

Imagine a thread pool with `T` threads. Tasks arrive with a given duration. Assign each task to the thread that becomes free **earliest** (lowest finish-time). If multiple threads tie, pick the one with the **smallest index**. Print the thread assignment and finish time for each task in arrival order.

This models `Executors.newFixedThreadPool(T)` with tasks submitted sequentially.

## Java mental model

```java
ExecutorService pool = Executors.newFixedThreadPool(3);
for (Task t : tasks) {
    pool.submit(() -> { /* run task */ });
}
pool.shutdown();
pool.awaitTermination(1, TimeUnit.MINUTES);
```

The problem below simulates which thread handles each task, deterministically.

## Problem statement

Read `T` (number of threads) on the first line, then `N` (number of tasks) on the second line, then `N` integers on the third line representing task durations (in time units). All threads start free at time 0. For each task (in order), assign it to the thread that becomes available earliest (smallest finish time). On a tie, choose the thread with the smallest 0-based index. Print one line per task: `Task <i>: thread <t>, finishes at <time>`.

### Example

Input:
```
2
4
3 1 4 2
```

Output:
```
Task 0: thread 0, finishes at 3
Task 1: thread 1, finishes at 1
Task 2: thread 1, finishes at 5
Task 3: thread 0, finishes at 5
```

Explanation:
- Task 0 (duration 3) goes to thread 0 (both free at 0, pick index 0). Thread 0 free at 3.
- Task 1 (duration 1) goes to thread 1 (thread 1 free at 0 < thread 0 free at 3). Thread 1 free at 1.
- Task 2 (duration 4) goes to thread 1 (free at 1) vs thread 0 (free at 3). Thread 1 wins. Thread 1 free at 5.
- Task 3 (duration 2) goes to thread 0 (free at 3) vs thread 1 (free at 5). Thread 0 wins. Thread 0 free at 5.

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 12: Threads and Multiprocessing: https://math.hws.edu/javanotes/
