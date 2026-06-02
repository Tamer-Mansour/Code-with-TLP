# Amdahl's Law and Speedup Limits

Every program has parts that can be parallelized and parts that cannot. Amdahl's Law quantifies exactly how much overall speedup is achievable when you improve only a fraction of the execution — and the answer is often sobering.

## The Formula

Let:
- **p** = fraction of execution time that benefits from the improvement (0 ≤ p ≤ 1)
- **s** = speedup factor applied to that fraction (e.g., 4 for 4× faster)
- **Speedup** = overall improvement in execution time

```
Speedup = 1 / ((1 - p) + p/s)
```

The term `(1 - p)` is the **serial fraction** — the part of the program that cannot be improved. It is the hard floor on execution time.

## Deriving the Formula

Original time: `T`
- Serial portion: `(1 - p) × T`
- Parallelizable portion: `p × T`, improved to `(p × T) / s`

New time: `T_new = (1 - p)T + (p/s)T`

```
Speedup = T / T_new = 1 / ((1 - p) + p/s)
```

## The Brutal Limit: s → ∞

When you make the parallel fraction infinitely fast (s = ∞), the formula simplifies to:

```
Maximum Speedup = 1 / (1 - p)
```

| Serial fraction (1-p) | Max possible speedup |
|---|---|
| 50% | 2× |
| 25% | 4× |
| 10% | 10× |
| 5% | 20× |
| 1% | 100× |
| 0.1% | 1000× |

A program that is 90% parallelizable cannot exceed **10×** speedup no matter how many cores you add or how fast you make the parallel portion. This is a hard mathematical limit, not an engineering challenge.

## Worked Example

A simulation spends 70% of its time in a vectorizable inner loop (`p = 0.70`). You add AVX-512 SIMD support, achieving `s = 8×` speedup on that portion. What is the overall speedup?

```
Speedup = 1 / ((1 - 0.70) + 0.70/8)
        = 1 / (0.30 + 0.0875)
        = 1 / 0.3875
        ≈ 2.58×
```

Despite making 70% of the code 8× faster, the overall speedup is only ~2.6×. The 30% serial fraction dominates the final result.

```python
def amdahl_speedup(p: float, s: float) -> float:
    """
    p: parallel fraction (0.0 to 1.0)
    s: speedup of the parallel portion
    Returns: overall speedup
    """
    return 1.0 / ((1.0 - p) + p / s)

# Example
print(f"{amdahl_speedup(0.70, 8):.4f}")   # 2.5806
print(f"{amdahl_speedup(0.90, 16):.4f}")  # 6.4000
print(f"{amdahl_speedup(0.95, 1000):.4f}") # 19.9600 ≈ 20
```

## Gustafson's Counterpoint

Amdahl's Law assumes a **fixed problem size**. In practice, when you add more processors you often also increase the problem size — running a bigger simulation in the same time. Gustafson's Law reframes the question: "How much more work can we do in fixed time?"

```
Scaled Speedup = s + (1 - s) × (1 - p)
```

Gustafson argues that for many real workloads, parallelism pays off better than Amdahl suggests because we grow the problem. This is why modern HPC clusters are useful: they run problems that would never complete on one machine.

## Practical Implications for Systems Design

- **Find the bottleneck first.** Profiling is not optional. Optimizing a function that takes 2% of execution time is almost always wasted effort.
- **Serial code is expensive.** A 10% serial fraction caps you at 10× regardless of budget. Reducing the serial fraction from 10% to 1% is often more valuable than any hardware upgrade.
- **Law applies to all improvement types.** Amdahl's Law applies to hardware upgrades, cache size, faster disk, GPU acceleration — any localized improvement.

## Common Interview Pitfall

Candidates sometimes calculate speedup by multiplying individual speedups. If I make part A 3× faster and part B 4× faster, the total is not 12×. Each fraction must be weighted against total execution time.

> **Interview answer:** "Amdahl's Law states that overall speedup is bounded by the serial fraction of a program: Speedup = 1 / ((1-p) + p/s). Even with infinite parallelism, a 10% serial fraction caps speedup at 10×. This means profiling to find the true bottleneck is essential — optimizing anything other than the dominant cost yields diminishing returns."
