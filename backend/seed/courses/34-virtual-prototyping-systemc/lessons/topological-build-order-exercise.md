# Compute a Topological Build Order from Dependencies

Build systems like `make` determine which targets to build and in what order by performing a **topological sort** of the dependency graph. In this exercise, you will implement that algorithm from scratch.

## What You Will Implement

Given a list of build targets and their dependencies, compute a valid topological build order — an order in which every target appears **after** all of its dependencies.

If the dependency graph contains a **cycle** (circular dependency), your program must detect it and output `CYCLE DETECTED` instead.

## Why This Matters

Understanding topological sort is essential for:

- Reasoning about why `make` builds things in the order it does.
- Diagnosing `Circular dependency` errors in Makefiles.
- Implementing custom build orchestrators or task schedulers.

## Input Format

- First line: `N` — the number of targets (1 ≤ N ≤ 100).
- Next `N` lines, each: `target: dep1 dep2 ...` — the target name followed by a colon, then zero or more space-separated dependencies. A target with no dependencies still appears with an empty right-hand side.

All names are alphanumeric strings. Every dependency listed is guaranteed to appear as a target on its own line.

## Output Format

- If no cycle: print the targets in a valid topological order, one per line. If multiple valid orders exist, output them in **lexicographic order** (sort nodes with equal priority alphabetically).
- If a cycle exists: print exactly `CYCLE DETECTED`.

## Sample

**Input:**
```
5
sim: main.o cpu.o
main.o: main.cpp
cpu.o: cpu.cpp
main.cpp:
cpu.cpp:
```

**Output:**
```
cpu.cpp
cpu.o
main.cpp
main.o
sim
```

## Getting Started

Your solution should:

1. Parse the input into a dependency graph.
2. Compute in-degree for each node.
3. Use Kahn's algorithm (BFS-based topological sort) with a min-heap / sorted queue to produce lexicographic ordering.
4. If not all nodes were processed, report `CYCLE DETECTED`.

```python
import sys

def solve():
    data = sys.stdin.read().splitlines()
    # TODO: parse, build graph, topological sort
    pass

solve()
```
