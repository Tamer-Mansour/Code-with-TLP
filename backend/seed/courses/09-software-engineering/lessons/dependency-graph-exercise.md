# Exercise: Dependency Graph Cycle Detector

A key design quality metric is keeping your module dependency graph **acyclic**. Circular dependencies — where module A depends on B, B depends on C, and C depends back on A — violate good coupling principles and create serious practical problems:

- **Build failures:** many build tools cannot resolve circular dependencies
- **Testing difficulties:** you cannot test module A in isolation without also loading B and C
- **Tight coupling:** a change in any one module in the cycle forces re-evaluation of all others
- **Conceptual confusion:** if A depends on B and B depends on A, which one is "higher level"?

The **Dependency Inversion Principle** (the D in SOLID) exists precisely to break cycles: introduce an abstraction (interface) that both modules depend on, so neither depends directly on the other.

**Free resource:** *Software Engineering: A Modern Approach* by Marco Tulio Valente — [softengbook.org](https://softengbook.org/) — discusses module coupling and dependency management in Chapter 5.

## Task

Given a directed dependency graph of software modules (an edge A → B means "A depends on B"), determine whether any circular dependency (cycle) exists.

- If a **cycle** exists: print `CYCLE DETECTED` and list one cycle as space-separated module names (starting and ending at the same node).
- If **no cycle** exists: print `NO CYCLE` and print the modules in a valid build/load order (topological sort — dependencies before dependents).

## Input Format

```
N M
module_1
module_2
...
module_N
A B        ← A depends on B (edge A → B)
...
```

- First line: `N` (modules) and `M` (dependency edges)
- Next `N` lines: module names (one per line)
- Next `M` lines: each has two module names `A B` meaning A depends on B

## Output Format

**No cycle:**
```
NO CYCLE
module_a module_b module_c ...
```

**Cycle found:**
```
CYCLE DETECTED
module_x module_y module_z module_x
```

## Example

**Input:**
```
4 3
auth
database
utils
config
auth database
database utils
auth config
```

**Output:**
```
NO CYCLE
auth config database utils
```

## Hints

- Use **Kahn's algorithm** (BFS-based topological sort): repeatedly remove nodes with in-degree 0. If all nodes are removed, no cycle exists. If any nodes remain, they form cycles.
- To find and report a specific cycle, use DFS with a recursion stack on the remaining nodes after Kahn's detects a cycle.
- Sort neighbours before processing to get deterministic output.
