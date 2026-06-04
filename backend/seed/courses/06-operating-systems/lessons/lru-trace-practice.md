# Practice: LRU Page Replacement — Detailed Trace

This exercise extends the basic LRU fault-counter exercise by requiring you to output a **full trace**: for each page access, whether it was a HIT or FAULT, and the current frame contents after the access.

## Background

The **Least Recently Used (LRU)** algorithm evicts the page that was accessed least recently. Unlike FIFO, LRU exploits temporal locality — pages used recently are likely to be needed again soon.

A key operation: on every HIT, update the recency order (promote the accessed page to "most recently used"). On every FAULT with a full frame set, evict the least recently used page before loading the new one.

## Input Format

```
F
p1 p2 p3 ... pN
```

- `F`: number of frames (1 ≤ F ≤ 10)
- Second line: space-separated reference string of page numbers

## Output Format

One line per page access:

```
Access <page>: <HIT|FAULT>  frames=<sorted list>
```

- HIT/FAULT is left-justified in a field of 6 characters (pad with spaces)
- The frames list is sorted numerically

Final line:

```
Total page faults: N
```

## Example

**Input:**
```
3
1 2 3 4 1 2 5 1 2 3 4 5
```

**Output:**
```
Access 1: FAULT  frames=[1]
Access 2: FAULT  frames=[1, 2]
Access 3: FAULT  frames=[1, 2, 3]
Access 4: FAULT  frames=[2, 3, 4]
Access 1: FAULT  frames=[1, 3, 4]
Access 2: FAULT  frames=[1, 2, 4]
Access 5: FAULT  frames=[1, 2, 5]
Access 1: HIT    frames=[1, 2, 5]
Access 2: HIT    frames=[1, 2, 5]
Access 3: FAULT  frames=[1, 2, 3]
Access 4: FAULT  frames=[2, 3, 4]
Access 5: FAULT  frames=[3, 4, 5]
Total page faults: 10
```

## Further Reading

- OSTEP Chapter 22 — Beyond Physical Memory: Policies: https://pages.cs.wisc.edu/~remzi/OSTEP/
- Think OS — Virtual Memory chapter: https://greenteapress.com/thinkos/
