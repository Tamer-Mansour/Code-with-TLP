# Docker Network Reachability Simulator

## Problem

You are given a set of containers and the Docker networks each container belongs to. Answer reachability queries: can container A reach container B?

**Rule**: Two containers are reachable from each other if and only if they **share at least one network** in common.

The `default` network is treated exactly like any other named network.

## Input Format

```
N
container_name network1 network2 ...
...
Q
container_a container_b
...
```

- First line: `N` — number of containers.
- Next `N` lines: container name followed by one or more network names (space-separated).
- Then `Q` — number of queries.
- Next `Q` lines: two container names per query.

## Output Format

One line per query: `YES` if the containers share at least one network, `NO` otherwise.

## Example

Input:
```
4
web frontend default
api frontend backend
db backend
logs monitoring
5
web api
api db
web db
db logs
web logs
```

Output:
```
YES
YES
NO
NO
NO
```

**Explanation:**
- `web` ↔ `api`: share `frontend` → YES
- `api` ↔ `db`: share `backend` → YES
- `web` ↔ `db`: web={frontend,default}, db={backend} — no overlap → NO
- `db` ↔ `logs`: db={backend}, logs={monitoring} — no overlap → NO
- `web` ↔ `logs`: web={frontend,default}, logs={monitoring} — no overlap → NO

## Example 2

Input:
```
3
proxy frontend backend
app backend
db backend
2
proxy db
app proxy
```

Output:
```
YES
YES
```

`proxy` is connected to both `frontend` and `backend`, so it can reach everything in either network.

## Constraints

- 1 ≤ N ≤ 50
- 1 ≤ Q ≤ 100
- Each container belongs to at least 1 network.
- Container names in queries always appear in the container list.
- Network and container names are lowercase alphanumeric strings.
