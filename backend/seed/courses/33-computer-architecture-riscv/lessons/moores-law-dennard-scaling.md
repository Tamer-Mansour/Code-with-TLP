# Moore's Law, Dennard Scaling, and the Power Wall

Three decades of exponential progress in computing rested on two self-reinforcing trends: Moore's Law and Dennard Scaling. When one of them broke, it triggered the most significant architectural shift since the invention of the microprocessor.

## Moore's Law

In 1965, Gordon Moore observed that the number of transistors on an integrated circuit was doubling roughly every two years (later revised to 18 months for practical purposes). This was not a law of physics — it was an industry observation and commitment.

| Year | Process Node | Transistors (Intel CPU) |
|---|---|---|
| 1971 | 10 µm | 2,300 (Intel 4004) |
| 1989 | 1 µm | 1,000,000 (Intel 486) |
| 2000 | 180 nm | 42,000,000 (Pentium 4) |
| 2012 | 22 nm | 1,400,000,000 (Ivy Bridge) |
| 2023 | 3 nm | ~20,000,000,000 (Apple M2) |

More transistors enabled larger caches, more cores, wider SIMD units, and deeper out-of-order windows — all architectural improvements.

## Dennard Scaling

Dennard Scaling (Robert Dennard, 1974) provided the economic engine behind Moore's Law. It stated: **as transistors shrink, their power density stays constant**. Specifically:

- Transistor area scales by **1/k²** (k = scaling factor per generation, typically √2).
- Voltage and current both scale by **1/k**.
- Switching speed improves by **k** (can raise clock frequency).
- Power per transistor scales by **1/k²**.

Since you fit k² more transistors in the same area, and each uses 1/k² less power, **total power stays constant** while you get k² more transistors running k times faster. This allowed clock frequencies to double alongside transistor counts.

```
Generation N:   transistors = T,  freq = f,  power = P
Generation N+1: transistors = 2T, freq = kf, power ≈ P
```

Free performance. Every two years, the same chip area could do more work at the same power budget.

## The End of Dennard Scaling (~2005)

Dennard Scaling requires voltage to fall proportionally with feature size. Below ~1 V, **leakage current** — transistors that leak charge even when switched off — became dominant. Reducing voltage further caused transistors to fail to switch reliably.

The result: voltage stopped scaling. Power density began increasing with each new process node. Clock frequencies plateaued:

- 2001: Intel Pentium 4 at 2.0 GHz
- 2004: Intel Pentium 4 at 3.8 GHz (peak)
- 2006: Core 2 Duo at 3.0 GHz (two cores, lower frequency each)
- 2024: Intel Core Ultra 9 at 5.7 GHz (single-core boost, but with 24 cores)

Pushing clock frequency higher now requires exponentially more power — the **power wall**.

## The Power Wall

Power in a CMOS circuit is approximately:

```
P = α × C × V² × f
```

Where:
- `α` = activity factor (fraction of transistors switching per cycle)
- `C` = total capacitance
- `V` = supply voltage
- `f` = clock frequency

Since `V` stopped falling, every 10% increase in `f` now costs ~21% more power (P ∝ V² × f, and higher f also requires slightly higher V for timing closure). A 3 GHz chip might consume 65 W; pushing it to 6 GHz without microarchitectural changes would consume ~260 W — far beyond practical cooling limits.

## Architectural Responses

The industry responded to the power wall with architectural innovation rather than raw frequency scaling:

- **Multi-core processors** — divide the power budget across many simpler cores, exploit task-level parallelism.
- **Heterogeneous architectures** — big.LITTLE (ARM), Efficiency + Performance cores (Intel). Assign each workload to the most efficient core type.
- **Domain-specific accelerators** — GPUs for graphics/ML, TPUs for tensor operations, NPUs for inference. These achieve high throughput per watt for narrow workloads.
- **Dark silicon** — at any moment, only a fraction of chip transistors are active to stay within the thermal envelope.
- **Approximate computing** — trading exact correctness for energy savings in domains like image processing and ML inference.

## Is Moore's Law Dead?

Moore's Law as a cost-per-transistor predictor has slowed significantly — from 2-year doubling to 3–4 years for leading-edge nodes. But density continues to improve through 3D stacking (High-Bandwidth Memory, TSMC CoWoS, Intel Foveros), even as 2D planar scaling faces physical limits from atomic-scale feature sizes.

> **Interview answer:** "Moore's Law described exponential transistor density growth. Dennard Scaling made this free in power, enabling frequency scaling. Around 2005, Dennard Scaling broke down because leakage current prevented further voltage reduction. The result was the power wall — further frequency increases are thermally infeasible. The industry responded with multi-core designs, heterogeneous architectures, and domain-specific accelerators rather than faster clocks."
