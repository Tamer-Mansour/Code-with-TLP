# Exercise: Amdahl's Law Calculator

Apply Amdahl's Law programmatically to measure the maximum achievable speedup given a parallelizable fraction and speedup factor.

## Background

Amdahl's Law states:

```
Speedup_overall = 1 / ((1 - f) + f / S)
```

Where `f` is the fraction of the workload being improved and `S` is how much faster that fraction runs. The remaining `(1 - f)` fraction is the serial bottleneck.

## Your Task

For each line of input containing `f` and `S`, compute and print the overall speedup rounded to 4 decimal places.

See the exercise panel for the full specification and examples.
