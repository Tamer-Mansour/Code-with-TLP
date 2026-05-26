# Amdahl's Law Calculator

Apply Amdahl's Law to compute the overall speedup when a fraction of a program is accelerated.

## Input Format

Each line of input contains two numbers:
```
f S
```

- `f` — the fraction of the program that is optimized (0 < f < 1, a float)
- `S` — the speedup factor for that fraction (S ≥ 1, a float)

Input continues until EOF. There will be between 1 and 100 lines.

## Output Format

For each input line, print the overall speedup rounded to **4 decimal places**.

```
Speedup_overall = 1 / ((1 - f) + f / S)
```

## Examples

**Input:**
```
0.4 10
0.8 20
0.5 2
```

**Output:**
```
1.5625
4.1667
1.3333
```

**Verification:**
- Line 1: f=0.4, S=10 → 1 / (0.6 + 0.04) = 1/0.64 = 1.5625
- Line 2: f=0.8, S=20 → 1 / (0.2 + 0.04) = 1/0.24 ≈ 4.1667
- Line 3: f=0.5, S=2  → 1 / (0.5 + 0.25) = 1/0.75 ≈ 1.3333
