# Resolve Delta-Cycle Update Ordering

In this exercise you will simulate the delta-cycle propagation mechanism of SystemC's evaluate-update model. Given a network of combinational logic gates and an initial set of signal values, you will determine the final stable values of all signals and the number of delta cycles required to reach quiescence.

## What You Will Implement

You will build a delta-cycle simulator that:

1. Accepts a set of signals with initial values.
2. Accepts a set of combinational gates (NOT, AND, OR), each reading input signals and writing an output signal.
3. Simulates the evaluate-update loop: in each delta, evaluate all gates whose inputs have changed, queue the new output values, then commit all updates.
4. Repeats until no signal changes (quiescence).
5. Reports the final value of each signal (alphabetical order) and the total delta count.

## Why This Matters

Understanding delta-cycle propagation is essential for:
- Predicting how many deltas a combinational chain takes to settle.
- Identifying potential infinite oscillation (combinational loops).
- Debugging unexpected values in simulation waveforms that show intermediate states.

The evaluate-update loop you implement here is exactly what the SystemC kernel does for `sc_signal<bool>` and `SC_METHOD` processes.

## Skills Practiced

- Graph-based signal propagation
- Fixed-point iteration (evaluate until quiescence)
- Deferred-write / double-buffering semantics
- Parsing structured input

## Getting Started

Your solution reads from standard input and writes to standard output. Refer to the prompt file for the exact input/output format, gate definitions, and sample cases.

Key insight: a gate should only be re-evaluated in a delta if at least one of its inputs changed in the previous update phase. This mirrors the sensitivity-list mechanism in SystemC.
