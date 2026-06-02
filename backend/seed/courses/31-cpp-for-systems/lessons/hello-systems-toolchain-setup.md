# Setting Up g++/clang++, -std, and Your First Build

Before writing any systems code you need a working toolchain. This lesson walks through installing g++ and clang++, understanding the most important compiler flags, and building a multi-file project from scratch.

## Installing the Compiler

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install build-essential clang
g++ --version
clang++ --version
```

`build-essential` installs g++, the GNU linker, and the standard library headers.

### macOS

```bash
xcode-select --install     # installs Apple clang
brew install gcc           # optional: upstream GCC via Homebrew
clang++ --version
```

On macOS, `g++` is typically an alias for Apple's clang. To use upstream GCC, call it as `g++-13` (version number varies).

### Windows

Options in order of least friction:

1. **WSL 2** (Windows Subsystem for Linux) — install Ubuntu then follow the Linux steps above.
2. **MSYS2 / MinGW-w64** — provides a native Windows `g++`.
3. **MSVC** (`cl.exe`) — included with Visual Studio; supports the same standards.

## Essential Compiler Flags

| Flag | Meaning |
|---|---|
| `-std=c++17` | Use the C++17 standard (also: `c++14`, `c++20`, `c++23`) |
| `-Wall` | Enable all common warnings |
| `-Wextra` | Enable extra warnings beyond `-Wall` |
| `-Werror` | Treat warnings as errors (recommended for CI) |
| `-O2` | Optimization level 2 (good default for release) |
| `-O0 -g` | No optimization + debug symbols (good for debugging) |
| `-o outfile` | Specify output file name |
| `-c` | Compile only — produce `.o`, do not link |
| `-I/path` | Add directory to header search path |
| `-L/path` | Add directory to library search path |
| `-lfoo` | Link against `libfoo.a` or `libfoo.so` |

Always develop with at least `-Wall -Wextra`. Many real bugs are caught as warnings.

## Your First Single-File Build

```cpp
// hello.cpp
#include <iostream>

int main() {
    std::cout << "Systems ready.\n";
    return 0;
}
```

```bash
g++ -std=c++17 -Wall -Wextra -o hello hello.cpp
./hello
```

Expected output:

```
Systems ready.
```

## Multi-File Build

Real projects span many files. Here is a minimal two-file example:

```cpp
// math.h
#pragma once
int square(int x);
```

```cpp
// math.cpp
#include "math.h"
int square(int x) { return x * x; }
```

```cpp
// main.cpp
#include <iostream>
#include "math.h"

int main() {
    std::cout << square(7) << "\n";
}
```

Build in two steps (compile separately, then link):

```bash
g++ -std=c++17 -Wall -c math.cpp -o math.o
g++ -std=c++17 -Wall -c main.cpp -o main.o
g++ math.o main.o -o program
./program
```

Or in one command (g++ handles the steps internally):

```bash
g++ -std=c++17 -Wall math.cpp main.cpp -o program
```

## Checking the Standard

To confirm which standard your compiler supports:

```bash
g++ --version
g++ -std=c++20 -x c++ - < /dev/null 2>&1 | head -1
```

If you get `error: unrecognized command line option '-std=c++20'`, your compiler is too old.

## clang++ vs g++

Both are production-quality compilers that support the same flags. Key differences:

| Property | g++ | clang++ |
|---|---|---|
| Error messages | Good | Often more readable |
| Sanitizers | Supported | Also supported, sometimes faster |
| LTO | Supported | Full LTO via LLVM |
| Default on macOS | Alias for clang | Native clang |
| Default on Linux | Native GCC | Needs installation |

For learning, use either. In CI, many projects compile with both to catch compiler-specific issues.

## Inspecting What Was Built

```bash
file program          # shows ELF/PE/Mach-O and bitness
nm program            # list symbols
ldd program           # list shared library dependencies (Linux)
otool -L program      # equivalent on macOS
```

## Common Pitfall

Omitting `-std=c++17` (or whichever standard you need) causes features from that standard to be unavailable or silently interpreted differently. Always specify the standard explicitly — never rely on the compiler default, which varies between GCC versions and distributions.

> **Interview answer:** "Install g++ or clang++ via your package manager, always specify `-std=c++17` (or the required standard), enable warnings with `-Wall -Wextra`, and compile with `-O0 -g` for debugging or `-O2` for release. For multi-file projects, compile each `.cpp` to a `.o` with `-c`, then link them together. Both g++ and clang++ support the same flags; clang++ often produces clearer error messages."
