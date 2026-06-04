# Exercise: Amdahl's Law Speedup Calculator

This exercise extends your understanding of Amdahl's Law by computing both the actual speedup for a finite number of processors AND the theoretical maximum speedup as processors approach infinity.

## The Serial Bottleneck

Amdahl's Law reveals an uncomfortable truth: even a small serial fraction severely limits achievable speedup. Consider these examples:

| Serial Fraction | Max Possible Speedup |
|-----------------|---------------------|
| 50% (P=0.5)     | 2×                  |
| 10% (P=0.9)     | 10×                 |
| 5%  (P=0.95)    | 20×                 |
| 1%  (P=0.99)    | 100×                |
| 0.1% (P=0.999)  | 1000×               |

This is why modern parallel computing research focuses heavily on **reducing serial fractions** rather than simply adding more cores.

## Gustafson's Law (Counterpoint)

Amdahl's Law assumes a **fixed problem size**. Gustafson observed that in practice, more processors are used to solve **larger problems** in the same time. Gustafson's Law:

```
Speedup = N - alpha × (N - 1)
```

where alpha is the serial fraction. This gives a more optimistic view — relevant for scientific computing where problem size scales with available hardware.

## This Exercise

Handle multiple test cases, computing Speedup and Max Speedup for each (P, N) pair, and handle the special case P=1.0 where the maximum speedup is infinite.
