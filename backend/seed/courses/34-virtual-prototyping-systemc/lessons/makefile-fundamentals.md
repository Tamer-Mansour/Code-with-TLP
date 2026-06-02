# Makefile Fundamentals: Targets and Rules

`make` is the standard build orchestration tool for C and C++ projects, including SystemC virtual platforms. A `Makefile` describes **what** to build, **how** to build it, and — crucially — **when** to rebuild based on file timestamps. Understanding Makefiles lets you read, debug, and extend the build systems you will find in every open-source SystemC project.

## Anatomy of a Rule

```makefile
target: prerequisite1 prerequisite2
	recipe line 1
	recipe line 2
```

- **target** — the file to produce (or a phony name like `all`, `clean`).
- **prerequisites** — files that the target depends on.
- **recipe** — shell commands that produce the target. **Must be indented with a real TAB character, not spaces.**

`make` rebuilds a target only when a prerequisite is newer than the target. This is the key to incremental builds.

## A Minimal SystemC Makefile

```makefile
# Variables
CXX      := g++
CXXFLAGS := -std=c++17 -Wall -I/opt/systemc/include
LDFLAGS  := -L/opt/systemc/lib
LDLIBS   := -lsystemc -lpthread

# Default target (first rule wins)
all: sim

# Executable
sim: main.o cpu_model.o bus_model.o
	$(CXX) $^ $(LDFLAGS) $(LDLIBS) -o $@

# Object files
main.o: main.cpp cpu_model.h bus_model.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

cpu_model.o: cpu_model.cpp cpu_model.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

bus_model.o: bus_model.cpp bus_model.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Phony targets
.PHONY: clean all

clean:
	rm -f *.o sim
```

## Automatic Variables

| Variable | Meaning |
|----------|---------|
| `$@` | The target name |
| `$<` | The first prerequisite |
| `$^` | All prerequisites (space-separated, duplicates removed) |
| `$*` | The stem of a pattern rule (the `%` part) |

## Pattern Rules

Repeating a compile rule for every file is tedious. A **pattern rule** generalises it:

```makefile
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@
```

Now any `.o` file can be built from the corresponding `.cpp` without an explicit rule.

## Phony Targets

A phony target is a recipe with no corresponding file:

```makefile
.PHONY: clean run

clean:
	rm -f *.o sim

run: sim
	./sim
```

Declaring `.PHONY` prevents `make` from treating `clean` as a file to check timestamps on.

## Variables and Overriding

Makefiles use `=` (recursively expanded) or `:=` (simply expanded, preferred):

```makefile
BUILD := debug
CXXFLAGS := -std=c++17

# Override on command line:
# make BUILD=release CXXFLAGS="-std=c++17 -O2"
```

## Automatic Dependency Generation

The biggest weakness of hand-written Makefiles is that they miss header changes. The fix is to generate `.d` dependency files automatically:

```makefile
DEPFLAGS = -MT $@ -MMD -MP -MF $*.d
DEPS     := $(OBJS:.o=.d)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(DEPFLAGS) -c $< -o $@

-include $(DEPS)    # the leading '-' ignores missing .d files on first build
```

`-MMD` tells the compiler to write a `.d` file listing every header included. `make` reads these on subsequent runs and rebuilds the right `.o` files when headers change.

## Common Pitfalls

- **Spaces instead of TAB** — `make` will error with `missing separator`.
- **Wrong prerequisite order** — if a prerequisite is missing from the list, `make` won't rebuild the target when that file changes.
- **Circular dependencies** — `make` detects these and reports an error.
- **Forgetting `.PHONY`** — if a file named `clean` exists, `make clean` does nothing.

## Interview Answer

> "A Makefile rule has three parts: the target, its prerequisites, and the recipe. `make` rebuilds a target only when a prerequisite is newer than the target, enabling fast incremental builds. Pattern rules and automatic dependency generation eliminate boilerplate and keep header changes tracked."
