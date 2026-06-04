# Exercise: LRU Page Replacement Simulator

Page replacement is a core OS/architecture concept. This exercise simulates the LRU algorithm — the gold standard replacement policy that approximates optimal behavior using the principle of temporal locality.

## Why LRU Matters

Unlike FIFO (which blindly evicts the oldest page), LRU evicts the page that has not been used for the longest time — predicting that recently used pages are more likely to be needed again.

Consider the sequence `1 2 3 4 1 2 5 1 2 3 4 5` with 4 frames:

- **FIFO**: 8 faults
- **LRU**: 8 faults (same here, but LRU is better in general)
- **OPT**: 6 faults (theoretical minimum)

LRU is significantly better than FIFO when programs exhibit strong temporal locality.

## The Belady Anomaly

An interesting quirk: with FIFO, adding more frames can sometimes cause **more** page faults. LRU does not have this anomaly — more frames always means fewer or equal faults. This property (called **stack algorithm**) makes LRU theoretically preferable.

## Implementation Note

Tracking exact LRU order is easy in software using an ordered dictionary. In hardware, exact LRU tracking for caches with many ways requires expensive comparison logic, which is why real caches use pseudo-LRU or random replacement instead.
