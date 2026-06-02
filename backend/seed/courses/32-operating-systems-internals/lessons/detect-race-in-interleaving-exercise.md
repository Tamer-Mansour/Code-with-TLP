# Exercise: Detect a Lost Update From an Interleaving Trace

In this exercise you will analyze a **thread interleaving trace** — a step-by-step log of two threads executing a shared-memory increment — and determine the final value of the shared variable and whether a lost update occurred.

## What You Will Practice

- Reading a concurrent execution trace and tracking register and memory state.
- Identifying the exact interleaving step where the race condition produces a stale read.
- Predicting the final in-memory value of a counter after a lossy concurrent execution.

## Problem Statement

Two threads, **Thread A** and **Thread B**, each execute a simple increment on a shared integer `counter` (initially `0`). The increment is implemented as three micro-steps:

- `LOAD r` — copy `counter` from memory into the thread's private register `r`.
- `ADD r` — compute `r = r + 1`.
- `STORE r` — write `r` back to `counter` in memory.

You are given a trace of numbered steps showing which thread performed which micro-step and in what order. Your program must determine:

1. The **final value** of `counter` after all steps complete.
2. Whether a **lost update** occurred (`YES` or `NO`).

A lost update occurs when the final value of `counter` is less than the number of completed (LOAD, ADD, STORE) increment triples.

## Input / Output

See the companion prompt file `os-detect-race-in-interleaving-exercise.prompt.md` for the exact input/output specification, constraints, and sample test cases.

## Approach

Work through the trace sequentially, maintaining:

- A memory cell for `counter`.
- A private register for Thread A (`rA`) and Thread B (`rB`).

Apply each step to update the appropriate register or memory location. At the end, compare `counter` against the expected value (number of full increment triples) to detect a lost update.
