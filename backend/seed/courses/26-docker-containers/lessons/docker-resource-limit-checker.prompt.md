# Container Resource Limit Checker

## Problem

You are given a list of containers, each with a **memory limit (MB)** and a **CPU share weight**. Then you receive a series of resource requests. For each request, decide whether it should be **ALLOWED** or **DENIED**.

A request is **DENIED** if **either** condition is true:
- The requested memory exceeds the container's memory limit, **OR**
- The requested CPU percentage exceeds `floor((cpu_shares / total_cpu_shares_of_all_containers) * 100)`

Otherwise print **ALLOWED**.

## Input Format

```
N
name1 mem_limit_mb cpu_shares
name2 mem_limit_mb cpu_shares
...
M
container_name requested_mem_mb requested_cpu_pct
...
```

- First line: `N` — number of containers.
- Next `N` lines: container name, memory limit in MB, CPU share weight (all integers).
- Then `M` — number of requests.
- Next `M` lines: container name, requested memory in MB, requested CPU percentage (integer).

## Output Format

One line per request: `ALLOWED` or `DENIED`.

## Example

Input:
```
3
web 512 1024
db 2048 2048
cache 256 512
4
web 400 28
db 1000 57
web 600 10
cache 100 15
```

Output:
```
ALLOWED
ALLOWED
DENIED
DENIED
```

**Explanation:**
- Total shares = 1024 + 2048 + 512 = 3584
- `web` max CPU = floor(1024/3584 * 100) = floor(28.57) = **28**
- `db`  max CPU = floor(2048/3584 * 100) = floor(57.14) = **57**
- `cache` max CPU = floor(512/3584 * 100) = floor(14.28) = **14**

Request 1: web 400 MB (≤512) and 28% (≤28) → ALLOWED  
Request 2: db 1000 MB (≤2048) and 57% (≤57) → ALLOWED  
Request 3: web 600 MB (>512) → DENIED  
Request 4: cache 100 MB (≤256) but 15% (>14) → DENIED

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ M ≤ 200
- All memory values are positive integers.
- All CPU share values are positive integers.
- Container names in requests always exist in the container list.
