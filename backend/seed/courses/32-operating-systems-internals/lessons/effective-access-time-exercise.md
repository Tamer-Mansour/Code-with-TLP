# Exercise: Compute Effective Access Time From Hit Ratios

In this exercise you will implement a program that computes Effective Memory Access Time (EMAT) for a TLB-based memory system given configurable parameters.

## What You Will Implement

Write a program that reads a series of scenarios from standard input. Each scenario provides:

- The TLB hit ratio
- The memory access time (in nanoseconds)
- The number of page-table levels (k)

For each scenario, output the EMAT rounded to **two decimal places**, using the simplified formula:

```
EMAT = h * t_mem + (1 - h) * (k + 1) * t_mem
```

This is the standard textbook formula that treats the TLB lookup time as negligible and counts the walk as k additional full memory accesses.

## Input / Output

See the prompt file for exact format, constraints, and sample cases.
