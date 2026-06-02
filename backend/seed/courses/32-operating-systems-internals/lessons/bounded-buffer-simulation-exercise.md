# Exercise: Simulate a Bounded Buffer From an Operation Trace

In this exercise you will simulate the state of a bounded circular buffer as a sequence of producer and consumer operations are applied to it. This is the kind of step-by-step reasoning you need to answer concurrency trace questions in technical interviews.

## What You Will Implement

Given a buffer capacity `N` and a list of operations (`PRODUCE <value>` or `CONSUME`), your program must:

1. Track the circular buffer contents and the `head` (read) and `tail` (write) pointers.
2. For each `PRODUCE` operation: if the buffer is **full**, print `FULL`; otherwise insert the value and print the buffer state.
3. For each `CONSUME` operation: if the buffer is **empty**, print `EMPTY`; otherwise remove the oldest value and print it along with the buffer state.

Output the buffer state after every operation as a space-separated list of current items in insertion order (oldest first), wrapped in square brackets. If the buffer is empty after an operation, print `[]`.

## Skills Practiced

- Circular buffer (ring buffer) index arithmetic: `tail = (tail + 1) % N`
- Distinguishing full vs. empty using an item count
- Tracing concurrent data structure state — the exact reasoning you apply when evaluating whether a race condition or protocol violation has occurred

## Getting Started

Read the prompt file for the exact input/output format, constraints, and sample test cases. Implement your solution in Python using only the standard library.

The core logic fits in under 40 lines. Focus on getting the index arithmetic right before worrying about output formatting.
