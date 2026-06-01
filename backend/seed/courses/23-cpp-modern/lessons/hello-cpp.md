# Hello, Modern C++

C++ is a compiled, multi-paradigm systems language with deep history. "Modern C++" — roughly C++11 onward — is a different language from the C++98 your parents used: cleaner syntax, RAII, smart pointers, lambdas, modules. We focus on C++17 / C++20 here.

## Install a modern toolchain

You want:

- A C++20-capable compiler: **GCC 11+**, **Clang 13+**, or **MSVC 19.30+**.
- A build system: **CMake** is the de-facto standard.

```bash
# macOS
brew install gcc cmake
# Ubuntu
sudo apt install -y g++-12 cmake
# Windows: install Visual Studio with C++ workload, or LLVM clang
```

## A first program

`hello.cpp`:

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name = "Modern C++";
    std::cout << "Hello, " << name << "\n";
    return 0;
}
```

Compile and run:

```bash
g++ -std=c++20 -O2 -Wall -Wextra hello.cpp -o hello
./hello
```

`-std=c++20` enables modern features. `-Wall -Wextra` turns on warnings.

## CMake basics

```cmake
cmake_minimum_required(VERSION 3.20)
project(hello CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(hello hello.cpp)
```

```bash
cmake -B build
cmake --build build
./build/hello
```

CMake feels heavyweight at first; it's the price of cross-platform builds.

## Package management

C++ has no built-in package manager. The two main ones:

- **vcpkg** — Microsoft's; integrates with CMake.
- **Conan** — Python-based, widely used in industry.

Both fetch and build dependencies into your project.

## Headers and source files

C++ traditionally splits declarations (`.h`) and definitions (`.cpp`):

```cpp
// math.h
#pragma once
int add(int a, int b);
```

```cpp
// math.cpp
#include "math.h"
int add(int a, int b) { return a + b; }
```

C++20 introduces **modules** (`import math;`) as a faster alternative, but tool support is still uneven. Stick with headers for now in mixed teams.

## What modern C++ is good for

- Game engines (Unreal, Unity's native side).
- Trading systems, HFT.
- High-performance libraries (LLVM, TensorFlow internals).
- Embedded systems with rich features.
- Graphics, simulation, scientific computing.

## What it's painful at

- Long compile times.
- Header dependency hell (modules will help).
- Steep learning curve — language is sprawling.
- Memory bugs *if* you skip modern practices (raw pointers, manual `new`/`delete`).

## The modern style in one paragraph

Use `std::string` not `char*`. Use `std::vector` not arrays. Use `std::unique_ptr` / `std::shared_ptr` not `new`/`delete`. Use range-based `for`. Use `auto` for local types. Use lambdas. Lean on the STL algorithms. Write code that looks more like Python with types than like 1990s C.
