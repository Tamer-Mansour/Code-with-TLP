# Exercise: Compute Effective Access Time With Page Faults

The **Effective Memory Access Time (EAT)** formula accounts for the probability that any given memory access triggers a page fault, which forces the CPU to stall while a page is fetched from disk.

## Formula

```
EAT = (1 - p) × mem_time + p × page_fault_time
```

Where:
- `p` — page fault rate (a fraction between 0 and 1 inclusive)
- `mem_time` — time for a normal memory access when no fault occurs (nanoseconds)
- `page_fault_time` — total time to handle one page fault (nanoseconds), which includes disk I/O, PTE update, and re-executing the instruction

## Why this matters

A single page fault can cost 10,000× a normal memory access. Even a fault rate of 1 in 1,000 accesses (p = 0.001) can double effective access time. This formula appears in OS design trade-off analyses and is a classic interview calculation question.

## What you will implement

Write a program that reads multiple scenarios from stdin and, for each scenario, computes EAT rounded to the nearest nanosecond. Each scenario is one line with three space-separated values: `p mem_time page_fault_time`.

- `p` is given as a floating-point number (e.g., `0.001`).
- `mem_time` and `page_fault_time` are integers in nanoseconds.
- Output one integer per line: `round(EAT)`.

See the prompt file for exact input/output specification, constraints, and sample test cases.
