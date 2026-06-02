# Exercise: Compute a Topological Build Order from Dependencies

## Problem Statement

Build systems like `make` determine build order by topologically sorting a dependency graph. Given a set of build targets and their dependencies, compute a valid build order (topological sort). If the graph contains a cycle, report it.

## Input Format

```
N
target1: dep1a dep1b ...
target2: dep2a ...
...
```

- Line 1: integer `N` (1 ≤ N ≤ 100) — number of targets.
- Lines 2 through N+1: each line has the form `name: dep1 dep2 ...`
  - `name` is the target; everything after the colon (and optional whitespace) is a space-separated list of dependencies.
  - A target with no dependencies has an empty list after the colon.
  - All names are non-empty alphanumeric strings (letters, digits, dots, underscores, hyphens).
  - Every dependency name is guaranteed to be a target defined on another line.

## Output Format

- **No cycle:** print each target on its own line in a valid topological order. When multiple orderings are valid, print in **lexicographic (alphabetical) order** — i.e., at each step choose the available node with the smallest name.
- **Cycle detected:** print exactly:
  ```
  CYCLE DETECTED
  ```

Trailing newline after the last line is acceptable.

## Constraints

- 1 ≤ N ≤ 100
- Each target name length: 1–40 characters
- No self-loops in the input

## Algorithm Hint

Use **Kahn's algorithm**:
1. Compute in-degree for every node.
2. Initialise a min-heap with all nodes whose in-degree is 0.
3. Pop the lexicographically smallest node, add it to the result, and decrement the in-degree of its dependents.
4. Push any dependent whose in-degree drops to 0.
5. If the result list length equals N, output it; otherwise output `CYCLE DETECTED`.

## Sample Input 1

```
5
sim: main.o cpu.o
main.o: main.cpp
cpu.o: cpu.cpp
main.cpp:
cpu.cpp:
```

## Sample Output 1

```
cpu.cpp
cpu.o
main.cpp
main.o
sim
```

## Sample Input 2 (Cycle)

```
3
a: b
b: c
c: a
```

## Sample Output 2

```
CYCLE DETECTED
```

## Sample Input 3 (Single Node)

```
1
libfoo.a:
```

## Sample Output 3

```
libfoo.a
```
