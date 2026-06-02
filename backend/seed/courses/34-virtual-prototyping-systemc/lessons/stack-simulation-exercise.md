# Simulate a Stack: Push/Pop and Report Top

In this exercise you will build a software model of a downward-growing stack — exactly the kind of structure an ISS maintains when tracking the stack pointer and stack contents during firmware simulation.

## What You Will Implement

You will read a sequence of commands from standard input and simulate a fixed-size integer stack that grows **downward** (i.e., the initial "stack pointer" starts at the top of the allocated array, and each push decrements it before writing). Your program must:

1. Process `PUSH <value>` commands — decrement the stack pointer and store the value.
2. Process `POP` commands — read the value at the current stack pointer, then increment it.
3. Process `TOP` commands — report the value at the current stack pointer without changing it.
4. Detect and report `OVERFLOW` (push onto a full stack) and `UNDERFLOW` (pop or top from an empty stack).

After processing all commands, print the final stack pointer offset and any output produced by `POP`, `TOP`, `OVERFLOW`, and `UNDERFLOW` events.

## Skills Practiced

- LIFO data structure mechanics
- Downward-growing pointer arithmetic
- Boundary condition handling (overflow / underflow)
- Translating hardware stack semantics into code

## Getting Started

The stack has a fixed capacity given on the first line of input. All values are integers. Commands arrive one per line.

Open the prompt file for the full specification, constraints, and sample test cases. Implement your solution in Python reading from `stdin` and writing to `stdout`.
