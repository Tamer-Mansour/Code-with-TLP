# Build Dependency Ordering

Before `make` can build a target it must build all prerequisites first — and those prerequisites may have their own prerequisites. This chain of dependencies forms a **directed acyclic graph (DAG)**. `make` performs a topological sort of that graph to find a valid build order, then executes only the rules whose targets are out-of-date.

## What Is a Build DAG?

Each node in the DAG is a build artifact (source file, object file, or final binary). Each directed edge means "A depends on B" (so B must exist before A can be built).

```
sim
├── main.o
│   ├── main.cpp
│   └── cpu_model.h
├── cpu_model.o
│   ├── cpu_model.cpp
│   └── cpu_model.h
└── libsystemc.a  (external)
```

If `cpu_model.h` is modified, `make` traverses the graph and determines that both `cpu_model.o` and `main.o` are stale and must be rebuilt before `sim` is relinked.

## Topological Sort

A **topological sort** of the DAG produces an order where every node comes after all of its dependencies. There may be multiple valid orderings; `make` picks one deterministically.

Example: for the graph above, one valid build order is:

1. `cpu_model.h` (source, already exists)
2. `cpu_model.cpp` (source, already exists)
3. `main.cpp` (source, already exists)
4. `cpu_model.o`
5. `main.o`
6. `sim`

If the DAG has a cycle (A depends on B and B depends on A), no topological sort is possible and `make` reports an error: `Circular dependency dropped`.

## Parallel Builds (`-j`)

Once the topological sort is known, nodes that have no dependency relationship can be built in parallel. `make -j4` launches up to 4 build jobs simultaneously:

```bash
make -j$(nproc)    # use all CPU cores
```

For a large SystemC VP with 50 source files, parallel compilation can cut build time from 60 seconds to 10 seconds. The final link step must still wait for all `.o` files.

## Minimal Rebuilds

The power of the DAG is that `make` only rebuilds stale targets:

| Change | What rebuilds |
|--------|--------------|
| Edit `cpu_model.cpp` | `cpu_model.o`, `sim` |
| Edit `cpu_model.h` | `cpu_model.o`, `main.o`, `sim` |
| Edit `main.cpp` | `main.o`, `sim` |
| No changes | Nothing (`make: 'sim' is up to date`) |

This requires that your Makefile lists **all** true prerequisites, including headers. Missing a header dependency means `make` won't rebuild when that header changes — a silent correctness bug.

## Checking Dependencies Automatically

As covered in the Makefile lesson, the `-MMD` compiler flag generates `.d` files that `make` includes to learn the correct header dependencies automatically:

```makefile
DEPFLAGS := -MMD -MP -MF $*.d
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(DEPFLAGS) -c $< -o $@
-include $(OBJS:.o=.d)
```

## Order-Only Prerequisites

Sometimes a target depends on a directory existing but shouldn't rebuild if the directory's timestamp changes. Use `|` to declare an order-only prerequisite:

```makefile
build/cpu_model.o: cpu_model.cpp | build/
	$(CXX) $(CXXFLAGS) -c $< -o $@

build/:
	mkdir -p $@
```

## Common Pitfalls

- **Under-specified prerequisites** — missing a header means stale rebuilds when the header changes.
- **Over-specified prerequisites** — listing an unnecessary prerequisite causes unnecessary rebuilds.
- **Forced targets** — some Makefiles use `.FORCE` as a prerequisite to always rebuild; this defeats incremental builds unless truly needed.
- **Non-deterministic ordering** — if two recipes can run in any order and both write the same file, parallel builds race. Ensure each output file is written by exactly one recipe.

## Interview Answer

> "Build dependencies form a DAG. A topological sort gives a valid build order where every target is built after its prerequisites. `make` only rebuilds targets that are stale (a prerequisite is newer), and `-j` exploits the DAG to build independent targets in parallel."
