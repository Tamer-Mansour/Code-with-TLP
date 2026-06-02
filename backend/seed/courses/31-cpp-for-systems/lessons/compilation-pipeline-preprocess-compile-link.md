# Preprocess, Compile, Assemble, Link: The Build Pipeline

Every C++ source file goes through four distinct stages before it becomes an executable. Understanding this pipeline helps you interpret error messages accurately, diagnose linker failures, and write better build systems. Compilers hide the stages by default, but each can be inspected individually.

## The Four Stages

```
Source (.cpp)
    │
    ▼  Stage 1: Preprocessor (cpp)
Preprocessed source (.i)
    │
    ▼  Stage 2: Compiler proper (cc1plus)
Assembly (.s)
    │
    ▼  Stage 3: Assembler (as)
Object file (.o / .obj)
    │
    ▼  Stage 4: Linker (ld / lld)
Executable or shared library
```

### Stage 1 — Preprocessor

The preprocessor performs **pure text substitution** before any C++ parsing occurs. It handles:

- `#include` — copies the contents of another file in-place.
- `#define` / `#undef` — macro substitution.
- `#ifdef` / `#ifndef` / `#if` / `#endif` — conditional compilation.
- `#pragma` — compiler-specific directives.

```cpp
// main.cpp before preprocessing
#include <iostream>
#define MAX 100

int main() {
    int arr[MAX];
}
```

After preprocessing (inspect with `g++ -E main.cpp`), `MAX` becomes `100` and the contents of `<iostream>` are pasted in — often tens of thousands of lines.

```bash
g++ -E main.cpp -o main.i   # stop after preprocessing
```

### Stage 2 — Compiler Proper

The compiler parses the preprocessed source, performs type checking, optimization, and emits **assembly**. This is where most of the interesting errors occur: syntax errors, type mismatches, undeclared identifiers.

```bash
g++ -S main.cpp -o main.s   # stop after compiling, emit assembly
```

The resulting `.s` file contains human-readable assembly:

```asm
; x86-64 assembly excerpt
movl    $100, %eax
```

Optimization flags (`-O0`, `-O1`, `-O2`, `-O3`, `-Os`) are applied here. Higher optimization = more passes = slower build, faster binary.

### Stage 3 — Assembler

The assembler converts assembly mnemonics into binary **machine code** and packages the result as an **object file** (`.o` on Linux/macOS, `.obj` on Windows). Object files contain:

- Machine code for the functions defined in this translation unit.
- A **symbol table** listing exported and imported names.
- Relocation entries — placeholder addresses for symbols not yet resolved.

```bash
g++ -c main.cpp -o main.o   # stop after assembling
```

Inspect the symbol table with:

```bash
nm main.o        # Linux/macOS
```

### Stage 4 — Linker

The linker combines multiple object files and library archives (`.a` / `.lib`) into a single executable. It:

1. **Resolves symbols** — matches every "undefined reference" in one object file to a definition in another.
2. **Relocates** — fills in the actual addresses where placeholders existed.
3. **Produces the final binary** — ELF on Linux, PE/COFF on Windows, Mach-O on macOS.

```bash
g++ main.o util.o -o program   # link two object files
```

Linker errors say things like `undefined reference to 'foo'` — this means Stage 2 succeeded (the compiler saw a declaration) but the definition was never compiled and linked in.

## Running All Stages at Once

```bash
g++ -std=c++17 -O2 main.cpp util.cpp -o program
```

This runs all four stages transparently. Add `-v` to see each sub-command invoked.

## Why This Matters for Debugging

| Error type | Stage | Example message |
|---|---|---|
| Syntax / type error | Compiler | `error: expected ';'` |
| Missing declaration | Compiler | `error: 'foo' was not declared` |
| Undefined reference | Linker | `undefined reference to 'foo()'` |
| Missing library | Linker | `cannot find -lfoo` |
| Bad address at runtime | Runtime | segmentation fault |

## Common Pitfall

Forgetting to pass all `.cpp` files (or their `.o` files) to the linker. If `util.cpp` defines `helper()` and you only compile `main.cpp`, the linker will complain about an undefined reference even though the declaration was in a header you included.

> **Interview answer:** "The C++ build pipeline is: (1) Preprocessor expands macros and `#include`s, (2) Compiler parses C++ and emits assembly, (3) Assembler converts assembly to binary object files, (4) Linker combines object files, resolves symbol references, and produces the final executable. Compiler errors come from stages 1-2; linker errors come from stage 4."
