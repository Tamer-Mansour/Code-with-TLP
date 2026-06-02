# -g, Optimization Levels, and Debug vs Release

Understanding the difference between a debug build and a release build is foundational. Using the wrong build for the wrong task leads either to impossible-to-debug crashes or to performance numbers that don't reflect production reality.

## Debug Symbols: The `-g` Flag

By default, a compiled binary contains only machine code — no function names, no variable names, no line numbers. The `-g` flag embeds DWARF (Debugging With Attributed Record Format) metadata into the binary so that debuggers like gdb can map machine instructions back to source code.

```bash
g++ -g -o program program.cpp        # debug symbols, no optimization
g++ -g3 -o program program.cpp       # maximum debug info (macro definitions too)
g++ -ggdb -o program program.cpp     # DWARF format tuned for gdb specifically
```

Without `-g`, a gdb session shows only assembly addresses:

```
(gdb) bt
#0  0x00007f8a3c12 in ?? ()
#1  0x00007f8a3c45 in ?? ()
```

With `-g`, you get human-readable context:

```
(gdb) bt
#0  crash_here (ptr=0x0) at main.cpp:17
#1  main () at main.cpp:42
```

## Optimization Levels

The `-O` flag controls how aggressively the compiler transforms code to improve speed or reduce size.

| Flag | Name | Effect |
|------|------|--------|
| `-O0` | No optimization | Code matches source exactly; fastest compilation |
| `-O1` | Basic | Simple optimizations, no significant trade-offs |
| `-O2` | Standard release | Inlining, loop unrolling, vectorization; most projects use this |
| `-O3` | Aggressive | All of `-O2` plus more transformations; may increase binary size |
| `-Os` | Size-optimized | Minimize binary size; useful for embedded targets |
| `-Og` | Debug-friendly | Light optimizations that preserve debuggability |

## Debug vs Release Builds

These two configurations serve completely different goals.

**Debug build:**
```bash
g++ -g -O0 -DDEBUG -o program_debug program.cpp
```
- Full debug symbols, no optimization
- Variables exist where you expect them; stepping works line by line
- Assertions and debug-only code (`#ifdef DEBUG`) are compiled in
- Typically 2–10x slower than release

**Release build:**
```bash
g++ -O2 -DNDEBUG -o program_release program.cpp
```
- No debug symbols (or stripped after build)
- `assert()` calls are compiled out (`NDEBUG` disables them)
- Inlining and reordering make the binary hard to follow in a debugger
- This is the build that must pass performance benchmarks

## The Optimization-Debuggability Conflict

Optimization is the enemy of debuggability. At `-O2`, the compiler may:

- Eliminate variables that were "never used" in the optimized sense
- Reorder instructions to fill CPU pipelines
- Inline functions so they disappear from the call stack
- Hold values in registers rather than memory

```bash
# Attempting to print a variable in gdb under -O2
(gdb) print count
$1 = <optimized out>
```

This is why `-Og` exists — it applies only the optimizations that do not obscure the source-level view, making it the best choice for day-to-day development on performance-sensitive code.

## Stripping Symbols from Release Binaries

```bash
# Build with symbols first (useful for crash analysis)
g++ -O2 -g -o program program.cpp

# Strip symbols for deployment
strip program

# Or split symbols into a separate file
objcopy --only-keep-debug program program.debug
strip --strip-debug program
```

Keeping a `.debug` file archived alongside each release build lets you load it into gdb later if a core dump arrives from the field.

## Worked Example: CMake Config

```cmake
# Debug configuration
set(CMAKE_BUILD_TYPE Debug)
# CMake sets -g -O0 automatically

# Release configuration
set(CMAKE_BUILD_TYPE Release)
# CMake sets -O3 -DNDEBUG automatically

# RelWithDebInfo — useful for profiling
set(CMAKE_BUILD_TYPE RelWithDebInfo)
# CMake sets -O2 -g -DNDEBUG
```

`RelWithDebInfo` is a practical middle ground for profiling: optimized code with symbols intact so profilers can attribute hot paths to actual functions.

> **Interview answer:** `-g` embeds DWARF debug symbols so gdb can map addresses to source lines and variables. `-O0` disables optimization so the program's runtime behavior matches the source exactly. A release build uses `-O2 -DNDEBUG` for performance, while a debug build uses `-g -O0` for debuggability — you should never debug a stripped release binary without a matching symbol file.
