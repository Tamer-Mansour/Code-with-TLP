# Modeling Average Memory Access Time

The **Average Memory Access Time (AMAT)** is the single most important formula for quantifying memory hierarchy performance. It allows you to predict how fast a program will run given cache parameters, and to diagnose where most cycles are being lost.

## The AMAT Formula

For a two-level hierarchy (one cache + main memory):

```
AMAT = Hit Time_L1 + Miss Rate_L1 × Miss Penalty_L1
```

Where:
- **Hit Time_L1**: cycles to access L1 cache (always paid, whether hit or miss)
- **Miss Rate_L1**: fraction of accesses that miss L1
- **Miss Penalty_L1**: additional cycles paid when a miss occurs (time to fetch from next level)

## Extending to Multiple Levels

For a three-level hierarchy (L1, L2, L3, main memory):

```
AMAT = HT_L1 + MR_L1 × (HT_L2 + MR_L2 × (HT_L3 + MR_L3 × MR_DRAM_penalty))
```

Or equivalently using **local miss rates** at each level:

```
AMAT = HT_L1
     + MR_L1 × HT_L2
     + MR_L1 × MR_L2 × HT_L3
     + MR_L1 × MR_L2 × MR_L3 × DRAM_latency
```

Note: `MR_L2` here is the **local miss rate** — the fraction of requests that reach L2 and miss L2 (not the fraction of all requests that miss L2).

## Worked Example 1: Two-Level Hierarchy

Given:
- L1 hit time: 2 cycles
- L1 miss rate: 8%
- DRAM latency: 100 cycles

```
AMAT = 2 + 0.08 × 100
     = 2 + 8
     = 10 cycles
```

Adding an L2 cache:
- L2 hit time: 10 cycles
- L2 local miss rate: 40%

```
AMAT = 2 + 0.08 × (10 + 0.40 × 100)
     = 2 + 0.08 × (10 + 40)
     = 2 + 0.08 × 50
     = 2 + 4
     = 6 cycles
```

The L2 cache reduces AMAT from 10 to 6 cycles — a 40% improvement.

## Worked Example 2: Real Parameters

Suppose a server-class processor has:

| Level | Hit Time | Local Miss Rate |
|-------|---------|----------------|
| L1 | 4 cycles | 5% |
| L2 | 12 cycles | 30% |
| L3 | 45 cycles | 20% |
| DRAM | 250 cycles | — |

```
AMAT = 4
     + 0.05 × 12
     + 0.05 × 0.30 × 45
     + 0.05 × 0.30 × 0.20 × 250

     = 4
     + 0.6
     + 0.675
     + 0.75

     = 6.025 cycles
```

The DRAM term contributes only 0.75 cycles on average despite a 250-cycle penalty, because the probability of reaching DRAM is 0.05 × 0.30 × 0.20 = 0.3%.

## Global vs Local Miss Rate

These terms are frequently confused:

- **Local miss rate** = (misses at level L) / (accesses that reach level L)
- **Global miss rate** = (misses at level L) / (total CPU memory accesses)

For the example above:
- L2 local miss rate = 30% (30% of requests that reach L2 miss L2)
- L2 global miss rate = 5% × 30% = 1.5% (only 1.5% of all CPU requests miss both L1 and L2)

The AMAT formula uses **local** miss rates when written in the nested form shown above.

## Sensitivity Analysis

Which parameter should you optimize? Take the partial derivative:

```
ΔAMAT ≈ ΔHT_L1                    (changing L1 hit time affects every access)
       + MR_L1 × Δ(Miss Penalty)  (changing miss penalty affects only misses)
```

Because the L1 hit time is paid on every access, even a 1-cycle improvement in L1 latency (e.g., by reducing L1 size) can be more valuable than a large reduction in miss penalty.

## Python Calculation

```python
def amat(hit_time, miss_rate, miss_penalty):
    return hit_time + miss_rate * miss_penalty

# Two-level with L2
l2 = amat(hit_time=10, miss_rate=0.40, miss_penalty=100)  # L2's effective penalty
result = amat(hit_time=2, miss_rate=0.08, miss_penalty=l2)
print(f"AMAT = {result} cycles")  # 6.0 cycles
```

## Common Pitfalls

- **Using global miss rate in the nested formula**: This double-counts. Use local miss rates in the nested form, or global miss rates in the flat sum form.
- **Ignoring write misses**: Write-allocate caches fetch the missing block on a write miss; write-no-allocate caches do not. AMAT models typically count only read misses unless specified otherwise.
- **Treating miss penalty as constant**: In real hardware, miss penalty varies with DRAM bank state, DRAM row buffer hits, and memory bus congestion.

> **Interview answer:** AMAT = Hit Time + Miss Rate × Miss Penalty; for multiple levels the formula nests so each level's miss penalty includes the AMAT of the next level down, weighted by the probability of reaching it.
