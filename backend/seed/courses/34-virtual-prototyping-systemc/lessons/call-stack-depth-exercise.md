# Compute Maximum Call-Stack Depth from a Trace

In firmware bring-up and virtual prototyping, one of the most useful metrics you can extract from an execution trace is the **maximum call-stack depth**: the deepest nesting level reached during the run. This metric drives stack-size allocation decisions — size the stack too small and the firmware crashes; size it too large and you waste precious on-chip SRAM.

## What You Will Implement

You will parse a simplified execution trace where each line is either a function call (`CALL <name>`) or a function return (`RETURN`). Your program must:

1. Track the current call-stack depth as calls and returns are processed.
2. Record the maximum depth reached at any point during execution.
3. Output the maximum depth and the name of the function that was on top of the stack when that maximum was first reached.
4. Report an error if a `RETURN` is encountered with an empty stack.

This mirrors exactly what a SystemC VP profiler does: it intercepts branch-and-link / return instructions from the ISS, updates a software call-stack model, and records high-water-mark depth.

## Skills Practiced

- Call-stack modeling with a Python list
- High-water-mark tracking
- Trace parsing and event-driven simulation
- Error condition detection in execution traces

## Getting Started

Input arrives on stdin. Each line contains a single command. There are no recursive calls in the trace (each function name appears at most once at any time in the stack). Implement your solution in Python using only the standard library.

Open the prompt file for the full input/output specification, constraints, and sample test cases.
