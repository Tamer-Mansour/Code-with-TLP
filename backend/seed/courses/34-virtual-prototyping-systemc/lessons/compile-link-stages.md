# Preprocess, Compile, Assemble, Link

Building a C++ program is not a single step — it is a four-stage pipeline. Understanding each stage is essential for debugging build errors, optimizing compilation, and understanding how SystemC virtual platforms are assembled from many source files.

## The Four Stages

| Stage | Input | Output | Tool |
|-------|-------|--------|------|
| Preprocess | `.cpp` + headers | Expanded `.i` file | `cpp` / compiler front-end |
| Compile | `.i` expanded source | Assembly `.s` | `cc1plus` (inside `g++`) |
| Assemble | `.s` assembly | Object file `.o` | `as` |
| Link | `.o` files + libraries | Executable or `.so` | `ld` (via `g++`) |

### Stage 1 — Preprocessing

The preprocessor handles directives that start with `#`. It expands macros, includes header files recursively, and strips comments.

```bash
g++ -E main.cpp -o main.i   # stop after preprocessing
```

Common pitfalls: circular includes, missing include guards, and macros that silently change expressions.

### Stage 2 — Compilation

The compiler translates preprocessed C++ into target-specific assembly. This is where syntax checking, type checking, template instantiation, and optimisation happen.

```bash
g++ -S main.i -o main.s     # stop after compiling to assembly
```

The assembly output is human-readable and useful for understanding what the compiler actually generates for a piece of code.

### Stage 3 — Assembly

The assembler converts assembly mnemonics into machine-code bytes stored in an **object file** (`.o` / `.obj`). Each object file contains:

- **Text section** — compiled machine code
- **Data section** — initialised global variables
- **BSS section** — uninitialised globals (just a size, no bytes on disk)
- **Symbol table** — names exported or imported by this translation unit

```bash
as main.s -o main.o         # assemble manually
```

### Stage 4 — Linking

The linker resolves external symbol references across object files and libraries, then combines everything into a single executable or shared library.

```bash
g++ main.o helper.o -lsystemc -L/opt/systemc/lib -o sim
```

Linker errors ("undefined reference") mean a symbol was declared but its definition was never provided to the linker.

## Seeing All Stages at Once

```bash
# Run all four stages explicitly
g++ -c main.cpp -o main.o       # preprocess + compile + assemble
g++ main.o -lsystemc -o sim     # link
```

The shorthand `g++ main.cpp -o sim` does all four automatically.

## Worked Example — SystemC Helo World

```cpp
// main.cpp
#include <systemc.h>         // pulled in at preprocess time

SC_MODULE(Top) {
    SC_CTOR(Top) {}
};

int sc_main(int, char**) {
    Top top("top");
    sc_start();
    return 0;
}
```

Build steps:

```bash
# 1. Compile the translation unit
g++ -c main.cpp -I/opt/systemc/include -o main.o

# 2. Link against the SystemC static library
g++ main.o -L/opt/systemc/lib -lsystemc -lpthread -o sim

# 3. Run
./sim
```

## Common Pitfalls

- **Forgetting `-I`** — compiler cannot find `systemc.h` and fails at stage 1.
- **Forgetting `-L` / `-l`** — linker cannot find `libsystemc.a` and fails at stage 4.
- **ODR violations** — defining the same symbol in two `.o` files causes a linker error or silent bad behaviour.

## Interview Answer

> "C++ compilation is a four-stage pipeline: the **preprocessor** expands macros and includes, the **compiler** turns C++ into assembly, the **assembler** creates an object file, and the **linker** resolves cross-file symbols and produces the final executable."
