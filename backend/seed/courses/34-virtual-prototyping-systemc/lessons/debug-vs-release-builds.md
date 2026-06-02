# Debug vs Release Builds and Flags

Every C++ project, including SystemC virtual platforms, should be built in at least two configurations: **debug** for development and **release** for performance measurement and delivery. Mixing flags from the two modes or using the wrong mode for the task at hand is a common source of confusion.

## The Core Trade-off

| Feature | Debug | Release |
|---------|-------|---------|
| Compiler optimisation | None (`-O0`) | Aggressive (`-O2` / `-O3`) |
| Debug symbols | Yes (`-g`) | No (or stripped) |
| Assertions | Enabled | Disabled (`-DNDEBUG`) |
| Binary size | Large | Small |
| Simulation speed | Slow | Fast |
| GDB / debugger usability | Excellent | Poor (inlined, reordered code) |

## Debug Build Flags

```makefile
# Debug configuration
CXXFLAGS_DBG := -std=c++17 -Wall -Wextra \
                -O0 \          # no optimisation — preserves program structure
                -g3 \          # maximum debug info (includes macro definitions)
                -fsanitize=address,undefined \  # catch memory bugs at runtime
                -fno-omit-frame-pointer
LDFLAGS_DBG  := -fsanitize=address,undefined
```

`-g3` stores variable names, source file references, and macro expansions in the ELF `.debug_*` sections so that GDB can display them.

`-fsanitize=address` (ASan) instruments every memory access to detect out-of-bounds reads/writes and use-after-free — invaluable when debugging a complex virtual platform.

## Release Build Flags

```makefile
# Release configuration
CXXFLAGS_REL := -std=c++17 -Wall \
                -O2 \          # good balance of speed and compile time
                -DNDEBUG \     # disables assert() and SC_ASSERT
                -march=native  # tune for the host CPU (do not use when cross-compiling)
```

`-O3` enables additional optimisations like auto-vectorisation and aggressive inlining. Profile-guided optimisation (`-fprofile-generate` + `-fprofile-use`) can further improve hotspots.

## Switching Configurations in a Makefile

```makefile
BUILD ?= debug

ifeq ($(BUILD),debug)
  CXXFLAGS += -O0 -g3 -fsanitize=address,undefined
  LDFLAGS  += -fsanitize=address,undefined
else ifeq ($(BUILD),release)
  CXXFLAGS += -O2 -DNDEBUG
endif

# Usage:
#   make             -> debug (default)
#   make BUILD=release
```

## SystemC-Specific Considerations

- SystemC's `SC_ASSERT` macro respects `NDEBUG` — always define it in release builds to eliminate assertion overhead in the kernel.
- Debug builds of a large virtual platform can run **10–50x slower** than release builds because of the overhead of ASan, no inlining, and no vectorisation.
- Use **debug build** when tracking down simulation bugs or using a waveform viewer; use **release build** when measuring execution time or running long regression suites.

## Separating Object Directories

Debug and release builds should produce separate `.o` files to avoid mixing incompatible objects:

```makefile
OBJ_DIR := build/$(BUILD)

$(OBJ_DIR)/%.o: %.cpp | $(OBJ_DIR)/
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJ_DIR)/:
	mkdir -p $@
```

## Common Pitfalls

- **Debugging an optimised binary** — GDB shows wrong variable values or cannot set breakpoints on certain lines. Always use `-O0 -g` for debug sessions.
- **Shipping a debug binary** — includes symbol tables (large, slow) and may expose internal structure names.
- **`assert()` in production** — omitting `-DNDEBUG` from release builds leaves assertion checks that abort the program on unexpected conditions.

## Interview Answer

> "Debug builds use `-O0 -g` to preserve program structure for the debugger and may add sanitisers. Release builds use `-O2 -DNDEBUG` for maximum performance and minimal binary size. Never mix objects from the two configurations in the same link."
