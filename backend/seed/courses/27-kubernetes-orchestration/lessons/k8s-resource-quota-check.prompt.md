# ResourceQuota Admission Check

A Kubernetes namespace has a `ResourceQuota` that limits total CPU and memory requests.

You receive:
1. Two integers on the first line: `cpu_limit` (millicores) and `mem_limit` (MiB) — the namespace quota.
2. An integer `n` — the number of pods to process.
3. `n` lines, each: `pod_name cpu_request mem_request` (cpu in millicores, mem in MiB).

Pods are evaluated in order. A pod is **ADMITTED** if adding its requests does NOT exceed either quota. A pod is **REJECTED** otherwise. Once a pod is rejected, its resources are NOT counted.

Print one line per pod: `pod_name ADMITTED` or `pod_name REJECTED`.

## Example

**Input:**
```
1000 512
4
web 300 128
api 400 200
worker 400 250
batch 100 50
```

**Output:**
```
web ADMITTED
api ADMITTED
worker REJECTED
batch ADMITTED
```

Explanation:
- After `web`: used 300m CPU, 128 MiB.
- After `api`: used 700m CPU, 328 MiB.
- `worker` would use 1100m CPU > 1000m limit → REJECTED.
- `batch` uses 100m CPU → total 800m CPU, 378 MiB → ADMITTED.
