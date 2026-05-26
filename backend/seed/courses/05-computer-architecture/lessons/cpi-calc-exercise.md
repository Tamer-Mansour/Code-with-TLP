# Exercise: CPU Time Calculator

This exercise reinforces the fundamental CPU performance equation. Given instruction count, CPI, and clock frequency, compute execution time in nanoseconds.

## Background

The CPU performance equation is:

```
CPU Time = Instruction Count × CPI × Clock Period
         = IC × CPI × (1 / clock_frequency)
```

Breaking down the three factors:
- **Instruction Count (IC)**: how many instructions the program executes. Reduced by better algorithms, compilers, and ISA design.
- **CPI (Cycles Per Instruction)**: average number of clock cycles each instruction takes. Reduced by pipelining, caches, forwarding, out-of-order execution.
- **Clock Period (1/freq)**: how long one cycle takes. Reduced by faster transistor technology and circuit design.

This equation is the foundation of all CPU performance analysis. Any optimization must reduce at least one of these three quantities.

## Examples

Given `IC=1000, CPI=2.0, freq=2.0 GHz`:
```
Clock period = 1/2.0 = 0.5 ns
CPU time = 1000 × 2.0 × 0.5 = 1000.0 ns
```

Given `IC=500, CPI=1.5, freq=3.0 GHz`:
```
Clock period = 1/3.0 ≈ 0.3333 ns
CPU time = 500 × 1.5 × 0.3333 = 250.0 ns
```

## Task

Process multiple test cases (one per line) until EOF. For each, print the CPU time in nanoseconds rounded to 4 decimal places.
