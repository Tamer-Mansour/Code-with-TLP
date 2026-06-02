# Frame Allocation: Global vs Local, Fixed vs Proportional

Choosing a page replacement algorithm is only half the problem. The OS must also decide **how many frames to give each process** — the frame allocation policy. Poor allocation leads to thrashing; overly generous allocation wastes RAM.

## The Two Dimensions of Frame Allocation

Frame allocation policies vary along two axes:

1. **Scope**: Global vs. Local replacement
2. **Quota**: Fixed vs. Proportional allocation

## Global vs. Local Replacement

### Local Replacement

Each process can only evict pages from its **own** allocated frames. A process's page fault rate cannot be alleviated by taking frames from another process.

- **Pro**: Predictable behavior per process; one process cannot hurt another.
- **Con**: A process with a large working set may thrash even if other processes have idle frames.

### Global Replacement

Any process's fault handler can evict any page in the system, regardless of which process owns it.

- **Pro**: Better overall throughput; idle processes donate their frames to active ones automatically.
- **Con**: A single greedy process can starve others; behavior is harder to predict.

**Most general-purpose OSes (Linux, Windows) use global replacement** because it yields better overall performance.

## Fixed vs. Proportional Allocation

### Equal (Fixed) Allocation

Split the `f` available frames evenly: each of `n` processes gets `f / n` frames (integer division, with the remainder going to the OS or a free pool).

```
Total frames: 64
Processes:     4
Each process:  16 frames
```

Simple but ignores process size — a 4 MB process and a 400 MB process get the same quota.

### Proportional Allocation

Allocate frames in proportion to each process's virtual memory size (or working set size):

```
a_i = (s_i / S) * f
```

Where `s_i` is the size of process `i`, `S = Σ s_i`, and `f` is total frames.

```
Process A: size = 10 pages
Process B: size = 30 pages
Total frames: 40

a_A = (10/40) * 40 = 10 frames
a_B = (30/40) * 40 = 30 frames
```

### Priority-Based Allocation

Give higher-priority processes more frames, even if they are smaller. A real-time task should fault less than a background batch job.

```
a_i proportional to priority_i rather than size_i
```

## Thrashing

If a process is allocated fewer frames than its **working set** (the set of pages actively in use), it will continuously fault — the OS spends more time paging than executing user code. This is called **thrashing**.

### Working Set Model

Track the set of pages referenced in the last `Δ` (window) accesses. The working set size `|W(t, Δ)|` estimates how many frames the process needs right now.

```
Reference string: 1 2 3 4 2 1 5 6 2 3 ...
Window Δ = 5
At position 7 (after ref 5):
  Working set = {1, 2, 3, 4, 5}  → need 5 frames
```

### Page Fault Frequency (PFF) Control

Monitor the page fault rate for each process:

- **Rate too high** (above upper threshold): give the process more frames.
- **Rate too low** (below lower threshold): reclaim a frame from the process.

```
Upper threshold: 0.5 faults/sec → add a frame
Lower threshold: 0.1 faults/sec → remove a frame
```

PFF is a reactive, feedback-driven approach — simpler to implement than the full working set model.

## Summary Table

| Strategy | Basis | Pros | Cons |
|---|---|---|---|
| Equal fixed | Equal split | Simple | Ignores size/priority |
| Proportional | Process size | Fair | Static; ignores locality |
| Priority-based | Process priority | Important tasks fare better | May starve low-priority |
| Working set | Recent access window | Tracks actual need | Complex to implement |
| PFF control | Observed fault rate | Adaptive | Reactive lag |

> **Interview answer:** Frame allocation determines how many physical frames each process receives. Global replacement pools all frames across processes for better utilization, while local replacement gives each process a fixed quota for predictability. Proportional allocation is fairer than equal allocation, but the working set model or page-fault-frequency control are needed to prevent thrashing.
