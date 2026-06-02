# Compute Sync Points from a Time Quantum

In this exercise you will implement the logic that a TLM quantum keeper uses to determine when an initiator thread must synchronize with the global simulation time.

## Background

An initiator using temporal decoupling accumulates transaction delays in a local time variable. After each transaction, it checks whether the local time has exceeded the configured **time quantum**. If so, it synchronizes (resets the local time and advances the global clock).

Your task is to simulate this process: given a sequence of transaction delays and a quantum value, output the global time after each synchronization point and the total number of synchronizations required.

## What You Will Implement

Given:
- A quantum period `Q` (in nanoseconds)
- A list of per-transaction annotated delays (in nanoseconds)

Process each transaction in order:
1. Add the delay to the running local time.
2. If `local_time >= Q`, a synchronization occurs:
   - Global time advances by `local_time`.
   - Record the new global time as a sync point.
   - Reset local time to 0.
3. After all transactions, if `local_time > 0`, perform a final sync.

Output each sync point's global time (one per line), then print the total number of synchronizations.

## Example

```
Input:
  Q = 1000
  delays = [300, 300, 300, 300, 200, 600, 400]

Processing:
  tx1: local=300  (no sync)
  tx2: local=600  (no sync)
  tx3: local=900  (no sync)
  tx4: local=1200 >= 1000 → sync! global=1200, local=0
  tx5: local=200  (no sync)
  tx6: local=800  (no sync)
  tx7: local=1200 >= 1000 → sync! global=2400, local=0
  End: local=0    (no final sync)

Output:
  1200
  2400
  Total syncs: 2
```

This exercise builds the intuition for how quantum selection affects simulation speed — fewer syncs means faster simulation.
