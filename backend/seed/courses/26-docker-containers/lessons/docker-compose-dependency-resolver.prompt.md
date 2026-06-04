# Docker Compose Dependency Resolver

## Problem

Docker Compose starts services in **dependency order** based on `depends_on`. Given a list of services and their dependencies, output a valid startup order (topological sort).

If there is a **circular dependency**, print `CIRCULAR DEPENDENCY DETECTED`.

When multiple services are ready to start simultaneously (no outstanding dependencies), start them in **alphabetical order**.

## Input Format

```
N
service_name dep1 dep2 ...
service_name
...
```

- First line: `N` — number of services.
- Next `N` lines: service name followed by zero or more dependency names (space-separated).
- A service with no dependencies is listed with its name only.

## Output Format

Valid startup order, one service per line. If a circular dependency exists, print exactly:

```
CIRCULAR DEPENDENCY DETECTED
```

## Example 1

Input:
```
5
nginx app
app api db
db
redis
api redis db
```

Output:
```
db
redis
api
app
nginx
```

**Explanation:**
- `db` and `redis` have no dependencies → start first, alphabetically: `db`, then `redis`.
- `api` depends on `redis` and `db` — both now started → start `api`.
- `app` depends on `api` and `db` — both started → start `app`.
- `nginx` depends on `app` — started → start `nginx`.

## Example 2

Input:
```
3
a b
b c
c a
```

Output:
```
CIRCULAR DEPENDENCY DETECTED
```

`a → b → c → a` forms a cycle.

## Example 3

Input:
```
4
worker queue db
queue db
db
cache
```

Output:
```
cache
db
queue
worker
```

`cache` has no dependencies and starts first (alphabetically before `db`).

## Constraints

- 1 ≤ N ≤ 20
- Service names are lowercase alphanumeric strings.
- Dependency names always refer to services in the list.
- No duplicate service names.
