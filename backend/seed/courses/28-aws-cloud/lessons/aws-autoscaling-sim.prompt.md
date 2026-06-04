# Auto Scaling Policy Simulator

Simulate a simplified EC2 Auto Scaling Group with **target tracking** based on CPU utilization.

## Scaling Rules

Given: `min_capacity`, `max_capacity`, `desired_capacity`, and `target_cpu_percent`.

For each hourly CPU reading:

- **Scale OUT** (if `cpu > target`): new desired = `ceil(current * (cpu / target))`, clamped to `max_capacity`.
- **Scale IN** (if `cpu < target * 0.9`): new desired = `floor(current * (cpu / target))`, clamped to `min_capacity`.
- **No change** (if `target * 0.9 <= cpu <= target`): desired stays the same.

Print the desired capacity **after processing each reading**.

## Input Format

- Line 1: four space-separated values — `min_capacity max_capacity desired_capacity target_cpu_percent`
- Line 2: integer `N` — number of CPU readings
- Lines 3 to N+2: one CPU reading per line (float, 0–100)

## Output Format

`N` lines, one integer per line — the desired capacity after each reading.

## Example

```
Input:
2 10 3 60.0
5
45.0
75.0
90.0
30.0
20.0

Output:
2
3
5
2
2
```

Trace:
- cpu=45.0: 45 < 60×0.9=54 → scale in: floor(3 × 45/60) = floor(2.25) = 2, clamp to min=2 → **2**
- cpu=75.0: 75 > 60 → scale out: ceil(2 × 75/60) = ceil(2.5) = 3, clamp to max=10 → **3**
- cpu=90.0: 90 > 60 → scale out: ceil(3 × 90/60) = ceil(4.5) = 5 → **5**
- cpu=30.0: 30 < 54 → scale in: floor(5 × 30/60) = floor(2.5) = 2 → **2**
- cpu=20.0: 20 < 54 → scale in: floor(2 × 20/60) = floor(0.666) = 0, clamp to min=2 → **2**

## Constraints

- 1 ≤ min_capacity ≤ max_capacity ≤ 100
- 1 ≤ desired_capacity ≤ max_capacity
- 1 ≤ target_cpu_percent ≤ 100
- 1 ≤ N ≤ 100
- 0.0 ≤ cpu_reading ≤ 100.0
