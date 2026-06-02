# Parse an Instruction Trace to Find a Hang Loop

In this exercise you will analyze a simplified instruction trace — a sequence of `(instruction_count, PC)` pairs — and identify the tightest spin loop: the smallest set of unique program-counter addresses that repeats continuously, indicating the CPU is stuck.

## What You Will Implement

You will write a program that reads an instruction trace from standard input and prints the **start instruction count**, the **loop length** (number of unique PCs in the repeating block), and the **PC addresses** in the loop — in the order they first appear.

A spin loop is defined as a consecutive run of at least **2 distinct PC values** that repeats at least **3 times in a row**. You must find the first such repeating block that has the **maximum run count** among all candidates. If there are ties in run count, prefer the one that appears earliest in the trace (lowest start instruction count).

This mirrors the real-world technique of extracting the PC column and looking for the dominant repeating pattern to identify where a virtual prototype is stuck.

## Skills Practiced

- Parsing structured text (trace format)
- Sliding-window pattern detection
- Correlating instruction counts with loop boundaries

## Input Format

See the companion prompt file `vp-instruction-trace-parse-exercise.prompt.md` for the exact specification, constraints, and sample cases.

## Getting Started

Your solution should read from `stdin` and print to `stdout`. No file I/O or third-party libraries are allowed. The solution must work within the time and memory limits stated in the prompt file.

Think about the algorithm before coding: for each possible loop length L (from 2 upward), scan the trace to find consecutive runs where the PC sequence repeats. Track the run with the highest consecutive repeat count.
