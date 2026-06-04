# HPA Scaling Decision Engine

Implement the core Horizontal Pod Autoscaler (HPA) algorithm.

## Formula

```
desiredReplicas = ceil(currentReplicas * (currentMetricValue / desiredMetricValue))
```

Clamp the result: `max(1, min(maxReplicas, desiredReplicas))`.

## Cooldowns

- **Scale-up cooldown:** 180 seconds. A scale-up is only applied if `timestamp - lastScaleTime >= 180`.
- **Scale-down cooldown:** 300 seconds. A scale-down is only applied if `timestamp - lastScaleTime >= 300`.
- At time 0 there is no cooldown restriction (assume `lastScaleTime = -999999`).

If the desired replica count equals the current count, no scaling event occurs (cooldown timer is not reset).

## Input

```
Line 1: initial_replicas max_replicas desired_metric_value
Line 2: N (number of observations, 1 <= N <= 20)
Next N lines: timestamp_seconds current_metric_value
```

Constraints: `1 <= initial_replicas <= 10`, `1 <= max_replicas <= 50`, `desired_metric_value > 0`, timestamps are non-decreasing.

## Output

N lines: `timestamp replica_count`

Print the replica count **after** the HPA evaluates (and potentially scales) at that timestamp.

## Examples

Input:
```
2 10 50.0
6
0 50.0
15 80.0
30 90.0
45 40.0
315 20.0
600 50.0
```

Output:
```
0 2
15 4
30 4
45 4
315 2
600 2
```

Explanation:
- t=0: desired=ceil(2*50/50)=2. No change (equal).
- t=15: desired=ceil(2*80/50)=4. Scale up. 15-(-999999)>=180. lastScaleTime=15.
- t=30: desired=ceil(4*90/50)=8. Scale up wanted, but 30-15=15 < 180. Blocked.
- t=45: desired=ceil(4*40/50)=4. Scale down wanted, but 45-15=30 < 300. Blocked.
- t=315: desired=ceil(4*20/50)=2. Scale down. 315-15=300 >= 300. lastScaleTime=315.
- t=600: desired=ceil(2*50/50)=2. No change (equal).

Input:
```
3 8 100.0
4
0 100.0
15 200.0
200 50.0
520 50.0
```

Output:
```
0 3
15 6
200 6
520 3
```

Explanation:
- t=0: desired=ceil(3*100/100)=3. No change.
- t=15: desired=ceil(3*200/100)=6. Scale up. lastScaleTime=15.
- t=200: desired=ceil(6*50/100)=3. Scale down wanted, 200-15=185 < 300. Blocked.
- t=520: desired=ceil(6*50/100)=3. Scale down. 520-15=505 >= 300. lastScaleTime=520.

## Notes

- When the computed desired equals current, no scaling event occurs (cooldown is not updated).
- The minimum replicas is always 1.
- `ceil` rounds up: `ceil(2.1) = 3`, `ceil(3.0) = 3`.
