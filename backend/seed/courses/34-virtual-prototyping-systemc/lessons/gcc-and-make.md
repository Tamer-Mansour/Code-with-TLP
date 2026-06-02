# Building Code with gcc and make

SystemC is a C++ library. Every VP you write must be compiled and linked before it can run. `gcc`/`g++` is the compiler; `make` is the build orchestrator that decides what needs recompiling and in what order. These are the two most important tools in the VP build chain.

---

## gcc / g++ — The Compiler

`gcc` compiles C; `g++` compiles C++. SystemC always requires `g++`.

### Basic compilation pipeline

```
Source (.cpp) → Preprocessor → Compiler → Assembler → Object (.o) → Linker → Binary
```

Each stage has a corresponding flag to stop early:

| Flag | Stop after | Output |
|------|-----------|--------|
| `-E` | Preprocessing | `.i` (expanded source) |
| `-S` | Compilation | `.s` (assembly) |
| `-c` | Assembly | `.o` (object file) |
| (none) | Linking | executable |

### Compiling a SystemC file

```bash
# Compile one source file to an object file
g++ -c -std=c++17 \
    -I/opt/systemc-3.0/include \
    -o initiator.o \
    initiator.cpp

# Link all objects into an executable
g++ -std=c++17 \
    -L/opt/systemc-3.0/lib-linux64 \
    -o sim_top \
    initiator.o target.o main.o \
    -lsystemc -lpthread

# One-shot compile + link (small projects only)
g++ -std=c++17 \
    -I/opt/systemc-3.0/include \
    -L/opt/systemc-3.0/lib-linux64 \
    -o sim_top main.cpp initiator.cpp target.cpp \
    -lsystemc -lpthread
```

### Important g++ flags for VP work

| Flag | Purpose |
|------|---------|
| `-std=c++17` | Use C++17 standard (required by SystemC 3.x) |
| `-I<dir>` | Add header search directory |
| `-L<dir>` | Add library search directory |
| `-l<name>` | Link with `lib<name>.so` or `lib<name>.a` |
| `-O2` | Optimise (faster simulation) |
| `-g` | Include debug symbols (for gdb) |
| `-Wall -Wextra` | Enable warnings |
| `-DDEBUG` | Define a preprocessor macro |
| `-pthread` | Link POSIX threads |
| `-rpath <dir>` | Embed library path in the binary |

---

## make — Build Automation

Typing long `g++` commands by hand is error-prone. `make` reads a `Makefile` that describes the build graph and recompiles only what changed.

### Makefile structure

```makefile
# Variables
CXX       := g++
CXXFLAGS  := -std=c++17 -Wall -O2
SYSTEMC   := /opt/systemc-3.0
INC       := -I$(SYSTEMC)/include
LIBS      := -L$(SYSTEMC)/lib-linux64 -lsystemc -lpthread
BUILD     := build/obj

# Target: prerequisite(s)
#   <TAB> recipe

SRCS := initiator.cpp target.cpp main.cpp
OBJS := $(patsubst %.cpp,$(BUILD)/%.o,$(SRCS))

all: sim_top

sim_top: $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

$(BUILD)/%.o: src/%.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $(INC) -c -o $@ $<

$(BUILD):
	mkdir -p $(BUILD)

clean:
	rm -rf build/ sim_top

.PHONY: all clean
```

### Running make

```bash
# Build the default target (first target = "all")
make

# Build a specific target
make clean

# Parallel build — use N cores
make -j8

# Dry run — show what would be done without doing it
make -n

# Force rebuild everything
make -B

# Verbose — show each command
make VERBOSE=1
```

### Automatic variables in Makefiles

| Variable | Expands to |
|----------|-----------|
| `$@` | Target name |
| `$<` | First prerequisite |
| `$^` | All prerequisites |
| `$*` | Stem (matched by `%`) |

---

## Dependency Tracking

If `initiator.cpp` includes `initiator.h` and you change the header, `make` needs to know it should recompile `initiator.o`. Generate dependency files automatically:

```makefile
DEPFLAGS := -MMD -MP
$(BUILD)/%.o: src/%.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $(INC) $(DEPFLAGS) -c -o $@ $<

# Include generated .d files
-include $(OBJS:.o=.d)
```

`-MMD` generates a `.d` file alongside each `.o` listing all headers it depends on. `-include` silently skips them if they do not exist yet (first build).

---

## Worked Example — Full Build and Run

```bash
# 1. Set environment
export SYSTEMC_HOME=/opt/systemc-3.0
export LD_LIBRARY_PATH=$SYSTEMC_HOME/lib-linux64:$LD_LIBRARY_PATH

# 2. Build with 8 parallel jobs
make -j8
# g++ -std=c++17 -Wall -O2 -I/opt/systemc-3.0/include -c -o build/obj/initiator.o src/initiator.cpp
# g++ -std=c++17 -Wall -O2 -I/opt/systemc-3.0/include -c -o build/obj/target.o src/target.cpp
# g++ -std=c++17 -Wall -O2 -I/opt/systemc-3.0/include -c -o build/obj/main.o src/main.cpp
# g++ -std=c++17 -o sim_top build/obj/initiator.o build/obj/target.o build/obj/main.o -lsystemc -lpthread

# 3. Run the simulation
./sim_top
# SystemC 3.0 --- Jun  1 2025 10:22:14
#         Copyright (c) 1996-2024 Accellera. All Rights Reserved.
# TLM-2.0 transport ok. Total time: 100 ns

# 4. Clean up
make clean
```

---

## Common Build Errors

| Error message | Likely cause |
|--------------|-------------|
| `fatal error: systemc.h: No such file` | `-I` path is wrong |
| `cannot find -lsystemc` | `-L` path is wrong or library not built |
| `undefined reference to sc_main` | `main()` not declared as `int sc_main(int, char**)` |
| `error: 'sc_module' was not declared` | Missing `#include "systemc.h"` |

> **Interview answer:** `g++` compiles C++ source to object files and links them into a binary using `-I` for headers and `-L/-l` for libraries. `make` reads a Makefile that describes the dependency graph and recompiles only changed files, using `-j` for parallel jobs to speed up large SystemC builds.
