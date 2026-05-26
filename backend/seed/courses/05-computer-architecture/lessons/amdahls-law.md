# Amdahl's Law and Performance Analysis

Amdahl's Law is a foundational formula for understanding the limits of optimization and parallelism. It provides a rigorous answer to: "how much faster will my system be if I speed up part X?"

## The Formula

```
Speedup_overall = 1 / ((1 - f) + f / S)
```

Where:
- `f` = the fraction of **original** execution time spent in the part being improved (0 ≤ f ≤ 1)
- `S` = the speedup factor applied to that part (S > 1)
- `(1 - f)` = the fraction that is **not** improved (the serial bottleneck)

## Intuition

If only 50% of a program can be parallelized/optimized, the other 50% must still run at original speed. No matter how fast you make the 50%, the total speedup ceiling is:

```
Max speedup = 1 / (1 - 0.5) = 2×
```

This is the **serial bottleneck** — the irreducible minimum execution time.

## Worked Examples

### Example 1: Hardware Accelerator

A graphics kernel takes 80% of rendering time. You add a GPU that runs it 20× faster.

```
f = 0.80, S = 20
Speedup = 1 / (0.20 + 0.80/20)
        = 1 / (0.20 + 0.04)
        = 1 / 0.24
        ≈ 4.17×
```

Despite a 20× kernel speedup, the overall system only becomes ~4× faster.

### Example 2: Parallel Cores

A workload has a 90% parallel fraction. How does scaling cores help?

```
f = 0.90

N=2  cores: S=2  → 1 / (0.10 + 0.90/2)  = 1/0.55 ≈ 1.82×
N=4  cores: S=4  → 1 / (0.10 + 0.90/4)  = 1/0.325 ≈ 3.08×
N=10 cores: S=10 → 1 / (0.10 + 0.90/10) = 1/0.19 ≈ 5.26×
N=∞  cores: S=∞  → 1 / 0.10 = 10× ceiling
```

Doubling cores does not double performance once the serial fraction dominates.

## Strong vs Weak Scaling

- **Strong scaling** (Amdahl): fixed total problem size, add more processors. Serial fraction limits speedup.
- **Weak scaling** (Gustafson's Law): increase problem size with processors — often the realistic scenario for HPC. Serial fraction matters less because useful work grows with N.

## Applying Amdahl's Law to CPU Design

The same principle applies to microarchitecture:

| Optimization | f | S | Overall gain |
|---|---|---|---|
| FP unit 4× faster | 0.10 (FP fraction) | 4 | 1/(0.9 + 0.025) ≈ 1.08× |
| Memory latency halved | 0.40 | 2 | 1/(0.6 + 0.2) = 1.25× |
| Branch predictor 0 penalty | 0.15 | ∞ | 1/(0.85) ≈ 1.18× |

This shows why memory latency reduction has a bigger impact than FP throughput for general-purpose workloads.

## The Roofline Model (Extension)

For compute-intensive workloads, the **Roofline Model** combines Amdahl-style thinking with memory bandwidth:

```
Attainable performance = min(Peak FLOP/s, Bandwidth × Arithmetic Intensity)

Arithmetic Intensity = FLOPs performed / Bytes transferred from memory
```

A program below the "roofline" is memory-bandwidth bound; above it is compute-bound. This guides where to invest optimization effort.

## Key Takeaways

1. Profile first — optimize the actual bottleneck, not what seems slow.
2. The serial fraction sets a hard ceiling on parallel speedup.
3. Amdahl's Law applies to CPUs, multi-core systems, distributed clusters, and software optimizations alike.
4. Gustafson's Law is more optimistic for problems that scale with resources.
