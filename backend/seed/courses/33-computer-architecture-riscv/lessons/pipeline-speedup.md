# Computing Pipeline Speedup

The pipeline speedup formula is one of the most commonly tested topics in architecture interviews and exams. This lesson walks through the derivation, the ideal case, and the realistic case with stalls.

## Notation

| Symbol | Meaning |
|--------|---------|
| k | Number of pipeline stages |
| N | Number of instructions in the program |
| t_s | Time per stage (assumed equal) |
| CPI_stall | Average extra cycles per instruction due to stalls |
| T_seq | Total time, sequential (non-pipelined) |
| T_pipe | Total time, pipelined |

## Derivation: Sequential Execution

Without pipelining, each instruction takes k stages × t_s seconds:

```
T_seq = N × k × t_s
```

## Derivation: Ideal Pipelined Execution

The pipeline takes k cycles to fill (the "ramp-up" cost). After that, one instruction completes every cycle. For N instructions:

```
T_pipe = (k + N - 1) × t_s
```

The `k - 1` accounts for filling the pipeline before the first result appears.

## Ideal Speedup Formula

```
Speedup = T_seq / T_pipe
         = (N × k × t_s) / ((k + N - 1) × t_s)
         = (N × k) / (N + k - 1)
```

As N → ∞ (large programs dominate), the speedup approaches k:

```
lim(N→∞) Speedup = k
```

This is why k-stage pipeline is often said to give a "k-fold speedup" — true only for very large N.

## Realistic Speedup with Stalls

Real pipelines stall. Let `s` be the average number of stall cycles per instruction. The CPI becomes:

```
CPI = 1 + s
```

Pipelined execution time:

```
T_pipe_real = N × (1 + s) × t_s  +  (k - 1) × t_s
            ≈ N × (1 + s) × t_s   (for large N)
```

Realistic speedup (for large N):

```
Speedup_real = (N × k × t_s) / (N × (1 + s) × t_s)
             = k / (1 + s)
```

## Worked Examples

### Example 1: Ideal Case

A 5-stage pipeline, 1 ns per stage, running 1000 instructions.

```python
k = 5
N = 1000
t_s = 1  # ns

T_seq  = N * k * t_s         # = 5000 ns
T_pipe = (k + N - 1) * t_s   # = 1004 ns

speedup = T_seq / T_pipe      # = 5000 / 1004 ≈ 4.98x
```

Very close to the theoretical maximum of 5x.

### Example 2: With Stalls

Same 5-stage pipeline, but 20% of instructions cause a 1-cycle stall (e.g., load-use hazards), and 10% of branches cause a 2-cycle penalty.

```python
k = 5
N = 1000
t_s = 1  # ns

s = 0.20 * 1 + 0.10 * 2   # = 0.20 + 0.20 = 0.40 stall cycles/inst
CPI = 1 + s                 # = 1.40

T_seq  = N * k * t_s        # = 5000 ns
T_pipe = N * CPI * t_s      # ≈ 1400 ns  (large N, ignore fill cost)

speedup = 5000 / 1400       # ≈ 3.57x
```

Stalls reduced the speedup from nearly 5x to 3.57x.

### Example 3: Amdahl's Law Connection

Suppose only 80% of the program is pipelinable; the other 20% runs sequentially (e.g., due to system calls):

```python
f_pipeline = 0.80
speedup_pipeline = 5  # ideal k-fold

# Amdahl's Law:
speedup_total = 1 / ((1 - f_pipeline) + f_pipeline / speedup_pipeline)
             # = 1 / (0.20 + 0.16) = 1 / 0.36 ≈ 2.78x
```

Even with a perfect 5-stage pipeline, the 20% sequential portion limits total speedup to 2.78x.

## Summary of Formulas

```
Ideal speedup (large N):         k
Ideal time:                       (N + k - 1) × t_s
Realistic CPI:                    1 + s
Realistic speedup (large N):      k / (1 + s)
```

## Common Mistakes to Avoid

- Forgetting the fill cost `(k - 1)` for small N
- Using CPI = 1 when stalls are present
- Conflating "k-fold speedup" with actual speedup for realistic N and stall rates
- Ignoring that faster clock frequency in a deeper pipeline partially offsets stall penalties

> **Interview answer:** An ideal k-stage pipeline gives a k-fold speedup over sequential execution as N grows large; with stall cycles at rate s per instruction, the realistic speedup is k / (1 + s), showing that hazard avoidance directly multiplies throughput.
